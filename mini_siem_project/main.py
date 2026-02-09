# main.py
from fastapi import FastAPI, Depends, HTTPException
from typing import List
from sqlmodel import Session, select
from database import create_db_and_tables, get_session
from models import LogEvent
from schemas import LogEventCreate
from datetime import datetime

app = FastAPI(title="mini-siem - collector API", version="0.1.0")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.post("/logs", response_model=dict)
def ingest_log(payload: LogEventCreate, session: Session = Depends(get_session)):
    # populate timestamp if none provided
    ts = payload.timestamp or datetime.utcnow()
    log = LogEvent(
        timestamp=ts,
        host=payload.host or "unknown",
        source=payload.source,
        event_type=payload.event_type,
        message=payload.message,
        raw=payload.raw,
    )
    session.add(log)
    session.commit()
    session.refresh(log)
    return {"status": "ok", "id": log.id}

@app.get("/logs", response_model=List[dict])
def list_logs(limit: int = 50, session: Session = Depends(get_session)):
    statement = select(LogEvent).order_by(LogEvent.timestamp.desc()).limit(limit)
    results = session.exec(statement).all()
    # convert to simple dicts
    out = []
    for r in results:
        out.append({
            "id": r.id,
            "timestamp": r.timestamp.isoformat(),
            "host": r.host,
            "source": r.source,
            "event_type": r.event_type,
            "message": r.message,
            "raw": r.raw,
        })
    return out