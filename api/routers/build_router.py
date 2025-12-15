from fastapi import APIRouter, Query, Body

from database_utils import DatabaseUtils
from common_utils import CommonUtils
from models.build_model import BuildRequest, BuildResponse, BuildResult

router = APIRouter()

@router.get("", response_model=list[BuildResponse])
async def get_builds(
    project: str = Query(min_length=1, max_length=128),
    lastbuildid: int = Query(ge=0)
):
    results = []

    sql = """
        SELECT
            Badges.Id,
            Badges.ChangeNumber,
            Badges.BuildType,
            Badges.Result,
            Badges.Url,
            Projects.Name,
            Badges.ArchivePath
        FROM ugs_db.Badges
        INNER JOIN ugs_db.Projects
            ON Projects.Id = Badges.ProjectId
        WHERE Badges.Id > %s
            AND Projects.Name LIKE %s
        ORDER BY Badges.Id
    """

    project_stream_like = f'%{CommonUtils.get_project_stream(project)}%'

    for build in await DatabaseUtils.fetch_objects(sql, (lastbuildid, project_stream_like)):
        build_id = build[0]
        change_number = build[1]
        build_type = build[2]
        build_result = build[3]
        url = build[4]
        project_name = build[5]
        archive_path = build[6]

        results.append(BuildResponse(
            Id=build_id,
            ChangeNumber=change_number,
            BuildType=build_type,
            Result=build_result,
            Url=url,
            Project=project_name,
            ArchivePath=archive_path
        ))

    return results

@router.post("")
async def post_build(request: BuildRequest = Body()):
    project_id = await CommonUtils.find_or_add_project(request.Project)
    build_result = BuildResult(request.Result).name

    sql = """
        INSERT INTO ugs_db.Badges
            (ChangeNumber, BuildType, Result, Url, ArchivePath, ProjectId)
        VALUES
            (%s, %s, %s, %s, %s, %s)
    """

    await DatabaseUtils.execute_sql(sql, (
        request.ChangeNumber,
        request.BuildType,
        build_result,
        request.Url,
        request.ArchivePath,
        project_id
    ))
