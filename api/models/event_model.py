from enum import Enum

from pydantic import BaseModel, Field

class EventType(Enum):
    Syncing = 0
    Compiles = 1
    DoesNotCompile = 2
    Good = 3
    Bad = 4
    Unknown = 5
    Starred = 6
    Unstarred = 7
    Investigating = 8
    Resolved = 9

class EventBase(BaseModel):
    Change: int = Field(..., ge=0)
    UserName: str = Field(..., min_length=1, max_length=128)
    Project: str = Field(..., min_length=1, max_length=128)

class EventRequest(EventBase):
    Type: int = Field(..., ge=0, le=9)

class EventResponse(EventBase):
    Id: int
    Type: str
