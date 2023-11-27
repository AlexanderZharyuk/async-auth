from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import APIKeyCookie

from src.db.postgres import DatabaseSession, RefreshTokensStorage
from src.db.redis import BlacklistSignatureStorage
from src.v1.auth.schemas import (TokensResponse, UserCreate, UserLogin,
                                UserResponse, LogoutResponse, UserLogout, VerifyTokenResponse,
                                RefreshTokens)
from src.v1.auth.service import AuthService
from src.core.config import settings

router = APIRouter(prefix="/auth", tags=["Авторизация"])
cookie_scheme = APIKeyCookie(name=settings.sessions_cookie_name)


@router.post(
    "/signup",
    summary="Регистрация в сервисе",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def signup(db_session: DatabaseSession, user: UserCreate) -> UserResponse:
    """Регистрация пользователя в сервисе."""
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
    """Авторизация пользователя в сервисе"""
    tokens = await AuthService.signin(db_session, refresh_token_storage, user, request, response)
    return TokensResponse(data=tokens)


@router.post(
    "/verify", 
    summary="Верификация переданного access_token", 
    response_model=VerifyTokenResponse
)
async def verify_token(
    blacklist_signatures_storage: BlacklistSignatureStorage,
    access_token: str | None = Depends(cookie_scheme)
) -> VerifyTokenResponse:
    """Выход из всех сессий пользователя"""
    return await AuthService.verify(access_token, blacklist_signatures_storage)


@router.post(
    "/refresh", 
    summary="Выдача новой пары JWT-токенов", 
    response_model=TokensResponse
)
async def refresh_tokens(
    db_session: DatabaseSession,
    refresh_token_storage: RefreshTokensStorage,
    response: Response,
    data: RefreshTokens,
) -> TokensResponse:
    """Выход из всех сессий пользователя"""
    tokens = await AuthService.refresh_tokens(
        db_session,
        refresh_token_storage,
        response,
        data.refresh_token
    )
    return TokensResponse(data=tokens)


@router.post("/logout", summary="Выход из текущей сессии", response_model=LogoutResponse)
async def logout(
    db_session: DatabaseSession,
    refresh_token_storage: RefreshTokensStorage,
    response: Response,
    data: UserLogout,
    access_token: str | None = Depends(cookie_scheme)
) -> LogoutResponse:
    """Выход из текущей сессии"""
    await AuthService.logout(
        db_session, 
        refresh_token_storage, 
        response, 
        data.refresh_token
    )
    return LogoutResponse()


@router.post(
    "/logout_all", 
    summary="Выход из всех сессий пользователя", 
    response_model=LogoutResponse
)
async def terminate_all_sessions(
    db_session: DatabaseSession,
    blacklist_signatures_storage: BlacklistSignatureStorage,
    refresh_token_storage: RefreshTokensStorage,
    response: Response,
    access_token: str | None = Depends(cookie_scheme)
) -> LogoutResponse:
    """Выход из всех сессий пользователя"""
    await AuthService.terminate_all_sessions(
        db_session,
        blacklist_signatures_storage,
        refresh_token_storage, 
        response, 
        access_token
    )
    return LogoutResponse()