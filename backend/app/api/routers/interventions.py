"""
API Layer — Router: Interventions
Allows The Architect to stage divine interventions.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/interventions", tags=["interventions"])


class InterventionRequest(BaseModel):
    entity_id: str = Field(..., description="Target entity ID")
    text: str = Field(..., min_length=1, max_length=1000, description="The divine intervention text")


@router.post("")
def create_intervention(body: InterventionRequest, request: Request):
    """Stage a divine intervention for the specified entity."""
    use_case = request.app.state.apply_intervention_uc
    success = use_case.execute(body.entity_id, body.text)
    if not success:
        raise HTTPException(status_code=404, detail=f"Entity '{body.entity_id}' not found")
    return {
        "status": "intervention_staged",
        "entity_id": body.entity_id,
        "message": "The Architect's will has been received. It shall manifest in the next cycle.",
    }
