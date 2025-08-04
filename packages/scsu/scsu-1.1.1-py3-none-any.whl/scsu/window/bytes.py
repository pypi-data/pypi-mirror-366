"""
Functions for validating and decoding single-byte window parameters.
"""


from typing import Generator

from .bases import *
from .types import DynamicWindow


def valid_window_parameters() -> Generator[int, None, None]:
    """Generate valid window parameter bytes."""
    yield from range(0x01, 0x67+1)
    yield from range(0x68, 0xA7+1)
    yield from range(0xF9, 0xFF+1)


def decode_window_parameter(b: int) -> DynamicWindow:
    """Decode a dynamic window parameter byte."""
    if 0x01 <= b <= 0x67:
        return DynamicWindow(b * 0x80)
    elif 0x68 <= b <= 0xA7:
        return DynamicWindow(b * 0x80 + 0xAC00)
    elif b == 0xF9:
        return DynamicWindow(B_LATIN_1_HALF_EXTENDED)
    elif b == 0xFA:
        return DynamicWindow(B_IPA_EXTENSIONS)
    elif b == 0xFB:
        return DynamicWindow(B_GREEK)
    elif b == 0xFC:
        return DynamicWindow(B_ARMENIAN)
    elif b == 0xFD:
        return DynamicWindow(B_HIRAGANA)
    elif b == 0xFE:
        return DynamicWindow(B_KATAKANA)
    elif b == 0xFF:
        return DynamicWindow(B_HALF_WIDTH_KATAKANA)

    raise ValueError(f"invalid window parameter 0x{b:02X}")
