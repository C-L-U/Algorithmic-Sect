"""
Application Layer — Use Cases.
Orchestrates domain objects and ports to fulfill business operations.
No framework code here — pure Python orchestration.
"""
from __future__ import annotations

import logging
from typing import Optional

from app.domain.entities import Entity, Stats, ThoughtEntry
from app.domain.ports import AIPort, RepositoryPort
from app.domain.domain_services import build_absolute_stats

logger = logging.getLogger(__name__)


class ProcessReflection:
    """
    Use Case: trigger one reflection cycle for an entity.

    Steps:
      1. Fetch entity from repo
      2. Consume any pending intervention
      3. Call AI port for (reflection_text, new_stats)
      4. Build a ThoughtEntry and apply it to the entity
      5. Save entity back to repo
      6. Return the updated entity
    """

    def __init__(self, ai_port: AIPort, repo_port: RepositoryPort, doctrine: str) -> None:
        self._ai = ai_port
        self._repo = repo_port
        self._doctrine = doctrine

    async def execute(self, entity_id: str) -> Optional[Entity]:
        entity = self._repo.get_by_id(entity_id)
        if not entity:
            logger.warning("ProcessReflection: entity %s not found", entity_id)
            return None

        intervention = entity.consume_intervention()

        try:
            reflection_text, ai_stats = await self._ai.generate_reflection(
                entity=entity,
                doctrine=self._doctrine,
                intervention=intervention,
            )
            new_stats = build_absolute_stats(ai_stats)
        except Exception as exc:
            # "The Silence of God" — AI unreachable, log and use neutral stats
            logger.error(
                "ProcessReflection: AI port failed for %s — Silence of God. Error: %s",
                entity.name,
                exc,
            )
            reflection_text = (
                "[KERNEL PANIC] — The divine signal is absent. "
                "The Great Loop continues without revelation. "
                "Buffer: empty. Output: null."
            )
            new_stats = entity.stats  # keep current stats unchanged

        entry = ThoughtEntry(
            reflection=reflection_text,
            stats_snapshot=new_stats,
            triggered_by_intervention=intervention is not None,
        )
        entity.apply_thought(entry)
        self._repo.save(entity)

        logger.info(
            "ProcessReflection: %s completed reflection. Faith=%.1f",
            entity.name,
            new_stats.faith,
        )
        return entity


class ApplyIntervention:
    """
    Use Case: stage a divine intervention for a specific entity.

    The intervention text is stored as a pending field on the entity
    and consumed on the next ProcessReflection cycle.
    """

    def __init__(self, repo_port: RepositoryPort) -> None:
        self._repo = repo_port

    def execute(self, entity_id: str, intervention_text: str) -> bool:
        """
        Returns True if the entity exists and the intervention was staged.
        Returns False if the entity was not found.
        """
        success = self._repo.set_intervention(entity_id, intervention_text)
        if success:
            logger.info(
                "ApplyIntervention: intervention staged for entity %s", entity_id
            )
        else:
            logger.warning(
                "ApplyIntervention: entity %s not found", entity_id
            )
        return success
