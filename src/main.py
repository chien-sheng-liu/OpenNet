"""CLI entry point for reel search and validation.

Runs the heuristic search to produce a reels configuration near the target
RTP and win-rate, validates it with more spins, and writes a JSON artifact.
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Tuple

from slot.reel import Reel
from slot.search import ReelSearch, SearchConfig
from slot.slot_machine import SlotMachine
from slot.simulator import Simulator
from slot.exact import ExactEvaluator


def serialize_reels(reels: Tuple[Reel, Reel, Reel]) -> Dict[str, Any]:
    """Convert a tuple of `Reel` objects to the public JSON structure."""
    return {f"reel_{i+1}": r.symbols for i, r in enumerate(reels)}


def main() -> None:
    """Parse CLI args, run search, validate, and write output JSON."""
    parser = argparse.ArgumentParser(description="Search for a valid slot game reel configuration.")
    parser.add_argument("--spins", type=int, default=100_000, help="Spins to validate final config.")
    parser.add_argument("--steps", type=int, default=800, help="Search steps.")
    parser.add_argument("--eval-spins", type=int, default=50_000, help="Spins per evaluation during search.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    parser.add_argument("--out", type=Path, default=Path("reels_config.json"), help="Output JSON file for reels.")
    args = parser.parse_args()

    cfg = SearchConfig(max_steps=args.steps, spins_per_eval=args.eval_spins, seed=args.seed)
    search = ReelSearch(cfg)
    candidate = search.search()

    # Validate exactly (no Monte Carlo variance)
    machine = SlotMachine(candidate.reels, bet_amount=1.0)
    exact = ExactEvaluator(machine)
    validation = exact.run()

    # Strict validation: keep searching in batches until constraints are met
    target_rtp = 0.95
    min_win = 0.55
    tol = 1e-6
    attempts = 0
    max_attempts = 8
    steps = args.steps
    while (abs(validation.rtp - target_rtp) > tol or validation.win_rate < min_win) and attempts < max_attempts:
        attempts += 1
        # increase steps moderately for subsequent attempts
        steps = int(steps * 1.5)
        cfg = SearchConfig(max_steps=steps, spins_per_eval=args.eval_spins, seed=args.seed + attempts)
        search = ReelSearch(cfg)
        candidate = search.search()
        machine = SlotMachine(candidate.reels, bet_amount=1.0)
        exact = ExactEvaluator(machine)
        validation = exact.run()

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

    # Persist the result for reuse by API/front-end
    args.out.write_text(json.dumps(data, indent=2))

    print("Best candidate saved to:", args.out)
    print("RTP:", validation.rtp)
    print("Win rate:", validation.win_rate)
    if abs(validation.rtp - target_rtp) > tol or validation.win_rate < min_win:
        # Non‑zero exit to indicate requirements were not met
        print("Warning: constraints not met within tolerance; consider increasing steps/spins.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
