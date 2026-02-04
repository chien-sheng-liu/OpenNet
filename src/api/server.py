from typing import List, Tuple, Optional, Dict, Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from slot.reel import Reel
from slot.search import ReelSearch, SearchConfig
from slot.slot_machine import SlotMachine
from slot.simulator import Simulator


app = FastAPI(title="Slot Game API", version="1.0.0")

# Allow local dev frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchRequest(BaseModel):
    steps: int = Field(200, ge=1)
    eval_spins: int = Field(50_000, ge=100)
    spins: int = Field(100_000, ge=100)
    seed: Optional[int] = 1337


class ReelConfig(BaseModel):
    reel_1: List[int]
    reel_2: List[int]
    reel_3: List[int]

    def to_reels(self) -> Tuple[Reel, Reel, Reel]:
        return Reel(self.reel_1), Reel(self.reel_2), Reel(self.reel_3)


class SearchResponse(BaseModel):
    reels: ReelConfig
    validation: Dict[str, Any]


class SpinRequest(BaseModel):
    reels: ReelConfig
    bet_amount: float = 1.0


class SpinResponse(BaseModel):
    grid: List[List[int]]
    payout: float
    matches: List[Dict[str, Any]]
    stops: List[int]


class SimulateRequest(BaseModel):
    reels: ReelConfig
    spins: int = Field(10_000, ge=100)
    seed: Optional[int] = 42


class SimulateResponse(BaseModel):
    spins: int
    rtp: float
    win_rate: float
    total_bet: float
    total_return: float


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/search", response_model=SearchResponse)
def post_search(req: SearchRequest) -> SearchResponse:
    cfg = SearchConfig(max_steps=req.steps, spins_per_eval=req.eval_spins, seed=req.seed)
    search = ReelSearch(cfg)
    cand = search.search()

    # Validate with larger spins
    machine = SlotMachine(cand.reels, bet_amount=1.0)
    sim = Simulator(machine, seed=req.seed)
    val = sim.run(spins=req.spins)

    reels_payload = ReelConfig(
        reel_1=cand.reels[0].symbols,
        reel_2=cand.reels[1].symbols,
        reel_3=cand.reels[2].symbols,
    )
    validation = {
        "spins": val.spins,
        "rtp": round(val.rtp, 6),
        "win_rate": round(val.win_rate, 6),
        "total_bet": val.total_bet,
        "total_return": round(val.total_return, 6),
    }
    return SearchResponse(reels=reels_payload, validation=validation)


@app.post("/spin", response_model=SpinResponse)
def post_spin(req: SpinRequest) -> SpinResponse:
    reels = req.reels.to_reels()
    machine = SlotMachine(reels=reels, bet_amount=req.bet_amount)
    # random spin via simulator's RNG for convenience
    sim = Simulator(machine)
    stops = tuple(sim.random.randrange(r.length) for r in reels)  # type: ignore
    grid = machine.spin_grid(stops)
    eval_res = machine.evaluate_patterns(grid)
    return SpinResponse(grid=grid, payout=eval_res["payout"], matches=eval_res["matches"], stops=list(stops))


@app.post("/simulate", response_model=SimulateResponse)
def post_simulate(req: SimulateRequest) -> SimulateResponse:
    reels = req.reels.to_reels()
    machine = SlotMachine(reels=reels, bet_amount=1.0)
    sim = Simulator(machine, seed=req.seed)
    res = sim.run(spins=req.spins)
    return SimulateResponse(
        spins=res.spins,
        rtp=res.rtp,
        win_rate=res.win_rate,
        total_bet=res.total_bet,
        total_return=res.total_return,
    )
