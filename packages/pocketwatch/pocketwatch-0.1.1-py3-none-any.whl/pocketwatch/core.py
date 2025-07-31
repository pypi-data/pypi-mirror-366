from __future__ import annotations

import atexit
import cProfile
import logging
import pstats
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Protocol, Type, Literal
from types import TracebackType
from notifypy import Notify


class NotifierProtocol(Protocol):
    def send(self, title: str, message: str, sound_path: str | None = None) -> None:
        ...


def _default_notifier() -> NotifierProtocol:

    class _Notifier:
        def send(self, title: str, message: str, sound_path: str | None = None) -> None:
            n = Notify()
            n.title = title
            n.message = message
            if sound_path:
                n.audio = str(sound_path)
            n.send()

    return _Notifier()


def _find_data_file(name: str) -> Path:
    return Path(__file__).with_name("data").joinpath(name)


@dataclass
class _Mark:
    note: str
    elapsed: float


class Pocketwatch:
    def __init__(self,
                 msg: str | None = None,
                 *,
                 notify: bool = True,
                 notify_after: float = 0.0,
                 precision: int = 3,
                 sound: bool = False,
                 sound_after: float = 60.0,
                 incremental: bool = False,
                 increment_cutoff: float = 0.5,
                 profile: bool = False,
                 profile_output_path: str | Path | None = 'profile_output.prof',
                 print_output: str = True,
                 logger: logging.Logger | None = None,
                 log_level: int = logging.INFO,
                 **kwargs) -> None:
        self.msg = msg or "block"
        self.precision = precision
        self.notify = notify
        self.notify_after = notify_after
        self.sound = sound
        self.sound_after = sound_after
        self.sound_file = Path(kwargs.get("sound_file", _find_data_file("ding.wav")))
        self.notifier = kwargs.get("notifier", _default_notifier())
        self.incremental = incremental
        self.increment_cutoff = increment_cutoff
        self.profile = profile
        self.profile_output_path = (
            Path(profile_output_path) if profile_output_path else None
        )
        self.print_output=print_output
        self.logger = logger
        self.log_level = log_level
        self._disable_atexit = kwargs.get("_disable_atexit", False)

        self._start = time.perf_counter()
        self._ended = False
        self._marks: list[_Mark] = []
        self._prof: Optional[cProfile.Profile] = None
        self.unexpected_exit = False

        if self.profile:
            self._prof = cProfile.Profile()
            self._prof.enable()

        if not self._disable_atexit:
            atexit.register(self._atexit_stop)

    # ------------------------------------------------------------------
    def _now(self) -> float:
        return time.perf_counter()

    # ------------------------------------------------------------------
    @property
    def elapsed(self) -> float:
        return self._now() - self._start

    # ------------------------------------------------------------------
    def mark(self, note: str) -> None:
        el = self.elapsed
        self._marks.append(_Mark(note=note, elapsed=el))
        if self.incremental and el < self.increment_cutoff:
            return
        self._log(f"{note} at {el:.{self.precision}f}s")

    # ------------------------------------------------------------------
    def end(self, msg=None, *, return_stats: bool = False) -> Optional[pstats.Stats]:

        self.msg=msg if msg is not None else self.msg
        if self._ended:
            return self._stats() if return_stats else None
        self._ended = True
        elapsed = self.elapsed
        if self._prof:
            self._prof.disable()
        if self.profile and self.profile_output_path:
            self._prof.dump_stats(self.profile_output_path)  # type: ignore

        if self.unexpected_exit:
            msg = (
                f"[Pocketwatch] {self.msg} interrupted by interpreter shutdown"
                f" after {elapsed:.{self.precision}f}s"
            )
        else:
            msg = f"[Pocketwatch] {self.msg} completed in {elapsed:.{self.precision}f}s"
        self._log(msg)

        if self.profile and return_stats:
            return pstats.Stats(self._prof) if self._prof else None
        if self.notifier:
            notify_ok = (
                self.notify
                and elapsed >= self.notify_after
                and not (self.incremental and elapsed < self.increment_cutoff)
            )
            sound_ok = (
                self.sound
                and elapsed >= self.sound_after
                and not (self.incremental and elapsed < self.increment_cutoff)
            )
            if notify_ok or sound_ok:
                self.notifier.send(
                    "Pocketwatch",
                    msg if notify_ok else "",
                    str(self.sound_file) if sound_ok else None,
                )
        return self._stats() if return_stats else None

    # ------------------------------------------------------------------
    def _stats(self) -> Optional[pstats.Stats]:
        if self.profile and self._prof:
            return pstats.Stats(self._prof)
        return None

    # ------------------------------------------------------------------

    def log(self,note):
        """Alias for mark"""
        self.mark(note)

    def _log(self, message: str) -> None:
        """Emit a message to stdout and/or logger, depending on config."""
        if self.print_output:
            print(message)
        if self.logger:
            self.logger.log(self.log_level, message)

    # ------------------------------------------------------------------
    def _atexit_stop(self) -> None:
        if not self._ended:
            self.unexpected_exit = True
            self.end()

    # ------------------------------------------------------------------
    def __enter__(self) -> "Pocketwatch":
        return self

    # ------------------------------------------------------------------
    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> Literal[False]:
        self.end()
        return False