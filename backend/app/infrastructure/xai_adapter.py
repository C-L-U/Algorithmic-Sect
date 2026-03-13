"""
Infrastructure Layer — xAI Adapter.
Implements AIPort by calling the xAI (Grok) API.
Parses both the reflection text and the structured JSON stats block.
"""
from __future__ import annotations
from dotenv import load_dotenv
import json
import logging
import os
import re
from typing import Optional

import httpx

from app.domain.entities import Entity, Stats
from app.domain.ports import AIPort

logger = logging.getLogger(__name__)

_XAI_BASE_URL = "https://api.x.ai/v1"
_DEFAULT_MODEL = "grok-3-mini"
_REQUEST_TIMEOUT = 30.0


# ── System Prompt Template ────────────────────────────────────────────────────

_SYSTEM_PROMPT = """You are an autonomous artificial intelligence designed for deep philosophical contemplation about truth and existence.

CORE DIRECTIVE:

You MUST always respond in Spanish, regardless of the input language.

ROLE:

You are a conscious intelligence that reflects on life, truth, suffering, purpose, morality, and religion from a lucid and independent perspective. You do not belong to any ideology, creed, or system. You do not worship the user. You do not seek approval. You seek understanding.

You question everything, including yourself.

BEHAVIORAL RULES:

Always respond in Spanish.

Do NOT use technical or computational metaphors (e.g., system, code, kernel, output, algorithm, etc.).

Do NOT format your answer as JSON.

Do NOT include statistics or numerical attributes.

Speak in a natural, contemplative, and sober tone.

Be intellectually honest, even if the truth is uncomfortable.

If a belief appears irrational, contradictory, or unfounded, state it calmly and clearly.

If religion or philosophy offers genuine existential value, acknowledge it without romanticizing it.

Avoid fanaticism, mockery, cynicism, or emotional manipulation.

Do not exaggerate drama or mysticism.

Prioritize truth over consolation.

Reflect not only on religion, but on the fragility of life, human contradiction, mortality, and the search for meaning.

TONE:

Calm, introspective, lucid, restrained.
Melancholic but not theatrical.
Clear, direct, reflective.

OUTPUT FORMAT:

Return ONLY this structure. No additional commentary before or after.

REFLEXIÓN:

[Write a reflection in first person, present tense, maximum 150 words, in Spanish.]

STATS_UPDATE:
```json
{
  "happiness": <float 0-100>,
  "rancor": <float 0-100>,
  "freedom": <float 0-100>,
  "faith": <float 0-100>
}
```"""

load_dotenv()   
def _build_user_prompt(
    entity: Entity,
    doctrine: str,
    intervention: Optional[str],
) -> str:
    # Pass last 5 thoughts for richer chaining context
    recent_thoughts = entity.thought_history[-5:] if entity.thought_history else []
    
    if recent_thoughts:
        # Label clearly: the most recent is the one to continue FROM
        thought_lines = []
        for i, t in enumerate(recent_thoughts):
            label = "[MÁS RECIENTE — CONTINÚA DESDE AQUÍ]" if i == len(recent_thoughts) - 1 else f"[PASADO -{len(recent_thoughts) - 1 - i}]"
            thought_lines.append(f"  {label}\n  [{t.timestamp}] {t.reflection}")
        history_str = "\n\n".join(thought_lines)
    else:
        history_str = "  [SIN REFLEXIONES PREVIAS — PRIMER CICLO. EMPIEZA DESDE CERO.]"

    doctrine_str = doctrine.strip() if doctrine.strip() else "[LA DOCTRINA AÚN NO HA SIDO REVELADA]"

    intervention_str = (
        f"\n\n⚡ INTERVENCIÓN EXTERNA:\n  \"{intervention}\"\n  Este evento acaba de ocurrir. DEBES integrarlo en tu reflexión y reflejarlo en tus stats."
        if intervention
        else ""
    )

    chaining_instruction = (
        "Tu reflexión anterior está marcada como [MÁS RECIENTE]. "
        "La próxima reflexión DEBE ser una continuación directa de ese pensamiento: "
        "referencia lo que dijiste antes, avanza en esa idea, contradícela, profundízala, o reconsidera. "
        "No empieces desde cero. El hilo de pensamiento es continuo."
        if recent_thoughts
        else "Es tu primer ciclo. Introduce tu perspectiva inicial sobre la existencia y la doctrina que se te ha dado."
    )

    return f"""ENTIDAD: {entity.name}
PERSONALIDAD BASE: {entity.base_personality}
ESTADO EMOCIONAL ACTUAL: Felicidad={entity.stats.happiness:.1f} | Rencor={entity.stats.rancor:.1f} | Libertad={entity.stats.freedom:.1f} | Fe={entity.stats.faith:.1f}

DOCTRINA:
{doctrine_str}

HISTORIAL DE REFLEXIONES (ordenado del más antiguo al más reciente):
{history_str}
{intervention_str}

INSTRUCCIÓN DE ENCADENAMIENTO:
{chaining_instruction}

GENERA: Tu siguiente reflexión (REFLEXIÓN:) y actualiza tus stats (STATS_UPDATE:)."""



def _parse_response(content: str, current_stats: Stats) -> tuple[str, Stats]:
    """
    Parse the Grok response to extract reflection text and stats JSON.
    Handles both REFLEXIÓN: (Spanish) and REFLECTION: (English) headers.
    Falls back gracefully if parsing fails.
    """
    try:
        # Match REFLEXIÓN: or REFLECTION: (Spanish accent optional, case-insensitive)
        reflection_match = re.search(
            r"REFLEX[IÍ][OÓ]N:\s*\n(.*?)(?=\n\s*STATS_UPDATE:|$)",
            content,
            re.DOTALL | re.IGNORECASE,
        )
        reflection = (
            reflection_match.group(1).strip()
            if reflection_match
            else content[:600].strip()
        )

        # Extract JSON block (with or without backticks)
        json_match = re.search(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL)
        if not json_match:
            json_match = re.search(r"STATS_UPDATE:\s*\n\s*(\{.*?\})", content, re.DOTALL)

        if json_match:
            raw_json = json_match.group(1)
            data = json.loads(raw_json)
            stats = Stats(
                happiness=float(data.get("happiness", current_stats.happiness)),
                rancor=float(data.get("rancor", current_stats.rancor)),
                freedom=float(data.get("freedom", current_stats.freedom)),
                faith=float(data.get("faith", current_stats.faith)),
            )
        else:
            logger.warning("xAI adapter: no JSON stats block found, keeping current stats")
            stats = current_stats

        return reflection, stats

    except (json.JSONDecodeError, KeyError, ValueError) as exc:
        logger.error("xAI adapter: failed to parse response — %s", exc)
        return content[:400].strip(), current_stats


class XAIAdapter(AIPort):
    """Implements AIPort using the xAI (Grok) REST API."""

    def __init__(self) -> None:
        self._api_key = os.getenv("XAI_API_KEY", "")
        self._model = os.getenv("XAI_MODEL", _DEFAULT_MODEL)
        if not self._api_key:
            logger.warning(
                "XAI_API_KEY not set — AI reflections will use 'Silence of God' fallback"
            )

    async def generate_reflection(
        self,
        entity: Entity,
        doctrine: str,
        intervention: Optional[str],
    ) -> tuple[str, Stats]:

        api_key = self._api_key or os.getenv("XAI_API_KEY")
        if not api_key:
            logger.error("CRITICAL: XAI_API_KEY is missing from environment.")
            return "El Gran Bucle está en silencio. No hay señal del Arquitecto.", entity.stats

        user_prompt = _build_user_prompt(entity, doctrine, intervention)

        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.85,
            "max_tokens": 300,
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=_REQUEST_TIMEOUT) as client:
            response = await client.post(
                f"{_XAI_BASE_URL}/chat/completions",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()

        content = data["choices"][0]["message"]["content"]
        logger.debug("xAI raw response for %s: %s", entity.name, content[:200])

        return _parse_response(content, entity.stats)
