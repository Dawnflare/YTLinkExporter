"""
Plain Text Link List Exporter

Writes one YouTube URL per line to a ``.txt`` file.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from src.core.extractor import VideoMeta

logger = logging.getLogger(__name__)


def export_text_list(
    videos: list[VideoMeta],
    playlist_title: str,
    output_dir: str,
) -> str:
    """Write a plain-text file containing one video URL per line.

    Filename: ``{playlist_title}_links.txt``

    Args:
        videos: List of ``VideoMeta`` objects to export.
        playlist_title: Used as the filename stem.
        output_dir: Directory to write the file into.

    Returns:
        The absolute path of the written text file.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    safe_title = playlist_title or "Untitled Playlist"
    filepath = out_path / f"{safe_title}_links.txt"

    lines = [video.url for video in videos if video.url]
    content = "\n".join(lines) + "\n"

    filepath.write_text(content, encoding="utf-8")
    logger.info("Wrote %d URLs to %s", len(lines), filepath)
    return str(filepath)
