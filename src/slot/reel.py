from dataclasses import dataclass
from typing import List


@dataclass
class Reel:
    symbols: List[int]

    def __post_init__(self) -> None:
        if not self.symbols:
            raise ValueError("Reel must contain at least one symbol")

    @property
    def length(self) -> int:
        return len(self.symbols)

    def window(self, start: int) -> List[int]:
        """Return three consecutive symbols (rows 0..2) with wrap-around."""
        n = self.length
        return [self.symbols[(start + offset) % n] for offset in range(3)]

