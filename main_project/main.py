from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

from models import LogEntry, AlertStatusUpdate
from database import init_db, get_db
from engine import process_log

app = FastAPI(title="Mini SIEM API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

os.makedirs(os.path.join(os.path.dirname(__file__), 'static'), exist_ok=True)
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), 'static')), name="static")

@app.post("/api/logs")
def ingest_log(log: LogEntry):
    process_log(log)
    return {"status": "success"}

@app.get("/api/logs")
def get_logs(host: str = None, event_type: str = None, limit: int = 50):
    with get_db() as conn:
        query = 'SELECT * FROM logs WHERE 1=1'
        params = []
        if host:
            query += ' AND host = ?'
            params.append(host)
        if event_type:
            query += ' AND event_type = ?'
            params.append(event_type)
        query += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)
        
        cursor = conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

@app.get("/api/alerts")
def get_alerts(limit: int = 50):
    with get_db() as conn:
        cursor = conn.execute('SELECT * FROM alerts ORDER BY timestamp DESC LIMIT ?', (limit,))
        return [dict(row) for row in cursor.fetchall()]

@app.post("/api/alerts/{alert_id}/status")
def update_alert_status(alert_id: int, status_update: AlertStatusUpdate):
    with get_db() as conn:
        cursor = conn.execute('UPDATE alerts SET status = ? WHERE id = ?', (status_update.status, alert_id))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Alert not found")
        conn.commit()
        return {"status": "success", "new_status": status_update.status}

@app.delete("/api/database")
def clear_database():
    with get_db() as conn:
        conn.execute('DELETE FROM logs')
        conn.execute('DELETE FROM alerts')
        conn.commit()
    return {"status": "success", "message": "Database cleared"}

@app.get("/", response_class=HTMLResponse)
def read_root():
    index_path = os.path.join(os.path.dirname(__file__), 'static', 'index.html')
    if os.path.exists(index_path):
        with open(index_path, 'r') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Dashboard not found</h1><p>Ensure static/index.html is created.</p>")
