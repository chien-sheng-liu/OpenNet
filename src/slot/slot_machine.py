"""Core slot machine logic.

Builds the 3×3 grid from reels, evaluates payouts against winning patterns,
and provides detailed match information for visualization.
"""

from dataclasses import dataclass
from typing import List, Tuple, Dict, Any

from .patterns import Pattern, winning_patterns
from .reel import Reel
from .symbols import SymbolSet


Grid = List[List[int]]  # 3×3 of symbol keys


@dataclass
class SlotMachine:
    """A 3-reel, 3×3 slot machine with fixed patterns and symbol set."""
    reels: Tuple[Reel, Reel, Reel]
    bet_amount: float = 1.0
    patterns: List[Pattern] = None

    def __post_init__(self) -> None:
        """Initialize default patterns and symbol set, validate inputs."""
        if self.patterns is None:
            self.patterns = winning_patterns()
        if len(self.reels) != 3:
            raise ValueError("SlotMachine requires exactly 3 reels")
        self.symbols = SymbolSet()

    def spin_grid(self, stops: Tuple[int, int, int]) -> Grid:
        """Construct a 3×3 grid from the reels given stop indices per reel."""
        # Each reel returns a column of 3 symbols (top→bottom) for a given stop.
        cols = [reel.window(stop) for reel, stop in zip(self.reels, stops)]
        # Transpose columns into a row-major 3×3 grid for evaluation and UI.
        return [[cols[c][r] for c in range(3)] for r in range(3)]

    def payout(self, grid: Grid) -> float:
        """Compute total payout for a grid across all winning patterns."""
        total = 0.0
        for p in self.patterns:
            coords = p.coords
            first_r, first_c = coords[0]
            symbol = grid[first_r][first_c]
            # A pattern wins only if all cells in its shape match the same symbol.
            if all(grid[r][c] == symbol for r, c in coords):
                total += self.bet_amount * self.symbols.get(symbol).multiplier * p.weight
        return total

    def evaluate_patterns(self, grid: Grid) -> Dict[str, Any]:
        """Return payout and per-pattern match details for visualization.

        The result contains the total payout and a list of matches with
        pattern name, coordinates, winning symbol, weight, multiplier,
        and per-pattern payout contribution.
        """
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
