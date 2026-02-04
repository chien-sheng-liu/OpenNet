"""Exact evaluation of RTP and win rate.

Computes expected return to player (RTP) and win rate by enumerating all
combinations of reel stops. This removes Monte Carlo variance and allows
strict checks against DS-HomeWork.md constraints.
"""

from dataclasses import dataclass
from typing import Tuple

from .slot_machine import SlotMachine


@dataclass
class ExactMetrics:
    spins: int
    total_bet: float
    total_return: float
    win_rate: float
    rtp: float


class ExactEvaluator:
    """Enumerate all stop combinations to compute exact metrics."""

    def __init__(self, machine: SlotMachine) -> None:
        self.machine = machine

    def run(self) -> ExactMetrics:
        reels = self.machine.reels
        lengths = [r.length for r in reels]
        total_combos = lengths[0] * lengths[1] * lengths[2]
        wins = 0
        total_return = 0.0

        for i in range(lengths[0]):
            for j in range(lengths[1]):
                for k in range(lengths[2]):
                    stops: Tuple[int, int, int] = (i, j, k)
                    # Build the grid produced by these stop indices
                    grid = self.machine.spin_grid(stops)
                    payout = self.machine.payout(grid)
                    total_return += payout
                    if payout > 0:
                        wins += 1

        total_bet = total_combos * self.machine.bet_amount
        win_rate = wins / total_combos if total_combos > 0 else 0.0
        # RTP is expected return per unit bet
        rtp = total_return / total_bet if total_bet > 0 else 0.0
        return ExactMetrics(
            spins=total_combos,
            total_bet=total_bet,
            total_return=total_return,
            win_rate=win_rate,
            rtp=rtp,
        )
