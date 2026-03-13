/**
 * Port Interface — IApiPort
 * Defines the contract for all backend communication.
 * The domain/components depend on this interface, not the concrete adapter.
 */

import type {
    IEntitySummary,
    IEntity,
    IInterventionPayload,
    IInterventionResponse,
    ISimulationStatus,
    IWSMessage,
} from '../domain/types';

export interface IApiPort {
    /** Fetch summary of all entities (stats + last thought) */
    getEntities(): Promise<IEntitySummary[]>;

    /** Fetch full entity data including complete thought history */
    getEntity(id: string): Promise<IEntity>;

    /** Stage a divine intervention for an entity */
    postIntervention(payload: IInterventionPayload): Promise<IInterventionResponse>;

    /** Start or stop the simulation ticker */
    toggleSimulation(running: boolean): Promise<ISimulationStatus>;

    /** Get current simulation running status */
    getSimulationStatus(): Promise<ISimulationStatus>;

    /**
     * Subscribe to real-time simulation updates via WebSocket.
     * Returns a cleanup function to disconnect.
     */
    subscribeToUpdates(callback: (msg: IWSMessage) => void): () => void;
}
