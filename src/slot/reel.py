"""Reel abstraction.

Represents a circular reel as a list of integer symbol keys and exposes a
3-row window used to build the slot's columns given a stop index.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class Reel:
    """A circular reel storing symbol keys in order."""
    symbols: List[int]

    def __post_init__(self) -> None:
        """Validate the reel has at least one symbol."""
        if not self.symbols:
            raise ValueError("Reel must contain at least one symbol")

    @property
    def length(self) -> int:
        """Return the number of symbols on the reel."""
        return len(self.symbols)

    def window(self, start: int) -> List[int]:
        """Return three consecutive symbols with wrap-around.

        The returned list corresponds to rows 0..2 in a single column.
        """
        n = self.length
        return [self.symbols[(start + offset) % n] for offset in range(3)]
