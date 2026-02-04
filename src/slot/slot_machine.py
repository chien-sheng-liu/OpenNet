from dataclasses import dataclass
from typing import List, Tuple, Dict, Any

from .patterns import Pattern, winning_patterns
from .reel import Reel
from .symbols import SymbolSet


Grid = List[List[int]]  # 3x3 of symbol keys


@dataclass
class SlotMachine:
    reels: Tuple[Reel, Reel, Reel]
    bet_amount: float = 1.0
    patterns: List[Pattern] = None

    def __post_init__(self) -> None:
        if self.patterns is None:
            self.patterns = winning_patterns()
        if len(self.reels) != 3:
            raise ValueError("SlotMachine requires exactly 3 reels")
        self.symbols = SymbolSet()

    def spin_grid(self, stops: Tuple[int, int, int]) -> Grid:
        cols = [reel.window(stop) for reel, stop in zip(self.reels, stops)]
        # Convert to 3x3 grid (rows of columns)
        return [[cols[c][r] for c in range(3)] for r in range(3)]

    def payout(self, grid: Grid) -> float:
        total = 0.0
        for p in self.patterns:
            coords = p.coords
            first_r, first_c = coords[0]
            symbol = grid[first_r][first_c]
            if all(grid[r][c] == symbol for r, c in coords):
                total += self.bet_amount * self.symbols.get(symbol).multiplier * p.weight
        return total

    def evaluate_patterns(self, grid: Grid) -> Dict[str, Any]:
        """Return payout and detailed match info for visualization."""
        matches: List[Dict[str, Any]] = []
        total = 0.0
        for p in self.patterns:
            coords = p.coords
            first_r, first_c = coords[0]
            symbol = grid[first_r][first_c]
            if all(grid[r][c] == symbol for r, c in coords):
                mult = self.symbols.get(symbol).multiplier
                payout = self.bet_amount * mult * p.weight
                total += payout
                matches.append({
                    "pattern": p.name,
                    "coords": coords,
                    "symbol": symbol,
                    "weight": p.weight,
                    "multiplier": mult,
                    "payout": payout,
                })
        return {"payout": total, "matches": matches}
