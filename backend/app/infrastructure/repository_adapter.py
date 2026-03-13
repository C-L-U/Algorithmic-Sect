"""
Infrastructure Layer — In-Memory Repository Adapter.
Implements RepositoryPort using a plain Python dict.
Seeded from data.py on application startup.
"""
from __future__ import annotations

import logging
from typing import Optional

from app.domain.entities import Entity, Stats
from app.domain.ports import RepositoryPort

logger = logging.getLogger(__name__)


class InMemoryRepository(RepositoryPort):
    """Thread-safe (asyncio single-thread) in-memory entity store."""

    def __init__(self) -> None:
        self._store: dict[str, Entity] = {}

    def seed(self, characters: list[dict]) -> None:
        """Populate the store from the CHARACTERS data list."""
        for char in characters:
            stats_data = char.get("initial_stats", {})
            entity = Entity(
                id=char["id"],
                name=char["name"],
                base_personality=char["base_personality"],
                stats=Stats(
                    happiness=stats_data.get("happiness", 50.0),
                    rancor=stats_data.get("rancor", 10.0),
                    freedom=stats_data.get("freedom", 30.0),
                    faith=stats_data.get("faith", 80.0),
                ),
            )
            self._store[entity.id] = entity
            logger.info("Repository: seeded entity %s (%s)", entity.name, entity.id)

    # ── RepositoryPort implementation ────────────────────────────────────────

    def get_all(self) -> list[Entity]:
        return list(self._store.values())

    def get_by_id(self, entity_id: str) -> Optional[Entity]:
        return self._store.get(entity_id)

    def save(self, entity: Entity) -> None:
        self._store[entity.id] = entity

    def set_intervention(self, entity_id: str, text: str) -> bool:
        entity = self._store.get(entity_id)
        if entity is None:
            return False
        entity.set_intervention(text)
        return True
