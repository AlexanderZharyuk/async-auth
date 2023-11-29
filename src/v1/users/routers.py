import logging
from uuid import uuid4

from fastapi import APIRouter, Path, Query, status, Depends
from pydantic import UUID4
from typing_extensions import Annotated

from src.v1.dependencies import require_roles
from src.db.postgres import DatabaseSession
from src.v1.roles.schemas import SeveralRolesResponse
from src.v1.roles.constants import RolesChoices
from src.v1.users.models import User
from src.v1.users.schemas import UserResponse, UserLoginsResponse, UserUpdate, UserBase, RoleUser, UserHasRole
from src.v1.users.service import UserService, UserRolesService


router = APIRouter(prefix="/users", tags=["Пользователи"])
logger = logging.getLogger(__name__)


@router.get(
    "/{user_id}",
    summary="Получение информации о пользователе.",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    description="Получение информации о пользователе.",
)
async def get_user(
    db_session: DatabaseSession,
    user_id: Annotated[UUID4, Path(examples=[uuid4()])],
    current_user: User = Depends(require_roles([RolesChoices.ADMIN]))
) -> UserResponse:
    """
    Получение информации о конкретном пользователе.
    """

    user = await UserService.get(db_session=db_session, attribute="id", attribute_value=user_id)
    return UserResponse(data=UserBase.model_validate(user))


@router.patch(
    "/{user_id}",
    summary="Изменение информации о пользователе.",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    description="Изменение информации о пользователе.",
)
async def update_user(
    db_session: DatabaseSession,
    user_id: Annotated[UUID4, Path(examples=[uuid4()])],
    user_change_data: UserUpdate,
    current_user: User = Depends(require_roles([RolesChoices.ADMIN]))
) -> UserResponse:
    """
    Изменение информации о пользователе.
    """
    user = await UserService.update(
        db_session=db_session, user_id=user_id, update_data=user_change_data
    )
    return UserResponse(data=user)


@router.get(
    "/{user_id}/history",
    summary="Получение списка последних логинов пользователя.",
    response_model=UserLoginsResponse,
    status_code=status.HTTP_200_OK,
    description="Получение списка последних логинов пользователя.",
)
async def get_user_login_history(
    db_session: DatabaseSession,
    user_id: Annotated[UUID4, Path(examples=[uuid4()])],
    page: Annotated[int, Query(examples=[1], ge=1)] = 1,
    per_page: Annotated[int, Query(examples=[10], ge=1)] = 10,
    current_user: User = Depends(require_roles([RolesChoices.ADMIN]))
) -> UserLoginsResponse:
    """
    Получение списка последних логинов пользователя.
    """
    logins = await UserService.get_login_history(
        db_session=db_session, user_id=user_id, page=page, per_page=per_page
    )
    return UserLoginsResponse(data=logins)

@router.get(
    "/{user_id}/roles",
    summary="Получить список ролей пользователя.",
    response_model=SeveralRolesResponse,
    status_code=status.HTTP_200_OK,
    description="Получить список ролей пользователя.",
)
async def get_roles(
    db_session: DatabaseSession, 
    user_id: Annotated[UUID4, Path(examples=uuid4())],
    current_user: User = Depends(require_roles([RolesChoices.ADMIN]))
) -> SeveralRolesResponse:
    roles = await UserRolesService.get_roles(session=db_session, user_id=user_id)
    return SeveralRolesResponse(data=roles)


@router.post(
    "/{user_id}/roles",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Назначить роль пользователю.",
    description="Назначить роль пользователю.",
)
async def add_role(
    db_session: DatabaseSession, role: RoleUser, 
    user_id: Annotated[UUID4, Path(examples=uuid4())],
    current_user: User = Depends(require_roles([RolesChoices.ADMIN]))
) -> UserResponse:
    await UserRolesService.add_role(session=db_session, user_id=user_id, data=role)
    return UserResponse(data={})


@router.delete(
    "/{user_id}/roles/{role_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Отозвать роль у пользователя.",
    description="Отозвать роль у пользователя.",
)
async def delete_role(
    db_session: DatabaseSession, 
    role_id: Annotated[int, Path(examples=127856)], 
    user_id: Annotated[UUID4, Path(examples=uuid4())],
    current_user: User = Depends(require_roles([RolesChoices.ADMIN]))
) -> UserResponse:
    await UserRolesService.delete_role(session=db_session, user_id=user_id, role_id=role_id)
    return UserResponse(data={})


@router.get(
    "/{user_id}/roles/{role_id}",
    summary="Проверить наличие запрашиваемой роли у пользователя.",
    response_model=UserHasRole,
    status_code=status.HTTP_200_OK,
    description="Проверить наличие запрашиваемой роли у пользователя.",
)
async def has_role(
    db_session: DatabaseSession,
    user_id: Annotated[UUID4, Path(examples=uuid4())],
    role_id: Annotated[int, Path(examples=127856)],
) -> UserHasRole:
    result = await UserRolesService.has_role(session=db_session, user_id=user_id, role_id=role_id)
    return UserHasRole(data=result)
