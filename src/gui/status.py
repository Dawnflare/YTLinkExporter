"""
Status Panel — Progress Bar & Scrolling Log

Provides real-time visual feedback during extraction and export
operations.  All public methods are safe to call from background
threads — they internally marshal updates onto the Tkinter main
thread via ``after()``.
"""

from __future__ import annotations

import customtkinter as ctk


class StatusPanel(ctk.CTkFrame):
    """A compound widget containing a progress bar and a scrolling log.

    Usage::

        panel = StatusPanel(parent)
        panel.pack(fill="x")
        panel.log("Starting export…")
        panel.set_progress(0.5)   # 50 %
    """

    def __init__(self, master: ctk.CTk | ctk.CTkFrame, **kwargs):
        """Initialise the status panel.

        Args:
            master: Parent Tkinter widget.
            **kwargs: Extra keyword arguments forwarded to ``CTkFrame``.
        """
        super().__init__(master, **kwargs)

        # --- Section label ---
        self._label = ctk.CTkLabel(self, text="Status", font=ctk.CTkFont(size=14, weight="bold"))
        self._label.pack(anchor="w", padx=10, pady=(10, 4))

        # --- Progress bar ---
        self._progress = ctk.CTkProgressBar(self)
        self._progress.pack(fill="x", padx=10, pady=(0, 6))
        self._progress.set(0)

        # --- Scrolling log ---
        self._log = ctk.CTkTextbox(self, height=140, state="disabled", font=ctk.CTkFont(size=12))
        self._log.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    # ------------------------------------------------------------------
    # Public API (thread-safe)
    # ------------------------------------------------------------------

    def log(self, message: str) -> None:
        """Append a line to the scrolling log.

        Safe to call from any thread.

        Args:
            message: The text to append (a newline is added
                automatically).
        """
        self.after(0, self._append_log, message)

    def set_progress(self, value: float) -> None:
        """Set the progress bar value.

        Safe to call from any thread.

        Args:
            value: A float between 0.0 and 1.0.
        """
        self.after(0, self._progress.set, value)

    def reset(self) -> None:
        """Clear the log and reset progress to 0.

        Safe to call from any thread.
        """
        self.after(0, self._do_reset)

    # ------------------------------------------------------------------
    # Internal helpers (must run on the main thread)
    # ------------------------------------------------------------------

    def _append_log(self, message: str) -> None:
        """Insert text at the bottom of the log and auto-scroll."""
        self._log.configure(state="normal")
        self._log.insert("end", message + "\n")
        self._log.see("end")
        self._log.configure(state="disabled")

    def _do_reset(self) -> None:
        """Clear all log text and zero the progress bar."""
        self._log.configure(state="normal")
        self._log.delete("1.0", "end")
        self._log.configure(state="disabled")
        self._progress.set(0)
