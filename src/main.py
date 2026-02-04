import argparse
import json
from pathlib import Path
from typing import Any, Dict

from slot.reel import Reel
from slot.search import ReelSearch, SearchConfig
from slot.slot_machine import SlotMachine
from slot.simulator import Simulator


def serialize_reels(reels: tuple[Reel, Reel, Reel]) -> Dict[str, Any]:
    return {f"reel_{i+1}": r.symbols for i, r in enumerate(reels)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Search for a valid slot game reel configuration.")
    parser.add_argument("--spins", type=int, default=100_000, help="Spins to validate final config.")
    parser.add_argument("--steps", type=int, default=200, help="Search steps.")
    parser.add_argument("--eval-spins", type=int, default=50_000, help="Spins per evaluation during search.")
    parser.add_argument("--seed", type=int, default=1337, help="Random seed.")
    parser.add_argument("--out", type=Path, default=Path("reels_config.json"), help="Output JSON file for reels.")
    args = parser.parse_args()

    cfg = SearchConfig(max_steps=args.steps, spins_per_eval=args.eval_spins, seed=args.seed)
    search = ReelSearch(cfg)
    candidate = search.search()

    # Validate with more spins
    machine = SlotMachine(candidate.reels, bet_amount=1.0)
    sim = Simulator(machine, seed=args.seed)
    validation = sim.run(spins=args.spins)

    data = {
        "reels": serialize_reels(candidate.reels),
        "validation": {
            "spins": validation.spins,
            "rtp": round(validation.rtp, 4),
            "win_rate": round(validation.win_rate, 4),
            "total_bet": validation.total_bet,
            "total_return": round(validation.total_return, 2),
        },
        "requirements": {"rtp": 0.95, "min_win_rate": 0.55},
    }

    args.out.write_text(json.dumps(data, indent=2))

    print("Best candidate saved to:", args.out)
    print("RTP:", validation.rtp)
    print("Win rate:", validation.win_rate)


if __name__ == "__main__":
    main()

