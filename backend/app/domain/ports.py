"""
Domain Layer — Port Interfaces (Abstract Base Classes).
These define the contracts between the Domain and Infrastructure.
No implementation details here — only interface signatures.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities import Entity, Stats


class AIPort(ABC):
    """
    Output Port: contract for any AI inference service.
    The Domain doesn't know about xAI, OpenAI, or any specific vendor.
    """

    @abstractmethod
    async def generate_reflection(
        self,
        entity: Entity,
        doctrine: str,
        intervention: Optional[str],
    ) -> tuple[str, Stats]:
        """
        Generate a reflection for the entity given the current doctrine
        and an optional divine intervention.

        Returns:
            A tuple of (reflection_text, new_stats).
        """
        ...


class RepositoryPort(ABC):
    """
    Output Port: contract for any persistence mechanism.
    """

    @abstractmethod
    def get_all(self) -> list[Entity]:
        """Return all entities in the simulation."""
        ...

    @abstractmethod
    def get_by_id(self, entity_id: str) -> Optional[Entity]:
        """Return the entity with the given ID, or None."""
        ...

    @abstractmethod
    def save(self, entity: Entity) -> None:
        """Persist the entity state."""
        ...

    @abstractmethod
    def set_intervention(self, entity_id: str, text: str) -> bool:
        """
        Stage a pending intervention for the entity.
        Returns False if entity not found.
        """
        ...
