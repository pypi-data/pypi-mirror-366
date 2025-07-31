from __future__ import annotations

import os
import sys
import pstats
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
from src.pocketwatch import Pocketwatch


class FakeNotifier:
    def __init__(self) -> None:
        self.sent: list[tuple[str, str, str | None]] = []

    def send(self, title: str, message: str, sound_path: str | None = None) -> None:
        self.sent.append((title, message, sound_path))


def _set_time(monkeypatch: pytest.MonkeyPatch, values: list[float]) -> None:
    seq = iter(values)
    monkeypatch.setattr(core.time, "perf_counter", lambda: next(seq))


def test_end_logs_and_notify(monkeypatch, capsys):
    _set_time(monkeypatch, [0.0, 2.0])
    n = FakeNotifier()
    pw = Pocketwatch(
        "demo",
        notifier=n,
        notify=True,
        notify_after=0,
        sound=False,
        log_mode="print",
        _disable_atexit=True,
    )
    pw.end()
    out = capsys.readouterr().out
    assert "completed in 2.000s" in out
    assert n.sent


def test_incremental_suppresses(monkeypatch, capsys):
    _set_time(monkeypatch, [0.0, 0.1, 1.0])
    pw = Pocketwatch(
        "demo",
        notify=False,
        incremental=True,
        increment_cutoff=0.5,
        log_mode="print",
        _disable_atexit=True,
    )
    pw.mark("hi")
    pw.end()
    out = capsys.readouterr().out
    assert "hi at" not in out
    assert "completed in 1.000s" in out


def test_profile_returns_stats(monkeypatch):
    _set_time(monkeypatch, [0.0, 1.0])
    with Pocketwatch(
        profile=True, notify=False, sound=False, _disable_atexit=True,profile_output_path=None
    ) as pw:
        pass
    stats = pw.end(return_stats=True)
    assert isinstance(stats, pstats.Stats)


def test_exception_reraises(monkeypatch):
    _set_time(monkeypatch, [0.0, 1.0])
    pw = Pocketwatch(notify=False, _disable_atexit=True)
    with pytest.raises(ValueError):
        with pw:
            raise ValueError("boom")
    assert pw._ended


def test_sound(monkeypatch):
    _set_time(monkeypatch, [0.0, 2.0])
    n = FakeNotifier()
    pw = Pocketwatch(
        sound=True,
        sound_after=1.0,
        notify=False,
        notifier=n,
        _disable_atexit=True,
    )
    pw.end()
    assert n.sent
    assert n.sent[0][2] is not None


def test_atexit_stop(monkeypatch):
    _set_time(monkeypatch, [0.0, 1.0])
    pw = Pocketwatch(notify=False, sound=False, _disable_atexit=True)
    pw._atexit_stop()
    assert pw.unexpected_exit
    assert pw._ended