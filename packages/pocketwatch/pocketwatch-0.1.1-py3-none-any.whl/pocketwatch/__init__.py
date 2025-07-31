from .core import Pocketwatch

__all__ = ["Pocketwatch"]


def __getattr__(name: str):
    if name == "spellbook":
        from . import spellbook as sb
        return sb
    raise AttributeError(name)