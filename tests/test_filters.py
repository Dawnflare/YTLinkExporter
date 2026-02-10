"""Unit tests for src.core.filters."""

import pytest
from src.core.extractor import VideoMeta
from src.core.filters import apply_filters


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_video(title: str = "Video", upload_date: str = "20250601") -> VideoMeta:
    """Create a minimal VideoMeta for testing."""
    return VideoMeta(
        title=title,
        url=f"https://youtube.com/watch?v={title.replace(' ', '')}",
        video_id=title.replace(" ", ""),
        upload_date=upload_date,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestApplyFilters:
    """Verify each filter mode independently and in combination."""

    def test_no_filters_returns_all(self):
        """When no filters are set, all videos pass through."""
        videos = [_make_video(f"V{i}") for i in range(5)]
        assert len(apply_filters(videos)) == 5

    def test_date_start_filter(self):
        """Videos before start date are excluded."""
        videos = [
            _make_video("Old", "20240101"),
            _make_video("New", "20250601"),
        ]
        result = apply_filters(videos, date_start="20250101")
        assert len(result) == 1
        assert result[0].title == "New"

    def test_date_end_filter(self):
        """Videos after end date are excluded."""
        videos = [
            _make_video("Old", "20240101"),
            _make_video("New", "20250601"),
        ]
        result = apply_filters(videos, date_end="20241231")
        assert len(result) == 1
        assert result[0].title == "Old"

    def test_date_range_filter(self):
        """Only videos within the date range pass."""
        videos = [
            _make_video("Before", "20230101"),
            _make_video("Inside", "20240601"),
            _make_video("After", "20250601"),
        ]
        result = apply_filters(videos, date_start="20240101", date_end="20241231")
        assert len(result) == 1
        assert result[0].title == "Inside"

    def test_keyword_include(self):
        """Only videos whose title contains the keyword pass."""
        videos = [
            _make_video("Python Tutorial"),
            _make_video("JavaScript Review"),
            _make_video("Python Deep Dive"),
        ]
        result = apply_filters(videos, keyword_include="Python")
        assert len(result) == 2

    def test_keyword_exclude(self):
        """Videos whose title contains the keyword are removed."""
        videos = [
            _make_video("Python Tutorial"),
            _make_video("JavaScript Review"),
        ]
        result = apply_filters(videos, keyword_exclude="JavaScript")
        assert len(result) == 1
        assert result[0].title == "Python Tutorial"

    def test_keyword_case_insensitive(self):
        """Keyword matching is case-insensitive for both include and exclude."""
        videos = [
            _make_video("PYTHON tutorial"),
            _make_video("javaScript Basics"),
            _make_video("GoLang Guide"),
        ]

        # Test Include: "python" (lower) matching "PYTHON" (upper)
        assert len(apply_filters(videos, keyword_include="python")) == 1

        # Test Include: "JAVASCRIPT" (upper) matching "javaScript" (mixed)
        assert len(apply_filters(videos, keyword_include="JAVASCRIPT")) == 1

        # Test Exclude: "golang" (lower) excluding "GoLang" (mixed)
        result = apply_filters(videos, keyword_exclude="golang")
        assert len(result) == 2
        assert "GoLang Guide" not in [v.title for v in result]

        # Test Exclude: "PYTHON" (upper) excluding "PYTHON" (upper)
        result = apply_filters(videos, keyword_exclude="PYTHON")
        assert len(result) == 2
        assert "PYTHON tutorial" not in [v.title for v in result]

    def test_limit(self):
        """Limit truncates the result list."""
        videos = [_make_video(f"V{i}") for i in range(10)]
        result = apply_filters(videos, limit=3)
        assert len(result) == 3

    def test_combined_filters(self):
        """Multiple filters stack correctly."""
        videos = [
            _make_video("Python Intro", "20240601"),
            _make_video("Python Advanced", "20240801"),
            _make_video("JavaScript Basics", "20240701"),
            _make_video("Python Tips", "20230101"),  # too old
        ]
        result = apply_filters(
            videos,
            date_start="20240101",
            date_end="20241231",
            keyword_include="Python",
            limit=1,
        )
        assert len(result) == 1
        assert result[0].title == "Python Intro"

    def test_empty_upload_date_excluded_when_date_filter_active(self):
        """Videos with no upload_date are dropped when a date filter is set."""
        videos = [_make_video("No Date", upload_date="")]
        result = apply_filters(videos, date_start="20240101")
        assert len(result) == 0
