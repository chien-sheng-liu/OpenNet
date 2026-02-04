import math
import random
from dataclasses import dataclass
from typing import List, Tuple, Optional

from .reel import Reel
from .slot_machine import SlotMachine
from .simulator import Simulator, SimulationResult


@dataclass
class SearchConfig:
    target_rtp: float = 0.95
    min_win_rate: float = 0.55
    max_steps: int = 200
    spins_per_eval: int = 50_000
    seed: Optional[int] = 1337


@dataclass
class Candidate:
    reels: Tuple[Reel, Reel, Reel]
    result: SimulationResult


class ReelSearch:
    """Heuristic search over reel symbol distributions to meet targets.

    Approach:
    - Start with random reels (lengths 20..50).
    - Iteratively mutate (swap entries, tweak symbol frequencies, rotate reel).
    - Keep best candidates by minimizing a loss function that penalizes
      RTP distance and win-rate shortfall.
    """

    SYMBOL_KEYS = [0, 1, 2, 3, 4]

    def __init__(self, cfg: Optional[SearchConfig] = None) -> None:
        self.cfg = cfg or SearchConfig()
        self.rng = random.Random(self.cfg.seed)

    def _random_reel(self, length: int) -> Reel:
        # Bias towards lower multipliers to keep RTP controllable; adjust via weights
        weights = [5, 5, 4, 2, 1]
        symbols = self.rng.choices(self.SYMBOL_KEYS, weights=weights, k=length)
        return Reel(symbols)

    def _random_candidate(self) -> Tuple[Reel, Reel, Reel]:
        lengths = [self.rng.randint(20, 50) for _ in range(3)]
        return tuple(self._random_reel(l) for l in lengths)  # type: ignore

    def _mutate(self, reels: Tuple[Reel, Reel, Reel]) -> Tuple[Reel, Reel, Reel]:
        rlist = [list(r.symbols) for r in reels]
        choice = self.rng.random()
        if choice < 0.4:
            # swap two positions on a random reel
            i = self.rng.randrange(3)
            if len(rlist[i]) > 1:
                a, b = self.rng.sample(range(len(rlist[i])), 2)
                rlist[i][a], rlist[i][b] = rlist[i][b], rlist[i][a]
        elif choice < 0.8:
            # tweak a random position
            i = self.rng.randrange(3)
            j = self.rng.randrange(len(rlist[i]))
            rlist[i][j] = self.rng.choices(self.SYMBOL_KEYS, weights=[5, 5, 4, 2, 1])[0]
        else:
            # rotate a reel
            i = self.rng.randrange(3)
            k = self.rng.randrange(1, len(rlist[i]))
            rlist[i] = rlist[i][k:] + rlist[i][:k]
        return tuple(Reel(s) for s in rlist)  # type: ignore

    def _loss(self, result: SimulationResult) -> float:
        # Penalize RTP distance and win-rate shortfall; small regularization on excess
        rtp_err = abs(result.rtp - self.cfg.target_rtp)
        win_deficit = max(0.0, self.cfg.min_win_rate - result.win_rate)
        # weight win-rate deficits more heavily
        return rtp_err + 2.0 * win_deficit + 0.1 * max(0.0, result.win_rate - self.cfg.min_win_rate)

    def _evaluate(self, reels: Tuple[Reel, Reel, Reel]) -> SimulationResult:
        machine = SlotMachine(reels=reels, bet_amount=1.0)
        sim = Simulator(machine, seed=self.rng.randrange(1_000_000_000))
        return sim.run(spins=self.cfg.spins_per_eval)

    def search(self) -> Candidate:
        # Initialize with random candidate
        current_reels = self._random_candidate()
        current_result = self._evaluate(current_reels)
        current_loss = self._loss(current_result)
        best = Candidate(reels=current_reels, result=current_result)
        best_loss = current_loss

        temperature = 1.0
        for step in range(self.cfg.max_steps):
            proposal = self._mutate(current_reels)
            res = self._evaluate(proposal)
            loss = self._loss(res)

            accept = loss < current_loss
            if not accept:
                # Simulated annealing style acceptance
                prob = math.exp((current_loss - loss) / max(1e-6, temperature))
                if self.rng.random() < prob:
                    accept = True

            if accept:
                current_reels, current_result, current_loss = proposal, res, loss
                if loss < best_loss:
                    best, best_loss = Candidate(proposal, res), loss

            # Cool down slowly
            temperature *= 0.98

            # Early exit if constraints satisfied closely
            if res.rtp and abs(res.rtp - self.cfg.target_rtp) < 0.01 and res.win_rate >= self.cfg.min_win_rate:
                best = Candidate(proposal, res)
                break

        return best
