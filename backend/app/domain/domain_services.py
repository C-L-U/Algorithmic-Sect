"""
Domain Layer — Domain Services.
Pure stateless logic that doesn't naturally belong to a single Entity.
No framework code here.
"""
from __future__ import annotations

from app.domain.entities import Stats


_STAT_MIN = 0.0
_STAT_MAX = 100.0


def clamp(value: float) -> float:
    """Clamp a float to the valid [0, 100] stat range."""
    return max(_STAT_MIN, min(_STAT_MAX, value))


def clamp_stats(stats: Stats) -> Stats:
    """
    Return a new Stats instance with all values clamped to [0, 100].
    Ensures no stat escapes the defined range regardless of AI output.
    """
    return Stats(
        happiness=clamp(stats.happiness),
        rancor=clamp(stats.rancor),
        freedom=clamp(stats.freedom),
        faith=clamp(stats.faith),
    )


def apply_delta(current: Stats, delta: Stats) -> Stats:
    """
    Apply a stat delta on top of current stats and clamp the result.
    Used to merge AI-proposed changes into the current entity state.
    """
    new_stats = Stats(
        happiness=current.happiness + delta.happiness,
        rancor=current.rancor + delta.rancor,
        freedom=current.freedom + delta.freedom,
        faith=current.faith + delta.faith,
    )
    return clamp_stats(new_stats)


def build_absolute_stats(ai_stats: Stats) -> Stats:
    """
    When the AI returns absolute stat values (not deltas), just clamp them.
    The xAI adapter uses this path since Grok returns target values.
    """
    return clamp_stats(ai_stats)
