**Overview**
- 3×3 slot game per `DS-HomeWork.md` with 5 symbols and 5 winning patterns.
- Simulator and heuristic search target RTP=0.95 and win rate ≥ 0.55.

**Prerequisites**
- Python 3.9
- pip (optional: virtualenv)
- Node 18+ (for the frontend)

**Conda Setup (recommended)**
- Create and activate the environment:
  - `conda env create -f environment.yml`
  - `conda activate opennet-slot`
- Or create manually and install via pip:
  - `conda create -n opennet-slot python=3.9`
  - `conda activate opennet-slot`
  - `pip install -r requirements.txt`

**Makefile Tasks**
- `make setup` installs Python dependencies with pip.
- `make setup-conda` creates/updates the Conda env (activate with `conda activate opennet-slot`).
- `make run-api` runs the FastAPI server on port 8000.
- `make run-web` runs the Vite dev server in `web/`.

**Quickstart (CLI)**
- From repo root, run search + exact validation:
  - `PYTHONPATH=src python -m src.main --steps 800 --eval-spins 50000 --spins 100000 --seed 42`
  - Produces `reels_config.json` with reels and exact validation metrics.
- Alternatively from `src/`:
  - `python main.py --steps 800 --eval-spins 50000 --spins 100000 --seed 42`

**CLI Options**
- `--steps` number of search steps (mutation iterations) [default 800]
- `--eval-spins` spins per step to estimate quality [default 50000]
- `--spins` validation spins for the best candidate [default 100000]
- `--seed` optional RNG seed for determinism [default 42]

**API Server**
- Start server: `make run-api` (or `PYTHONPATH=src uvicorn api.server:app --reload --port 8000`)
- Endpoints:
  - `GET /health`
  - `POST /search_auto` (default; used by the frontend) — adaptive search that returns reels meeting RTP ≥ 0.95 and Win Rate ≥ 0.55 with exact validation.
  - `POST /search` body: `{ steps:int, eval_spins:int, spins:int, seed?:int }` (manual parameters)
  - `POST /spin` body: `{ reels:{reel_1:int[],reel_2:int[],reel_3:int[]}, bet_amount:number }`
  - `POST /simulate` body: `{ reels:{...}, spins:int, seed?:int }`

**React Frontend**
- `cd web`
- Install: `npm install` (or `pnpm i`/`yarn`)
- Run dev: `npm run dev` (or `make run-web` from repo root)
- Open http://localhost:5173 (defaults to API at http://localhost:8000). Override with `VITE_API_BASE`.
- Click “Auto Search” to get a configuration that passes exact validation (RTP ≥ 0.95, Win Rate ≥ 0.55). The UI shows a brief progress status while it searches.

**Repository Layout**
- `src/slot/symbols.py` — symbol definitions and multipliers
- `src/slot/patterns.py` — winning patterns and weights
- `src/slot/reel.py` — reel representation and windowing
- `src/slot/slot_machine.py` — grid construction and payout evaluation
- `src/slot/simulator.py` — Monte Carlo simulation engine
- `src/slot/search.py` — heuristic reel configuration search
- `src/main.py` — CLI entry point
- `src/api/server.py` — FastAPI server (search/spin/simulate)
- `web/` — Vite/React frontend

**Development & Testing**
- Smoke tests after engine changes:
  - CLI: `PYTHONPATH=src python -m src.main --steps 10 --eval-spins 1000 --spins 5000`
  - API: `PYTHONPATH=src uvicorn api.server:app --reload` then `GET /health`
  - Frontend: `npm run dev` and verify search/spin/simulate
- Keep Python 3.9 compatibility; avoid newer typing syntax.

**Notes**
- RTP: expected payout per unit bet via Monte Carlo simulation.
- Win rate: fraction of spins with ≥1 winning pattern.
- Reels are circular; each spin draws a stop per reel and uses three consecutive symbols per column.
