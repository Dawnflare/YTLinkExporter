"""
Offline HTML Catalog Exporter

Generates a single, self-contained HTML file with embedded CSS and
Base64-encoded thumbnail images.  The file can be viewed completely
offline in any modern browser.
"""

from __future__ import annotations

import html
import logging
from pathlib import Path
from typing import Callable, Optional

from src.core.extractor import VideoMeta
from src.core.thumbnail import download_and_encode

logger = logging.getLogger(__name__)


def export_html_catalog(
    videos: list[VideoMeta],
    playlist_title: str,
    output_dir: str,
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> str:
    """Generate a self-contained HTML catalog of videos.

    Args:
        videos: List of ``VideoMeta`` objects to include.
        playlist_title: Used for the ``<title>`` and ``<h1>``, and as
            the output filename stem.
        output_dir: Directory to write the HTML file into.
        progress_callback: Optional ``(current, total)`` callable
            invoked after each thumbnail is downloaded.

    Returns:
        The absolute path of the written HTML file.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    safe_title = playlist_title or "Untitled Playlist"
    filepath = out_path / f"{safe_title}.html"

    total = len(videos)
    cards: list[str] = []

    for idx, video in enumerate(videos):
        thumb_data = download_and_encode(video.thumbnail_url)
        cards.append(_render_card(video, thumb_data))
        if progress_callback:
            progress_callback(idx + 1, total)

    page_html = _render_page(safe_title, cards, total)
    filepath.write_text(page_html, encoding="utf-8")

    logger.info("Wrote HTML catalog with %d videos to %s", total, filepath)
    return str(filepath)


# ---------------------------------------------------------------------------
# HTML rendering helpers
# ---------------------------------------------------------------------------

def _render_card(video: VideoMeta, thumb_b64: str) -> str:
    """Render a single video card as an HTML string.

    Args:
        video: The video metadata.
        thumb_b64: A Base64-encoded data-URI for the thumbnail.

    Returns:
        An HTML string for one grid card.
    """
    esc_title = html.escape(video.title)
    esc_url = html.escape(video.url)
    date_display = _format_display_date(video.upload_date)

    return f"""
    <div class="card">
      <a href="{esc_url}" target="_blank" rel="noopener noreferrer">
        <img src="{thumb_b64}" alt="{esc_title}" loading="lazy" />
      </a>
      <div class="card-body">
        <a href="{esc_url}" target="_blank" rel="noopener noreferrer" class="title">
          {esc_title}
        </a>
        <span class="date">{date_display}</span>
      </div>
    </div>"""


def _render_page(title: str, cards: list[str], count: int) -> str:
    """Assemble the full HTML page from rendered cards.

    Args:
        title: Page title / heading.
        cards: List of HTML card strings.
        count: Total number of videos (for the subtitle).

    Returns:
        A complete HTML document string.
    """
    esc_title = html.escape(title)
    cards_html = "\n".join(cards)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{esc_title} — YTLinkExporter</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #0f0f0f; color: #e8e8e8; padding: 2rem;
    }}
    header {{
      text-align: center; margin-bottom: 2rem;
    }}
    header h1 {{
      font-size: 1.8rem; font-weight: 600;
    }}
    header p {{
      color: #aaa; margin-top: 0.4rem; font-size: 0.9rem;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 1.2rem;
    }}
    .card {{
      background: #1a1a1a; border-radius: 10px; overflow: hidden;
      transition: transform 0.15s ease, box-shadow 0.15s ease;
    }}
    .card:hover {{
      transform: translateY(-3px);
      box-shadow: 0 6px 20px rgba(0,0,0,0.5);
    }}
    .card img {{
      width: 100%; aspect-ratio: 16/9; object-fit: cover; display: block;
    }}
    .card-body {{
      padding: 0.8rem 1rem 1rem;
    }}
    .card-body .title {{
      color: #e8e8e8; text-decoration: none; font-size: 0.95rem;
      font-weight: 500; display: -webkit-box;
      -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
    }}
    .card-body .title:hover {{ color: #3ea6ff; }}
    .card-body .date {{
      display: block; margin-top: 0.4rem; color: #888; font-size: 0.8rem;
    }}
    footer {{
      text-align: center; margin-top: 3rem; color: #555; font-size: 0.8rem;
    }}
  </style>
</head>
<body>
  <header>
    <h1>{esc_title}</h1>
    <p>{count} videos · Exported with YTLinkExporter</p>
  </header>
  <div class="grid">
    {cards_html}
  </div>
  <footer>
    Generated by YTLinkExporter — offline archive
  </footer>
</body>
</html>"""


def _format_display_date(raw: str) -> str:
    """Convert ``YYYYMMDD`` to a human-readable ``YYYY-MM-DD``.

    Args:
        raw: Raw date string.

    Returns:
        Formatted date or ``"—"`` if unavailable.
    """
    if raw and len(raw) == 8 and raw.isdigit():
        return f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}"
    return "—"
