from fastapi import APIRouter, Query

from database_utils import DatabaseUtils
from common_utils import CommonUtils
from models.comment_model import CommentRequest, CommentResponse

router = APIRouter()

@router.get("", response_model=list[CommentResponse])
async def get_comments(
    project: str = Query(min_length=1, max_length=128),
    lastcommentid: int = Query(ge=0)
):
    results = []

    sql = """
        SELECT
            Comments.Id,
            Comments.ChangeNumber,
            Comments.UserName,
            Comments.Text,
            Comments.Project
        FROM ugs_db.Comments
        INNER JOIN ugs_db.Projects
            ON Projects.Id = Comments.ProjectId
        WHERE Comments.Id > %s
            AND Projects.Name LIKE %s
        ORDER BY Comments.Id
    """

    project_stream_like = f'%{CommonUtils.get_project_stream(project)}%'

    for comment in await DatabaseUtils.fetch_objects(sql, (lastcommentid, project_stream_like)):
        comment_id = comment[0]
        change_number = comment[1]
        user_name = comment[2]
        text = comment[3]
        project_name = comment[4]

        results.append(CommentResponse(
            Id=comment_id,
            ChangeNumber=change_number,
            UserName=user_name,
            Text=text,
            Project=project_name
        ))

    return results

@router.post("")
async def post_comment(request: CommentRequest):
    project_id = await CommonUtils.find_or_add_project(request.Project)

    sql = """
        INSERT INTO ugs_db.Comments
            (ChangeNumber, UserName, Text, Project, ProjectId)
        VALUES
            (%s, %s, %s, %s, %s)
    """

    await DatabaseUtils.execute_sql(sql, (
        request.ChangeNumber,
        request.UserName,
        request.Text,
        request.Project,
        project_id
    ))
