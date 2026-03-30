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
   - A premium, dark-themed responsive UI (now with 5 interchangeable themes via the top nav).
   - Built with live-updating logs, an interactive Chart.js line graph, and action buttons to update alert statuses without reloading the page.
   - **Investigate Modal**: Pop up detailed views of specific alerts without dashboard refresh conflicts.
   - **Database Clearing**: A one-click button to reset the database and logs.

## Recent Enhancements & Bug Fixes
- **Investigate Alert Form**: Instead of fighting the dashboard's 1-second background refresh cycle, clicking "Investigate" now successfully pulls logs into a dedicated modal popup overlay that persists cleanly while you review it.
- **Multiple Color Themes**: The "Toggle Theme" button now smoothly cycles through 5 distinct themes: `Theme: dark`, `Theme: light`, `Theme: dracula`, `Theme: cyberpunk`, and `Theme: solarized`. Chart.js graph grids automatically adapt to the specific theme's brightness.
- **Clear DB Refinements**: The underlying `DELETE` API has been visually connected to a success confirmation alert in the frontend so that you explicitly know the database rows were dropped before the simulator immediately repopulates them.

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
2. `source venv/bin/activate && python3 simulator.py`

## How to Stop It
If you are running the backend and simulator in a terminal window, simply press **`Ctrl+C`** in that terminal to stop the process.

To explicitly stop any instances running in the background, open a terminal and run:
```bash
pkill -f uvicorn
pkill -f "simulator.py"
```
