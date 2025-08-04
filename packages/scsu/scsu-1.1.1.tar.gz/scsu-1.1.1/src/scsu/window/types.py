"""
Window types.
"""


from dataclasses import dataclass

from .bases import *

WINDOW_SIZE = 128


@dataclass
class Window:
    """Base class for encoding and decoding a compressible character."""
    base: int

    @property
    def aligned(self) -> bool:
        """Determine if the window is aligned to a Unicode block boundary."""
        return (self.base & 0x7F) == 0

    def __contains__(self, item: str) -> bool:
        """Determine if a given character is in the window."""
        assert len(item) == 1

        if self.base == B_CJK_SYMBOLS_AND_PUNCTUATION:
            return self.base <= ord(item) < (self.base + 0x40)
        elif self.base in (B_IPA_EXTENSIONS, B_ARMENIAN, B_HIRAGANA, B_KATAKANA):
            return self.base <= ord(item) < (self.base + 0x60)
        elif self.base == B_FULL_WIDTH_ASCII:
            return self.base <= ord(item) < (self.base + 0x61)
        elif self.base == B_COMBINING_DIACRITICAL_MARKS:
            return self.base <= ord(item) < (self.base + 0x70)
        elif self.base == B_HALF_WIDTH_KATAKANA:
            return (self.base + 1) <= ord(item) < (self.base + WINDOW_SIZE)
        else:
            return self.base <= ord(item) < (self.base + WINDOW_SIZE)


@dataclass
class StaticWindow(Window):
    """Class for encoding and decoding a compressible character in a static window."""
    def encode(self, c: str) -> int:
        """Encode a character in a static window as a byte."""
        assert c in self
        return (ord(c) - self.base) & 0x7F

    def decode(self, b: int) -> str:
        """Decode a byte as a character in a static window."""
        assert b & 0x80 == 0
        return chr(self.base + (b & 0x7F))


@dataclass
class DynamicWindow(Window):
    """Class for encoding and decoding a compressible character in a dynamic window."""
    def encode(self, c: str) -> int:
        """Encode a character in a dynamic window as a byte."""
        assert c in self
        return ((ord(c) - self.base) & 0x7F) | 0x80

    def decode(self, b: int) -> str:
        """Decode a byte as a character in a dynamic window."""
        assert b & 0x80 == 0x80
        return chr(self.base + (b & 0x7F))

    def __hash__(self):
        return self.base


def default_static_windows() -> list[StaticWindow]:
    """Get a list of default static windows."""
    return [
        StaticWindow(B_ASCII),
        StaticWindow(B_LATIN_1_SUPPLEMENT),
        StaticWindow(B_LATIN_EXTENDED_A),
        StaticWindow(B_COMBINING_DIACRITICAL_MARKS),
        StaticWindow(B_GENERAL_PUNCTUATION),
        StaticWindow(B_CURRENCY_SYMBOLS),
        StaticWindow(B_LETTER_LIKE_SYMBOLS_AND_NUMBER_FORMS),
        StaticWindow(B_CJK_SYMBOLS_AND_PUNCTUATION)
    ]


def default_dynamic_windows() -> list[DynamicWindow]:
    """Get a list of default dynamic windows."""
    return [
        DynamicWindow(B_LATIN_1_SUPPLEMENT),
        DynamicWindow(B_LATIN_1_HALF_EXTENDED),
        DynamicWindow(B_CYRILLIC),
        DynamicWindow(B_ARABIC),
        DynamicWindow(B_DEVANAGARI),
        DynamicWindow(B_HIRAGANA),
        DynamicWindow(B_KATAKANA),
        DynamicWindow(B_FULL_WIDTH_ASCII)
    ]
