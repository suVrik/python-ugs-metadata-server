from datetime import datetime

from pydantic import BaseModel, Field

class TelemetryRequest(BaseModel):
    Action: str = Field(..., min_length=1, max_length=128)
    Result: str = Field(..., min_length=1, max_length=128)
    UserName: str = Field(..., min_length=1, max_length=128)
    Project: str = Field(..., min_length=1, max_length=128)
    Timestamp: datetime
    Duration: float = Field(..., ge=0)
