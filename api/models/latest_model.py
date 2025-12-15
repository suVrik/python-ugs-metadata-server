from pydantic import BaseModel

class LatestResponse(BaseModel):
    LastEventId: int
    LastCommentId: int
    LastBuildId: int
