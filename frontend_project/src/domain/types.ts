/**
 * Domain Types — All TypeScript interfaces for the Synthetic Zealot simulation.
 * These are the only shape definitions used throughout the frontend.
 * No adapter-specific types here — purely domain contracts.
 */

//stats of characters
export interface IStats {
    happiness: number;  // 0–100
    rancor: number;     // 0–100
    freedom: number;    // 0–100
    faith: number;      // 0–100
}

export interface IThoughtEntry {
    id: string;
    timestamp: string;  // ISO 8601
    reflection: string;
    stats_snapshot: IStats;
    triggered_by_intervention: boolean;
}

export interface IEntity {
    id: string;
    name: string;
    base_personality: string;
    stats: IStats;
    thought_history: IThoughtEntry[];
    has_pending_intervention?: boolean;
}

/** Lightweight snapshot used for the real-time vitals panel */
export interface IEntitySummary {
    id: string;
    name: string;
    stats: IStats;
    last_thought: IThoughtEntry | null;
    has_pending_intervention: boolean;
}

export interface ISimulationStatus {
    running: boolean;
}

export interface IInterventionPayload {
    entity_id: string;
    text: string;
}

export interface IInterventionResponse {
    status: string;
    entity_id: string;
    message: string;
}

/** WebSocket message types sent from the server */
export type WSMessageType = 'initial_state' | 'simulation_tick';

export interface IWSMessage {
    type: WSMessageType;
    entities: IEntitySummary[];
    simulation_running?: boolean;
}
//very important