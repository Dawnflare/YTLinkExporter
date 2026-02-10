"""
Persistent Settings Manager

Reads and writes user preferences to a JSON file located at
``~/.ytlinkexporter/settings.json``.  Provides sensible defaults for
every key so the application can always start cleanly.
"""

import json
import os
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
_SETTINGS_DIR = Path.home() / ".ytlinkexporter"
_SETTINGS_FILE = _SETTINGS_DIR / "settings.json"

_DEFAULTS: dict[str, Any] = {
    "default_save_path": str(Path.home() / "Downloads" / "YTLinkExporter"),
    "cookies_path": "",
    "theme": "system",  # "system" | "dark" | "light"
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_settings() -> dict[str, Any]:
    """Load settings from disk, merging with defaults for any missing keys.

    Returns:
        dict[str, Any]: A dictionary of all settings values.  Missing keys
        are filled from ``_DEFAULTS``.
    """
    settings = dict(_DEFAULTS)  # start with a copy of defaults
    if _SETTINGS_FILE.exists():
        try:
            with open(_SETTINGS_FILE, "r", encoding="utf-8") as fh:
                stored = json.load(fh)
            if isinstance(stored, dict):
                settings.update(stored)
        except (json.JSONDecodeError, OSError):
            # Corrupt file — silently fall back to defaults.
            pass
    return settings


def save_settings(settings: dict[str, Any]) -> None:
    """Persist the given settings dictionary to disk.

    Args:
        settings: A dictionary of key/value pairs to save.  Only the
            keys present in this dictionary are written.

    Raises:
        OSError: If the settings directory cannot be created.
    """
    _SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
    with open(_SETTINGS_FILE, "w", encoding="utf-8") as fh:
        json.dump(settings, fh, indent=2)


def get(key: str) -> Any:
    """Convenience helper — load settings and return a single value.

    Args:
        key: The setting name to retrieve.

    Returns:
        The stored value, or the default if the key has never been set.
    """
    return load_settings().get(key, _DEFAULTS.get(key))


def update(key: str, value: Any) -> None:
    """Convenience helper — update a single key and persist.

    Args:
        key: The setting name to update.
        value: The new value to store.
    """
    settings = load_settings()
    settings[key] = value
    save_settings(settings)
