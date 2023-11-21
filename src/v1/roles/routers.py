from typing import Union

from fastapi import APIRouter, Depends, Path, Query, status
from typing_extensions import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.v1.roles.service import PostgreRolesService, get_role_service
from src.v1.roles.models import Role
from src.db import postgres
from src.db.postgres import PostgresDatabase, get_postgres_storage

router = APIRouter(prefix="/roles", tags=["Управление ролями"])

db_session = postgres.PostgresDatabase()
DatabaseSession = Annotated[AsyncSession, Depends(db_session)]
@router.get("/", summary="Получить все роли")
async def get_roles(db: DatabaseSession) -> None:
    res = await db.execute(select(Role))
    print(res)
    return None
