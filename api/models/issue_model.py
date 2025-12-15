from datetime import datetime

from pydantic import BaseModel, Field

class IssueWatcherRequest(BaseModel):
    UserName: str = Field(..., min_length=1, max_length=128)

class IssueBuildBase(BaseModel):
    Stream: str = Field(..., min_length=1, max_length=128)
    Change: int = Field(..., ge=0)
    JobName: str = Field(..., min_length=1, max_length=1024)
    JobUrl: str = Field(..., min_length=1, max_length=1024)
    JobStepName: str = Field(..., min_length=1, max_length=1024)
    JobStepUrl: str = Field(..., min_length=1, max_length=1024)
    ErrorUrl: str = Field(..., min_length=1, max_length=1024)
    Outcome: int

class IssueBuildRequest(IssueBuildBase):
    pass

class IssueBuildResponse(IssueBuildBase):
    Id: int

class IssueBuildCreateResponse(BaseModel):
    Id: int

class IssueBuildUpdateRequest(BaseModel):
    Outcome: int

class IssueDiagnosticBase(BaseModel):
    BuildId: int | None = Field(None, ge=0)
    Message: str = Field(..., min_length=1, max_length=1024)
    Url: str | None = Field(None, min_length=1, max_length=1024)

class IssueDiagnosticRequest(IssueDiagnosticBase):
    pass

class IssueDiagnosticResponse(IssueDiagnosticBase):
    pass

class IssueBase(BaseModel):
    CreatedAt: datetime
    RetrievedAt: datetime
    Project: str = Field(..., min_length=1, max_length=64)
    Summary: str = Field(..., min_length=1, max_length=256)
    Owner: str = Field(..., min_length=1, max_length=128)
    NominatedBy: str = Field(..., min_length=1, max_length=128)
    AcknowledgedAt: datetime | None = None
    FixChange: int = Field(..., ge=0)
    ResolvedAt: datetime | None = None
    bNotify: bool

class IssueRequest(IssueBase):
    pass

class IssueResponse(IssueBase):
    Id: int

class IssueCreateResponse(BaseModel):
    Id: int

class IssueUpdateRequest(BaseModel):
    Summary: str | None = Field(None, min_length=1, max_length=256)
    Owner: str | None = Field(None, min_length=1, max_length=128)
    NominatedBy: str | None = Field(None, min_length=1, max_length=128)
    Acknowledged: bool | None = None
    FixChange: int | None = Field(None, ge=0)
    Resolved: bool | None = None
