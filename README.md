**Overview**
- Implements a 3x3 slot game with 5 symbols and 5 winning patterns per DS-HomeWork.md.
- Provides a simulator and a heuristic search to find reel configurations that target RTP=0.95 and win rate ≥ 0.55.

**Layout**
- `src/slot/symbols.py`: Symbol definitions and multipliers.
- `src/slot/patterns.py`: Winning patterns and weights.
- `src/slot/reel.py`: Reel representation and windowing.
- `src/slot/slot_machine.py`: Core game logic and payout evaluation.
- `src/slot/simulator.py`: Monte Carlo simulation engine.
- `src/slot/search.py`: Heuristic reel configuration search.
- `src/main.py`: CLI entry point.

**Usage**
- From the repository root, run search and validate:
  - `PYTHONPATH=src python -m src.main --steps 200 --eval-spins 50000 --spins 100000 --seed 1337`
  - Outputs `reels_config.json` with the reels and validation metrics.

- Or run from inside `src/` directly:
  - `python main.py --steps 200 --eval-spins 50000 --spins 100000 --seed 1337`

**API Server (Backend)**
- Install deps: `pip install fastapi uvicorn pydantic`
- Run server from repo root: `PYTHONPATH=src uvicorn api.server:app --reload --port 8000`
- Endpoints:
  - `GET /health`
  - `POST /search` body: `{steps, eval_spins, spins, seed}`
  - `POST /spin` body: `{reels: {reel_1, reel_2, reel_3}, bet_amount}`
  - `POST /simulate` body: `{reels: {...}, spins, seed}`

**React Frontend**
- cd `web`
- Install deps: `npm install` (or `pnpm i`/`yarn`)
- Start dev server: `npm run dev`
- Open the app (default http://localhost:5173). It targets `http://localhost:8000` by default; set `VITE_API_BASE` env to override.

**Notes**
- RTP is measured as expected payout per unit bet via Monte Carlo simulation.
- Win rate is the fraction of spins with any winning pattern.
- Reels are modeled as circular lists; each spin samples a stop index per reel and uses three consecutive symbols for the column.
# OpenNet
