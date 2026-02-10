"""
Windows Shortcut (.url) Exporter

Generates one ``.url`` file per video.  Each file follows the standard
Windows ``[InternetShortcut]`` format and opens the video URL in the
user's default browser when double-clicked.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Callable, Optional

from src.core.extractor import VideoMeta
from src.core.sanitizer import sanitize_filename

logger = logging.getLogger(__name__)


def export_shortcuts(
    videos: list[VideoMeta],
    output_dir: str,
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> int:
    """Write a ``.url`` shortcut file for each video.

    Filename format: ``{YYYY-MM-DD} - {SanitizedTitle}.url``

    Args:
        videos: List of ``VideoMeta`` objects to export.
        output_dir: Filesystem directory to write files into.  Created
            automatically if it does not exist.
        progress_callback: Optional ``(current, total) -> None``
            callable invoked after each file is written.

    Returns:
        The number of ``.url`` files successfully written.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    total = len(videos)
    written = 0

    for idx, video in enumerate(videos):
        try:
            # Format the upload date as YYYY-MM-DD when available.
            date_prefix = _format_date(video.upload_date) or "Unknown"
            safe_title = sanitize_filename(video.title)
            filename = f"{date_prefix} - {safe_title}.url"

            filepath = out_path / filename
            content = f"[InternetShortcut]\nURL={video.url}\n"

            filepath.write_text(content, encoding="utf-8")
            written += 1
        except OSError:
            logger.warning("Failed to write shortcut for '%s'", video.title, exc_info=True)

        if progress_callback:
            progress_callback(idx + 1, total)

    logger.info("Wrote %d / %d shortcut files to %s", written, total, output_dir)
    return written


def _format_date(raw: str) -> str:
    """Convert ``YYYYMMDD`` to ``YYYY-MM-DD``.

    Args:
        raw: Date string in ``YYYYMMDD`` format.

    Returns:
        Formatted ``YYYY-MM-DD`` string, or empty string if *raw* is
        not exactly 8 digits.
    """
    if raw and len(raw) == 8 and raw.isdigit():
        return f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}"
    return ""
