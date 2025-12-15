from pydantic import BaseModel, Field

class BuildBase(BaseModel):
    ChangeNumber: int = Field(..., ge=0)
    BuildType: str = Field(..., min_length=1, max_length=32)
    Result: str = Field(..., min_length=1, max_length=10)
    Url: str = Field(..., min_length=1, max_length=512)
    Project: str = Field(..., min_length=1, max_length=512)
    ArchivePath: str | None = Field(None, min_length=1, max_length=512)

class BuildRequest(BuildBase):
    pass

class BuildResponse(BuildBase):
    Id: int
 