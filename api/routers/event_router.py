from fastapi import APIRouter, Query

from database_utils import DatabaseUtils
from common_utils import CommonUtils
from models.event_model import EventRequest, EventResponse

router = APIRouter()

@router.get("", response_model=list[EventResponse])
async def get_user_votes(
    project: str = Query(min_length=1, max_length=128),
    lasteventid: int = Query(ge=0)
):
    result = []

    sql = """
        SELECT
            UserVotes.Id,
            UserVotes.Changelist,
            UserVotes.UserName,
            UserVotes.Verdict,
            UserVotes.Project
        FROM ugs_db.UserVotes
        INNER JOIN ugs_db.Projects
            ON Projects.Id = UserVotes.ProjectId
        WHERE UserVotes.Id > %s
            AND Projects.Name LIKE %s
        ORDER BY UserVotes.Id
    """

    project_stream_like = f'%{CommonUtils.get_project_stream(project)}%'

    for event in await DatabaseUtils.fetch_objects(sql, (lasteventid, project_stream_like)):
        event_id = event[0]
        changelist = event[1]
        user_name = event[2]
        verdict = event[3]
        project_name = event[4]

        result.append(EventResponse(
            Id=event_id,
            Change=changelist,
            UserName=user_name,
            Type=verdict,
            Project=project_name
        ))

    return result

@router.post("")
async def post_event(request: EventRequest):
    project_id = await CommonUtils.find_or_add_project(request.Project)

    sql = """
        INSERT INTO ugs_db.UserVotes
            (Changelist, UserName, Verdict, Project, ProjectId)
        VALUES
            (%s, %s, %s, %s, %s)
    """

    await DatabaseUtils.execute_sql(sql, (
        request.Change,
        request.UserName,
        request.Type,
        request.Project,
        project_id
    ))
