from uuid import uuid4
from typing_extensions import Annotated

from fastapi import APIRouter, Path
from pydantic import UUID4

from src.db.postgres import DatabaseSession
from src.v1.users.service import UserRolesService

router = APIRouter(prefix="/users", tags=["Users"])

#b9834ac3-a090-49eb-947e-fddecac769f3

@router.get("/{user_id}/roles", summary="Получить всех пользователей")
async def get_roles(db_session: DatabaseSession, user_id: Annotated[UUID4, Path(example=uuid4())]) -> None:
    await UserRolesService.get_roles(db_session, obj_id=user_id)
    return None

@router.post("/{user_id}/roles", summary="Получить всех пользователей")
async def get_roles() -> None:
    return None
