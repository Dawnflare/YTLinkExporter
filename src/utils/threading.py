"""
Background Thread Helper

Provides a simple wrapper around ``threading.Thread`` that integrates
with Tkinter's ``after()`` mechanism so that long-running operations
never block the GUI event loop.
"""

from __future__ import annotations

import threading
import traceback
from typing import Any, Callable, Optional


def run_in_background(
    fn: Callable[..., Any],
    *,
    args: tuple = (),
    kwargs: dict | None = None,
    on_success: Optional[Callable[[Any], None]] = None,
    on_error: Optional[Callable[[Exception], None]] = None,
    daemon: bool = True,
) -> threading.Thread:
    """Run *fn* on a background thread with optional callbacks.

    After *fn* completes, either *on_success* or *on_error* is invoked
    **on the same background thread**.  If the caller needs to update
    the GUI, those callbacks should use ``widget.after()`` to marshal
    the update back onto the main thread.

    Args:
        fn: The callable to run in the background.
        args: Positional arguments forwarded to *fn*.
        kwargs: Keyword arguments forwarded to *fn*.
        on_success: Called with the return value of *fn* on success.
        on_error: Called with the caught ``Exception`` on failure.
        daemon: Whether the thread is daemonic (default ``True``).

    Returns:
        The started ``threading.Thread`` instance.
    """
    kwargs = kwargs or {}

    def _worker() -> None:
        try:
            result = fn(*args, **kwargs)
            if on_success:
                on_success(result)
        except Exception as exc:
            if on_error:
                on_error(exc)
            else:
                traceback.print_exc()

    thread = threading.Thread(target=_worker, daemon=daemon)
    thread.start()
    return thread
