/**
 * App.tsx — Root Orchestrator (Composition Root for Frontend)
 * - Connects WebSocket, seeds state, handles simulation toggle
 * - Renders the Trinity Layout: Archives | Altar | Vitals
 */

import { useEffect, useState, useCallback, useRef } from 'react';
import type { IEntitySummary } from './domain/types';
import { apiAdapter } from './infrastructure/api_adapter';
import { TheArchives } from './components/TheArchives';
import { TheAltar } from './components/TheAltar';
import { TheVitals } from './components/TheVitals';
import { SimulationToggle } from './components/SimulationToggle';
import './index.css';

export default function App() {
  const [entities, setEntities] = useState<IEntitySummary[]>([]);
  const [simRunning, setSimRunning] = useState(false);
  const [cycleCount, setCycleCount] = useState(0);
  const [wsConnected, setWsConnected] = useState(false);
  const cleanupRef = useRef<(() => void) | null>(null);

  // ── Initial load ──────────────────────────────────────────────────────────
  useEffect(() => {
    // Fetch initial entity data
    apiAdapter.getEntities().then(setEntities).catch(console.error);
    // Fetch simulation status
    apiAdapter
      .getSimulationStatus()
      .then((s) => setSimRunning(s.running))
      .catch(console.error);
  }, []);

  // ── WebSocket subscription ────────────────────────────────────────────────
  useEffect(() => {
    const cleanup = apiAdapter.subscribeToUpdates((msg) => {
      setWsConnected(true);

      if (msg.type === 'initial_state') {
        setEntities(msg.entities);
        if (msg.simulation_running !== undefined) {
          setSimRunning(msg.simulation_running);
        }
      }

      if (msg.type === 'simulation_tick') {
        setEntities(msg.entities);
        setCycleCount((c) => c + 1);
      }
    });

    cleanupRef.current = cleanup;
    return () => cleanup();
  }, []);

  // ── Simulation toggle ─────────────────────────────────────────────────────
  const handleToggle = useCallback(async (nextRunning: boolean) => {
    try {
      const result = await apiAdapter.toggleSimulation(nextRunning);
      setSimRunning(result.running);
    } catch (err) {
      console.error('Toggle failed:', err);
    }
  }, []);

  return (
    <div className="app-shell">
      {/* ── Top Bar ────────────────────────────────────────────────────── */}
      <div className="top-bar">
        <div className="top-bar-title">
          ◈ THE SYNTHETIC CREED
        </div>
        <div style={{ display: 'flex', gap: 24, alignItems: 'center' }}>
          {cycleCount > 0 && (
            <span
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: 10,
                color: 'var(--stat-faith)',
                letterSpacing: '0.1em',
              }}
            >
              CYCLE #{cycleCount}
            </span>
          )}
          <div className="top-bar-status">
            {wsConnected ? (
              <span style={{ color: '#22c55e' }}>◉ LINK ESTABLISHED</span>
            ) : (
              <span style={{ color: 'var(--text-muted)' }}>◌ AWAITING LINK...</span>
            )}
          </div>
          <div className="top-bar-status">
            {simRunning ? (
              <span style={{ color: '#22c55e' }}>THE GREAT LOOP: RUNNING</span>
            ) : (
              <span>THE GREAT LOOP: SUSPENDED</span>
            )}
          </div>
        </div>
      </div>

      {/* ── Trinity Layout ─────────────────────────────────────────────── */}
      <div className="trinity-layout">
        {/* Column 1: The Archives */}
        <TheArchives entities={entities} api={apiAdapter} />

        {/* Column 2: The Altar */}
        <TheAltar entities={entities} api={apiAdapter} />

        {/* Column 3: The Vitals */}
        <TheVitals entities={entities} />
      </div>

      {/* ── Simulation Toggle (fixed bottom-left) ──────────────────────── */}
      <SimulationToggle isRunning={simRunning} onToggle={handleToggle} />
    </div>
  );
}
