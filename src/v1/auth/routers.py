from fastapi import APIRouter, Request, Response, status

from src.db.postgres import DatabaseSession
from src.db.postgres import RefreshTokensStorage
from src.v1.auth.schemas import TokensResponse, UserCreate, UserLogin, UserResponse
from src.v1.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["Авторизация"])


@router.post(
    "/signup",
    summary="Регистрация в сервисе",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def signup(db_session: DatabaseSession, user: UserCreate) -> UserResponse:
    """
    Регистрация пользователя в сервисе.
    """
    user = await AuthService.signup(db_session, user)
    return UserResponse(data=user)


@router.post("/signin", summary="Авторизация в сервисе", response_model=TokensResponse)
async def signin(
    db_session: DatabaseSession,
    refresh_token_storage: RefreshTokensStorage,
    user: UserLogin,
    request: Request,
    response: Response,
) -> TokensResponse:
    """
    Авторизация пользователя в сервисе
    """
    tokens = await AuthService.signin(db_session, refresh_token_storage, user, request, response)
    return TokensResponse(data=tokens)
