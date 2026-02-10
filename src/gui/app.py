"""
Root Application Window

Assembles all GUI panels (Header → Filters → Export Options → Status)
into a single ``CTk`` window and wires the **Export** button to a
background-thread pipeline: extract → filter → export.
"""

from __future__ import annotations

import logging
import os
from tkinter import messagebox

import customtkinter as ctk

from src.config.settings import get as get_setting
from src.core.extractor import PlaylistInfo, extract_playlist
from src.core.filters import apply_filters
from src.core.sanitizer import sanitize_filename
from src.exporters.html_catalog import export_html_catalog
from src.exporters.shortcut import export_shortcuts
from src.exporters.text_list import export_text_list
from src.gui.export_opts import ExportOptionsPanel
from src.gui.filters import FilterPanel
from src.gui.header import HeaderPanel
from src.gui.status import StatusPanel
from src.utils.threading import run_in_background
# ... (imports done)

# ... (inside App class)

    def _on_export(self) -> None:
        """Handle the "Export" click.

        Runs the filter → export pipeline on a background thread.
        """
        if not self._playlist_info:
            return

        opts = self._export_opts.get_options()
        base_output_dir = opts["output_dir"]
        if not base_output_dir:
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

        # Determine final output directory
        if opts["subfolder"] and title:
            safe_title = sanitize_filename(title)
            output_dir = os.path.join(base_output_dir, safe_title)
            try:
                os.makedirs(output_dir, exist_ok=True)
                self._status.log(f"Exporting to subfolder: {safe_title}")
            except OSError as e:
                self._status.log(f"⚠ Could not create subfolder '{safe_title}': {e}")
                output_dir = base_output_dir
        else:
            output_dir = base_output_dir

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
            self.after(0, lambda: self._export_btn.configure(state="normal"))

        def _on_error(exc: Exception):
            self._status.log(f"❌ Export failed: {exc}")
            self.after(0, lambda: self._export_btn.configure(state="normal"))
            self.after(0, lambda: messagebox.showerror("Export Error", str(exc)))

        run_in_background(_run, on_success=_on_success, on_error=_on_error)
