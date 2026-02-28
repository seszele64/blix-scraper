"""Unit tests for BeautifulSoup helper utilities."""

import pytest
from bs4 import BeautifulSoup

from src.utils.soup_helpers import get_first_element, get_single_attribute


@pytest.mark.unit
class TestGetSingleAttribute:
    """Tests for get_single_attribute function."""

    def test_get_attribute_with_list_value(self):
        """Test getting attribute when BeautifulSoup returns a list."""
        html = '<a href="/path" class="link active">Link</a>'
        soup = BeautifulSoup(html, "html.parser")
        tag = soup.a

        # In BeautifulSoup, class returns a list
        result = get_single_attribute(tag, "class")

        # Should return first item from list
        assert result == "link"

    def test_get_attribute_with_single_value(self):
        """Test getting attribute with single string value."""
        html = '<a href="/path">Link</a>'
        soup = BeautifulSoup(html, "html.parser")
        tag = soup.a

        result = get_single_attribute(tag, "href")

        assert result == "/path"

    def test_get_attribute_with_none_tag(self):
        """Test getting attribute when tag is None."""
        result = get_single_attribute(None, "href")

        assert result is None

    def test_get_attribute_with_missing_attribute(self):
        """Test getting attribute that doesn't exist."""
        html = "<a>Link</a>"
        soup = BeautifulSoup(html, "html.parser")
        tag = soup.a

        result = get_single_attribute(tag, "href")

        assert result is None

    def test_get_attribute_id(self):
        """Test getting id attribute."""
        html = '<div id="main-content">Content</div>'
        soup = BeautifulSoup(html, "html.parser")
        tag = soup.div

        result = get_single_attribute(tag, "id")

        assert result == "main-content"

    def test_get_attribute_src(self):
        """Test getting src attribute from img tag."""
        html = '<img src="image.jpg" alt="Image"/>'
        soup = BeautifulSoup(html, "html.parser")
        tag = soup.img

        result = get_single_attribute(tag, "src")

        assert result == "image.jpg"

    def test_get_attribute_data_value(self):
        """Test getting data-* attribute."""
        html = '<div data-value="123">Content</div>'
        soup = BeautifulSoup(html, "html.parser")
        tag = soup.div

        result = get_single_attribute(tag, "data-value")

        assert result == "123"

    def test_get_attribute_empty_string(self):
        """Test getting attribute with empty string value."""
        html = '<a href="">Link</a>'
        soup = BeautifulSoup(html, "html.parser")
        tag = soup.a

        result = get_single_attribute(tag, "href")

        assert result == ""

    def test_get_attribute_empty_list(self):
        """Test getting attribute when BeautifulSoup returns empty list."""
        html = '<div class="">Content</div>'
        soup = BeautifulSoup(html, "html.parser")
        tag = soup.div

        result = get_single_attribute(tag, "class")

        assert result is None

    def test_get_attribute_multiple_classes(self):
        """Test getting class attribute with multiple classes."""
        html = '<span class="bold italic underline">Text</span>'
        soup = BeautifulSoup(html, "html.parser")
        tag = soup.span

        result = get_single_attribute(tag, "class")

        # Returns first class in the list
        assert result == "bold"


@pytest.mark.unit
class TestGetFirstElement:
    """Tests for get_first_element function."""

    def test_finds_first_matching_element(self):
        """Test finding the first element matching a selector."""
        html = "<div><span>First</span><span>Second</span></div>"
        soup = BeautifulSoup(html, "html.parser")

        result = get_first_element(soup, "span")

        assert result is not None
        assert result.text == "First"

    def test_returns_none_for_missing_element(self):
        """Test that None is returned when no element matches."""
        html = "<div>Content</div>"
        soup = BeautifulSoup(html, "html.parser")

        result = get_first_element(soup, ".nonexistent")

        assert result is None

    def test_finds_first_div(self):
        """Test finding first div element."""
        html = '<div id="first">First</div><div id="second">Second</div>'
        soup = BeautifulSoup(html, "html.parser")

        result = get_first_element(soup, "div")

        assert result is not None
        assert result.get("id") == "first"

    def test_finds_by_id_selector(self):
        """Test finding element by ID selector."""
        html = '<div id="main"><span>Content</span></div>'
        soup = BeautifulSoup(html, "html.parser")

        result = get_first_element(soup, "#main")

        assert result is not None
        assert result.get("id") == "main"

    def test_finds_by_class_selector(self):
        """Test finding element by class selector."""
        html = '<div class="highlight">First</div><div>Second</div>'
        soup = BeautifulSoup(html, "html.parser")

        result = get_first_element(soup, ".highlight")

        assert result is not None
        assert "highlight" in result.get("class", [])

    def test_finds_nested_element(self):
        """Test finding nested element with complex selector."""
        html = "<div><ul><li>Item</li></ul></div>"
        soup = BeautifulSoup(html, "html.parser")

        result = get_first_element(soup, "li")

        assert result is not None
        assert result.text == "Item"

    def test_empty_soup(self):
        """Test with empty BeautifulSoup object."""
        soup = BeautifulSoup("", "html.parser")

        result = get_first_element(soup, "div")

        assert result is None

    def test_finds_by_attribute_selector(self):
        """Test finding element by attribute selector."""
        html = '<a href="/page">Link</a><a>No href</a>'
        soup = BeautifulSoup(html, "html.parser")

        result = get_first_element(soup, "a[href]")

        assert result is not None
        assert result.get("href") == "/page"

    def test_finds_input_by_type(self):
        """Test finding input element by type."""
        html = '<input type="text"/><input type="checkbox"/>'
        soup = BeautifulSoup(html, "html.parser")

        result = get_first_element(soup, "input[type='text']")

        assert result is not None
        assert result.get("type") == "text"

    def test_handles_empty_html(self):
        """Test with empty HTML string."""
        html = ""
        soup = BeautifulSoup(html, "html.parser")

        result = get_first_element(soup, "body")

        assert result is None
