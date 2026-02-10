"""
YTLinkExporter — Entry Point

Launches the CustomTkinter GUI application. This module is the single
entry point for the entire application and should be invoked directly:

    python src/main.py
"""

import sys
import os

# ---------------------------------------------------------------------------
# Ensure the project root (parent of src/) is on sys.path so that
# intra-package imports like `from src.core import ...` resolve correctly
# when running this file directly.
# ---------------------------------------------------------------------------
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)


def main() -> None:
    """Create and launch the YTLinkExporter application window.

    This function initialises the root CTk window via ``App`` and enters
    the Tkinter main-loop.  It is intentionally kept thin so that all
    real logic lives in the ``gui`` and ``core`` packages.
    """
    # Lazy import so that the module can be imported for testing without
    # immediately spinning up a GUI.
    from src.gui.app import App  # noqa: WPS433 (nested import)

    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
