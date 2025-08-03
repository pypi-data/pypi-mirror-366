# models.py

from dataclasses import dataclass, field
from datetime import date, time, datetime
from typing import Optional

@dataclass
class TodoItem:
    title: str
    date_att: Optional[date] = None
    time_att: Optional[time] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self):
        return {
            "title": self.title,
            "date": self.date_att.isoformat() if self.date_att else None,
            "time": self.time_att.isoformat() if self.time_att else None,
            "created_at": self.created_at.isoformat()
        }
        
    @staticmethod
    def from_dict(d):
        return TodoItem(
            title=d["title"],
            date_att=date.fromisoformat(d["date"]) if d["date"] else None,
            time_att=time.fromisoformat(d["time"]) if d["time"] else None,
            created_at=datetime.fromisoformat(d["created_at"])
        )