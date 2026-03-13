/**
 * Component — Simulation Toggle
 * Master ON/OFF control positioned at the bottom-left.
 */

interface SimulationToggleProps {
    isRunning: boolean;
    onToggle: (nextState: boolean) => void;
}

export function SimulationToggle({ isRunning, onToggle }: SimulationToggleProps) {
    return (
        <button
            id="sim-toggle-btn"
            className={`sim-toggle${isRunning ? ' running' : ''}`}
            onClick={() => onToggle(!isRunning)}
            title={isRunning ? 'Pause the simulation' : 'Start the simulation'}
        >
            <div className="sim-toggle-pip" />
            {isRunning ? (
                <>SYSTEM: ONLINE — PAUSE</>
            ) : (
                <>SYSTEM: OFFLINE — ENGAGE</>
            )}
        </button>
    );
}
