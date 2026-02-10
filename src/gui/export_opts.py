"""
Export Options Panel — Format Checkboxes & Output Path

Lets the user choose which export formats to generate and where to
save them.
"""

from __future__ import annotations

from tkinter import filedialog
from typing import Optional

import customtkinter as ctk

from src.config.settings import get as get_setting


class ExportOptionsPanel(ctk.CTkFrame):
    """Panel with format checkboxes and a save-path selector."""

    def __init__(self, master: ctk.CTk | ctk.CTkFrame, **kwargs):
        """Initialise the export options panel.

        Args:
            master: Parent Tkinter widget.
            **kwargs: Forwarded to ``CTkFrame``.
        """
        super().__init__(master, **kwargs)

        # --- Section label ---
        title = ctk.CTkLabel(self, text="Export Options", font=ctk.CTkFont(size=14, weight="bold"))
        title.pack(anchor="w", padx=10, pady=(10, 6))

        # --- Checkboxes ---
        cb_frame = ctk.CTkFrame(self, fg_color="transparent")
        cb_frame.pack(fill="x", padx=10, pady=(0, 6))

        self.shortcut_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(cb_frame, text="Windows Shortcuts (.url)", variable=self.shortcut_var).pack(anchor="w", pady=2)

        self.html_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(cb_frame, text="Offline HTML Catalog (.html)", variable=self.html_var).pack(anchor="w", pady=2)

        self.text_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(cb_frame, text="Plain Text List (.txt)", variable=self.text_var).pack(anchor="w", pady=2)

        # --- Save path ---
        path_label = ctk.CTkLabel(self, text="Save Location", font=ctk.CTkFont(size=12))
        path_label.pack(anchor="w", padx=10, pady=(6, 2))

        path_frame = ctk.CTkFrame(self, fg_color="transparent")
        path_frame.pack(fill="x", padx=10, pady=(0, 10))

        default_path = get_setting("default_save_path") or ""
        self.path_var = ctk.StringVar(value=default_path)
        self._path_entry = ctk.CTkEntry(
            path_frame, textvariable=self.path_var, height=32,
            font=ctk.CTkFont(size=12),
        )
        self._path_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))

        browse_btn = ctk.CTkButton(
            path_frame, text="Browse…", width=90, height=32,
            command=self._browse,
        )
        browse_btn.pack(side="right")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_options(self) -> dict:
        """Return the current export options.

        Returns:
            A dict with keys ``shortcuts``, ``html``, ``text``
            (booleans) and ``output_dir`` (string path).
        """
        return {
            "shortcuts": self.shortcut_var.get(),
            "html": self.html_var.get(),
            "text": self.text_var.get(),
            "output_dir": self.path_var.get().strip(),
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _browse(self) -> None:
        """Open a folder-selection dialog."""
        folder = filedialog.askdirectory(title="Select save folder")
        if folder:
            self.path_var.set(folder)
