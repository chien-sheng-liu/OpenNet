"""Symbol definitions for the slot game.

Exposes a small, fixed set of symbols and their payout multipliers,
as mandated by DS-HomeWork.md. The mapping is intentionally immutable
at runtime to avoid accidental drift from the rules.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class Symbol:
    """A single symbol with its integer key and payout multiplier."""
    key: int
    multiplier: float


class SymbolSet:
    """Container of the five allowed symbols and multipliers.

    Mapping per DS-HomeWork.md:
    {0: 0.25, 1: 0.55, 2: 1.0, 3: 3.0, 4: 5.0}
    """

    def __init__(self) -> None:
        mapping: Dict[int, float] = {0: 0.25, 1: 0.55, 2: 1.0, 3: 3.0, 4: 5.0}
        self._symbols: Dict[int, Symbol] = {k: Symbol(k, v) for k, v in mapping.items()}

    def get(self, key: int) -> Symbol:
        """Return the `Symbol` for a given integer key."""
        return self._symbols[key]

    def all(self) -> Dict[int, Symbol]:
        """Return a shallow copy of the symbol mapping (key -> Symbol)."""
        return dict(self._symbols)
