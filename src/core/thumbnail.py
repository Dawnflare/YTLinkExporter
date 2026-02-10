"""
Thumbnail Downloader & Base64 Encoder

Downloads a thumbnail image from a URL, resizes it to a maximum width
(default 320 px), and returns it as a Base64-encoded data-URI string
suitable for embedding directly in an ``<img>`` tag.
"""

from __future__ import annotations

import base64
import io
import logging
from typing import Optional

import requests
from PIL import Image

logger = logging.getLogger(__name__)

# A 1×1 transparent PNG used as a fallback when thumbnail download fails.
_PLACEHOLDER_B64 = (
    "data:image/png;base64,"
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVQI12Ng"
    "AAIABQABNjN9GQAAAABJRU5ErkJggg=="
)

# Reasonable timeout for thumbnail downloads (seconds).
_DOWNLOAD_TIMEOUT = 15


def download_and_encode(
    url: str,
    max_width: int = 320,
    timeout: int = _DOWNLOAD_TIMEOUT,
) -> str:
    """Download a thumbnail and return it as a Base64 data-URI string.

    The image is:
    1. Downloaded via HTTP GET.
    2. Resized so that its width does not exceed *max_width* while
       preserving the aspect ratio.
    3. Re-encoded as JPEG (quality 80) for a good size/quality trade-off.
    4. Converted to a ``data:image/jpeg;base64,...`` string.

    Args:
        url: The thumbnail image URL.
        max_width: Maximum pixel width after resize.  Height is scaled
            proportionally.
        timeout: HTTP request timeout in seconds.

    Returns:
        A ``data:image/jpeg;base64,…`` string on success, or a tiny
        transparent-PNG placeholder on failure.
    """
    if not url:
        return _PLACEHOLDER_B64

    try:
        raw_bytes = _download_image(url, timeout)
        resized_bytes = _resize_image(raw_bytes, max_width)
        return _bytes_to_data_uri(resized_bytes)
    except Exception:
        logger.warning("Thumbnail download/encode failed for %s", url, exc_info=True)
        return _PLACEHOLDER_B64


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _download_image(url: str, timeout: int) -> bytes:
    """Fetch raw image bytes from *url*.

    Args:
        url: The image URL.
        timeout: Request timeout in seconds.

    Returns:
        Raw bytes of the downloaded image.

    Raises:
        requests.RequestException: On any network error.
    """
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.content


def _resize_image(raw_bytes: bytes, max_width: int) -> bytes:
    """Resize an image so its width ≤ *max_width*, keeping aspect ratio.

    The output is always JPEG at quality 80.

    Args:
        raw_bytes: The original image bytes (any format Pillow supports).
        max_width: Desired maximum width in pixels.

    Returns:
        JPEG-encoded bytes of the resized image.
    """
    img = Image.open(io.BytesIO(raw_bytes))

    # Convert palette / RGBA images to RGB for JPEG output.
    if img.mode in ("P", "RGBA", "LA"):
        img = img.convert("RGB")

    if img.width > max_width:
        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        img = img.resize((max_width, new_height), Image.LANCZOS)

    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=80, optimize=True)
    return buffer.getvalue()


def _bytes_to_data_uri(jpeg_bytes: bytes) -> str:
    """Encode JPEG bytes as a Base64 data-URI.

    Args:
        jpeg_bytes: JPEG image bytes.

    Returns:
        A string like ``data:image/jpeg;base64,/9j/4AAQ...``.
    """
    encoded = base64.b64encode(jpeg_bytes).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"
