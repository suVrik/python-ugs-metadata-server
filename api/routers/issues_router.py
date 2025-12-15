from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Path, Body

from database_utils import DatabaseUtils
from common_utils import CommonUtils
from models.issue_model import (IssueRequest, IssueResponse, IssueUpdateRequest,
    IssueBuildRequest, IssueBuildResponse, IssueBuildCreateResponse, IssueBuildUpdateRequest,
    IssueDiagnosticRequest, IssueDiagnosticResponse, IssueWatcherRequest, IssueCreateResponse)

router = APIRouter()

async def get_issues_internal(
    issue_id: int | None = None,
    user_name: str | None = None,
    include_resolved: bool = False,
    max_results: int | None = None
) -> list[IssueResponse]:
    sql = f"""
        SELECT
            Issues.Id,
            Issues.CreatedAt,
            UTC_TIMESTAMP(),
            Issues.Project,
            Issues.Summary,
            OwnerUsers.Name,
            NominatedByUsers.Name,
            Issues.AcknowledgedAt,
            Issues.FixChange,
            Issues.ResolvedAt,
            {"IssueWatchers.UserId" if user_name is not None else "NULL"}
        FROM ugs_db.Issues
        LEFT JOIN ugs_db.Users AS OwnerUsers
            ON OwnerUsers.Id = Issues.OwnerId
        LEFT JOIN ugs_db.Users AS NominatedByUsers
            ON NominatedByUsers.Id = Issues.NominatedById
    """

    params = []

    if user_name is not None:
        sql += """
            LEFT JOIN ugs_db.IssueWatchers
                ON IssueWatchers.IssueId = Issues.Id
                AND IssueWatchers.UserId = %s
        """
        params.append(await CommonUtils.find_or_add_user(user_name))

    if issue_id is not None:
        sql += "WHERE Issues.Id = %s"
        params.append(issue_id)
    elif not include_resolved:
        sql += "WHERE Issues.ResolvedAt IS NULL"

    if max_results is not None:
        sql += "ORDER BY Issues.Id DESC LIMIT %s"
        params.append(max_results)

    results = []

    for row in await DatabaseUtils.fetch_objects(sql, tuple(params)):
        results.append(IssueResponse(
            Id=row[0],
            CreatedAt=row[1],
            RetrievedAt=row[2],
            Project=row[3],
            Summary=row[4],
            Owner=row[5],
            NominatedBy=row[6],
            AcknowledgedAt=row[7],
            FixChange=row[8],
            ResolvedAt=row[9],
            bNotify=row[10] is not None
        ))

    return results

@router.get("", response_model=list[IssueResponse])
async def get_issues(
    includeresolved: bool = False,
    maxresults: int | None = Query(None, gt=0),
    user: str | None = Query(None, min_length=1, max_length=128)
):
    if user is not None:
        return await get_issues_internal(user_name=user)
    else:
        return await get_issues_internal(include_resolved=includeresolved, max_results=maxresults)

@router.get("/{issue_id}", response_model=IssueResponse)
async def get_issue(issue_id: int = Path(..., ge=0)):
    issues = await get_issues_internal(issue_id=issue_id, include_resolved=True)
    if len(issues) == 0:
        raise HTTPException(status_code=404)
    return issues[0]

@router.put("/{issue_id}")
async def put_issue(
    issue_id: int = Path(..., ge=0),
    request: IssueUpdateRequest = Body()
):
    updates = []
    params = []
    
    if request.Summary is not None:
        updates.append("Summary = %s")
        params.append(request.Summary[:256])

    if request.Owner is not None:
        updates.append("OwnerId = %s")
        params.append(await CommonUtils.find_or_add_user(request.Owner))
    
    if request.NominatedBy is not None:
        updates.append("NominatedById = %s")
        params.append(await CommonUtils.find_or_add_user(request.NominatedBy))
    
    if request.Acknowledged is not None:
        if request.Acknowledged:
            updates.append("AcknowledgedAt = UTC_TIMESTAMP()")
        else:
            updates.append("AcknowledgedAt = NULL")
    
    if request.FixChange is not None:
        updates.append("FixChange = %s")
        params.append(request.FixChange)
    
    if request.Resolved is not None:
        if request.Resolved:
            updates.append("ResolvedAt = UTC_TIMESTAMP()")
        else:
            updates.append("ResolvedAt = NULL")
    
    if not updates:
        return
    
    sql = f"UPDATE ugs_db.Issues SET {', '.join(updates)} WHERE Id = %s"
    params.append(issue_id)
    
    await DatabaseUtils.execute_sql(sql, tuple(params))

@router.post("", response_model=IssueCreateResponse)
async def post_issues(request: IssueRequest = Body()):
    sql = """
        INSERT INTO ugs_db.Issues (Project, Summary, OwnerId, CreatedAt, FixChange)
        VALUES (%s, %s, %s, UTC_TIMESTAMP(), 0)
    """
    
    owner_id = await CommonUtils.find_or_add_user(request.Owner)
    issue_id = await DatabaseUtils.execute_sql(sql, (request.Project, request.Summary[:256], owner_id))

    return IssueCreateResponse(Id=issue_id)

@router.delete("/{issue_id}")
async def delete_issue(issue_id: int = Path(..., ge=0)):
    await DatabaseUtils.execute_sqls((
        "DELETE FROM ugs_db.IssueWatchers WHERE IssueId = %s",
        "DELETE FROM ugs_db.IssueBuilds WHERE IssueId = %s",
        "DELETE FROM ugs_db.Issues WHERE Id = %s"
    ), ((issue_id,), (issue_id,), (issue_id,)))

@router.get("/{issue_id}/builds", response_model=list[IssueBuildResponse])
async def get_issue_builds_sub(issue_id: int = Path(..., ge=0)):
    sql = """
        SELECT IssueBuilds.Id, IssueBuilds.Stream, IssueBuilds.Change, IssueBuilds.JobName,
               IssueBuilds.JobUrl, IssueBuilds.JobStepName, IssueBuilds.JobStepUrl,
               IssueBuilds.ErrorUrl, IssueBuilds.Outcome
        FROM ugs_db.IssueBuilds
        WHERE IssueBuilds.IssueId = %s
    """
    
    results = []

    for row in await DatabaseUtils.fetch_objects(sql, (issue_id,)):
        results.append(IssueBuildResponse(
            Id=row[0],
            Stream=row[1],
            Change=row[2],
            JobName=row[3],
            JobUrl=row[4],
            JobStepName=row[5],
            JobStepUrl=row[6],
            ErrorUrl=row[7],
            Outcome=row[8]
        ))
    
    return results

@router.post("/{issue_id}/builds", response_model=IssueBuildCreateResponse)
async def post_issue_builds_sub(
    issue_id: int = Path(..., ge=0),
    request: IssueBuildRequest = Body()
):
    sql = """
        INSERT INTO ugs_db.IssueBuilds
            (IssueId, Stream, Change, JobName, JobUrl, JobStepName, JobStepUrl, ErrorUrl, Outcome)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    build_id = await DatabaseUtils.execute_sql(sql, (
        issue_id,
        request.Stream,
        request.Change,
        request.JobName,
        request.JobUrl,
        request.JobStepName,
        request.JobStepUrl,
        request.ErrorUrl,
        request.Outcome
    ))
    
    return IssueBuildCreateResponse(Id=build_id)

@router.get("/{issue_id}/diagnostics", response_model=list[IssueDiagnosticResponse])
async def get_issue_diagnostics_sub(issue_id: int = Path(..., ge=0)):
    sql = """
        SELECT BuildId, Message, Url
        FROM ugs_db.IssueDiagnostics
        WHERE IssueDiagnostics.IssueId = %s
    """
    
    results = []

    for row in await DatabaseUtils.fetch_objects(sql, (issue_id,)):
        results.append(IssueDiagnosticResponse(
            BuildId=row[0],
            Message=row[1],
            Url=row[2]
        ))

    return results

@router.post("/{issue_id}/diagnostics")
async def post_issue_diagnostics_sub(
    issue_id: int = Path(..., ge=0),
    request: IssueDiagnosticRequest = Body()
):
    sql = """
        INSERT INTO ugs_db.IssueDiagnostics (IssueId, BuildId, Message, Url)
        VALUES (%s, %s, %s, %s)
    """

    await DatabaseUtils.execute_sql(sql, (
        issue_id,
        request.BuildId,
        request.Message[:1000],
        request.Url
    ))

@router.get("/{issue_id}/watchers", response_model=list[str])
async def get_issue_watchers(issue_id: int = Path(..., ge=0)):
    sql = """
        SELECT Users.Name
        FROM ugs_db.IssueWatchers
        LEFT JOIN ugs_db.Users ON IssueWatchers.UserId = Users.Id
        WHERE IssueWatchers.IssueId = %s
    """
    
    results = []

    for row in await DatabaseUtils.fetch_objects(sql, (issue_id,)):
        results.append(row[0])
    
    return results

@router.post("/{issue_id}/watchers")
async def post_issue_watchers(
    issue_id: int = Path(..., ge=0),
    request: IssueWatcherRequest = Body()
):
    user_id = await CommonUtils.find_or_add_user(request.UserName)
    
    sql = "INSERT IGNORE INTO ugs_db.IssueWatchers (IssueId, UserId) VALUES (%s, %s)"
    
    await DatabaseUtils.execute_sql(sql, (issue_id, user_id))

@router.delete("/{issue_id}/watchers")
async def delete_issue_watchers(
    issue_id: int = Path(..., ge=0),
    request: IssueWatcherRequest = Body()
):
    user_id = await CommonUtils.find_or_add_user(request.UserName)

    sql = "DELETE FROM ugs_db.IssueWatchers WHERE IssueId = %s AND UserId = %s"

    await DatabaseUtils.execute_sql(sql, (issue_id, user_id))

router_issuebuilds = APIRouter()

@router_issuebuilds.get("/{build_id}", response_model=IssueBuildResponse | None)
async def get_issue_builds(build_id: int = Path(..., ge=0)):
    sql = """
        SELECT IssueBuilds.Id, IssueBuilds.Stream, IssueBuilds.Change, IssueBuilds.JobName,
               IssueBuilds.JobUrl, IssueBuilds.JobStepName, IssueBuilds.JobStepUrl,
               IssueBuilds.ErrorUrl, IssueBuilds.Outcome
        FROM ugs_db.IssueBuilds
        WHERE IssueBuilds.Id = %s
    """
    
    row = await DatabaseUtils.fetch_object(sql, (build_id,))
    if row is None:
        return

    return IssueBuildResponse(
        Id=row[0],
        Stream=row[1],
        Change=row[2],
        JobName=row[3],
        JobUrl=row[4],
        JobStepName=row[5],
        JobStepUrl=row[6],
        ErrorUrl=row[7],
        Outcome=row[8]
    )

@router_issuebuilds.put("/{build_id}")
async def put_issue_builds(
    build_id: int = Path(..., ge=0),
    request: IssueBuildUpdateRequest = Body()
):
    sql = """
        UPDATE ugs_db.IssueBuilds
        SET Outcome = %s
        WHERE Id = %s
    """
    
    await DatabaseUtils.execute_sql(sql, (request.Outcome, build_id))
