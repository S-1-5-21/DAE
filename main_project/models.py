from pydantic import BaseModel
from typing import Optional

class LogEntry(BaseModel):
    timestamp: str
    host: str
    event_type: str
    raw_message: str
    source_ip: Optional[str] = None
    dest_ip: Optional[str] = None

class AlertStatusUpdate(BaseModel):
    status: str
