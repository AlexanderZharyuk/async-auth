from fastapi import APIRouter, Path, status
from typing_extensions import Annotated

from src.db.postgres import DatabaseSession
from src.v1.roles.schemas import RoleCreate, RoleModify, SeveralRolesResponse, SingleRolesResponse
from src.v1.roles.service import RoleService

router = APIRouter(prefix="/roles", tags=["Управление ролями"])


@router.get(
    "/",
    summary="Получить список существующих ролей.",
    response_model=SeveralRolesResponse,
    status_code=status.HTTP_200_OK,
    description="Получить список существующих ролей.",
)
async def get_roles(db_session: DatabaseSession) -> SeveralRolesResponse:
    roles = await RoleService.get_roles(session=db_session)
    return SeveralRolesResponse(data=roles)


@router.post(
    "/",
    summary="Создать новую роль.",
    response_model=SingleRolesResponse,
    status_code=status.HTTP_200_OK,
    description="Создать новую роль.",
)
async def create_role(role: RoleCreate, db_session: DatabaseSession) -> SingleRolesResponse:
    role = await RoleService.create_role(session=db_session, data=role.model_dump())
    return SingleRolesResponse(data=role)


@router.patch(
    "/{role_id}",
    summary="Редактировать роль.",
    response_model=SingleRolesResponse,
    status_code=status.HTTP_200_OK,
    description="Редактировать роль.",
)
async def modify_role(
    role: RoleModify, role_id: Annotated[int, Path(example=127856)], db_session: DatabaseSession
) -> SingleRolesResponse:
    role = await RoleService.modify_role(
        session=db_session, obj_id=role_id, data=role.model_dump()
    )
    return SingleRolesResponse(data=role)


@router.delete(
    "/{role_id}",
    summary="Удалить роль.",
    response_model=SingleRolesResponse,
    status_code=status.HTTP_200_OK,
    description="Удалить роль.",
)
async def delete_role(
    role_id: Annotated[int, Path(example=127856)], db_session: DatabaseSession
) -> SingleRolesResponse:
    role = await RoleService.delete_role(session=db_session, obj_id=role_id)
    return SingleRolesResponse(data=role)