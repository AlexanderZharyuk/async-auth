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

@router.get("/", summary="Получить все роли")
async def get_roles(service: PostgreRolesService = Depends(get_role_service)) -> None:
    r = await service.get()
    return None
