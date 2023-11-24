from fastapi import APIRouter, Path, status
from typing_extensions import Annotated

from src.db.postgres import DatabaseSession
from src.v1.roles.schemas import RoleCreate, RoleUpdate, SeveralRolesResponse, SingleRoleResponse
from src.v1.roles.service import RoleService

router = APIRouter(prefix="/roles", tags=["Управление ролями"])


@router.get(
    "/",
    summary="Получить список существующих ролей.",
    response_model=SeveralRolesResponse,
    status_code=status.HTTP_200_OK,
    description="Получить список существующих ролей.",
)
async def get(db_session: DatabaseSession) -> SeveralRolesResponse:
    roles = await RoleService.get(session=db_session)
    return SeveralRolesResponse(data=roles)


@router.post(
    "/",
    summary="Создать новую роль.",
    response_model=SingleRoleResponse,
    status_code=status.HTTP_200_OK,
    description="Создать новую роль.",
)
async def create(role: RoleCreate, db_session: DatabaseSession) -> SingleRoleResponse:
    role = await RoleService.create(session=db_session, data=role)
    return SingleRoleResponse(data=role)


@router.patch(
    "/{role_id}",
    summary="Редактировать роль.",
    response_model=SingleRoleResponse,
    status_code=status.HTTP_200_OK,
    description="Редактировать роль.",
)
async def update(
    role: RoleUpdate, role_id: Annotated[int, Path(example=127856)], db_session: DatabaseSession
) -> SingleRoleResponse:
    role = await RoleService.update(session=db_session, role_id=role_id, data=role)
    return SingleRoleResponse(data=role)


@router.delete(
    "/{role_id}",
    summary="Удалить роль.",
    response_model=SingleRoleResponse,
    status_code=status.HTTP_200_OK,
    description="Удалить роль.",
)
async def delete(
    role_id: Annotated[int, Path(example=127856)], db_session: DatabaseSession
) -> SingleRoleResponse:
    await RoleService.delete(session=db_session, role_id=role_id)
    return SingleRoleResponse(data=[])
