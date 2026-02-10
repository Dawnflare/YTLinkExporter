"""
Filter Panel — Date Range, Count Limit, Keyword Filter

A collapsible frame that groups all optional extraction filters.
Includes a date-filter toggle that controls visibility of date fields
and signals to the app whether full extraction is needed.
"""

from __future__ import annotations

from datetime import date, timedelta
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

        # ---- Date Filter Toggle ----
        self._date_enabled_var = ctk.BooleanVar(value=False)
        date_toggle_row = ctk.CTkFrame(self._content, fg_color="transparent")
        date_toggle_row.pack(fill="x", pady=(2, 0))
        ctk.CTkSwitch(
            date_toggle_row,
            text="Enable Date Filter",
            variable=self._date_enabled_var,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._on_date_toggle,
        ).pack(side="left")

        # Hint label (shown when date filter is toggled)
        self._date_hint = ctk.CTkLabel(
            date_toggle_row,
            text="⚠ Reload metadata for dates",
            font=ctk.CTkFont(size=11),
            text_color=("orange", "#FFA500"),
        )
        # Initially hidden — shown when date filter is toggled on.

        # ---- Date fields container (hidden by default) ----
        self._date_frame = ctk.CTkFrame(self._content, fg_color="transparent")
        # Not packed yet — shown when toggle is on.

        # Start Date
        self._add_label(self._date_frame, "Start Date (YYYY-MM-DD)")
        self.date_start_var = ctk.StringVar()
        start_row = ctk.CTkFrame(self._date_frame, fg_color="transparent")
        start_row.pack(fill="x", pady=(0, 2))
        ctk.CTkEntry(
            start_row, textvariable=self.date_start_var,
            placeholder_text="e.g. 2024-01-01", height=32,
        ).pack(side="left", fill="x", expand=True)

        # Quick-select buttons for start date
        presets_frame = ctk.CTkFrame(self._date_frame, fg_color="transparent")
        presets_frame.pack(fill="x", pady=(0, 6))

        presets = [
            ("1W", 7),
            ("1M", 30),
            ("6M", 182),
            ("1Y", 365),
            ("2Y", 730),
            ("5Y", 1825),
            ("10Y", 3650),
        ]
        for label, days in presets:
            ctk.CTkButton(
                presets_frame,
                text=label,
                width=42,
                height=26,
                font=ctk.CTkFont(size=11),
                command=lambda d=days: self._set_start_ago(d),
            ).pack(side="left", padx=(0, 4))

        # End Date
        self._add_label(self._date_frame, "End Date (YYYY-MM-DD)")
        self.date_end_var = ctk.StringVar()
        end_row = ctk.CTkFrame(self._date_frame, fg_color="transparent")
        end_row.pack(fill="x", pady=(0, 6))
        ctk.CTkEntry(
            end_row, textvariable=self.date_end_var,
            placeholder_text="e.g. 2024-12-31", height=32,
        ).pack(side="left", fill="x", expand=True, padx=(0, 6))

        ctk.CTkButton(
            end_row,
            text="Today",
            width=70,
            height=32,
            font=ctk.CTkFont(size=11),
            command=self._set_end_today,
        ).pack(side="right")

        # ---- Count limit (always visible) ----
        self._add_label(self._content, "Max Videos (0 = all)")
        self.limit_var = ctk.StringVar(value="0")
        ctk.CTkEntry(
            self._content, textvariable=self.limit_var,
            placeholder_text="0", height=32,
        ).pack(fill="x", pady=(0, 6))

        # ---- Keyword include (always visible) ----
        self._add_label(self._content, "Include Keyword")
        self.keyword_include_var = ctk.StringVar()
        ctk.CTkEntry(
            self._content, textvariable=self.keyword_include_var,
            placeholder_text="e.g. Tutorial", height=32,
        ).pack(fill="x", pady=(0, 6))

        # ---- Keyword exclude (always visible) ----
        self._add_label(self._content, "Exclude Keyword")
        self.keyword_exclude_var = ctk.StringVar()
        ctk.CTkEntry(
            self._content, textvariable=self.keyword_exclude_var,
            placeholder_text="e.g. Shorts", height=32,
        ).pack(fill="x", pady=(0, 6))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def date_filter_enabled(self) -> bool:
        """Whether the date filter toggle is on."""
        return self._date_enabled_var.get()

    def get_filters(self) -> dict:
        """Return the current filter values as a dictionary.

        Returns:
            A dict with keys ``date_start``, ``date_end``, ``limit``,
            ``keyword_include``, and ``keyword_exclude``.  Empty strings
            represent unused filters, and ``limit`` is ``None`` when
            set to 0 or empty.  Date values are only returned when the
            date filter toggle is enabled.
        """
        limit_raw = self.limit_var.get().strip()
        try:
            limit = int(limit_raw) if limit_raw else None
        except ValueError:
            limit = None

        if limit is not None and limit <= 0:
            limit = None

        # Only apply date filters when the toggle is on.
        if self._date_enabled_var.get():
            date_start = self.date_start_var.get().strip() or None
            date_end = self.date_end_var.get().strip() or None
        else:
            date_start = None
            date_end = None

        return {
            "date_start": date_start,
            "date_end": date_end,
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

    def _on_date_toggle(self) -> None:
        """Show or hide the date fields based on the toggle."""
        if self._date_enabled_var.get():
            # Insert date frame right after the toggle row (before Max Videos).
            self._date_frame.pack(fill="x", pady=(4, 0),
                                  after=self._date_frame.master.winfo_children()[1])
            self._date_hint.pack(side="left", padx=(10, 0))
        else:
            self._date_frame.pack_forget()
            self._date_hint.pack_forget()
            # Clear date values when toggling off.
            self.date_start_var.set("")
            self.date_end_var.set("")

    def _set_start_ago(self, days: int) -> None:
        """Set the start date to *days* ago from today."""
        target = date.today() - timedelta(days=days)
        self.date_start_var.set(target.isoformat())

    def _set_end_today(self) -> None:
        """Set the end date to today's date."""
        self.date_end_var.set(date.today().isoformat())
