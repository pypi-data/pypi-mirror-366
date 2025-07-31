from __future__ import annotations

import os
import sys
import types
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import importlib

try:
    importlib.import_module("notifypy")
except Exception:
    dummy = types.ModuleType("notifypy")
    class DummyNotify:
        def __init__(self) -> None:
            self.title = ""
            self.message = ""
            self.audio: str | None = None

        def send(self) -> None:
            pass
    setattr(dummy, "Notify", DummyNotify)
    sys.modules["notifypy"] = dummy

import src.pocketwatch.core as core
from src.pocketwatch.decorators import stopwatch


class FakeNotifier:
    def __init__(self) -> None:
        self.sent: list[tuple[str, str, str | None]] = []

    def send(self, title: str, message: str, sound_path: str | None = None) -> None:
        self.sent.append((title, message, sound_path))


class Logger:
    def __init__(self, storage: list[str]) -> None:
        self.name = "Pocketwatch"
        self._store = storage

    def log(self, level: int, message: str) -> None:
        self._store.append(message)

    def addHandler(self, handler) -> None:  # pragma: no cover
        pass

    def removeHandler(self, handler) -> None:  # pragma: no cover
        pass


def _set_time(monkeypatch: pytest.MonkeyPatch, values: list[float]) -> None:
    seq = iter(values)
    monkeypatch.setattr(core.time, "perf_counter", lambda: next(seq))


def test_stopwatch_default(monkeypatch):
    _set_time(monkeypatch, [0.0, 1.0])
    monkeypatch.setattr(core.atexit, "register", lambda *a, **k: None)

    n = FakeNotifier()
    monkeypatch.setattr(core, "_default_notifier", lambda: n)

    @stopwatch
    def demo() -> str:
        return "ok"

    assert demo() == "ok"
    assert n.sent


def test_stopwatch_with_kwargs(monkeypatch, capsys):
    _set_time(monkeypatch, [0.0, 2.0])
    monkeypatch.setattr(core.atexit, "register", lambda *a, **k: None)
    n = FakeNotifier()
    monkeypatch.setattr(core, "_default_notifier", lambda: n)
    logger_msgs: list[str] = []
    orig_get = core.logging.getLogger

    def get_logger(name: str | None = None) -> Logger:
        if name == "Pocketwatch":
            return Logger(logger_msgs)
        return orig_get(name)

    monkeypatch.setattr(core.logging, "getLogger", get_logger)

    @stopwatch(msg="custom", notify=False, log_mode="print")
    def task() -> None:
        pass

    task()
    out = capsys.readouterr().out
    assert "custom completed in 2.000s" in out
    assert not n.sent
