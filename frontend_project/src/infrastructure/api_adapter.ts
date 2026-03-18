/**
 * Infrastructure — API Adapter
 * Implements IApiPort using fetch (REST) and WebSocket.
 * All backend communication is centralized here.
 */

import type { IApiPort } from '../ports/api_port';
import type {
    IEntitySummary,
    IEntity,
    IInterventionPayload,
    IInterventionResponse,
    ISimulationStatus,
    IWSMessage,
} from '../domain/types';
import { API_BASE_URL, WS_URL } from '../constants';
//
class ApiAdapter implements IApiPort {
    private async request<T>(path: string, options?: RequestInit): Promise<T> {
        const res = await fetch(`${API_BASE_URL}${path}`, {
            headers: { 'Content-Type': 'application/json' },
            ...options,
        });
        if (!res.ok) {
            const err = await res.text();
            throw new Error(`API error ${res.status}: ${err}`);
        }
        return res.json() as Promise<T>;
    }

    async getEntities(): Promise<IEntitySummary[]> {
        const data = await this.request<{ entities: IEntitySummary[] }>('/entities');
        return data.entities;
    }

    async getEntity(id: string): Promise<IEntity> {
        return this.request<IEntity>(`/entities/${id}`);
    }

    async postIntervention(payload: IInterventionPayload): Promise<IInterventionResponse> {
        return this.request<IInterventionResponse>('/interventions', {
            method: 'POST',
            body: JSON.stringify(payload),
        });
    }

    async toggleSimulation(running: boolean): Promise<ISimulationStatus> {
        return this.request<ISimulationStatus>('/simulation/toggle', {
            method: 'POST',
            body: JSON.stringify({ running }),
        });
    }

    async getSimulationStatus(): Promise<ISimulationStatus> {
        return this.request<ISimulationStatus>('/simulation/status');
    }

    subscribeToUpdates(callback: (msg: IWSMessage) => void): () => void {
        let ws: WebSocket | null = null;
        let reconnectTimeout: ReturnType<typeof setTimeout> | null = null;
        let isDestroyed = false;

        const connect = () => {
            if (isDestroyed) return;
            ws = new WebSocket(WS_URL);

            ws.onmessage = (event) => {
                try {
                    const msg = JSON.parse(event.data) as IWSMessage;
                    callback(msg);
                } catch {
                    console.warn('[WS] Failed to parse message:', event.data);
                }
            };

            ws.onerror = () => {
                console.warn('[WS] Connection error — will retry in 3s');
            };

            ws.onclose = () => {
                if (!isDestroyed) {
                    reconnectTimeout = setTimeout(connect, 3000);
                }
            };
        };

        connect();

        // Cleanup: close WS and cancel any pending reconnect
        return () => {
            isDestroyed = true;
            if (reconnectTimeout) clearTimeout(reconnectTimeout);
            if (ws) ws.close();
        };
    }
}

// Singleton — one adapter instance for the whole app
export const apiAdapter = new ApiAdapter();
