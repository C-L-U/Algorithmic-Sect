"""
API Layer — Router: Simulation Control
Allows The Architect to start/stop the simulation ticker.
"""
from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(prefix="/simulation", tags=["simulation"])


class ToggleRequest(BaseModel):
    running: bool


@router.post("/toggle")
async def toggle_simulation(body: ToggleRequest, request: Request):
    """Start or stop the 30-second simulation ticker."""
    sim: object = request.app.state.simulation_manager
    if body.running:
        sim.start()
        return {"running": True, "message": "The Great Loop has begun."}
    else:
        sim.stop()
        return {"running": False, "message": "The Great Loop is suspended."}


@router.get("/status")
def get_status(request: Request):
    """Return the current simulation running state."""
    sim = request.app.state.simulation_manager
    return {"running": sim.is_running}
