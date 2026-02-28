"""Unit tests for URL helper utilities."""

import pytest

from src.utils.url_helpers import DEFAULT_BASE_URL, absolutize_url


@pytest.mark.unit
class TestAbsolutizeUrl:
    """Tests for absolutize_url function."""

    def test_relative_url_with_base(self):
        """Test converting relative URL with explicit base URL."""
        result = absolutize_url("/sklep/biedronka/", "https://blix.pl")
        assert result == "https://blix.pl/sklep/biedronka/"

    def test_relative_url_without_trailing_slash(self):
        """Test converting relative URL without trailing slash."""
        result = absolutize_url("/sklep/biedronka", "https://blix.pl")
        assert result == "https://blix.pl/sklep/biedronka"

    def test_already_absolute_https_url(self):
        """Test that already absolute HTTPS URL is returned unchanged."""
        result = absolutize_url("https://example.com/page", "https://blix.pl")
        assert result == "https://example.com/page"

    def test_already_absolute_http_url(self):
        """Test that already absolute HTTP URL is returned unchanged."""
        result = absolutize_url("http://example.com/page", "https://blix.pl")
        assert result == "http://example.com/page"

    def test_relative_url_default_base(self):
        """Test relative URL using default base URL."""
        result = absolutize_url("/sklep/biedronka/", None)
        assert result == "https://blix.pl/sklep/biedronka/"

    def test_relative_url_default_base_explicit(self):
        """Test relative URL using default constant."""
        result = absolutize_url("/sklep/biedronka/", DEFAULT_BASE_URL)
        assert result == "https://blix.pl/sklep/biedronka/"

    def test_empty_url_returns_base(self):
        """Test that empty URL returns the base URL."""
        result = absolutize_url("", "https://blix.pl")
        assert result == "https://blix.pl"

    def test_empty_url_with_default_base(self):
        """Test that empty URL returns default base URL."""
        result = absolutize_url("", None)
        assert result == DEFAULT_BASE_URL

    def test_relative_url_without_leading_slash(self):
        """Test relative URL without leading slash gets base appended."""
        result = absolutize_url("sklep/biedronka/", "https://blix.pl")
        assert result == "https://blix.pl/sklep/biedronka/"

    def test_relative_url_with_query_string(self):
        """Test relative URL with query string."""
        result = absolutize_url("/search?q=test", "https://blix.pl")
        assert result == "https://blix.pl/search?q=test"

    def test_relative_url_with_fragment(self):
        """Test relative URL with fragment."""
        result = absolutize_url("/page#section", "https://blix.pl")
        assert result == "https://blix.pl/page#section"

    def test_base_url_without_trailing_slash(self):
        """Test base URL without trailing slash is handled correctly."""
        result = absolutize_url("/page", "https://blix.pl")
        assert result == "https://blix.pl/page"

    def test_base_url_with_trailing_slash(self):
        """Test base URL with trailing slash is handled correctly."""
        result = absolutize_url("/page", "https://blix.pl/")
        assert result == "https://blix.pl/page"

    def test_https_url_preserves_https(self):
        """Test that HTTPS URLs preserve HTTPS protocol."""
        result = absolutize_url("https://secure.example.com/", "http://blix.pl")
        assert result == "https://secure.example.com/"

    def test_http_url_preserves_http(self):
        """Test that HTTP URLs preserve HTTP protocol."""
        result = absolutize_url("http://insecure.example.com/", "https://blix.pl")
        assert result == "http://insecure.example.com/"

    def test_root_path(self):
        """Test root path relative URL."""
        result = absolutize_url("/", "https://blix.pl")
        # Note: The function appends the slash, so result is "https://blix.pl/"
        assert result == "https://blix.pl/"

    def test_multiple_path_segments(self):
        """Test URL with multiple path segments."""
        result = absolutize_url("/category/subcategory/product", "https://blix.pl")
        assert result == "https://blix.pl/category/subcategory/product"

    def test_url_with_port(self):
        """Test URL with port number."""
        result = absolutize_url("https://example.com:8080/page", "https://blix.pl")
        assert result == "https://example.com:8080/page"

    def test_url_with_credentials(self):
        """Test URL with username and password."""
        result = absolutize_url("https://user:pass@example.com/page", "https://blix.pl")
        assert result == "https://user:pass@example.com/page"

    def test_relative_url_complex_path(self):
        """Test complex relative path with multiple segments."""
        result = absolutize_url("/sklep/biedronka/oferty/2024", "https://blix.pl")
        assert result == "https://blix.pl/sklep/biedronka/oferty/2024"
