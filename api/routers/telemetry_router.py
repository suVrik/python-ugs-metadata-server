from fastapi import APIRouter, Query, Body

from database_utils import DatabaseUtils
from common_utils import CommonUtils
from models.telemetry_model import TelemetryRequest

router = APIRouter()

@router.post("")
async def post_telemetry(
    request: TelemetryRequest = Body(),
    version: str = Query(min_length=1, max_length=64),
    ipaddress: str = Query(min_length=1, max_length=64)
):
    project_id = await CommonUtils.find_or_add_project(request.Project)

    sql = """
        INSERT INTO ugs_db.Telemetry_v2
            (Action, Result, UserName, Project, Timestamp, Duration, Version, IpAddress, ProjectId)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    await DatabaseUtils.execute_sql(sql, (
        request.Action,
        request.Result,
        request.UserName,
        request.Project,
        request.Timestamp,
        request.Duration,
        version,
        ipaddress,
        project_id
    ))
