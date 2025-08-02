# src/pakto/core/logging.py  (drop-in)
from __future__ import annotations

import atexit
import logging
import multiprocessing as mp
from logging.handlers import QueueHandler, QueueListener
from multiprocessing import Queue
from typing import Final, Optional

# ── TRACE support ───────────────────────────────────────────────────────────
TRACE: Final[int] = 5
logging.addLevelName(TRACE, "TRACE")


def trace(self, msg, *a, **kw):
    if self.isEnabledFor(TRACE):
        self._log(TRACE, msg, a, **kw)


logging.Logger.trace = trace  # type: ignore[attr-defined]

_FMT: Final[str] = "%(asctime)s [%(levelname)s] %(processName)s %(name)s: %(message)s"


def _level_from_verbose(v: int) -> int:
    return (
        logging.WARNING
        if v <= 0
        else logging.INFO
        if v == 1
        else logging.DEBUG
        if v == 2
        else TRACE
    )  # -vvv or more


# ── shared state ────────────────────────────────────────────────────────────
_listener: Optional[QueueListener] = None


def _ensure_listener(queue: Queue) -> None:
    """(Re)start the listener thread in the main process exactly once."""
    global _listener
    if _listener and _listener._thread.is_alive():  # pyright: ignore[reportPrivateUsage]
        return  # already healthy
    if _listener:
        _listener.stop()
        _listener = None

    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter(_FMT))
    _listener = QueueListener(queue, console, respect_handler_level=True)
    _listener.start()
    atexit.register(_listener.stop)


# ── public API ──────────────────────────────────────────────────────────────
def configure_logging(verbosity: int = 0) -> None:
    """Queue-based root logger; re-configures every call, fork-safe."""
    level = _level_from_verbose(verbosity)
    queue: Queue = Queue(-1)

    # only the main process owns the listener
    if mp.current_process().name == "MainProcess":
        _ensure_listener(queue)

    # always (re)install our QueueHandler & level
    logging.basicConfig(
        level=level,
        handlers=[QueueHandler(queue)],
        force=True,  # clobber any stray basicConfig
    )

    logging.getLogger("urllib3").setLevel(max(level, logging.WARNING))
