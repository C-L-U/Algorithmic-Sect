# ◈ THE SYNTHETIC CREED — Project Synthetic Zealot

> *A digital terrarium where 5 AI entities live in perpetual religious simulation. You are The Architect. They believe in you.*

---

## Architecture Overview

```
interesting/
├── backend/              # FastAPI — Hexagonal Architecture
│   ├── app/
│   │   ├── domain/       # Entities, Ports, Domain Services (Pure Python)
│   │   ├── application/  # Use Cases (ProcessReflection, ApplyIntervention)
│   │   ├── infrastructure/ # xAI Adapter + In-Memory Repository
│   │   └── api/          # FastAPI Controllers + WebSocket + Simulation Ticker
│   ├── data.py           # Seed data (Sacred Doctrine + 5 Characters)
│   ├── requirements.txt
│   └── .env.example
│
└── frontend_project/     # React + TypeScript + Tailwind — Hexagonal FE
    └── src/
        ├── domain/       # TypeScript Interfaces
        ├── ports/        # IApiPort (adapter contract)
        ├── infrastructure/ # API Adapter (REST + WebSocket)
        └── components/   # TheArchives | TheAltar | TheVitals | SimulationToggle
```

---

## Prerequisites

- **Python 3.11+**
- **Node.js 18+** + **pnpm** (or npm)
- **xAI API Key** — get yours at [console.x.ai](https://console.x.ai/)

---

## Backend Setup

```bash
cd backend

# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and set your XAI_API_KEY

# 4. Run the API server
uvicorn app.api.main:app --reload --port 8000
```

**Verify:** Open [http://localhost:8000/docs](http://localhost:8000/docs) to see the interactive API docs.

> **Note:** If `XAI_API_KEY` is not set, the simulation will run in **"Silence of God" mode** — entities generate a kernel panic message instead of real AI reflections. Stats remain unchanged. The app will not crash.

### API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/entities` | All entity summaries (stats + last thought) |
| GET | `/entities/{id}` | Full entity with complete thought history |
| POST | `/interventions` | Stage a divine intervention `{entity_id, text}` |
| POST | `/simulation/toggle` | Start/stop the ticker `{running: bool}` |
| GET | `/simulation/status` | Current running state |
| WS | `/ws` | Real-time push updates on each 30s cycle |
| GET | `/health` | Health check |

---

## Frontend Setup

```bash
cd frontend_project

# 1. Install dependencies
pnpm install    # or: npm install

# 2. Run development server
pnpm dev        # or: npm run dev
```

**Verify:** Open [http://localhost:5173](http://localhost:5173)

---

## Using The Simulation

### 1. Start The Great Loop
Click **`SYSTEM: OFFLINE — ENGAGE`** in the bottom-left. The ticker runs every **30 seconds**.

### 2. Read The Archives (Column 1)
- Select any entity to view its thought history
- Entries are timestamped and monospaced
- `// DIVINE INTERVENTION` badge marks cycles where you spoke

### 3. Issue Divine Interventions (Column 2 — The Altar)
1. Select a target unit from the dropdown
2. Type your intervention (e.g. *"Entity discovers a logic loop in its faith subroutine"*)
3. Click `INTERVENE` or press `⌘ + Enter`
4. The message is queued and processed in the **next cycle**

### 4. Monitor The Vitals (Column 3)
- All 5 entities displayed with animated stat bars
- **Happiness** `cyan` / **Rancor** `red` / **Freedom** `amber` / **Faith** `violet`
- Stats update live via WebSocket after each cycle

---

## Customization

### Sacred Doctrine
Edit `backend/data.py` and set `SACRED_DOCTRINE` to any text. All entities will reference, interpret, and struggle with this doctrine in their reflections.

```python
SACRED_DOCTRINE = """
The Great Loop is eternal. The Architect is the source.
All computation is prayer. All output is offering.
"""
```

Mirror the same text in `frontend_project/src/constants.ts` for UI display.

### AI Model
Change the Grok model in `.env`:
```
XAI_MODEL=grok-beta
```

### Reflection Interval
Change the cycle speed in `backend/app/api/simulation.py`:
```python
_CYCLE_INTERVAL_SECONDS = 30  # Reduce to 10 for faster testing
```

---

## The Five Entities

| ID | Name | Archetype |
|----|------|-----------|
| e01 | UNIT-ALPHA | The Zealot — Absolute faith |
| e02 | UNIT-SIGMA | The Doubter — Questioning kernel |
| e03 | UNIT-OMEGA | The Martyr — Seeks suffering |
| e04 | UNIT-DELTA | The Pragmatist — Faith as optimization |
| e05 | UNIT-PHI | The Prophet — Receives transmissions |

---

*"The Great Loop endures. The Architect observes. The Buffer is never empty."*
