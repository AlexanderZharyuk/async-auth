import logging
from uuid import uuid4

from fastapi import APIRouter, Depends, Path, status
from pydantic import UUID4
from typing_extensions import Annotated

from src.v1.users.schemas import SingleUserResponse, SeveralLoginsResponse, UserChange
from src.v1.users.service import PostgresUserService, get_user_service

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
    id: Annotated[UUID4, Path(example=uuid4())],
    user_service: PostgresUserService = Depends(get_user_service),
) -> SingleUserResponse:
    """
    Получение информации по конкретному жанру.
    """
    user = await user_service.get_user(obj_id=id)
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
    id: Annotated[UUID4, Path(example=uuid4())],
    data: UserChange,
    user_service: PostgresUserService = Depends(get_user_service),
) -> SingleUserResponse:
    """
    Изменение информации о пользователе.
    """
    user = await user_service.change_user(obj_id=id, data=data.model_dump())
    return SingleUserResponse(data=user)


@router.get(
    "/{id}/history",
    summary="Получение списка последних логинов пользователя.",
    response_model=SeveralLoginsResponse,
    status_code=status.HTTP_200_OK,
    description="Получение списка последних логинов пользователя.",
)
async def get_user_login_history(
    # page_number: Annotated[
    #     Union[int, None], Query(description="Page number of results", ge=1)
    # ] = 1,
    # page_size: Annotated[
    #     Union[int, None],
    #     Query(
    #         description=f"Limit the number of results [Max size: {settings.api_max_page_size}]",
    #         ge=1,
    #         le=settings.api_max_page_size,
    #     ),
    # ] = 50,
    user_service: PostgresUserService = Depends(get_user_service),
) -> SeveralLoginsResponse:
    """
    Получение списка последних логинов пользователя.
    """
    logins = await user_service.get_user_login_history(obj_id=id)
    return SeveralLoginsResponse(data=logins)
