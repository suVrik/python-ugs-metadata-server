from contextlib import asynccontextmanager
from fastapi import FastAPI

from routers import (build_router, comment_router, event_router, latest_router,
    issues_router, telemetry_router, error_router, user_router)
from database_utils import DatabaseUtils

@asynccontextmanager
async def lifespan(app: FastAPI):
    await DatabaseUtils.init_db()
    print("UGS Metadata Server started")

    yield

    await DatabaseUtils.close_db()
    print("UGS Metadata Server stopped")

app = FastAPI(lifespan=lifespan)

app.include_router(build_router.router, prefix="/api/build")
app.include_router(comment_router.router, prefix="/api/comment")
app.include_router(error_router.router, prefix="/api/error")
app.include_router(event_router.router, prefix="/api/event")
app.include_router(latest_router.router, prefix="/api/latest")
app.include_router(issues_router.router, prefix="/api/issues")
app.include_router(issues_router.router_issuebuilds, prefix="/api/issuebuilds")
app.include_router(telemetry_router.router, prefix="/api/telemetry")
app.include_router(user_router.router, prefix="/api/user")
