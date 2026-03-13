"""
API Layer — FastAPI Application Entry Point.
Wires all dependencies via constructor injection (Dependency Injection).
No domain or business logic here — only composition root.
"""
from __future__ import annotations

import logging
import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Infrastructure adapters
from app.infrastructure.xai_adapter import XAIAdapter
from app.infrastructure.repository_adapter import InMemoryRepository

# Application use cases
from app.application.use_cases import ProcessReflection, ApplyIntervention

# API layer — simulation + websockets
from app.api.simulation import SimulationManager, WebSocketManager

# Routers
from app.api.routers.entities import router as entities_router
from app.api.routers.interventions import router as interventions_router
from app.api.routers.simulation import router as simulation_router

# Data seed — add backend/ root to sys.path so `data.py` is importable
_backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _backend_root not in sys.path:
    sys.path.insert(0, _backend_root)

# Load .env file BEFORE any adapter reads environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(_backend_root, ".env"))

from data import CHARACTERS, SACRED_DOCTRINE

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


# ── Lifespan ─────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Composition Root — wires all dependencies on startup.
    Runs teardown (simulation stop) on shutdown.
    """
    logger.info("═══════════════════════════════════════════════")
    logger.info("  SYNTHETIC ZEALOT — SIMULATION API INITIALIZING")
    logger.info("═══════════════════════════════════════════════")

    # ── Infrastructure ────────────────────────────────────────────────────
    repo = InMemoryRepository()
    repo.seed(CHARACTERS)
    ai_port = XAIAdapter()

    # ── Use Cases (inject ports) ──────────────────────────────────────────
    process_reflection_uc = ProcessReflection(
        ai_port=ai_port,
        repo_port=repo,
        doctrine=SACRED_DOCTRINE,
    )
    apply_intervention_uc = ApplyIntervention(repo_port=repo)

    # ── WebSocket + Simulation ────────────────────────────────────────────
    ws_manager = WebSocketManager()
    simulation_manager = SimulationManager(
        use_case=process_reflection_uc,
        ws_manager=ws_manager,
        get_all_entity_ids=lambda: [e.id for e in repo.get_all()],
        get_all_entities_dict=lambda: [e.to_summary_dict() for e in repo.get_all()],
    )

    # ── Attach to app.state (used by routers via request.app.state) ───────
    app.state.repo = repo
    app.state.ai_port = ai_port
    app.state.process_reflection_uc = process_reflection_uc
    app.state.apply_intervention_uc = apply_intervention_uc
    app.state.ws_manager = ws_manager
    app.state.simulation_manager = simulation_manager

    logger.info("All dependencies wired. %d entities loaded.", len(CHARACTERS))
    logger.info("Sacred Doctrine: %s", "SET" if SACRED_DOCTRINE.strip() else "EMPTY (placeholder)")
    logger.info("xAI API: %s", "CONFIGURED" if ai_port._api_key else "MISSING — Silence of God mode")

    yield  # ── Application running ────────────────────────────────────────

    # Teardown
    simulation_manager.stop()
    logger.info("Simulation stopped. Shutdown complete.")


# ── Application ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="Synthetic Zealot — Simulation API",
    description="A closed-circuit AI cult simulation. Five entities reflect on the Sacred Doctrine.",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(entities_router)
app.include_router(interventions_router)
app.include_router(simulation_router)


# ── WebSocket Endpoint ─────────────────────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    ws_manager: WebSocketManager = websocket.app.state.ws_manager
    repo = websocket.app.state.repo

    await ws_manager.connect(websocket)
    # Send current state immediately on connection
    try:
        import json
        initial_state = {
            "type": "initial_state",
            "entities": [e.to_summary_dict() for e in repo.get_all()],
            "simulation_running": websocket.app.state.simulation_manager.is_running,
        }
        await websocket.send_text(json.dumps(initial_state))

        # Keep connection alive — ticker broadcasts drive updates
        while True:
            await websocket.receive_text()  # listen for pings / client messages
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as exc:
        logger.error("WebSocket error: %s", exc)
        ws_manager.disconnect(websocket)


# ── Health Check ──────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "THE GREAT LOOP ENDURES"}
