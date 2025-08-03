"""
Switch system and application settings based on the detected network environment.
"""
from __future__ import annotations

__prog__ = 'swenv'

__version__: str
__version_tuple__: tuple[int|str, ...]
try:
    from swenv._version import __version__, __version_tuple__  # type: ignore
except ModuleNotFoundError:
    __version__ = '?'
    __version_tuple__ = (0, 0, 0, '?')
