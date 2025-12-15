from enum import Enum

from pydantic import BaseModel, Field

class BuildResult(Enum):
    Starting = 0
    Failure = 1
    Warning = 2
    Success = 3
    Skipped = 4

class BuildBase(BaseModel):
    ChangeNumber: int = Field(..., ge=0)
    BuildType: str = Field(..., min_length=1, max_length=32)
    Url: str = Field(..., min_length=1, max_length=512)
    Project: str = Field(..., min_length=1, max_length=512)
    ArchivePath: str | None = Field(None, min_length=1, max_length=512)

class BuildRequest(BuildBase):
    Result: int = Field(..., ge=0, le=4)

class BuildResponse(BuildBase):
    Id: int
    Result: str
 