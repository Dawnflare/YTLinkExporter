"""Unit tests for src.exporters (shortcut, html_catalog, text_list)."""

import os
import pytest
from pathlib import Path

from src.core.extractor import VideoMeta
from src.exporters.shortcut import export_shortcuts
from src.exporters.html_catalog import export_html_catalog
from src.exporters.text_list import export_text_list


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_videos() -> list[VideoMeta]:
    """Return a small list of mock VideoMeta for testing."""
    return [
        VideoMeta(
            title="First Video",
            url="https://www.youtube.com/watch?v=AAA",
            video_id="AAA",
            thumbnail_url="",
            upload_date="20240615",
        ),
        VideoMeta(
            title="Second Video",
            url="https://www.youtube.com/watch?v=BBB",
            video_id="BBB",
            thumbnail_url="",
            upload_date="20240720",
        ),
    ]


# ---------------------------------------------------------------------------
# Shortcut tests
# ---------------------------------------------------------------------------

class TestExportShortcuts:
    """Verify .url file generation."""

    def test_creates_url_files(self, sample_videos, tmp_path):
        """A .url file is created for each video."""
        count = export_shortcuts(sample_videos, str(tmp_path))
        assert count == 2
        url_files = list(tmp_path.glob("*.url"))
        assert len(url_files) == 2

    def test_url_file_content(self, sample_videos, tmp_path):
        """Each .url file contains the [InternetShortcut] header and URL."""
        export_shortcuts(sample_videos, str(tmp_path))
        url_files = sorted(tmp_path.glob("*.url"))
        content = url_files[0].read_text(encoding="utf-8")
        assert "[InternetShortcut]" in content
        assert "URL=https://www.youtube.com/watch?v=" in content

    def test_filename_contains_date(self, sample_videos, tmp_path):
        """Filenames start with the formatted upload date."""
        export_shortcuts(sample_videos, str(tmp_path))
        names = [f.name for f in tmp_path.glob("*.url")]
        assert any("2024-06-15" in n for n in names)


# ---------------------------------------------------------------------------
# HTML catalog tests
# ---------------------------------------------------------------------------

class TestExportHtmlCatalog:
    """Verify self-contained HTML generation."""

    def test_creates_html_file(self, sample_videos, tmp_path):
        """An HTML file is created with the playlist title."""
        path = export_html_catalog(sample_videos, "Test Playlist", str(tmp_path))
        assert Path(path).exists()
        assert path.endswith(".html")

    def test_html_contains_titles(self, sample_videos, tmp_path):
        """The HTML file contains the video titles."""
        path = export_html_catalog(sample_videos, "Test Playlist", str(tmp_path))
        content = Path(path).read_text(encoding="utf-8")
        assert "First Video" in content
        assert "Second Video" in content

    def test_html_is_self_contained(self, sample_videos, tmp_path):
        """The HTML file embeds CSS (no external stylesheets)."""
        path = export_html_catalog(sample_videos, "Test Playlist", str(tmp_path))
        content = Path(path).read_text(encoding="utf-8")
        assert "<style>" in content
        # No external CSS links
        assert 'rel="stylesheet"' not in content


# ---------------------------------------------------------------------------
# Text list tests
# ---------------------------------------------------------------------------

class TestExportTextList:
    """Verify plain-text URL list generation."""

    def test_creates_txt_file(self, sample_videos, tmp_path):
        """A .txt file is created."""
        path = export_text_list(sample_videos, "Test Playlist", str(tmp_path))
        assert Path(path).exists()
        assert path.endswith("_links.txt")

    def test_one_url_per_line(self, sample_videos, tmp_path):
        """Each line contains exactly one URL."""
        path = export_text_list(sample_videos, "Test Playlist", str(tmp_path))
        lines = Path(path).read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2
        assert all(line.startswith("https://") for line in lines)
