from pydantic import BaseModel, Field

class CommentBase(BaseModel):
    ChangeNumber: int = Field(..., ge=0)
    UserName: str = Field(..., min_length=1, max_length=128)
    Text: str = Field(..., max_length=1024)
    Project: str = Field(..., min_length=1, max_length=128)

class CommentRequest(CommentBase):
    pass

class CommentResponse(CommentBase):
    Id: int
