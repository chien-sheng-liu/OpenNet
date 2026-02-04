from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class Symbol:
    key: int
    multiplier: float


class SymbolSet:
    """Defines the 5 symbols and their multipliers.

    Keys and multipliers per DS-HomeWork.md:
    {0: 0.25, 1: 0.55, 2: 1, 3: 3, 4: 5}
    """

    def __init__(self) -> None:
        mapping: Dict[int, float] = {0: 0.25, 1: 0.55, 2: 1.0, 3: 3.0, 4: 5.0}
        self._symbols: Dict[int, Symbol] = {k: Symbol(k, v) for k, v in mapping.items()}

    def get(self, key: int) -> Symbol:
        return self._symbols[key]

    def all(self) -> Dict[int, Symbol]:
        return dict(self._symbols)

