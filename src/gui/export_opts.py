"""
Export Options Panel — Format Checkboxes, Output Path & Cookies

Lets the user choose which export formats to generate, where to save
them, and optionally provide a cookies.txt file for restricted content.
Settings are persisted automatically when changed.
"""

from __future__ import annotations

from tkinter import filedialog

import customtkinter as ctk

from src.config.settings import get as get_setting, update as update_setting


class ExportOptionsPanel(ctk.CTkFrame):
    """Panel with format checkboxes, save-path selector, and cookies selector."""

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
        path_frame.pack(fill="x", padx=10, pady=(0, 6))

        default_path = get_setting("default_save_path") or ""
        self.path_var = ctk.StringVar(value=default_path)
        self._path_entry = ctk.CTkEntry(
            path_frame, textvariable=self.path_var, height=32,
            font=ctk.CTkFont(size=12),
        )
        self._path_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))

        browse_btn = ctk.CTkButton(
            path_frame, text="Browse…", width=90, height=32,
            command=self._browse_save_path,
        )
        browse_btn.pack(side="right")

        # --- Cookies path ---
        cookies_label = ctk.CTkLabel(self, text="Cookies File (optional)", font=ctk.CTkFont(size=12))
        cookies_label.pack(anchor="w", padx=10, pady=(4, 2))

        cookies_frame = ctk.CTkFrame(self, fg_color="transparent")
        cookies_frame.pack(fill="x", padx=10, pady=(0, 10))

        default_cookies = get_setting("cookies_path") or ""
        self.cookies_var = ctk.StringVar(value=default_cookies)
        self._cookies_entry = ctk.CTkEntry(
            cookies_frame, textvariable=self.cookies_var, height=32,
            font=ctk.CTkFont(size=12),
            placeholder_text="No cookies file selected",
        )
        self._cookies_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))

        cookies_btn = ctk.CTkButton(
            cookies_frame, text="Browse…", width=90, height=32,
            command=self._browse_cookies,
        )
        cookies_btn.pack(side="right")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_options(self) -> dict:
        """Return the current export options.

        Returns:
            A dict with keys ``shortcuts``, ``html``, ``text``
            (booleans), ``output_dir`` (string path), and
            ``cookies_path`` (string path or empty string).
        """
        return {
            "shortcuts": self.shortcut_var.get(),
            "html": self.html_var.get(),
            "text": self.text_var.get(),
            "output_dir": self.path_var.get().strip(),
            "cookies_path": self.cookies_var.get().strip(),
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _browse_save_path(self) -> None:
        """Open a folder-selection dialog and persist the choice."""
        folder = filedialog.askdirectory(title="Select save folder")
        if folder:
            self.path_var.set(folder)
            update_setting("default_save_path", folder)

    def _browse_cookies(self) -> None:
        """Open a file-selection dialog for cookies.txt and persist."""
        filepath = filedialog.askopenfilename(
            title="Select cookies.txt file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if filepath:
            self.cookies_var.set(filepath)
            update_setting("cookies_path", filepath)
