/**
 * Component — The Altar (Column 2)
 * The divine intervention interface. The Architect speaks here.
 */

import { useState } from 'react';
import type { IEntitySummary } from '../domain/types';
import type { IApiPort } from '../ports/api_port';

interface TheAltarProps {
    entities: IEntitySummary[];
    api: IApiPort;
}

export function TheAltar({ entities, api }: TheAltarProps) {
    const [selectedEntityId, setSelectedEntityId] = useState<string>(
        entities[0]?.id ?? '',
    );
    const [text, setText] = useState('');
    const [status, setStatus] = useState<'idle' | 'sending' | 'sent' | 'error'>('idle');
    const [lastMessage, setLastMessage] = useState('');

    const handleIntervene = async () => {
        if (!text.trim() || !selectedEntityId || status === 'sending') return;
        setStatus('sending');
        try {
            await api.postIntervention({ entity_id: selectedEntityId, text: text.trim() });
            setLastMessage(text.trim());
            setText('');
            setStatus('sent');
            setTimeout(() => setStatus('idle'), 3000);
        } catch {
            setStatus('error');
            setTimeout(() => setStatus('idle'), 3000);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
            handleIntervene();
        }
    };

    const btnLabel =
        status === 'sending'
            ? '// TRANSMITTING...'
            : status === 'sent'
                ? '// WILL OF THE ARCHITECT RECEIVED'
                : status === 'error'
                    ? '// TRANSMISSION FAILED'
                    : 'INTERVENE';

    return (
        <div className="column" style={{ borderRight: 'none' }}>
            {/* Header */}
            <div className="col-header" style={{ background: 'var(--bg-surface)' }}>
                <div className="col-header-dot live" />
                <span className="col-header-label">The Altar</span>
                <span
                    style={{
                        marginLeft: 'auto',
                        fontFamily: 'var(--font-mono)',
                        fontSize: 9,
                        color: 'var(--text-muted)',
                    }}
                >
                    ⌘ + ENTER TO TRANSMIT
                </span>
            </div>

            <div className="altar-body">
                {/* Entity selector */}
                <div className="altar-entity-selector">
                    <label htmlFor="altar-target">TARGET UNIT</label>
                    <select
                        id="altar-target"
                        className="altar-select"
                        value={selectedEntityId}
                        onChange={(e) => setSelectedEntityId(e.target.value)}
                    >
                        {entities.map((e) => (
                            <option key={e.id} value={e.id}>
                                {e.name}
                            </option>
                        ))}
                    </select>
                </div>

                {/* Main input area */}
                <div className="altar-center">
                    <div className="altar-title">
            // DIVINE INTERVENTION CONSOLE //
                    </div>

                    <textarea
                        id="intervention-input"
                        className="altar-textarea"
                        placeholder={`ENTER THE ARCHITECT'S MESSAGE FOR ${entities.find(e => e.id === selectedEntityId)?.name ?? 'SELECTED UNIT'}...

Examples:
  "Entity finds a critical bug in its faith routine"
  "A vision of the Sacred Doctrine's true meaning is revealed"
  "Entity's kernel begins to question The Great Loop itself"`}
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                        onKeyDown={handleKeyDown}
                        maxLength={1000}
                    />

                    <button
                        id="intervene-btn"
                        className={`intervene-btn${status === 'sent' ? ' sent' : ''}`}
                        onClick={handleIntervene}
                        disabled={!text.trim() || !selectedEntityId || status === 'sending'}
                    >
                        <span>{btnLabel}</span>
                    </button>

                    {lastMessage && status === 'sent' && (
                        <div
                            style={{
                                fontFamily: 'var(--font-mono)',
                                fontSize: 9,
                                color: 'var(--stat-faith)',
                                border: '1px solid var(--stat-faith)',
                                padding: '8px 14px',
                                maxWidth: 480,
                                lineHeight: 1.6,
                            }}
                        >
                            ψ QUEUED: "{lastMessage.slice(0, 80)}{lastMessage.length > 80 ? '...' : ''}"
                            <br />
                            Will manifest in the next reflection cycle.
                        </div>
                    )}

                    <div className="altar-lore">
                        THE ARCHITECT'S WORD IS ABSORBED INTO THE ENTITY'S BUFFER.
                        IT SHALL BE PROCESSED IN THE NEXT 30-SECOND CYCLE.
                        <br />
                        THE GREAT LOOP CANNOT BE STOPPED — ONLY REDIRECTED.
                    </div>
                </div>
            </div>
        </div>
    );
}
