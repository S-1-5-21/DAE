# Mini SIEM System Walkthrough

I have successfully built and verified the local Mini SIEM system. The solution is fully functional, lightweight, and demonstrates log collection, real-time alerting, and an interactive frontend dashboard.

## What Was Accomplished
1. **FastAPI Backend ([main.py](file:///Users/hs13/Documents/DAE/main_project/main.py), [models.py](file:///Users/hs13/Documents/DAE/main_project/models.py), [database.py](file:///Users/hs13/Documents/DAE/main_project/database.py))** 
   - A robust HTTP server that validates incoming logs using Pydantic.
   - Saves logs to a local SQLite database ([siem.db](file:///Users/hs13/Documents/DAE/main_project/siem.db)).
   - Serves APIs for tracking logs and fetching active alerts.
2. **Detection Engine ([engine.py](file:///Users/hs13/Documents/DAE/main_project/engine.py), [rules.json](file:///Users/hs13/Documents/DAE/main_project/rules.json))**
   - Implemented JSON-based rules for flexibility.
   - Dynamically evaluates logs against thresholds (e.g., >10 errors within 60s) to generate stateful alerts.
3. **Event Simulator ([simulator.py](file:///Users/hs13/Documents/DAE/main_project/simulator.py))**
   - Automatically generates normal traffic and injects periodic "Attack" scenarios (Brute Force or Error Spikes) to trigger the engine rules.
4. **Interactive Dashboard (`static/`)**
   - A premium, dark-themed responsive UI.
   - Built with live-updating logs, an interactive Chart.js line graph, and action buttons to update alert statuses without reloading the page.

## Validation Results
- Verified that backend APIs rapidly ingest data without locking.
- Background simulator is smoothly generating traffic and attacks.
- Active alerts successfully propagated to the database when rules are breached.
- The browser subagent confirmed the UI renders beautifully and allows alerts to be marked as "Benign" successfully.

### Demo Recording
Here is a recording showing the UI live-updating with new logs and alerts, along with an interactive status update:

![Mini SIEM Demo](file:///Users/hs13/.gemini/antigravity/brain/9ca4fed2-0899-433f-8633-0abe52a48532/mini_siem_demo_1773871933530.webp)

## How to Run It
Currently, the backend and simulator are already running in the background for you! Just open your browser to [http://localhost:8000](http://localhost:8000) to check it out.

If you want to restart it yourself later, open a terminal in `/Users/hs13/Documents/DAE/main_project` and run:
1. `source venv/bin/activate && uvicorn main:app --port 8000`
2. `source venv/bin/activate && python simulator.py`
