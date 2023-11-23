from uuid import uuid4
from typing_extensions import Annotated

from fastapi import APIRouter, Path, status
from pydantic import UUID4

from src.db.postgres import DatabaseSession
from src.v1.users.service import UserRolesService
from src.v1.roles.schemas import SeveralRolesResponse
from src.v1.users.schemas import RoleUser

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/{user_id}/roles", summary="Получить список ролей пользователя.",
    response_model=SeveralRolesResponse,
    status_code=status.HTTP_200_OK,
    description="Получить список ролей пользователя."
)
async def get_roles(db_session: DatabaseSession, user_id: Annotated[UUID4, Path(example=uuid4())]) -> SeveralRolesResponse:
    roles = await UserRolesService.get_roles(session=db_session, obj_id=user_id)
    return SeveralRolesResponse(data=roles)

@router.post(
    "/{user_id}/roles",
    status_code=status.HTTP_200_OK,
    summary="Назначить роль пользователю.",
    description="Назначить роль пользователю.")
async def add_role(db_session: DatabaseSession, role: RoleUser, user_id: Annotated[UUID4, Path(example=uuid4())]) -> None:
    await UserRolesService.add_role(session=db_session, obj_id=user_id, data=role.model_dump())
    return None

@router.delete(
    "/{user_id}/roles",
    status_code=status.HTTP_200_OK,
    summary="Отозвать роль у пользователя.",
    description="Отозвать роль у пользователя.")
async def delete_role(db_session: DatabaseSession, role: RoleUser, user_id: Annotated[UUID4, Path(example=uuid4())]) -> None:
    await UserRolesService.delete_role(session=db_session, obj_id=user_id, data=role.model_dump())
    return None
