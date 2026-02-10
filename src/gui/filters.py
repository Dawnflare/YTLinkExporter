"""
Filter Panel — Date Range, Count Limit, Keyword Filter

A collapsible frame that groups all optional extraction filters.
"""

from __future__ import annotations

from typing import Optional

import customtkinter as ctk


class FilterPanel(ctk.CTkFrame):
    """Collapsible panel containing date-range, count-limit, and keyword filters."""

    def __init__(self, master: ctk.CTk | ctk.CTkFrame, **kwargs):
        """Initialise the filter panel.

        Args:
            master: Parent Tkinter widget.
            **kwargs: Forwarded to ``CTkFrame``.
        """
        super().__init__(master, **kwargs)

        # --- Toggle button ---
        self._expanded = True
        self._toggle_btn = ctk.CTkButton(
            self,
            text="▼  Filters",
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray80", "gray30"),
            anchor="w",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._toggle,
        )
        self._toggle_btn.pack(fill="x", padx=6, pady=(6, 2))

        # --- Content frame (collapsible) ---
        self._content = ctk.CTkFrame(self, fg_color="transparent")
        self._content.pack(fill="x", padx=10, pady=(0, 10))

        # Date start
        self._add_label(self._content, "Start Date (YYYY-MM-DD)")
        self.date_start_var = ctk.StringVar()
        ctk.CTkEntry(
            self._content, textvariable=self.date_start_var,
            placeholder_text="e.g. 2024-01-01", height=32,
        ).pack(fill="x", pady=(0, 6))

        # Date end
        self._add_label(self._content, "End Date (YYYY-MM-DD)")
        self.date_end_var = ctk.StringVar()
        ctk.CTkEntry(
            self._content, textvariable=self.date_end_var,
            placeholder_text="e.g. 2024-12-31", height=32,
        ).pack(fill="x", pady=(0, 6))

        # Count limit
        self._add_label(self._content, "Max Videos (0 = all)")
        self.limit_var = ctk.StringVar(value="0")
        ctk.CTkEntry(
            self._content, textvariable=self.limit_var,
            placeholder_text="0", height=32,
        ).pack(fill="x", pady=(0, 6))

        # Keyword include
        self._add_label(self._content, "Include Keyword")
        self.keyword_include_var = ctk.StringVar()
        ctk.CTkEntry(
            self._content, textvariable=self.keyword_include_var,
            placeholder_text="e.g. Tutorial", height=32,
        ).pack(fill="x", pady=(0, 6))

        # Keyword exclude
        self._add_label(self._content, "Exclude Keyword")
        self.keyword_exclude_var = ctk.StringVar()
        ctk.CTkEntry(
            self._content, textvariable=self.keyword_exclude_var,
            placeholder_text="e.g. Shorts", height=32,
        ).pack(fill="x", pady=(0, 6))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_filters(self) -> dict:
        """Return the current filter values as a dictionary.

        Returns:
            A dict with keys ``date_start``, ``date_end``, ``limit``,
            ``keyword_include``, and ``keyword_exclude``.  Empty strings
            represent unused filters, and ``limit`` is ``None`` when
            set to 0 or empty.
        """
        limit_raw = self.limit_var.get().strip()
        try:
            limit = int(limit_raw) if limit_raw else None
        except ValueError:
            limit = None

        if limit is not None and limit <= 0:
            limit = None

        return {
            "date_start": self.date_start_var.get().strip() or None,
            "date_end": self.date_end_var.get().strip() or None,
            "limit": limit,
            "keyword_include": self.keyword_include_var.get().strip() or None,
            "keyword_exclude": self.keyword_exclude_var.get().strip() or None,
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _add_label(parent: ctk.CTkFrame, text: str) -> None:
        """Add a small label above an input field."""
        ctk.CTkLabel(parent, text=text, font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(2, 0))

    def _toggle(self) -> None:
        """Expand or collapse the filter content frame."""
        if self._expanded:
            self._content.pack_forget()
            self._toggle_btn.configure(text="▶  Filters")
        else:
            self._content.pack(fill="x", padx=10, pady=(0, 10))
            self._toggle_btn.configure(text="▼  Filters")
        self._expanded = not self._expanded
