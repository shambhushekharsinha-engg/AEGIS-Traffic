from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Any, Dict

from app.services.simulator.model import simulator

router = APIRouter(prefix="/api/v1/simulation", tags=["Simulation"])


class ScenarioRequest(BaseModel):
    current_green_sec: int
    cycle_length_sec: int
    current_queue_m: float
    scenario_parameters: List[int]  # list of proposed green seconds


@router.post("/scenarios")
def simulate_scenarios(req: ScenarioRequest):
    baseline = {"green_sec": req.current_green_sec, "queue_m": req.current_queue_m}

    scenarios = []
    for proposed_green in req.scenario_parameters:
        if proposed_green > req.cycle_length_sec:
            continue

        sim = simulator.simulate_signal_change(
            req.current_green_sec,
            proposed_green,
            req.cycle_length_sec,
            req.current_queue_m,
        )
        scenarios.append(sim)

    return {"baseline": baseline, "scenarios": scenarios}
