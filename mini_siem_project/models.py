# models.py
from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class LogEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    host: Optional[str] = Field(index=True, default="unknown")
    source: Optional[str] = Field(default=None)      # e.g., "sshd", "syslog", "app"
    event_type: Optional[str] = Field(default=None)  # e.g., "login_failed", "file_change"
    message: Optional[str] = Field(default=None)
    raw: Optional[str] = Field(default=None)