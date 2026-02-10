"""
YouTube Playlist / Channel Metadata Extractor

Wraps ``yt_dlp`` to extract video metadata from a playlist or channel
URL.  Returns lightweight ``VideoMeta`` dataclass instances rather than
raw dictionaries so that the rest of the application works with a
stable, typed contract.

Supports both **flat** extraction (fast, no upload dates) and **full**
extraction (slower, includes upload dates and uploader info).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

import yt_dlp

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data Model
# ---------------------------------------------------------------------------

@dataclass
class VideoMeta:
    """Lightweight container for a single video's extracted metadata.

    Attributes:
        title: The video title (may contain special characters).
        url: Full watch URL, e.g. ``https://www.youtube.com/watch?v=XXXX``.
        video_id: The YouTube video ID.
        thumbnail_url: URL of the best-available thumbnail image.
        upload_date: Upload date as ``YYYYMMDD`` string, or empty if
            unavailable.
        uploader: Channel / uploader name.
    """
    title: str
    url: str
    video_id: str
    thumbnail_url: str = ""
    upload_date: str = ""
    uploader: str = ""


@dataclass
class PlaylistInfo:
    """Container for top-level playlist / channel information.

    Attributes:
        title: The playlist or channel name.
        thumbnail_url: Representative thumbnail URL.
        video_count: Number of entries discovered (before filtering).
        videos: List of extracted ``VideoMeta`` objects.
    """
    title: str = ""
    thumbnail_url: str = ""
    video_count: int = 0
    videos: list[VideoMeta] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Extraction helpers
# ---------------------------------------------------------------------------

def _build_ydl_opts(
    cookies_path: Optional[str] = None,
    flat: bool = True,
) -> dict:
    """Construct the ``yt_dlp.YoutubeDL`` options dict.

    Args:
        cookies_path: Optional filesystem path to a Netscape-format
            ``cookies.txt`` file.
        flat: If True, use flat extraction (fast but no upload dates).
            If False, use full extraction (slower, includes dates).

    Returns:
        A dictionary suitable for passing to ``YoutubeDL()``.
    """
    opts: dict = {
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": True,        # Skip deleted / private entries.
        "skip_download": True,
    }
    if flat:
        opts["extract_flat"] = True
    if cookies_path:
        opts["cookiefile"] = cookies_path
    return opts


def _entry_to_meta(entry: dict, flat: bool = True) -> Optional[VideoMeta]:
    """Convert a single yt-dlp entry to a ``VideoMeta``.

    Args:
        entry: A raw dictionary returned by yt-dlp for one playlist
            entry.
        flat: Whether this entry came from flat extraction.

    Returns:
        A ``VideoMeta`` instance, or ``None`` if the entry is unusable
        (e.g. a deleted or private video stub).
    """
    if not entry:
        return None

    video_id = entry.get("id", "")
    title = entry.get("title", "")

    # yt-dlp marks unavailable videos with specific sentinel titles.
    if not title or title in ("[Deleted video]", "[Private video]"):
        logger.debug("Skipping unavailable entry: %s", video_id)
        return None

    # In flat mode, 'url' is the watch page URL.
    # In full mode, 'url' is the media stream URL — use 'webpage_url' instead.
    if flat:
        url = entry.get("url", "")
    else:
        url = entry.get("webpage_url", "") or entry.get("original_url", "")

    if not url and video_id:
        url = f"https://www.youtube.com/watch?v={video_id}"

    thumbnail = entry.get("thumbnail", "") or ""
    if not thumbnail:
        thumbs = entry.get("thumbnails") or []
        if thumbs:
            thumbnail = thumbs[-1].get("url", "")

    upload_date = entry.get("upload_date", "") or ""
    uploader = entry.get("uploader", "") or entry.get("channel", "") or ""

    return VideoMeta(
        title=title,
        url=url,
        video_id=video_id,
        thumbnail_url=thumbnail,
        upload_date=upload_date,
        uploader=uploader,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_playlist(
    url: str,
    cookies_path: Optional[str] = None,
    progress_callback=None,
    flat: bool = True,
) -> PlaylistInfo:
    """Extract metadata for all videos in a YouTube playlist or channel.

    Args:
        url: A YouTube playlist or channel URL.
        cookies_path: Optional path to a ``cookies.txt`` file for
            authenticated access.
        progress_callback: Optional callable ``(current: int, total: int) -> None``
            invoked after each entry is processed.
        flat: If True (default), use fast flat extraction (no upload
            dates).  If False, use full extraction to get dates/uploader.

    Returns:
        A ``PlaylistInfo`` object containing the playlist title and a
        list of ``VideoMeta`` entries (skipping deleted / private
        videos).

    Raises:
        yt_dlp.utils.DownloadError: If the URL is invalid or unreachable.
    """
    opts = _build_ydl_opts(cookies_path, flat=flat)
    info = PlaylistInfo()

    with yt_dlp.YoutubeDL(opts) as ydl:
        result = ydl.extract_info(url, download=False)

        if result is None:
            return info

        # Single video (not a playlist).
        if result.get("_type") != "playlist":
            meta = _entry_to_meta(result, flat=flat)
            if meta:
                info.title = meta.title
                info.videos = [meta]
                info.video_count = 1
            return info

        # Playlist / channel.
        info.title = result.get("title", "Untitled Playlist")
        info.thumbnail_url = result.get("thumbnail", "")

        # Entries may be a lazy iterator (full extraction) — materialise
        # inside the `with` block so the ydl session is still alive.
        entries = result.get("entries") or []
        entries_list = list(entries)

    total = len(entries_list)
    for idx, entry in enumerate(entries_list):
        if entry is None:
            # Full extraction with ignoreerrors can yield None entries.
            continue
        meta = _entry_to_meta(entry, flat=flat)
        if meta:
            info.videos.append(meta)
        if progress_callback and total:
            progress_callback(idx + 1, total)

    info.video_count = len(info.videos)
    return info
