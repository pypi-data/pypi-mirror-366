"""
Supplementary window candidate functions.
"""


from dataclasses import dataclass

from .types import DynamicWindow
from .unicode import in_smp


@dataclass
class SupplementaryWindowDefinition:
    """Class for describing a parameter and dynamic window for a supplementary character."""
    index: int
    window: DynamicWindow

    def __bytes__(self):
        window_param, base_param = self.index & 0x07, (self.window.base - 0x1_0000) >> 7
        param = (window_param << 13) | (base_param & 0x1FFF)
        return param.to_bytes(2, "big")


def define_supplementary_window(c: str, index: int) -> SupplementaryWindowDefinition:
    """Create a supplementary window definition."""
    assert in_smp(c)
    codepoint = ord(c)

    assert 0 <= index < 8
    return SupplementaryWindowDefinition(index, DynamicWindow(codepoint & 0xFF_FF80))


def decode_supplementary_window_parameter(b: bytes) -> SupplementaryWindowDefinition:
    """Decode a byte string as a supplementary window definition."""
    assert len(b) == 2
    index, base = (b[0] >> 5) & 0x07, 0x1_0000 + (((b[0] & 0x1F) << 8 | b[1]) << 7)

    return SupplementaryWindowDefinition(index, DynamicWindow(base))
