# Agent Working Instructions

This repo contains a 3×3 slot game used for the OpenNet Data Science homework. Treat this file as the single source of truth for constraints and interfaces when extending or maintaining the project.

## Core Requirements

- Source of truth: follow `DS-HomeWork.md` exactly. Do not change rules.
- Mechanics: 3×3 grid, 3 circular reels, any reel length.
- Symbols and multipliers: `{0:0.25, 1:0.55, 2:1, 3:3, 4:5}`.
- Winning patterns: four 2×2 corners (weight=1) and full 3×3 (weight=5).
- Payouts: corners pay `bet × multiplier`; full 3×3 pays `bet × multiplier × 5`.
- Targets: RTP = 0.95; win rate ≥ 0.55.

## Design Constraints

- Python 3.9 compatible (no `X | Y` union typing, etc.).
- Object‑oriented core with clear separation of concerns.
- Keep patches minimal and focused; avoid unrelated changes.
- Place engine logic under `src/slot/` to match existing structure.

## Repository Map

- `src/slot/` — game engine
  - `symbols.py` — symbol set and multipliers.
  - `patterns.py` — winning patterns and weights.
  - `reel.py` — reel abstraction (circular, 3‑symbol window).
  - `slot_machine.py` — grid construction, payouts, `evaluate_patterns` for viz.
  - `simulator.py` — Monte Carlo simulation (RTP and win rate).
  - `search.py` — heuristic reel search targeting RTP/win‑rate.
- `src/api/server.py` — FastAPI: search, spin, simulate.
- `src/main.py` — CLI wrapper for search + validation.
- `web/` — React (Vite) frontend for inputs, spins, viz.
- `DS-HomeWork.md` — authoritative rules.
- `README.md` — quickstart for CLI, API, frontend.

## FastAPI Contracts

- `POST /search_auto` (preferred)
  - Adaptive search that tries a small schedule of (steps, eval_spins, seed) and returns the first configuration that passes exact validation.
  - Response matches `POST /search` (reels + validation metrics), with metrics computed deterministically via exact enumeration.

- `POST /search`
  - Request: `{ steps:int, eval_spins:int, spins:int, seed?:int }`
  - Response:
    {
      "reels": {"reel_1": int[], "reel_2": int[], "reel_3": int[]},
      "validation": {"spins": int, "rtp": number, "win_rate": number, "total_bet": number, "total_return": number}
    }

- `POST /spin`
  - Request: `{ reels:{reel_1:int[],reel_2:int[],reel_3:int[]}, bet_amount:number }`
  - Response (includes exact `stops` and per‑pattern matches):
    {
      "grid": int[3][3],
      "payout": number,
      "matches": [{"pattern": string, "coords": [[r,c],...], "symbol": int, "weight": int, "multiplier": number, "payout": number}],
      "stops": [int, int, int]
    }

- `POST /simulate`
  - Request: `{ reels:{...}, spins:int, seed?:int }`
  - Response: `{ spins, rtp, win_rate, total_bet, total_return }`

## Frontend Expectations (Vite/React)

- Use auto-search via `POST /search_auto` (no manual tuning required). Show a brief in-progress status while searching.
- Optional advanced inputs (if reintroduced): `steps`, `eval_spins`, `spins` (validation), `seed`.
- Reels JSON editor with pretty/minify and client‑side validation.
- Visualizations:
  - 3×3 grid with winning cells highlighted via `matches.coords`.
  - Metric bars comparing RTP and Win Rate vs targets (0.95, 0.55).
  - Pattern legend with names and shapes.
  - Reel animation using actual reels and returned `stops`.
  - Reel stats chips: length and symbol frequencies per reel.

## Simulation & Search Guidance

- Use `Simulator` for heuristic scoring during search; use exact enumeration for validation.
  - Typical search evaluations: 10k–50k spins (tunable).
  - Validation: exact evaluation by enumerating all stop combinations.
- `ReelSearch` uses light simulated‑annealing‑style mutations with local run‑building; you may tune:
  - Mutation rates, symbol weights, steps, eval spins.
  - Loss: `abs(rtp - 0.95) + 2*max(0, 0.55 - win_rate)` (+ small regularization).
  - Early stop when `|rtp - 0.95| < 0.01` and `win_rate ≥ 0.55`.
  - Keep reels at moderate lengths (≈ 8–14) to keep exact validation fast.

## Quality & Testing

- Keep Python 3.9 compatibility; avoid newer typing syntax.
- Quick smoke tests after core changes:
  - CLI: `PYTHONPATH=src python -m src.main --steps 10 --eval-spins 1000 --spins 5000`.
  - API: `PYTHONPATH=src uvicorn api.server:app --reload` then `GET /health`.
  - Frontend: `npm run dev` and verify search/spin/simulate flows.
- Do not change payouts, weights, or pattern definitions unless explicitly instructed.

## Non‑Goals

- No real‑money or external integrations.
- No new frameworks/databases; keep in‑memory and deterministic per seed.
- Avoid premature optimization; prioritize clarity and correctness.

## Proposing Changes

- Keep patches small and self‑contained.
- Update `README.md` for any CLI/API/UX changes.
- New modules under `src/slot/` should mirror existing style and responsibilities.
