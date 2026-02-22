"""Scraper for search results."""

import hashlib
import json
import re
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional

from bs4 import BeautifulSoup
from dateutil import parser as date_parser
from selenium.webdriver.common.by import By

from ..domain.entities import SearchResult
from ..webdriver.helpers import human_delay, wait_for_element
from .base import BaseScraper


class SearchScraper(BaseScraper[SearchResult]):
    """
    Scraper for product search results.

    Extracts products from https://blix.pl/szukaj/?szukaj=<query>

    The data is in window.offers JavaScript variable:
    <script>
        window.offers = [{...}, {...}];
    </script>

    Shop names are extracted from the swiper slides at the top of the page,
    mapping leaflet IDs to brand names.
    """

    def __init__(self, driver, search_query: str, filter_by_name: bool = True) -> None:  # type: ignore[no-untyped-def]
        """
        Initialize search scraper.

        Args:
            driver: Selenium WebDriver
            search_query: Search query string
            filter_by_name: If True, only return products with query in name
        """
        super().__init__(driver)
        self.search_query = search_query
        self.filter_by_name = filter_by_name
        self.leaflet_shop_map: dict[int, str] = {}  # Map leaflet_id to shop_name

    def _wait_for_content(self) -> None:
        """Wait for search results to load."""
        # Wait a bit for dynamic content
        human_delay(3, 5)

        # Wait for results container
        try:
            wait_for_element(self.driver, By.CSS_SELECTOR, ".offer-list", timeout=10)
        except Exception:
            self._logger.debug("waiting_for_page_load")

    def _extract_entities(self, soup: BeautifulSoup, url: str) -> List[SearchResult]:
        """Extract SearchResult entities from HTML."""
        results: List[SearchResult] = []

        # Extract leaflet to shop mapping from swiper slides
        self._extract_leaflet_shop_map(soup)

        # Look for window.offers in script tags
        script_tags = soup.find_all("script")

        self._logger.debug("searching_scripts", total_scripts=len(script_tags))

        for i, script in enumerate(script_tags):
            script_content = script.string
            if not script_content:
                continue

            # Check if this script contains window.offers
            if "window.offers" not in script_content:
                continue

            self._logger.debug("found_window_offers_script", script_index=i)

            # Look for window.offers = [...]
            # Pattern handles both with and without semicolon
            match = re.search(r"window\.offers\s*=\s*(\[[\s\S]*?\]);?", script_content)

            if match:
                try:
                    offers_json = match.group(1)

                    self._logger.debug(
                        "extracted_json", json_length=len(offers_json), preview=offers_json[:200]
                    )

                    # Parse JSON
                    offers_data = json.loads(offers_json)

                    self._logger.info(
                        "found_offers_json", count=len(offers_data), query=self.search_query
                    )

                    # Parse each offer
                    total_parsed = 0
                    filtered_out = 0

                    for offer_data in offers_data:
                        try:
                            result = self._parse_product(offer_data)
                            if result:
                                total_parsed += 1

                                # Filter by name if enabled
                                if self.filter_by_name:
                                    if self._matches_query(result.name):
                                        results.append(result)
                                    else:
                                        filtered_out += 1
                                        self._logger.debug(
                                            "filtered_out_product",
                                            name=result.name,
                                            query=self.search_query,
                                        )
                                else:
                                    results.append(result)

                        except Exception as e:
                            self._logger.warning(
                                "product_parse_error",
                                error=str(e),
                                product_hash=offer_data.get("hash"),
                                product_name=offer_data.get("name"),
                            )
                            continue

                    self._logger.info(
                        "filtering_results",
                        total_parsed=total_parsed,
                        filtered_out=filtered_out,
                        final_count=len(results),
                        filter_enabled=self.filter_by_name,
                    )

                    # Found offers, stop searching
                    break

                except json.JSONDecodeError as e:
                    self._logger.error(
                        "json_decode_failed",
                        error=str(e),
                        json_preview=offers_json[:500] if len(offers_json) > 500 else offers_json,
                    )
                    continue
            else:
                self._logger.warning("regex_no_match", script_preview=script_content[:500])

        if not results:
            self._logger.warning("no_products_found", query=self.search_query)

        return results

    def _matches_query(self, product_name: str) -> bool:
        """
        Check if product name matches the search query.

        Args:
            product_name: Product name to check

        Returns:
            True if product name contains the query (case-insensitive)
        """
        # Normalize both strings for comparison
        name_normalized = product_name.lower().strip()
        query_normalized = self.search_query.lower().strip()

        # Check if query words are in the product name
        # Split query into words to handle multi-word queries
        query_words = query_normalized.split()

        # All query words must be present in product name
        return all(word in name_normalized for word in query_words)

    def _parse_product(self, data: dict[str, str]) -> Optional[SearchResult]:
        """
        Parse product from JSON data.

        Args:
            data: Product JSON object from window.offers

        Returns:
            SearchResult entity or None if parsing fails
        """
        # Required fields
        required = [
            "name",
            "image",
            "leafletId",
            "pageNumber",
            "productLeafletPageUuid",
            "dateStart",
            "dateEnd",
        ]

        for field in required:
            if field not in data:
                self._logger.debug("missing_required_field", field=field, name=data.get("name"))
                return None

        # Parse dates
        try:
            # Dates come as objects with date/timezone
            if isinstance(data["dateStart"], dict):
                date_start_str = data["dateStart"]["date"]
                date_end_str = data["dateEnd"]["date"]
            else:
                # Fallback if dates are strings
                date_start_str = data["dateStart"]
                date_end_str = data["dateEnd"]

            valid_from = date_parser.parse(date_start_str)
            valid_until = date_parser.parse(date_end_str)

            # Ensure timezone aware
            if valid_from.tzinfo is None:
                valid_from = valid_from.replace(tzinfo=timezone.utc)
            if valid_until.tzinfo is None:
                valid_until = valid_until.replace(tzinfo=timezone.utc)

        except Exception as e:
            self._logger.error("date_parse_failed", error=str(e), name=data.get("name"))
            return None

        # Parse position from area (optional - might not be present)
        position_x = 0.0
        position_y = 0.0
        width = 1.0
        height = 1.0

        if "area" in data and data["area"]:
            try:
                area = data["area"]
                top_left = area["topLeftCorner"]
                bottom_right = area["bottomRightCorner"]

                position_x = float(top_left["x"])
                position_y = float(top_left["y"])
                bottom_x = float(bottom_right["x"])
                bottom_y = float(bottom_right["y"])

                width = bottom_x - position_x
                height = bottom_y - position_y
            except Exception as e:
                self._logger.debug("position_parse_failed", error=str(e), name=data.get("name"))
                # Continue with defaults

        # Parse price (may be null)
        price = None
        if data.get("price") is not None:
            try:
                price = Decimal(str(data["price"]))
            except Exception as e:
                self._logger.debug("price_parse_failed", error=str(e), name=data.get("name"))

        # Generate hash if missing
        product_hash = data.get("hash")
        if not product_hash:
            # Generate simple hash from name + leaflet + page
            hash_str = f"{data['name']}{data['leafletId']}{data['pageNumber']}"
            product_hash = hashlib.md5(hash_str.encode()).hexdigest()[:9]

        # Parse shop name from leaflet mapping
        shop_name = self.leaflet_shop_map.get(int(data["leafletId"]))

        # Create SearchResult
        try:
            result = SearchResult(
                hash=product_hash,
                name=data["name"],
                image_url=data["image"],
                manufacturer_name=data.get("manufacturerName"),
                manufacturer_uuid=data.get("manufacturerUuid"),
                brand_name=data.get("brandName"),
                brand_uuid=data.get("brandUuid"),
                sub_brand_name=data.get("subBrandName"),
                sub_brand_uuid=data.get("subBrandUuid"),
                hiper_category_id=data.get("hiperCategoryId"),
                offer_subcategory_id=data.get("offerSubcategoryId"),
                product_leaflet_page_uuid=data["productLeafletPageUuid"],
                leaflet_id=int(data["leafletId"]),
                page_number=int(data["pageNumber"]),
                price=price,
                percent_discount=int(data.get("percentDiscount", 0)),
                valid_from=valid_from,
                valid_until=valid_until,
                position_x=position_x,
                position_y=position_y,
                width=width,
                height=height,
                search_query=self.search_query,
                scraped_at=datetime.now(timezone.utc),
                shop_name=shop_name,  # Updated: Use extracted shop name from mapping
            )

            self._logger.debug(
                "product_parsed", hash=result.hash, name=result.name, price=result.price_pln
            )

            return result

        except Exception as e:
            self._logger.error(
                "result_creation_failed", name=data.get("name"), error=str(e), exc_info=True
            )
            return None

    def _extract_leaflet_shop_map(self, soup: BeautifulSoup) -> None:
        """
        Extract mapping of leaflet IDs to shop names from page.

        Extracts from two sources:
        1. Swiper slides at the top (popular leaflets)
        2. Leaflet items at the bottom (complete list)

        Example HTML structures:

        Swiper slide:
        <div class="swiper-slide">
            <div class="page-wrapper"
                 data-leaflet-id="458087"
                 data-brand-name="Lidl">
            </div>
        </div>

        Leaflet item:
        <div class="leaflet"
             data-brand-name="Stokrotka"
             data-leaflet-id="457928">
        </div>

        Args:
            soup: Parsed HTML soup
        """
        # Extract from swiper slides (top of page - popular leaflets)
        swiper_slides = soup.find_all("div", class_="swiper-slide")

        self._logger.debug("extracting_from_swiper", total_slides=len(swiper_slides))

        for slide in swiper_slides:
            page_wrapper = slide.find("div", class_="page-wrapper")
            if page_wrapper:
                leaflet_id_str = page_wrapper.get("data-leaflet-id")
                brand_name = page_wrapper.get("data-brand-name")
                if leaflet_id_str and brand_name:
                    try:
                        leaflet_id = int(leaflet_id_str)
                        self.leaflet_shop_map[leaflet_id] = brand_name
                        self._logger.debug(
                            "mapped_leaflet_to_shop_swiper",
                            leaflet_id=leaflet_id,
                            shop_name=brand_name,
                        )
                    except ValueError:
                        self._logger.debug(
                            "invalid_leaflet_id_swiper", leaflet_id_str=leaflet_id_str
                        )

        # Extract from leaflet items (bottom of page - complete list)
        leaflet_items = soup.find_all("div", class_="leaflet")

        self._logger.debug("extracting_from_leaflets", total_items=len(leaflet_items))

        for item in leaflet_items:
            leaflet_id_str = item.get("data-leaflet-id")
            brand_name = item.get("data-brand-name")
            if leaflet_id_str and brand_name:
                try:
                    leaflet_id = int(leaflet_id_str)
                    # Only add if not already present (swiper has priority)
                    if leaflet_id not in self.leaflet_shop_map:
                        self.leaflet_shop_map[leaflet_id] = brand_name
                        self._logger.debug(
                            "mapped_leaflet_to_shop_item",
                            leaflet_id=leaflet_id,
                            shop_name=brand_name,
                        )
                except ValueError:
                    self._logger.debug("invalid_leaflet_id_item", leaflet_id_str=leaflet_id_str)

        self._logger.info(
            "extracted_leaflet_shop_map",
            count=len(self.leaflet_shop_map),
            from_swiper=len(swiper_slides),
            from_items=len(leaflet_items),
            leaflet_ids=sorted(self.leaflet_shop_map.keys()),
        )
