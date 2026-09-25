"""
Test suite for DuckDuckGo Search MCP Server.
Tests all 4 tools: search_web, search_news, search_images, search_videos.
"""

import pytest
from unittest.mock import patch, MagicMock
from server import search_web, search_news, search_images, search_videos


# ─────────────────────────────────────────────────────────────
# Fixtures — shared mock data
# ─────────────────────────────────────────────────────────────

@pytest.fixture
def mock_web_results():
    return [
        {"title": "Python Docs", "href": "https://python.org", "body": "Official Python documentation."},
        {"title": "Python Tutorial", "href": "https://tutorial.python.org", "body": "Learn Python step by step."},
    ]

@pytest.fixture
def mock_news_results():
    return [
        {
            "title": "Python 3.13 Released",
            "url": "https://news.python.org/release",
            "source": "Python.org",
            "date": "2024-10-01T00:00:00",
            "body": "Python 3.13 introduces exciting new features.",
        }
    ]

@pytest.fixture
def mock_image_results():
    return [
        {
            "title": "Python Logo",
            "image": "https://example.com/python.png",
            "thumbnail": "https://example.com/python_thumb.png",
            "source": "python.org",
            "url": "https://python.org",
        }
    ]

@pytest.fixture
def mock_video_results():
    return [
        {
            "title": "Python Tutorial for Beginners",
            "content": "https://youtube.com/watch?v=abc123",
            "description": "Full beginner Python course.",
            "publisher": "YouTube",
            "duration": "4:23:00",
            "embed_url": "https://youtube.com/embed/abc123",
        }
    ]


# ─────────────────────────────────────────────────────────────
# search_web tests
# ─────────────────────────────────────────────────────────────

class TestSearchWeb:

    def test_returns_results_list(self, mock_web_results):
        """search_web should return a list of results."""
        with patch("server.DDGS") as MockDDGS:
            instance = MockDDGS.return_value.__enter__.return_value
            instance.text.return_value = iter(mock_web_results)
            result = search_web("Python programming")
        assert isinstance(result, list)
        assert len(result) == 2

    def test_result_has_expected_keys(self, mock_web_results):
        """Each result should contain title, href, and body."""
        with patch("server.DDGS") as MockDDGS:
            instance = MockDDGS.return_value.__enter__.return_value
            instance.text.return_value = iter(mock_web_results)
            result = search_web("Python programming")
        assert "title" in result[0]
        assert "href" in result[0]
        assert "body" in result[0]

    def test_empty_query_returns_error(self):
        """Empty query should return an error dict."""
        result = search_web("   ")
        assert result[0].get("error") == "Query cannot be empty"

    def test_max_results_capped_at_20(self, mock_web_results):
        """max_results above 20 should be capped to 20."""
        with patch("server.DDGS") as MockDDGS:
            instance = MockDDGS.return_value.__enter__.return_value
            instance.text.return_value = iter(mock_web_results)
            search_web("Python", max_results=100)
        call_kwargs = instance.text.call_args
        assert call_kwargs.kwargs.get("max_results", 20) <= 20

    def test_max_results_floor_is_1(self, mock_web_results):
        """max_results below 1 should be set to 1."""
        with patch("server.DDGS") as MockDDGS:
            instance = MockDDGS.return_value.__enter__.return_value
            instance.text.return_value = iter(mock_web_results)
            search_web("Python", max_results=-5)
        call_kwargs = instance.text.call_args
        assert call_kwargs.kwargs.get("max_results", 1) >= 1

    def test_no_results_returns_message(self):
        """Empty result set should return a 'No results found' message."""
        with patch("server.DDGS") as MockDDGS:
            instance = MockDDGS.return_value.__enter__.return_value
            instance.text.return_value = iter([])
            result = search_web("xyzxyzxyznonexistentquery12345")
        assert result[0].get("message") == "No results found"

    def test_ddgs_exception_returns_error(self):
        """Network/API errors should be caught and returned as error dict."""
        with patch("server.DDGS") as MockDDGS:
            instance = MockDDGS.return_value.__enter__.return_value
            instance.text.side_effect = Exception("Connection timeout")
            result = search_web("Python")
        assert "error" in result[0]
        assert "Connection timeout" in result[0]["error"]

    def test_custom_region_passed_to_ddgs(self, mock_web_results):
        """Region parameter should be forwarded to DDGS."""
        with patch("server.DDGS") as MockDDGS:
            instance = MockDDGS.return_value.__enter__.return_value
            instance.text.return_value = iter(mock_web_results)
            search_web("cricket", region="in-en")
        call_kwargs = instance.text.call_args
        assert call_kwargs.kwargs.get("region") == "in-en"

    def test_safe_search_parameter(self, mock_web_results):
        """safesearch parameter should be forwarded to DDGS."""
        with patch("server.DDGS") as MockDDGS:
            instance = MockDDGS.return_value.__enter__.return_value
            instance.text.return_value = iter(mock_web_results)
            search_web("Python", safe_search="on")
        call_kwargs = instance.text.call_args
        assert call_kwargs.kwargs.get("safesearch") == "on"


# ─────────────────────────────────────────────────────────────
# search_news tests
# ─────────────────────────────────────────────────────────────

class TestSearchNews:

    def test_returns_results_list(self, mock_news_results):
        """search_news should return a list."""
        with patch("server.DDGS") as MockDDGS:
            instance = MockDDGS.return_value.__enter__.return_value
            instance.news.return_value = iter(mock_news_results)
            result = search_news("Python release")
        assert isinstance(result, list)
        assert len(result) == 1

    def test_result_has_expected_keys(self, mock_news_results):
        """News results should have title, url, source, date, body."""
        with patch("server.DDGS") as MockDDGS:
            instance = MockDDGS.return_value.__enter__.return_value
            instance.news.return_value = iter(mock_news_results)
            result = search_news("Python release")
        assert "title" in result[0]
        assert "url" in result[0]
        assert "source" in result[0]

    def test_empty_query_returns_error(self):
        """Empty query should return an error."""
        result = search_news("")
        assert result[0].get("error") == "Query cannot be empty"

    def test_time_filter_passed_to_ddgs(self, mock_news_results):
        """time_filter param should be forwarded as timelimit to DDGS."""
        with patch("server.DDGS") as MockDDGS:
            instance = MockDDGS.return_value.__enter__.return_value
            instance.news.return_value = iter(mock_news_results)
            search_news("AI news", time_filter="d")
        call_kwargs = instance.news.call_args
        assert call_kwargs.kwargs.get("timelimit") == "d"

    def test_no_results_returns_message(self):
        """Empty result set should return 'No news articles found'."""
        with patch("server.DDGS") as MockDDGS:
            instance = MockDDGS.return_value.__enter__.return_value
            instance.news.return_value = iter([])
            result = search_news("xyznonexistent999")
        assert result[0].get("message") == "No news articles found"

    def test_exception_returns_error(self):
        """Exceptions should be returned as error dict."""
        with patch("server.DDGS") as MockDDGS:
            instance = MockDDGS.return_value.__enter__.return_value
            instance.news.side_effect = Exception("Rate limited")
            result = search_news("AI")
        assert "error" in result[0]
        assert "Rate limited" in result[0]["error"]

    def test_max_results_capped(self, mock_news_results):
        """max_results should be capped at 20."""
        with patch("server.DDGS") as MockDDGS:
            instance = MockDDGS.return_value.__enter__.return_value
            instance.news.return_value = iter(mock_news_results)
            search_news("AI", max_results=50)
        call_kwargs = instance.news.call_args
        assert call_kwargs.kwargs.get("max_results", 20) <= 20


# ─────────────────────────────────────────────────────────────
# search_images tests
# ─────────────────────────────────────────────────────────────

class TestSearchImages:

    def test_returns_results_list(self, mock_image_results):
        """search_images should return a list."""
        with patch("server.DDGS") as MockDDGS:
            instance = MockDDGS.return_value.__enter__.return_value
            instance.images.return_value = iter(mock_image_results)
            result = search_images("Python logo")
        assert isinstance(result, list)
        assert len(result) == 1

    def test_result_has_expected_keys(self, mock_image_results):
        """Image results should have title, image, thumbnail, source, url."""
        with patch("server.DDGS") as MockDDGS:
            instance = MockDDGS.return_value.__enter__.return_value
            instance.images.return_value = iter(mock_image_results)
            result = search_images("Python logo")
        assert "title" in result[0]
        assert "image" in result[0]
        assert "url" in result[0]

    def test_empty_query_returns_error(self):
        """Empty query should return an error."""
        result = search_images("  ")
        assert result[0].get("error") == "Query cannot be empty"

    def test_size_filter_passed_to_ddgs(self, mock_image_results):
        """size parameter should be forwarded to DDGS."""
        with patch("server.DDGS") as MockDDGS:
            instance = MockDDGS.return_value.__enter__.return_value
            instance.images.return_value = iter(mock_image_results)
            search_images("mountains", size="Large")
        call_kwargs = instance.images.call_args
        assert call_kwargs.kwargs.get("size") == "Large"

    def test_color_filter_passed_to_ddgs(self, mock_image_results):
        """color parameter should be forwarded to DDGS."""
        with patch("server.DDGS") as MockDDGS:
            instance = MockDDGS.return_value.__enter__.return_value
            instance.images.return_value = iter(mock_image_results)
            search_images("mountains", color="Monochrome")
        call_kwargs = instance.images.call_args
        assert call_kwargs.kwargs.get("color") == "Monochrome"

    def test_no_results_returns_message(self):
        """Empty result should return 'No images found'."""
        with patch("server.DDGS") as MockDDGS:
            instance = MockDDGS.return_value.__enter__.return_value
            instance.images.return_value = iter([])
            result = search_images("xyznonexistent999image")
        assert result[0].get("message") == "No images found"

    def test_exception_returns_error(self):
        """Exceptions should be caught and returned."""
        with patch("server.DDGS") as MockDDGS:
            instance = MockDDGS.return_value.__enter__.return_value
            instance.images.side_effect = Exception("Blocked")
            result = search_images("cats")
        assert "error" in result[0]


# ─────────────────────────────────────────────────────────────
# search_videos tests
# ─────────────────────────────────────────────────────────────

class TestSearchVideos:

    def test_returns_results_list(self, mock_video_results):
        """search_videos should return a list."""
        with patch("server.DDGS") as MockDDGS:
            instance = MockDDGS.return_value.__enter__.return_value
            instance.videos.return_value = iter(mock_video_results)
            result = search_videos("Python tutorial")
        assert isinstance(result, list)
        assert len(result) == 1

    def test_result_has_expected_keys(self, mock_video_results):
        """Video results should have title, content, description."""
        with patch("server.DDGS") as MockDDGS:
            instance = MockDDGS.return_value.__enter__.return_value
            instance.videos.return_value = iter(mock_video_results)
            result = search_videos("Python tutorial")
        assert "title" in result[0]
        assert "content" in result[0]
        assert "description" in result[0]

    def test_empty_query_returns_error(self):
        """Empty query should return an error."""
        result = search_videos("")
        assert result[0].get("error") == "Query cannot be empty"

    def test_duration_filter_passed_to_ddgs(self, mock_video_results):
        """duration parameter should be forwarded to DDGS."""
        with patch("server.DDGS") as MockDDGS:
            instance = MockDDGS.return_value.__enter__.return_value
            instance.videos.return_value = iter(mock_video_results)
            search_videos("Python course", duration="long")
        call_kwargs = instance.videos.call_args
        assert call_kwargs.kwargs.get("duration") == "long"

    def test_no_results_returns_message(self):
        """Empty result should return 'No videos found'."""
        with patch("server.DDGS") as MockDDGS:
            instance = MockDDGS.return_value.__enter__.return_value
            instance.videos.return_value = iter([])
            result = search_videos("xyznonexistent999video")
        assert result[0].get("message") == "No videos found"

    def test_exception_returns_error(self):
        """Exceptions should be caught and returned."""
        with patch("server.DDGS") as MockDDGS:
            instance = MockDDGS.return_value.__enter__.return_value
            instance.videos.side_effect = Exception("Timeout")
            result = search_videos("Python")
        assert "error" in result[0]
        assert "Timeout" in result[0]["error"]

    def test_max_results_capped(self, mock_video_results):
        """max_results should be capped at 20."""
        with patch("server.DDGS") as MockDDGS:
            instance = MockDDGS.return_value.__enter__.return_value
            instance.videos.return_value = iter(mock_video_results)
            search_videos("Python", max_results=999)
        call_kwargs = instance.videos.call_args
        assert call_kwargs.kwargs.get("max_results", 20) <= 20


# ─────────────────────────────────────────────────────────────
# Integration tests (live DuckDuckGo — skipped in CI by default)
# ─────────────────────────────────────────────────────────────

@pytest.mark.integration
class TestLiveSearch:
    """Live tests against real DuckDuckGo API. Run with: pytest -m integration"""

    def test_live_web_search(self):
        result = search_web("Python programming language", max_results=3)
        assert isinstance(result, list)
        assert len(result) > 0
        assert "error" not in result[0]
        assert "title" in result[0]

    def test_live_news_search(self):
        result = search_news("technology news", max_results=3)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_live_image_search(self):
        result = search_images("Python snake", max_results=3)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_live_video_search(self):
        result = search_videos("Python tutorial beginner", max_results=3)
        assert isinstance(result, list)
        assert len(result) > 0
