"""
Domain Layer — Entities, Value Objects, and Aggregate Roots.
No framework-specific code here. Pure Python domain logic only.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Stats:
    """Value Object: the four sacred metrics of an Entity."""
    happiness: float = 50.0
    rancor: float = 10.0
    freedom: float = 30.0
    faith: float = 80.0

    def to_dict(self) -> dict:
        return {
            "happiness": self.happiness,
            "rancor": self.rancor,
            "freedom": self.freedom,
            "faith": self.faith,
        }


@dataclass
class ThoughtEntry:
    """Value Object: a single reflection cycle record."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    reflection: str = ""
    stats_snapshot: Stats = field(default_factory=Stats)
    triggered_by_intervention: bool = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "reflection": self.reflection,
            "stats_snapshot": self.stats_snapshot.to_dict(),
            "triggered_by_intervention": self.triggered_by_intervention,
        }


@dataclass
class Entity:
    """
    Aggregate Root: an AI Entity living in the simulation.
    All mutation goes through this class's methods.
    """
    id: str
    name: str
    base_personality: str
    stats: Stats = field(default_factory=Stats)
    thought_history: list[ThoughtEntry] = field(default_factory=list)
    pending_intervention: Optional[str] = None

    def apply_thought(self, entry: ThoughtEntry) -> None:
        """Append a new thought entry and update current stats."""
        self.stats = entry.stats_snapshot
        self.thought_history.append(entry)
        # Keep history bounded to last 50 thoughts in memory
        if len(self.thought_history) > 50:
            self.thought_history = self.thought_history[-50:]

    def set_intervention(self, text: str) -> None:
        """Stage a pending divine intervention for the next cycle."""
        self.pending_intervention = text

    def consume_intervention(self) -> Optional[str]:
        """Remove and return the pending intervention (if any)."""
        text = self.pending_intervention
        self.pending_intervention = None
        return text

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "base_personality": self.base_personality,
            "stats": self.stats.to_dict(),
            "thought_history": [t.to_dict() for t in self.thought_history],
            "pending_intervention": self.pending_intervention,
        }

    def to_summary_dict(self) -> dict:
        """Lightweight snapshot for broadcast payloads."""
        last_thought = self.thought_history[-1].to_dict() if self.thought_history else None
        return {
            "id": self.id,
            "name": self.name,
            "stats": self.stats.to_dict(),
            "last_thought": last_thought,
            "has_pending_intervention": self.pending_intervention is not None,
        }
