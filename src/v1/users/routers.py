from uuid import uuid4

from fastapi import APIRouter, Path, status
from pydantic import UUID4
from typing_extensions import Annotated

from src.db.postgres import DatabaseSession
from src.v1.roles.schemas import SeveralRolesResponse
from src.v1.users.schemas import RoleUser, SingleUserResponse
from src.v1.users.service import UserRolesService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/{user_id}/roles",
    summary="Получить список ролей пользователя.",
    response_model=SeveralRolesResponse,
    status_code=status.HTTP_200_OK,
    description="Получить список ролей пользователя.",
)
async def get_roles(
    db_session: DatabaseSession, user_id: Annotated[UUID4, Path(example=uuid4())]
) -> SeveralRolesResponse:
    roles = await UserRolesService.get_roles(session=db_session, obj_id=user_id)
    return SeveralRolesResponse(data=roles)


@router.post(
    "/{user_id}/roles",
    response_model=SingleUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Назначить роль пользователю.",
    description="Назначить роль пользователю.",
)
async def add_role(
    db_session: DatabaseSession, role: RoleUser, user_id: Annotated[UUID4, Path(example=uuid4())]
) -> SingleUserResponse:
    await UserRolesService.add_role(session=db_session, obj_id=user_id, data=role.model_dump())
    return SingleUserResponse(data={})


@router.delete(
    "/{user_id}/roles",
    response_model=SingleUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Отозвать роль у пользователя.",
    description="Отозвать роль у пользователя.",
)
async def delete_role(
    db_session: DatabaseSession, role: RoleUser, user_id: Annotated[UUID4, Path(example=uuid4())]
) -> SingleUserResponse:
    await UserRolesService.delete_role(session=db_session, obj_id=user_id, data=role.model_dump())
    return SingleUserResponse(data=[])


@router.get(
    "/{user_id}/roles/{role_id}",
    summary="Проверить наличие запрашиваемой роли у пользователя.",
    response_model=SeveralRolesResponse,
    status_code=status.HTTP_200_OK,
    description="Проверить наличие запрашиваемой роли у пользователя.",
)
async def get_roles(
    db_session: DatabaseSession, user_id: Annotated[UUID4, Path(example=uuid4())]
) -> SeveralRolesResponse:
    roles = await UserRolesService.get_roles(session=db_session, obj_id=user_id)
    return SeveralRolesResponse(data=roles)