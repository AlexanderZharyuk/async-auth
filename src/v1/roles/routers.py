from typing import Union

from fastapi import APIRouter, Depends, Path, Query, status
from typing_extensions import Annotated

router = APIRouter(prefix="/roles", tags=["Управление ролями"])


@router.get("/", summary="Получить все роли")
async def get_roles() -> None:
    """
    Mock route.
    """
    return None
