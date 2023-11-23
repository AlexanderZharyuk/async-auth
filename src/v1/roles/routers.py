from fastapi import APIRouter, Path, status
from typing_extensions import Annotated

from src.db.postgres import DatabaseSession
from src.v1.roles.schemas import RoleCreate, RoleModify, SeveralRolesResponse, SingleRolesResponse
from src.v1.roles.service import RoleService

router = APIRouter(prefix="/roles", tags=["Управление ролями"])


@router.get(
    "/",
    summary="Получение списка существующих ролей.",
    response_model=SeveralRolesResponse,
    status_code=status.HTTP_200_OK,
    description="Получение списка существующих ролей.",
)
async def get_roles(db_session: DatabaseSession) -> SeveralRolesResponse:
    roles = await RoleService.get_roles(session=db_session)
    return SeveralRolesResponse(data=roles)


@router.post(
    "/",
    summary="Создание новой роли.",
    response_model=SingleRolesResponse,
    status_code=status.HTTP_200_OK,
    description="Создание новой роли.",
)
async def create_role(role: RoleCreate, db_session: DatabaseSession) -> SingleRolesResponse:
    role = await RoleService.create_role(session=db_session, data=role.model_dump())
    return SingleRolesResponse(data=role)


@router.patch(
    "/{role_id}",
    summary="Редактирование роли.",
    response_model=SingleRolesResponse,
    status_code=status.HTTP_200_OK,
    description="Редактирование роли.",
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
    summary="Удаление роли.",
    response_model=SingleRolesResponse,
    status_code=status.HTTP_200_OK,
    description="Удаление роли.",
)
async def delete_role(
    role_id: Annotated[int, Path(example=127856)], db_session: DatabaseSession
) -> SingleRolesResponse:
    role = await RoleService.delete_role(session=db_session, obj_id=role_id)
    return SingleRolesResponse(data=role)
