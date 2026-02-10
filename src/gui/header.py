"""
Header Panel — URL Input & Load Metadata Button

Contains the primary URL entry field and a "Load Metadata" button that
triggers flat metadata extraction to verify the link and display the
playlist title.
"""

from __future__ import annotations

from typing import Callable, Optional

import customtkinter as ctk


class HeaderPanel(ctk.CTkFrame):
    """Top section of the application with URL input and Load button.

    Attributes:
        url_var: A ``StringVar`` bound to the URL entry field.
    """

    def __init__(
        self,
        master: ctk.CTk | ctk.CTkFrame,
        on_load: Optional[Callable[[str], None]] = None,
        **kwargs,
    ):
        """Initialise the header panel.

        Args:
            master: Parent Tkinter widget.
            on_load: Callback invoked with the URL string when the user
                clicks "Load Metadata".
            **kwargs: Extra keyword arguments forwarded to ``CTkFrame``.
        """
        super().__init__(master, **kwargs)
        self._on_load = on_load

        # --- Section label ---
        title = ctk.CTkLabel(self, text="YouTube Playlist / Channel URL", font=ctk.CTkFont(size=14, weight="bold"))
        title.pack(anchor="w", padx=10, pady=(10, 4))

        # --- URL input row ---
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x", padx=10, pady=(0, 6))

        self.url_var = ctk.StringVar()
        self._entry = ctk.CTkEntry(
            input_frame,
            textvariable=self.url_var,
            placeholder_text="https://www.youtube.com/playlist?list=...",
            height=38,
            font=ctk.CTkFont(size=13),
        )
        self._entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self._load_btn = ctk.CTkButton(
            input_frame,
            text="Load Metadata",
            width=140,
            height=38,
            command=self._handle_load,
        )
        self._load_btn.pack(side="right")

        # --- Feedback labels ---
        self._info_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self._info_label.pack(anchor="w", padx=10, pady=(0, 6))

        self._error_label = ctk.CTkLabel(
            self, text="", text_color="#ff4444", font=ctk.CTkFont(size=12),
        )
        self._error_label.pack(anchor="w", padx=10, pady=(0, 10))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_info(self, text: str) -> None:
        """Display an informational message (e.g. playlist title).

        Args:
            text: The message to display.
        """
        self.after(0, lambda: self._info_label.configure(text=text))
        self.after(0, lambda: self._error_label.configure(text=""))

    def set_error(self, text: str) -> None:
        """Display a red error message.

        Args:
            text: The error message to display.
        """
        self.after(0, lambda: self._error_label.configure(text=text))
        self.after(0, lambda: self._info_label.configure(text=""))

    def set_loading(self, loading: bool) -> None:
        """Toggle the Load button enabled/disabled state.

        Args:
            loading: ``True`` to disable the button (show spinner-like
                text), ``False`` to re-enable it.
        """
        if loading:
            self.after(0, lambda: self._load_btn.configure(state="disabled", text="Loading…"))
        else:
            self.after(0, lambda: self._load_btn.configure(state="normal", text="Load Metadata"))

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _handle_load(self) -> None:
        """Validate the URL and invoke the on_load callback."""
        url = self.url_var.get().strip()
        if not url:
            self.set_error("Please enter a URL.")
            return
        if "youtube.com" not in url and "youtu.be" not in url:
            self.set_error("Please enter a valid YouTube URL.")
            return

        self._error_label.configure(text="")
        if self._on_load:
            self._on_load(url)
