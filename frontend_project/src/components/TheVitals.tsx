/**
 * Component — The Vitals (Column 3)
 * Real-time stat dashboard for all 5 entities.
 * Animated stat bars update on each WS tick.
 */

import type { IEntitySummary } from '../domain/types';

interface TheVitalsProps {
    entities: IEntitySummary[];
}

interface StatBarProps {
    label: string;
    value: number;
    colorClass: string;
}

function StatBar({ label, value, colorClass }: StatBarProps) {
    return (
        <div className="stat-row">
            <span className="stat-label">{label}</span>
            <div className="stat-bar-track">
                <div
                    className={`stat-bar-fill ${colorClass}`}
                    style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
                />
            </div>
            <span className="stat-value">{value.toFixed(0)}</span>
        </div>
    );
}

function VitalCard({ entity }: { entity: IEntitySummary }) {
    return (
        <div className="vital-card">
            <div className="vital-card-name">
                {entity.name}
                {entity.has_pending_intervention && (
                    <span
                        style={{
                            marginLeft: 8,
                            fontSize: 8,
                            color: 'var(--stat-faith)',
                            letterSpacing: '0.1em',
                        }}
                    >
                        [INTERVENTION PENDING]
                    </span>
                )}
            </div>
            <div className="vital-stats">
                <StatBar label="HAPP" value={entity.stats.happiness} colorClass="happiness" />
                <StatBar label="RANC" value={entity.stats.rancor} colorClass="rancor" />
                <StatBar label="FREE" value={entity.stats.freedom} colorClass="freedom" />
                <StatBar label="FAITH" value={entity.stats.faith} colorClass="faith" />
            </div>
            {entity.last_thought && (
                <div
                    style={{
                        marginTop: 10,
                        paddingTop: 8,
                        borderTop: '1px solid var(--border-dim)',
                        fontFamily: 'var(--font-mono)',
                        fontSize: 9,
                        color: 'var(--text-muted)',
                        lineHeight: 1.5,
                        overflow: 'hidden',
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                    }}
                >
                    &gt; {entity.last_thought.reflection.slice(0, 90)}
                    {entity.last_thought.reflection.length > 90 ? '...' : ''}
                </div>
            )}
        </div>
    );
}

export function TheVitals({ entities }: TheVitalsProps) {
    return (
        <div className="column" style={{ background: 'var(--bg-void)' }}>
            {/* Header */}
            <div className="col-header" style={{ background: 'var(--bg-surface)' }}>
                <div className="col-header-dot" />
                <span className="col-header-label">The Vitals</span>
                <span
                    style={{
                        marginLeft: 'auto',
                        fontFamily: 'var(--font-mono)',
                        fontSize: 9,
                        color: 'var(--text-muted)',
                    }}
                >
                    {entities.length} UNITS
                </span>
            </div>

            {/* Stat cards */}
            <div className="vitals-body">
                {entities.length === 0 && (
                    <div className="empty-state">AWAITING ENTITY DATA...</div>
                )}
                {entities.map((entity) => (
                    <VitalCard key={entity.id} entity={entity} />
                ))}

                {/* Spacer so toggle doesn't overlap last card */}
                <div style={{ height: 60 }} />
            </div>
        </div>
    );
}
