"""
API Layer — WebSocket Manager and Simulation Background Ticker.
Manages the 30-second reflection loop and broadcasts state to all connected clients.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Callable, Awaitable

from fastapi import WebSocket, WebSocketDisconnect

from app.application.use_cases import ProcessReflection

logger = logging.getLogger(__name__)

_CYCLE_INTERVAL_SECONDS = 30


class WebSocketManager:
    """Manages all active WebSocket connections and broadcasts."""

    def __init__(self) -> None:
        self._connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.append(websocket)
        logger.info("WS: client connected. Total connections: %d", len(self._connections))

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self._connections:
            self._connections.remove(websocket)
        logger.info("WS: client disconnected. Total connections: %d", len(self._connections))

    async def broadcast(self, data: dict) -> None:
        """Broadcast a JSON-serializable dict to all connected clients."""
        if not self._connections:
            return
        message = json.dumps(data)
        dead: list[WebSocket] = []
        for ws in self._connections:
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


class SimulationManager:
    """
    Manages the 30-second background ticker.
    On each tick, runs ProcessReflection for ALL entities and broadcasts
    the updated state to all WebSocket clients.
    """

    def __init__(
        self,
        use_case: ProcessReflection,
        ws_manager: WebSocketManager,
        get_all_entity_ids: Callable[[], list[str]],
        get_all_entities_dict: Callable[[], list[dict]],
    ) -> None:
        self._use_case = use_case
        self._ws = ws_manager
        self._get_ids = get_all_entity_ids
        self._get_all = get_all_entities_dict
        self._task: asyncio.Task | None = None
        self.is_running: bool = False

    def start(self) -> None:
        if self.is_running:
            return
        self.is_running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("Simulation: ticker STARTED")

    def stop(self) -> None:
        self.is_running = False
        if self._task:
            self._task.cancel()
            self._task = None
        logger.info("Simulation: ticker STOPPED")

    async def _run_loop(self) -> None:
        """Main simulation loop — runs every CYCLE_INTERVAL_SECONDS."""
        try:
            while self.is_running:
                await asyncio.sleep(_CYCLE_INTERVAL_SECONDS)
                if not self.is_running:
                    break
                await self._tick()
        except asyncio.CancelledError:
            logger.info("Simulation: loop cancelled cleanly")

    async def _tick(self) -> None:
        """Process one reflection cycle for all entities and broadcast."""
        logger.info("Simulation: TICK — processing all entity reflections")
        entity_ids = self._get_ids()

        for eid in entity_ids:
            try:
                await self._use_case.execute(eid)
            except Exception as exc:
                logger.error("Simulation: tick error for entity %s — %s", eid, exc)

        # Broadcast updated state snapshot to all WS clients
        entities_data = self._get_all()
        await self._ws.broadcast({
            "type": "simulation_tick",
            "entities": entities_data,
        })
        logger.info("Simulation: TICK complete — broadcasted to %d clients", len(self._ws._connections))
