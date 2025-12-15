from pydantic import BaseModel, Field

class EventBase(BaseModel):
    Change: int = Field(..., ge=0)
    UserName: str = Field(..., min_length=1, max_length=128)
    Type: str = Field(..., min_length=1, max_length=32)
    Project: str = Field(..., min_length=1, max_length=128)

class EventRequest(EventBase):
    pass

class EventResponse(EventBase):
    Id: int
