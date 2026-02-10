"""
Video Metadata Filters

Pure functions that narrow a list of ``VideoMeta`` objects by date
range, quantity limit, and keyword matching.  All filters are
optional — passing ``None`` or empty values means "no constraint".
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from src.core.extractor import VideoMeta


def apply_filters(
    videos: list[VideoMeta],
    date_start: Optional[str] = None,
    date_end: Optional[str] = None,
    limit: Optional[int] = None,
    keyword_include: Optional[str] = None,
    keyword_exclude: Optional[str] = None,
) -> list[VideoMeta]:
    """Return a filtered copy of *videos*.

    Filters are applied in order: date range → keyword → limit.  Each
    filter is skipped when its parameter is ``None`` or empty.

    Args:
        videos: The full list of ``VideoMeta`` to filter.
        date_start: Inclusive start date as ``YYYYMMDD`` or
            ``YYYY-MM-DD``.  Videos before this date are excluded.
        date_end: Inclusive end date in the same format.
        limit: Maximum number of videos to return (most recent first
            after other filters are applied).
        keyword_include: Case-insensitive substring that **must** appear
            in the video title.
        keyword_exclude: Case-insensitive substring that **must not**
            appear in the video title.

    Returns:
        A new list containing only the videos that pass all active
        filters.
    """
    result = list(videos)

    # --- Date range filter ---
    if date_start or date_end:
        result = _filter_by_date(result, date_start, date_end)

    # --- Keyword filters ---
    if keyword_include:
        kw_lower = keyword_include.lower()
        result = [v for v in result if kw_lower in v.title.lower()]

    if keyword_exclude:
        kw_lower = keyword_exclude.lower()
        result = [v for v in result if kw_lower not in v.title.lower()]

    # --- Quantity limit ---
    if limit is not None and limit > 0:
        result = result[:limit]

    return result


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_date(date_str: str) -> Optional[datetime]:
    """Parse a date string in ``YYYYMMDD`` or ``YYYY-MM-DD`` format.

    Args:
        date_str: The raw date string.

    Returns:
        A ``datetime`` object, or ``None`` if parsing fails.
    """
    for fmt in ("%Y%m%d", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


def _filter_by_date(
    videos: list[VideoMeta],
    date_start: Optional[str],
    date_end: Optional[str],
) -> list[VideoMeta]:
    """Keep only videos whose upload date falls within the range.

    Videos with empty or unparseable ``upload_date`` are **excluded**
    when a date filter is active, since full extraction should provide
    dates for all available videos.

    Args:
        videos: Input list.
        date_start: Inclusive start (``YYYYMMDD`` or ``YYYY-MM-DD``).
        date_end: Inclusive end.

    Returns:
        Filtered list.
    """
    start = _parse_date(date_start) if date_start else None
    end = _parse_date(date_end) if date_end else None

    filtered: list[VideoMeta] = []
    for v in videos:
        vdate = _parse_date(v.upload_date)
        if vdate is None:
            # No date available — exclude when date filter is active.
            continue
        if start and vdate < start:
            continue
        if end and vdate > end:
            continue
        filtered.append(v)

    return filtered
