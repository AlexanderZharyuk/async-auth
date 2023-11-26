import logging
from uuid import uuid4

from fastapi import APIRouter, Path, Query, status
from pydantic import UUID4
from typing_extensions import Annotated

from src.db.postgres import DatabaseSession
from src.v1.users.schemas import UserResponse, UserLoginsResponse, UserUpdate, UserBase
from src.v1.users.service import UserService

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
) -> UserResponse:
    """
    Получение информации о конкретном пользователе.
    """
    user = await UserService.get(db_session=db_session, user_id=user_id)
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
    page: Annotated[int, Query(examples=[1])],
    per_page: Annotated[int, Query(examples=[10])],
) -> UserLoginsResponse:
    """
    Получение списка последних логинов пользователя.
    """
    logins = await UserService.get_user_login_history(
        db_session=db_session, user_id=user_id, page=page, per_page=per_page
    )
    return UserLoginsResponse(data=logins)
