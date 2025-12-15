from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

class ErrorType(Enum):
    Crash = 0

class ErrorBase(BaseModel):
    Text: str = Field(..., min_length=1, max_length=1024)
    UserName: str = Field(..., min_length=1, max_length=128)
    Project: str = Field(..., min_length=1, max_length=128)
    Timestamp: datetime

class ErrorRequest(ErrorBase):
    Type: int = Field(..., ge=0, le=0)

class ErrorResponse(ErrorBase):
    Id: int
    Version: str
    IpAddress: str
    Type: str
