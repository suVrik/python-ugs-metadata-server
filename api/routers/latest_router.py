import asyncio

from fastapi import APIRouter, Query

from database_utils import DatabaseUtils
from common_utils import CommonUtils
from models.latest_model import LatestResponse

router = APIRouter()

@router.get("", response_model=LatestResponse)
async def get_latest_ids(project: str = Query(min_length=1, max_length=128)):
    query_events = """
        SELECT
            MAX(UserVotes.Id) AS Id,
            UserVotes.Changelist
        FROM ugs_db.UserVotes
        INNER JOIN ugs_db.Projects
            ON Projects.Id = UserVotes.ProjectId
        WHERE Projects.Name LIKE %s
        GROUP BY UserVotes.Changelist
        ORDER BY UserVotes.Changelist DESC
        LIMIT 1 OFFSET 99
    """

    query_comments = """
        SELECT
            MAX(Comments.Id) AS Id,
            Comments.ChangeNumber
        FROM ugs_db.Comments
        INNER JOIN ugs_db.Projects
            ON Projects.Id = Comments.ProjectId
        WHERE Projects.Name LIKE %s
        GROUP BY Comments.ChangeNumber
        ORDER BY Comments.ChangeNumber DESC
        LIMIT 1 OFFSET 99
    """

    query_badges = """
        SELECT
            MAX(Badges.Id) AS Id,
            Badges.ChangeNumber
        FROM ugs_db.Badges
        INNER JOIN ugs_db.Projects
            ON Projects.Id = Badges.ProjectId
        WHERE Projects.Name LIKE %s
        GROUP BY Badges.ChangeNumber
        ORDER BY Badges.ChangeNumber DESC
        LIMIT 1 OFFSET 99
    """

    project_stream_like = f'%{CommonUtils.get_project_stream(project)}%'

    last_event, last_comment, last_badge = await asyncio.gather(
        DatabaseUtils.fetch_object(query_events, (project_stream_like,)),
        DatabaseUtils.fetch_object(query_comments, (project_stream_like,)),
        DatabaseUtils.fetch_object(query_badges, (project_stream_like,))
    )

    last_event_id = last_event[0] if last_event is not None else 0
    last_comment_id = last_comment[0] if last_comment is not None else 0
    last_badge_id = last_badge[0] if last_badge is not None else 0

    return LatestResponse(
        LastEventId=last_event_id,
        LastCommentId=last_comment_id,
        LastBuildId=last_badge_id
    )
