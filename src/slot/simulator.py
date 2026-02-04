import random
from dataclasses import dataclass
from typing import Tuple, Optional

from .slot_machine import SlotMachine


@dataclass
class SimulationResult:
    spins: int
    total_bet: float
    total_return: float
    win_rate: float
    rtp: float


class Simulator:
    def __init__(self, machine: SlotMachine, seed: Optional[int] = None) -> None:
        self.machine = machine
        self.random = random.Random(seed)

    def run(self, spins: int = 100_000) -> SimulationResult:
        reels = self.machine.reels
        wins = 0
        total_return = 0.0
        for _ in range(spins):
            stops: Tuple[int, int, int] = tuple(
                self.random.randrange(reel.length) for reel in reels
            )  # type: ignore
            grid = self.machine.spin_grid(stops)
            payout = self.machine.payout(grid)
            total_return += payout
            if payout > 0:
                wins += 1
        total_bet = spins * self.machine.bet_amount
        win_rate = wins / spins
        rtp = total_return / total_bet if total_bet > 0 else 0.0
        return SimulationResult(
            spins=spins,
            total_bet=total_bet,
            total_return=total_return,
            win_rate=win_rate,
            rtp=rtp,
        )
