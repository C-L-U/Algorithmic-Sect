/**
 * Component — The Archives (Column 1)
 * Displays the entity selector list and a timestamped thought history log.
 * Full monospace "System Log" aesthetic.
 */

import { useState, useEffect, useRef } from 'react';
import type { IEntitySummary, IEntity } from '../domain/types';
import type { IApiPort } from '../ports/api_port';

interface TheArchivesProps {
    entities: IEntitySummary[];
    api: IApiPort;
}

function formatTimestamp(iso: string): string {
    try {
        const d = new Date(iso);
        const hh = String(d.getHours()).padStart(2, '0');
        const mm = String(d.getMinutes()).padStart(2, '0');
        const ss = String(d.getSeconds()).padStart(2, '0');
        return `${hh}:${mm}:${ss}`;
    } catch {
        return iso.slice(11, 19);
    }
}

export function TheArchives({ entities, api }: TheArchivesProps) {
    const [selectedId, setSelectedId] = useState<string | null>(null);
    const [fullEntity, setFullEntity] = useState<IEntity | null>(null);
    const [loading, setLoading] = useState(false);
    const logEndRef = useRef<HTMLDivElement>(null);

    // Auto-select first entity once entities data arrives (they load async)
    useEffect(() => {
        if (!selectedId && entities.length > 0) {
            setSelectedId(entities[0].id);
        }
    }, [entities, selectedId]);

    // Fetch full entity (with thought_history) when selection changes
    useEffect(() => {
        if (!selectedId) return;
        setLoading(true);
        api
            .getEntity(selectedId)
            .then(setFullEntity)
            .catch(() => setFullEntity(null))
            .finally(() => setLoading(false));
    }, [selectedId, api]);

    // Refresh thought history when entities update (after WS tick)
    useEffect(() => {
        if (!selectedId) return;
        api
            .getEntity(selectedId)
            .then(setFullEntity)
            .catch(() => { });
    }, [entities, selectedId, api]);

    // Auto-scroll log to bottom
    useEffect(() => {
        logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [fullEntity?.thought_history?.length]);

    const selectedSummary = entities.find((e) => e.id === selectedId);

    return (
        <div className="column" style={{ background: 'var(--bg-surface)' }}>
            {/* Header */}
            <div className="col-header">
                <div className="col-header-dot" />
                <span className="col-header-label">The Archives</span>
            </div>

            {/* Entity List */}
            <div className="entity-list">
                {entities.map((entity) => (
                    <div
                        key={entity.id}
                        className={`entity-item ${selectedId === entity.id ? 'selected' : ''}`}
                        onClick={() => setSelectedId(entity.id)}
                    >
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                            <span className="entity-name">{entity.name}</span>
                            {entity.has_pending_intervention && (
                                <span className="pending-badge">intervention pending</span>
                            )}
                        </div>
                        <span className="entity-faith">
                            ψ {entity.stats.faith.toFixed(0)}
                        </span>
                    </div>
                ))}
            </div>

            {/* Selected entity details */}
            {selectedSummary && (
                <div
                    style={{
                        padding: '10px 16px',
                        borderBottom: '1px solid var(--border-dim)',
                        flexShrink: 0,
                        background: 'var(--bg-elevated)',
                    }}
                >
                    <div
                        style={{
                            fontFamily: 'var(--font-mono)',
                            fontSize: 9,
                            color: 'var(--text-muted)',
                            lineHeight: 1.6,
                        }}
                    >
                        H:{selectedSummary.stats.happiness.toFixed(0)} &nbsp;
                        R:{selectedSummary.stats.rancor.toFixed(0)} &nbsp;
                        F:{selectedSummary.stats.freedom.toFixed(0)} &nbsp;
                        ψ:{selectedSummary.stats.faith.toFixed(0)}
                    </div>
                </div>
            )}

            {/* Thought Log */}
            <div className="thought-log">
                {loading && !fullEntity && (
                    <div className="empty-state">LOADING THOUGHT BUFFER...</div>
                )}

                {!loading && fullEntity && fullEntity.thought_history.length === 0 && (
                    <div className="empty-state">
                        NO REFLECTION CYCLES RECORDED.
                        <br />
                        START SIMULATION TO BEGIN.
                    </div>
                )}

                {fullEntity?.thought_history
                    .slice()
                    .reverse()
                    .map((entry) => (
                        <div
                            key={entry.id}
                            className={`thought-entry${entry.triggered_by_intervention ? ' intervention' : ''}`}
                        >
                            <div className="thought-timestamp">
                                [{formatTimestamp(entry.timestamp)}] &gt; REFLECTION CYCLE
                                {entry.triggered_by_intervention && (
                                    <span
                                        style={{ color: 'var(--stat-faith)', marginLeft: 6 }}
                                    >
                    // DIVINE INTERVENTION
                                    </span>
                                )}
                            </div>
                            <div className="thought-text">{entry.reflection}</div>
                            <div
                                style={{
                                    marginTop: 5,
                                    fontFamily: 'var(--font-mono)',
                                    fontSize: 9,
                                    color: 'var(--text-muted)',
                                }}
                            >
                                H:{entry.stats_snapshot.happiness.toFixed(0)} R:
                                {entry.stats_snapshot.rancor.toFixed(0)} F:
                                {entry.stats_snapshot.freedom.toFixed(0)} ψ:
                                {entry.stats_snapshot.faith.toFixed(0)}
                            </div>
                        </div>
                    ))}
                <div ref={logEndRef} />
            </div>
        </div>
    );
}
