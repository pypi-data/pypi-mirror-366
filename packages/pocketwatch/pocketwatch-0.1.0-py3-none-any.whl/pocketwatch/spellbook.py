from __future__ import annotations

from pathlib import Path

from .core import Pocketwatch


def haste(**kwargs) -> Pocketwatch:
    return Pocketwatch(increment_cutoff=0.25, notify_after=0, sound_after=30, **kwargs)


def slow(**kwargs) -> Pocketwatch:
    return Pocketwatch(increment_cutoff=1.0, notify_after=60, sound_after=120, **kwargs)


def stop(**kwargs) -> Pocketwatch:
    return Pocketwatch(**kwargs)


def meteor(**kwargs) -> Pocketwatch:
    sound_file = Path(__file__).with_name("data").joinpath("meteor.wav")
    return Pocketwatch(
        profile=True, sound=True, sound_after=0, sound_file=sound_file, **kwargs
    )


def float(**kwargs) -> Pocketwatch:
    return Pocketwatch(_disable_atexit=True, **kwargs)