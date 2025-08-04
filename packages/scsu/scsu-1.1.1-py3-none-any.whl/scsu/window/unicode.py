"""
Unicode-related functions.
"""


BYTE_ORDER_MARK = chr(0xFEFF)
ENCODING_UTF16_BE = "UTF-16BE"


def is_compressible(c: str) -> bool:
    """Determine if a character can be compressed into a single byte."""
    assert len(c) == 1
    b = ord(c)

    return 0 <= b < 0x3400 or 0xE000 <= b <= 0x10_FFFF


def is_surrogate_byte_pair(b: bytes) -> bool:
    """Determine if a byte sequence is an encoded surrogate."""
    return len(b) == 2 and 0xD8 <= b[0] <= 0xDF


def is_leading_surrogate_byte_pair(b: bytes) -> bool:
    """Determine if a byte sequence is an encoded leading surrogate."""
    return is_surrogate_byte_pair(b) and 0xD8 <= b[0] <= 0xDB


def is_trailing_surrogate_byte_pair(b: bytes) -> bool:
    """Determine if a byte sequence is an encoded trailing surrogate."""
    return is_surrogate_byte_pair(b) and 0xDC <= b[0] <= 0xDF


def in_bmp(c: str) -> bool:
    """Determine if a character is in the Basic Multilingual Plane."""
    assert len(c) == 1

    return 0 <= ord(c) <= 0xFFFF


def in_smp(c: str) -> bool:
    """Determine if a character is in any Supplementary Multilingual Plane."""
    assert len(c) == 1

    return 0x1_0000 <= ord(c) <= 0x10_FFFF


def encode_str(s: str) -> bytes:
    """Encode a string as UTF-16BE."""
    return s.encode(ENCODING_UTF16_BE)


def decode_bytes(b: bytes) -> str:
    """Decode a string as UTF-16BE."""
    return b.decode(ENCODING_UTF16_BE)
