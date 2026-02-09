from unittest.mock import Mock, patch
from deals import ScrapedDeal, feed_urls


class TestScrapedDealExtract:
    """Tests for the ScrapedDeal.extract static method."""

    def test_extract_with_snippet_div(self):
        """Test extraction when snippet div is present."""
        html_snippet = """
        <div class="snippet summary">
            This is a test description with some HTML
        </div>
        """
        result = ScrapedDeal.extract(html_snippet)
        assert isinstance(result, str)
        assert "test description" in result
        assert "\n" not in result

    def test_extract_without_snippet_div(self):
        """Test extraction when snippet div is not present."""
        html_snippet = "This is plain HTML without snippet div"
        result = ScrapedDeal.extract(html_snippet)
        assert result == "This is plain HTML without snippet div"

    def test_extract_removes_newlines(self):
        """Test that extract removes newline characters."""
        html_snippet = """
        <div class="snippet summary">
            Line 1
            Line 2
            Line 3
        </div>
        """
        result = ScrapedDeal.extract(html_snippet)
        assert "\n" not in result

    def test_extract_strips_whitespace(self):
        """Test that extract strips leading/trailing whitespace."""
        html_snippet = '<div class="snippet summary">   spaced text   </div>'
        result = ScrapedDeal.extract(html_snippet)
        assert result.strip() == result

    def test_extract_with_html_tags(self):
        """Test extraction with HTML tags in content."""
        html_snippet = """
        <div class="snippet summary">
            Text with <b>bold</b> and <i>italic</i> tags
        </div>
        """
        result = ScrapedDeal.extract(html_snippet)
        assert "Text with" in result
        # HTML tags should be removed
        assert "<b>" not in result and "<i>" not in result


class TestScrapedDealInit:
    """Tests for the ScrapedDeal.__init__ method."""

    @patch("deals.requests.get")
    def test_init_basic(self, mock_requests):
        """Test basic initialization of ScrapedDeal."""
        # Setup mocks
        mock_response = Mock()
        mock_response.content = b"""
            <html>content
            <div class='content-section'>Test Details\nmore\nFeatures\nTest Features</div>
            </html>
        """
        mock_requests.return_value = mock_response
        entry = {
            "title": "  Test Title  ",
            "summary": "<div class='snippet summary'>Test Summary</div>",
            "links": [{"href": "https://example.com"}],
        }

        deal = ScrapedDeal(entry)

        assert deal.title == "Test Title"
        assert deal.url == "https://example.com"
        assert mock_requests.called
        assert deal.details == "Test Details"
        assert deal.features == "Test Features"

    @patch("deals.requests.get")
    def test_init_basic_with_no_content(self, mock_requests):
        """Test basic initialization of ScrapedDeal."""
        # Setup mocks
        mock_response = Mock()
        mock_response.content = b"""
            <html>No content</html>
        """
        mock_requests.return_value = mock_response
        entry = {
            "title": "  Test Title  ",
            "summary": "<div class='snippet summary'>Test Summary</div>",
            "links": [{"href": "https://example.com"}],
        }

        deal = ScrapedDeal(entry)

        assert deal.title == "Test Title"
        assert deal.url == "https://example.com"
        assert mock_requests.called
        assert deal.details == ""
        assert deal.features == ""

    @patch("deals.requests.get")
    def test_init_without_features(self, mock_requests):
        """Test initialization when Features section does not exist."""
        mock_response = Mock()
        mock_response.content = b"""
            <html>content
            <div class='content-section'>Just details content\nmore\nAnd some more details</div>
            </html>
        """
        mock_requests.return_value = mock_response
        entry = {
            "title": "  Test Title  ",
            "summary": "<div class='snippet summary'>Test Summary</div>",
            "links": [{"href": "https://example.com"}],
        }

        deal = ScrapedDeal(entry)

        assert deal.features == ""
        assert deal.details == "Just details content And some more details"


class TestScrapedDealFetch:
    """Tests for the ScrapedDeal.fetch class method."""

    @patch("deals.feedparser.parse")
    @patch.object(ScrapedDeal, "__init__", return_value=None)
    @patch("deals.time.sleep")
    def test_fetch(self, mock_sleep, mock_init, mock_parse):
        """Test fetch method without progress bar."""
        mock_feed = Mock()
        mock_entry = Mock()
        mock_feed.entries = [mock_entry] * 20
        mock_parse.return_value = mock_feed

        ScrapedDeal.fetch(show_progress=False)

        assert mock_parse.call_count == len(feed_urls)
        assert mock_sleep.call_count == 50


class TestScrapedDealIntegration:
    """Integration tests for ScrapedDeal."""

    @patch("deals.requests.get")
    def test_full_deal_creation_workflow(self, mock_requests):
        """Test complete workflow of creating a ScrapedDeal."""
        # Setup mocks
        mock_response = Mock()
        mock_response.content = b"""
            <html>content
            <div class='content-section'>Some content details\nmore\nFeatures\nAnd here are some features\n\n</div>
            </html>
        """
        mock_requests.return_value = mock_response
        entry = {
            "title": "  Amazing Product Deal  ",
            "summary": "<div class='snippet summary'>Great deal on electronics</div>",
            "links": [
                {"href": "https://example.com/deal/123"},
                {"href": "https://example.com/deal2/"},
            ],
        }

        deal = ScrapedDeal(entry)

        # Verify all attributes are set correctly
        assert deal.title == "Amazing Product Deal"
        assert deal.summary == "Great deal on electronics"
        assert deal.url == "https://example.com/deal/123"
        assert deal.details == "Some content details"
        assert deal.features == "And here are some features"
