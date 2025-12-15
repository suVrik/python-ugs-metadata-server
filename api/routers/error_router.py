from fastapi import APIRouter, Query, Body

from database_utils import DatabaseUtils
from common_utils import CommonUtils
from models.error_model import ErrorRequest, ErrorResponse, ErrorType

router = APIRouter()

@router.get("", response_model=list[ErrorResponse])
async def get_error(records: int = Query(10, gt=0)):
    results = []

    sql = """
        SELECT
            Id,
            Type,
            Text,
            UserName,
            Project,
            Timestamp,
            Version,
            IpAddress
        FROM ugs_db.Errors
        ORDER BY Id DESC
        LIMIT %s
    """

    for error in await DatabaseUtils.fetch_objects(sql, (records,)):
        error_id = error[0]
        error_type = error[1]
        text = error[2]
        user_name = error[3]
        project = error[4]
        timestamp = error[5]
        version = error[6]
        ip_address = error[7]

        results.append(ErrorResponse(
            Id=error_id,
            Type=error_type,
            Text=text,
            UserName=user_name,
            Project=project,
            Timestamp=timestamp,
            Version=version,
            IpAddress=ip_address
        ))

    return results

@router.post("")
async def post_error(
    request: ErrorRequest = Body(),
    version: str = Query(min_length=1, max_length=64),
    ipaddress: str = Query(min_length=1, max_length=64)
):
    project_id = await CommonUtils.find_or_add_project(request.Project)
    error_type = ErrorType(request.Type).name

    sql = """
        INSERT INTO ugs_db.Errors
            (Type, Text, UserName, Project, Timestamp, Version, IpAddress, ProjectId)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    await DatabaseUtils.execute_sql(sql, (
        error_type,
        request.Text,
        request.UserName,
        request.Project,
        request.Timestamp,
        version,
        ipaddress,
        project_id
    ))
