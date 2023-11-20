import logging

import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import create_async_engine

import src.constants as const
from src.core.config import LOGGING, settings
from src.db import postgres
from src.models import BaseExceptionBody
from src.v1.auth.routers import router as auth_router
from src.v1.healthcheck.routers import router as healthcheck_router
from src.v1.roles.routers import router as roles_router
from src.v1.users.routers import router as user_router

v1_router = APIRouter(
    prefix="/api/v1",
    responses={
        404: {"model": BaseExceptionBody},
        400: {"model": BaseExceptionBody},
    },
)

v1_router.include_router(healthcheck_router)
v1_router.include_router(auth_router)
v1_router.include_router(user_router)
v1_router.include_router(roles_router)

app = FastAPI(
    title=const.APP_API_DOCS_TITLE,
    version=const.APP_VERSION,
    description=const.APP_DESCRIPTION,
    docs_url="/api/v1/docs",
    openapi_url="/api/v1/docs.json",
    default_response_class=ORJSONResponse,
)

app.include_router(v1_router)


@app.on_event("startup")
async def startup():
    postgres.pg = postgres.PostgresDatabase(
        engine=create_async_engine(settings.get_pg_dsn, echo=True, future=True)
    )


@app.on_event("shutdown")
async def shutdown():
    await postgres.pg.close()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.listen_addr,
        port=settings.listen_port,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
