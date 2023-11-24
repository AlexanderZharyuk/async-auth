from fastapi import APIRouter

from src.db.postgres import DatabaseSession
from src.v1.auth.schemas import User, UserCreate
from src.v1.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup", summary="Регистрация в сервисе")
async def signup(db_session: DatabaseSession, data: UserCreate) -> User:
    """
    Регистрация пользователя в сервисе.
    """
    user = await AuthService.signup(db_session, data)
    return user
