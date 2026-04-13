from pydantic import BaseModel

class LogEntry(BaseModel):
    timestamp: str
    host: str
    event_type: str
    raw_message: str

class AlertStatusUpdate(BaseModel):
    status: str
