"""
Root Application Window

Assembles all GUI panels (Header → Filters → Export Options → Status)
into a single ``CTk`` window and wires the **Export** button to a
background-thread pipeline: extract → filter → export.
"""

from __future__ import annotations

import logging
from tkinter import messagebox

import customtkinter as ctk

from src.config.settings import get as get_setting
from src.core.extractor import PlaylistInfo, extract_playlist
from src.core.filters import apply_filters
from src.exporters.html_catalog import export_html_catalog
from src.exporters.shortcut import export_shortcuts
from src.exporters.text_list import export_text_list
from src.gui.export_opts import ExportOptionsPanel
from src.gui.filters import FilterPanel
from src.gui.header import HeaderPanel
from src.gui.status import StatusPanel
from src.utils.threading import run_in_background

logger = logging.getLogger(__name__)

# Configure basic logging so messages show in the console during development.
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


class App(ctk.CTk):
    """Main YTLinkExporter application window.

    Manages the overall layout, holds references to each panel, and
    coordinates the extract-filter-export pipeline.
    """

    def __init__(self):
        """Initialise the application window and all child panels."""
        super().__init__()

        # --- Window setup ---
        self.title("YTLinkExporter")
        self.geometry("720x1020")
        self.minsize(600, 860)

        # Apply theme from settings.
        theme = get_setting("theme") or "system"
        ctk.set_appearance_mode(theme)
        ctk.set_default_color_theme("blue")

        # Internal state
        self._playlist_info: PlaylistInfo | None = None

        # --- Build panels ---
        self._header = HeaderPanel(self, on_load=self._on_load_metadata)
        self._header.pack(fill="x", padx=12, pady=(12, 4))

        self._filters = FilterPanel(self)
        self._filters.pack(fill="x", padx=12, pady=4)

        self._export_opts = ExportOptionsPanel(self)
        self._export_opts.pack(fill="x", padx=12, pady=4)

        # --- Export button ---
        self._export_btn = ctk.CTkButton(
            self,
            text="Export",
            height=42,
            font=ctk.CTkFont(size=15, weight="bold"),
            state="disabled",
            command=self._on_export,
        )
        self._export_btn.pack(fill="x", padx=12, pady=(8, 4))

        self._status = StatusPanel(self)
        self._status.pack(fill="both", expand=True, padx=12, pady=(4, 12))

    # ------------------------------------------------------------------
    # Load Metadata
    # ------------------------------------------------------------------

    def _on_load_metadata(self, url: str) -> None:
        """Handle the "Load Metadata" click.

        Runs extraction on a background thread so the GUI stays
        responsive.

        Args:
            url: The YouTube playlist/channel URL entered by the user.
        """
        self._header.set_loading(True)
        self._status.reset()
        self._status.log(f"Loading metadata for: {url}")

        cookies = self._export_opts.cookies_var.get().strip() or None

        def _extract():
            return extract_playlist(url, cookies_path=cookies)

        def _on_success(info: PlaylistInfo):
            self._playlist_info = info
            self.after(0, self._header.set_info, f"✓ {info.title}  ({info.video_count} videos)")
            self.after(0, self._header.set_loading, False)
            self.after(0, self._export_btn.configure, {"state": "normal"})
            self._status.log(f"Loaded {info.video_count} videos from \"{info.title}\".")

        def _on_error(exc: Exception):
            self.after(0, self._header.set_error, f"Error: {exc}")
            self.after(0, self._header.set_loading, False)
            self._status.log(f"❌ Failed: {exc}")

        run_in_background(_extract, on_success=_on_success, on_error=_on_error)

    # ------------------------------------------------------------------
    # Export Pipeline
    # ------------------------------------------------------------------

    def _on_export(self) -> None:
        """Handle the "Export" click.

        Runs the filter → export pipeline on a background thread.
        """
        if not self._playlist_info:
            return

        opts = self._export_opts.get_options()
        output_dir = opts["output_dir"]
        if not output_dir:
            messagebox.showwarning("No Save Location", "Please select a save location.")
            return

        if not (opts["shortcuts"] or opts["html"] or opts["text"]):
            messagebox.showwarning("No Format Selected", "Please select at least one export format.")
            return

        # Disable Export button during processing.
        self._export_btn.configure(state="disabled")
        self._status.reset()
        self._status.log("Starting export…")

        filters = self._filters.get_filters()
        videos = self._playlist_info.videos
        title = self._playlist_info.title

        def _run():
            # --- Apply filters ---
            filtered = apply_filters(
                videos,
                date_start=filters.get("date_start"),
                date_end=filters.get("date_end"),
                limit=filters.get("limit"),
                keyword_include=filters.get("keyword_include"),
                keyword_exclude=filters.get("keyword_exclude"),
            )
            self._status.log(f"Filtered to {len(filtered)} videos.")

            total_steps = 0
            if opts["shortcuts"]:
                total_steps += len(filtered)
            if opts["html"]:
                total_steps += len(filtered)
            if opts["text"]:
                total_steps += 1

            done = [0]

            def _tick(current, total):
                done[0] += 1
                if total_steps > 0:
                    self._status.set_progress(done[0] / total_steps)

            # --- Shortcuts ---
            if opts["shortcuts"]:
                self._status.log("Generating .url shortcut files…")
                count = export_shortcuts(filtered, output_dir, progress_callback=_tick)
                self._status.log(f"  → Wrote {count} shortcut files.")

            # --- HTML catalog ---
            if opts["html"]:
                self._status.log("Generating offline HTML catalog (downloading thumbnails)…")
                path = export_html_catalog(filtered, title, output_dir, progress_callback=_tick)
                self._status.log(f"  → Wrote HTML catalog: {path}")

            # --- Text list ---
            if opts["text"]:
                self._status.log("Generating plain-text link list…")
                path = export_text_list(filtered, title, output_dir)
                done[0] += 1
                if total_steps > 0:
                    self._status.set_progress(done[0] / total_steps)
                self._status.log(f"  → Wrote text list: {path}")

            self._status.set_progress(1.0)
            self._status.log("✅ Export complete!")

        def _on_success(_):
            self.after(0, self._export_btn.configure, {"state": "normal"})

        def _on_error(exc: Exception):
            self._status.log(f"❌ Export failed: {exc}")
            self.after(0, self._export_btn.configure, {"state": "normal"})
            self.after(0, messagebox.showerror, "Export Error", str(exc))

        run_in_background(_run, on_success=_on_success, on_error=_on_error)
