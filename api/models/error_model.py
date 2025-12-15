from datetime import datetime

from pydantic import BaseModel, Field

class ErrorBase(BaseModel):
    Type: str = Field(..., min_length=1, max_length=50)
    Text: str = Field(..., min_length=1, max_length=1024)
    UserName: str = Field(..., min_length=1, max_length=128)
    Project: str = Field(..., min_length=1, max_length=128)
    Timestamp: datetime

class ErrorRequest(ErrorBase):
    pass

class ErrorResponse(ErrorBase):
    Id: int
    Version: str
    IpAddress: str
