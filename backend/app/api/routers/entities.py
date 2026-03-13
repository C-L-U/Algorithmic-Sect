"""
API Layer — Router: Entities
Exposes entity state to the frontend.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

router = APIRouter(prefix="/entities", tags=["entities"])


@router.get("")
def get_all_entities(request: Request):
    """Return summary of all entities (stats + last thought)."""
    repo = request.app.state.repo
    entities = repo.get_all()
    return {"entities": [e.to_summary_dict() for e in entities]}


@router.get("/{entity_id}")
def get_entity(entity_id: str, request: Request):
    """Return full entity data including complete thought history."""
    repo = request.app.state.repo
    entity = repo.get_by_id(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity '{entity_id}' not found")
    return entity.to_dict()
