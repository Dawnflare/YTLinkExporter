"""
Windows-Safe Filename Sanitizer

Strips characters that are illegal in Windows filenames and handles
edge cases such as trailing dots/spaces, reserved device names, and
excessively long paths.
"""

import re


# Characters forbidden by Windows in filenames.
_ILLEGAL_CHARS_RE = re.compile(r'[<>:"/\\|?*]')

# Windows reserved device names (case-insensitive).
_RESERVED_NAMES = frozenset({
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
})

# Maximum filename length before the extension (conservative).
_MAX_STEM_LENGTH = 200


def sanitize_filename(name: str) -> str:
    """Return a Windows-safe version of *name*.

    The function:
    1. Replaces illegal characters (``< > : " / \\ | ? *``) with
       underscores.
    2. Strips leading/trailing whitespace.
    3. Removes trailing dots (Windows silently strips them, causing
       mismatches).
    4. Prefixes reserved device names (``CON``, ``NUL``, etc.) with an
       underscore.
    5. Truncates the result to ``_MAX_STEM_LENGTH`` characters.
    6. Falls back to ``"untitled"`` if the result would be empty.

    Args:
        name: The raw string to sanitize (typically a video title).

    Returns:
        A non-empty string safe for use as a Windows filename stem
        (without extension).
    """
    # Step 1 — replace illegal characters
    cleaned = _ILLEGAL_CHARS_RE.sub("_", name)

    # Step 2 — strip whitespace
    cleaned = cleaned.strip()

    # Step 3 — remove trailing dots
    cleaned = cleaned.rstrip(".")

    # Step 4 — handle reserved names
    if cleaned.upper() in _RESERVED_NAMES:
        cleaned = f"_{cleaned}"

    # Step 5 — truncate to a safe length
    if len(cleaned) > _MAX_STEM_LENGTH:
        cleaned = cleaned[:_MAX_STEM_LENGTH].rstrip()

    # Step 6 — fallback for empty or meaningless result
    if not cleaned or cleaned.strip("_") == "":
        cleaned = "untitled"

    return cleaned
