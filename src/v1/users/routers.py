import logging
from uuid import uuid4

from fastapi import APIRouter, Path, Query, status
from pydantic import UUID4
from typing_extensions import Annotated

from src.db.postgres import DatabaseSession
from src.v1.users.schemas import (
    SingleUserResponse,
    SeveralLoginsResponse,
    UserChange,
)
from src.v1.users.service import UserService

router = APIRouter(prefix="/users", tags=["Пользователи"])
logger = logging.getLogger(__name__)


@router.get(
    "/{id}",
    summary="Получение информации о пользователе.",
    response_model=SingleUserResponse,
    status_code=status.HTTP_200_OK,
    description="Получение информации о пользователе.",
)
async def get_user(
    db_session: DatabaseSession,
    id: Annotated[UUID4, Path(example=uuid4())],
) -> SingleUserResponse:
    """
    Получение информации о конкретном пользователе.
    """
    user = await UserService.get(db_session=db_session, obj_id=id)
    return SingleUserResponse(data=user)


@router.patch(
    "/{id}",
    summary="Изменение информации о пользователе.",
    response_model=SingleUserResponse,
    status_code=status.HTTP_200_OK,
    description="Изменение информации о пользователе.",
)
@router.put(
    "/{id}",
    summary="Изменение информации о пользователе.",
    response_model=SingleUserResponse,
    status_code=status.HTTP_200_OK,
    description="Изменение информации о пользователе.",
)
async def change_user(
    db_session: DatabaseSession,
    id: Annotated[UUID4, Path(example=uuid4())],
    user_change_data: UserChange,
) -> SingleUserResponse:
    """
    Изменение информации о пользователе.
    """
    user = await UserService.change(
        db_session=db_session, obj_id=id, data_to_change_user=user_change_data
    )
    return SingleUserResponse(data=user)


@router.get(
    "/{id}/history",
    summary="Получение списка последних логинов пользователя.",
    response_model=SeveralLoginsResponse,
    status_code=status.HTTP_200_OK,
    description="Получение списка последних логинов пользователя.",
)
async def get_user_login_history(
    db_session: DatabaseSession,
    id: Annotated[UUID4, Path(example=uuid4())],
    page: Annotated[int, Query(example=1)],
    per_page: Annotated[int, Query(example=10)],
) -> SeveralLoginsResponse:
    """
    Получение списка последних логинов пользователя.
    """
    logins = await UserService.get_user_login_history(
        db_session=db_session, obj_id=id, page=page, per_page=per_page
    )
    return SeveralLoginsResponse(data=logins)
