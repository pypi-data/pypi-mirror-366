"""
Codec state objects.
"""


from collections import deque
from dataclasses import dataclass, field
from enum import Enum

from ..window.bases import B_LATIN_1_SUPPLEMENT
from ..window.candidates import StaticWindowFit, DynamicWindowFit
from ..window.types import default_static_windows, default_dynamic_windows, StaticWindow, DynamicWindow


class Mode(Enum):
    """Codec mode flag."""
    SINGLE_BYTE = 1
    UNICODE = 2


@dataclass
class State:
    """Codec state."""
    signed: bool = True
    mode: Mode = Mode.SINGLE_BYTE
    active_window_index: int = 0
    dynamic_windows: list[DynamicWindow] = field(default_factory=default_dynamic_windows)
    static_windows: list[StaticWindow] = field(default_factory=default_static_windows)

    def ascii(self) -> StaticWindow:
        """Get the static window for ASCII characters."""
        return self.static_windows[0]

    def active_window(self) -> DynamicWindow:
        """Get the active dynamic window."""
        return self.dynamic_windows[self.active_window_index]


@dataclass
class EncoderState(State):
    """Encoder state."""
    dynamic_window_ages: list[int] = field(default_factory=lambda: [0] * 8)
    input_buffer: deque[str] = field(default_factory=lambda: deque(maxlen=3))

    def reset_window_age(self, index: int):
        """Reset the window age of a given dynamic window index."""
        assert 0 <= index < len(self.dynamic_window_ages)
        self.dynamic_window_ages[index] = 0

    def reset_active_window_age(self):
        """Reset the window age of the active dynamic window."""
        self.reset_window_age(self.active_window_index)

    def increment_window_ages(self):
        """Increment each dynamic window age by one."""
        self.dynamic_window_ages = list(map(lambda a: a + 1, self.dynamic_window_ages))

    def oldest_window_index(self):
        """Find the index of the oldest dynamic window."""
        oldest_age = max(self.dynamic_window_ages)
        oldest_windows = set((i, self.dynamic_windows[i], a) for i, a in enumerate(self.dynamic_window_ages)
                             if a == oldest_age)

        if len(oldest_windows) >= 2 and any(w.base == B_LATIN_1_SUPPLEMENT for i, w, a in oldest_windows):
            oldest_windows = set(filter(lambda t: t[1].base != B_LATIN_1_SUPPLEMENT, oldest_windows))

        return oldest_windows.pop()[0]

    def input_buffer_full(self):
        """Determine if the input buffer is full."""
        return len(self.input_buffer) == self.input_buffer.maxlen

    def static_window_fit(self, c: str) -> StaticWindowFit | None:
        """Find a static window that a given character fits into, or None if no static window can be found."""
        for index, window in enumerate(self.static_windows):
            if c in window:
                return StaticWindowFit(index, window)

        return None

    def dynamic_window_fit(self, c: str) -> DynamicWindowFit | None:
        """Find a dynamic window that a given character fits into, or None if no dynamic window can be found."""
        for index, window in enumerate(self.dynamic_windows):
            if c in window:
                return DynamicWindowFit(index, window)

        return None


@dataclass
class DecoderState(State):
    """Decoder state."""
    parameter_bytes_remaining: int = 0
    instruction_buffer: bytearray = field(default_factory=bytearray)
    surrogate_buffer: bytearray = field(default_factory=bytearray)
