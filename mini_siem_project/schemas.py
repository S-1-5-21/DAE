# schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class LogEventCreate(BaseModel):
    timestamp: Optional[datetime] = None
    host: Optional[str] = None
    source: Optional[str] = None
    event_type: Optional[str] = None
    message: Optional[str] = None
    raw: Optional[str] = None