"""
Window candidate functions.
"""


from dataclasses import dataclass
from typing import Generator

from .bases import B_LATIN_1_SUPPLEMENT
from .bytes import valid_window_parameters, decode_window_parameter
from .types import StaticWindow, DynamicWindow


@dataclass
class WindowFit:
    """Base class for describing which window a character fits into."""
    index: int


@dataclass
class StaticWindowFit(WindowFit):
    """Class for describing which static window a character fits into."""
    window: StaticWindow


@dataclass
class DynamicWindowFit(WindowFit):
    """Class for describing which dynamic window a character fits into."""
    window: DynamicWindow


@dataclass
class DynamicWindowCandidate:
    """Class for describing a parameter and dynamic window for a character."""
    parameter: int
    window: DynamicWindow

    def __hash__(self):
        return self.window.base << 8 | (self.parameter & 0xFF)


def dynamic_window_candidates(c: str) -> Generator[DynamicWindowCandidate, None, None]:
    """Generate all dynamic window candidates that a character fits into."""
    for parameter in valid_window_parameters():
        window = decode_window_parameter(parameter)

        if c in window:
            yield DynamicWindowCandidate(parameter, window)


def preferred_window_candidate(c: str, lookahead: str = "") -> DynamicWindowCandidate | None:
    """Find an optimal window candidate for a given character, or None if no dynamic window candidate is found."""
    candidates = set(dynamic_window_candidates(c))

    for c in lookahead:
        candidates &= set(dynamic_window_candidates(c))

    if len(candidates) == 0:
        return None

    if any(candidate.window.base == B_LATIN_1_SUPPLEMENT for candidate in candidates):
        return next(filter(lambda candidate: candidate.window.base == B_LATIN_1_SUPPLEMENT, candidates))

    if any(not candidate.window.aligned for candidate in candidates):
        return next(filter(lambda candidate: not candidate.window.aligned, candidates))

    return candidates.pop()
