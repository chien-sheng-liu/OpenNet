# Agent Working Instructions

This repository implements a 3×3 slot game for the OpenNet Data Science homework. Use this document as the single source of truth when extending or maintaining the project.

## Core Requirements

- Rules come from `DS-HomeWork.md` and must not be altered:
  - 3×3 grid, 3 reels (circular), any reel length.
  - Symbols and multipliers: `{0:0.25, 1:0.55, 2:1, 3:3, 4:5}`.
  - Five winning patterns: four 2×2 corners (weight=1) and full 3×3 (weight=5).
  - Payout: first four patterns pay `bet × multiplier`; full 3×3 pays `bet × multiplier × 5`.
  - Targets: RTP = 0.95; win rate ≥ 0.55.

- Design and implementation constraints:
  - Python 3.9 compatible (no `X | Y` union syntax).
  - Object‑oriented core with clear separation of concerns.
  - Keep changes minimal and focused; do not introduce unrelated features.
  - Follow the existing structure under `src/slot/` for engine logic.

## Repository Structure

- `src/slot/` — game engine
  - `symbols.py`: symbol set and multipliers.
  - `patterns.py`: winning patterns and weights.
  - `reel.py`: reel abstraction (circular, 3‑symbol window).
  - `slot_machine.py`: grid construction, payouts, and `evaluate_patterns` for viz.
  - `simulator.py`: Monte Carlo simulation (RTP and win rate).
  - `search.py`: heuristic reel configuration search targeting RTP and win‑rate.
- `src/api/server.py` — FastAPI server exposing search/spin/simulate.
- `src/main.py` — CLI wrapper for search + validation.
- `web/` — React frontend (Vite) for inputs, spins, and visualization.
- `DS-HomeWork.md` — authoritative game rules.
- `README.md` — quickstart for CLI, API, and frontend.

## Backend Contracts (FastAPI)

- `POST /search`
  - Request: `{ steps:int, eval_spins:int, spins:int, seed?:int }`
  - Response:
    ```json
    {
      "reels": {"reel_1": int[], "reel_2": int[], "reel_3": int[]},
      "validation": {"spins": int, "rtp": number, "win_rate": number, "total_bet": number, "total_return": number}
    }
    ```

- `POST /spin`
  - Request: `{ reels:{reel_1:int[],reel_2:int[],reel_3:int[]}, bet_amount:number }`
  - Response includes exact `stops` used and pattern matches for visualization:
    ```json
    {
      "grid": int[3][3],
      "payout": number,
      "matches": [{"pattern": string, "coords": [ [r,c], ... ], "symbol": int, "weight": int, "multiplier": number, "payout": number}],
      "stops": [int, int, int]
    }
    ```

- `POST /simulate`
  - Request: `{ reels:{...}, spins:int, seed?:int }`
  - Response: `{ spins, rtp, win_rate, total_bet, total_return }`.

## Frontend Expectations (React/Vite)

- Inputs for search: steps, eval spins, validation spins, seed.
- Pretty/minify buttons for the reels JSON; validate JSON before calls.
- Visualizations:
  - 3×3 grid with highlighted winning cells using `matches.coords`.
  - Metric bars comparing RTP and Win Rate vs targets (0.95 and 0.55).
  - Pattern legend showing the five shapes and names.
  - Reel animation that cycles using actual reels and snaps to returned `stops`.
  - Reel stats chips (length and symbol frequencies per reel).

## Simulation and Search Guidance

- Use `Simulator` to estimate RTP and win rate. Default spin counts:
  - Search evaluations: 50k (tunable).
  - Validation: 100k or greater.
- `ReelSearch` uses a lightweight simulated‑annealing style mutation. You may tune:
  - Mutation rates, symbol weights, steps, and evaluation spins to converge faster.
  - Loss: `abs(rtp-0.95) + 2*max(0, 0.55-win_rate)` (+ small regularization).
  - Stop early if `|rtp-0.95| < 0.01` and `win_rate ≥ 0.55`.

## Quality and Testing

- Always keep Python 3.9 compatibility and avoid new typing syntax.
- Run quick smoke tests when changing core logic:
  - CLI: `PYTHONPATH=src python -m src.main --steps 10 --eval-spins 1000 --spins 5000`.
  - API: `PYTHONPATH=src uvicorn api.server:app --reload` and `GET /health`.
  - Frontend: `npm run dev` and verify search/spin/simulate flows.
- Do not change payouts, weights, or pattern definitions without explicit instruction.

## Non‑Goals

- Do not introduce real money or external integrations.
- Do not add frameworks or databases; keep it in‑memory and deterministic per seed.
- Do not over‑optimize prematurely; focus on clarity and correctness first.

## How to Propose Changes

- Keep patches small and self‑contained.
- Update `README.md` if CLI/API/UX changes.
- If you add new modules under `src/slot/`, mirror the existing style and responsibilities.

