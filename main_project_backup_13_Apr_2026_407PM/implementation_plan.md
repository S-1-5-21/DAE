# Mini SIEM System Implementation

This document outlines the architecture for a lightweight, local Mini SIEM system, combining speed of implementation with a realistic feature set.

## Proposed Changes

### Backend Infrastructure (FastAPI)
We will use **FastAPI** for the backend server to leverage its modern features, automatic validation, and speed. We will use SQLite for local data storage.

#### [NEW] `/Users/hs13/Documents/DAE/main_project/models.py`
Defines Pydantic models for incoming logs and output alerts, ensuring data validation.

#### [NEW] `/Users/hs13/Documents/DAE/main_project/database.py`
Sets up the SQLite database (`siem.db`) with `logs` and `alerts` tables.

#### [NEW] `/Users/hs13/Documents/DAE/main_project/rules.json`
A JSON file defining the detection rules (e.g., threshold-based rules for failed logins).

#### [NEW] `/Users/hs13/Documents/DAE/main_project/engine.py`
The core SIEM engine. It will:
- Parse `rules.json`.
- Process incoming logs against the rules.
- Generate and store alerts in the database.

#### [NEW] `/Users/hs13/Documents/DAE/main_project/main.py`
The FastAPI application exposing REST endpoints:
- `POST /api/logs` - Ingest logs with validation.
- `GET /api/logs` - Retrieve recent logs (with filtering by host/event type).
- `GET /api/alerts` - Retrieve alerts.
- `POST /api/alerts/{id}/status` - Update alert status (e.g., 'New', 'Benign').

### Event Simulator
#### [NEW] `/Users/hs13/Documents/DAE/main_project/simulator.py`
A Python script that simulates both normal traffic and suspicious activity (e.g., brute-force, error spikes) and sends them directly to the `POST /api/logs` endpoint. This is a single script for simplicity.

### Frontend Dashboard
#### [NEW] `/Users/hs13/Documents/DAE/main_project/static/index.html`
A modern HTML layout displaying a live feed of logs, active alerts, and visual analytics.

#### [NEW] `/Users/hs13/Documents/DAE/main_project/static/styles.css`
A premium, dark-themed dashboard styling system.

#### [NEW] `/Users/hs13/Documents/DAE/main_project/static/main.js`
JavaScript to:
- Fetch logs and alerts via API.
- Render charts using Chart.js to visualize events over time.
- Handle filtering and user interactions for marking alerts as benign.

## Verification Plan

### Automated/Manual Testing
1. Install FastAPI and Uvicorn (`pip install fastapi uvicorn`).
2. Start the backend with `uvicorn main:app --reload`.
3. Open the UI at `http://localhost:8000` to verify it loads.
4. Run `python simulator.py` in a separate terminal.
5. Watch the dashboard to verify real-time ingestion of logs, chart updates, and creation of alerts.
6. Interact with the alerts and filters on the UI to ensure functionality.
