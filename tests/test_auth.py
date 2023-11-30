"""Auth routes tests."""
import uuid
from http import HTTPStatus
from datetime import datetime, timedelta

import asyncio
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt

from src.v1.auth.schemas import (
    UserResponse,
    TokensResponse,
    VerifyTokenResponse,
    RefreshTokens,
    LogoutResponse,
    UserLogout,
)
from src.core.config import settings
from src.v1.users.exceptions import UserNotFoundError
from src.v1.users.models import UserSignature, UserRefreshTokens
from src.v1.users.service import UserService


@pytest.mark.asyncio
async def test_signup_user_success(api_session: AsyncClient, db: AsyncSession):
    random_user_email = "some@example.com"
    new_user_data = {
        "email": random_user_email,
        "username": "someuser",
        "password": "somepass",
        "repeat_password": "somepass",
    }

    response = await api_session.post("/api/v1/auth/signup", json=new_user_data)
    assert response.status_code == HTTPStatus.CREATED
    assert UserResponse(**response.json())

    user_in_db = await UserService.get(
        db, attribute="email", attribute_value=random_user_email
    )
    assert new_user_data["username"] == user_in_db.username

    statement = select(UserSignature).where(UserSignature.user_id == user_in_db.id)
    result = await db.execute(statement)
    user_signature = result.scalars()
    assert len(user_signature.all()) == 1


@pytest.mark.parametrize(
    "incorrect_data",
    [
        {
            "email": "invalidemail.com",
        },
        {
            "email": "invalidemail.com",
            "username": "some_new_user",
        },
        {"email": "invalidemail.com", "username": "some_new_user", "password": "password"},
        {
            "email": "invalidemail.com",
            "username": "some_new_user",
            "password": "password",
            "repeat_password": "password",
        },
        {
            "email": "valid@email.com",
            "username": "some_new_user",
            "password": "password",
            "repeat_password": "password1",
        },
    ],
)
@pytest.mark.asyncio
async def test_signup_user_failed(api_session: AsyncClient, db: AsyncSession, incorrect_data):
    response = await api_session.post("/api/v1/auth/signup", json=incorrect_data)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    try:
        await UserService.get(
            db, attribute="email", attribute_value=incorrect_data.get("email")
        )
    except UserNotFoundError:
        pass


@pytest.mark.asyncio
async def test_signup_exist_user(api_session: AsyncClient):
    random_user_email = "newexistsuser@gmail.com"
    new_user_data = {
        "email": random_user_email,
        "username": "someusername",
        "password": "somepass",
        "repeat_password": "somepass",
    }

    response = await api_session.post("/api/v1/auth/signup", json=new_user_data)
    assert response.status_code == HTTPStatus.CREATED

    response = await api_session.post("/api/v1/auth/signup", json=new_user_data)
    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.asyncio
async def test_signin_success(api_session: AsyncClient):
    exists_user_data = {"email": "some@example.com", "password": "somepass"}

    response = await api_session.post("/api/v1/auth/signin", json=exists_user_data)
    assert response.status_code == HTTPStatus.OK
    assert TokensResponse(**response.json())
    assert response.cookies.get("access_token") is not None


@pytest.mark.parametrize(
    "invalid_data",
    [
        {"email": "some123@example.com", "password": "somepass"},
        {"email": "some@example.com", "password": "somepass213123"},
    ],
)
@pytest.mark.asyncio
async def test_signin_with_invalid_data(api_session: AsyncClient, invalid_data):
    response = await api_session.post("/api/v1/auth/signin", json=invalid_data)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_access_verify_complete(api_session: AsyncClient):
    exists_user_data = {"email": "some@example.com", "password": "somepass"}
    response = await api_session.post("/api/v1/auth/signin", json=exists_user_data)

    access_token = TokensResponse(**response.json()).data.access_token
    response = await api_session.post(
        "/api/v1/auth/verify", cookies={"access_token": access_token}
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == VerifyTokenResponse().model_dump()


@pytest.mark.asyncio
async def test_access_verify_failed(api_session: AsyncClient):
    exists_user_data = {"email": "some@example.com", "password": "somepass"}
    response = await api_session.post("/api/v1/auth/signin", json=exists_user_data)
    refresh_token = TokensResponse(**response.json()).data.refresh_token

    response = await api_session.post("/api/v1/auth/verify")
    assert response.status_code == HTTPStatus.FORBIDDEN

    response = await api_session.post(
        "/api/v1/auth/verify", cookies={"access_token": refresh_token}
    )
    assert response.json() == VerifyTokenResponse(data={"access": False}).model_dump()

    short_life_access_token_payload = {
        "exp": datetime.now() + timedelta(seconds=0.5),
        "user_id": str(uuid.uuid4()),
    }
    access_token = jwt.encode(
        short_life_access_token_payload,
        algorithm=settings.jwt_algorithm,
        key=settings.jwt_secret_key,
    )
    await asyncio.sleep(1)
    response = await api_session.post(
        "/api/v1/auth/verify", cookies={"access_token": access_token}
    )
    assert response.json() == VerifyTokenResponse(data={"access": False}).model_dump()


@pytest.mark.asyncio
async def test_success_refresh_jwt(api_session: AsyncClient):
    exists_user_data = {"email": "some@example.com", "password": "somepass"}
    response = await api_session.post("/api/v1/auth/signin", json=exists_user_data)
    data = RefreshTokens(refresh_token=TokensResponse(**response.json()).data.refresh_token)

    response = await api_session.post("/api/v1/auth/refresh", json=data.model_dump())
    assert response.status_code == HTTPStatus.OK
    assert TokensResponse(**response.json())


@pytest.mark.asyncio
async def test_success_logout(api_session: AsyncClient, db: AsyncSession):
    exists_user_data = {"email": "some@example.com", "password": "somepass"}
    response = await api_session.post("/api/v1/auth/signin", json=exists_user_data)
    tokens = TokensResponse(**response.json())
    access_token = tokens.data.access_token
    refresh_token = tokens.data.refresh_token

    statement = select(UserRefreshTokens).where(
        UserRefreshTokens.token == jwt.get_unverified_header(refresh_token).get("jti")
    )
    result = await db.execute(statement)
    assert len(result.all()) == 1

    data = {"refresh_token": refresh_token}
    response = await api_session.post(
        "/api/v1/auth/logout", json=data, cookies={"access_token": access_token}
    )
    assert response.status_code == HTTPStatus.OK
    assert LogoutResponse(**response.json())
    assert response.cookies.get("access_token") is None
    result = await db.execute(statement)
    assert len(result.all()) == 0


@pytest.mark.asyncio
async def test_failed_logout(api_session: AsyncClient, db: AsyncSession):
    response = await api_session.post("/api/v1/auth/logout")
    assert response.status_code == HTTPStatus.FORBIDDEN

    exists_user_data = {"email": "some@example.com", "password": "somepass"}
    response = await api_session.post("/api/v1/auth/signin", json=exists_user_data)

    tokens = TokensResponse(**response.json())
    access_token = tokens.data.access_token
    random_refresh = jwt.encode(
        {"exp": datetime.now() + timedelta(days=1)},
        algorithm=settings.jwt_algorithm,
        key=settings.jwt_secret_key,
    )
    data_payload = UserLogout(refresh_token=random_refresh)
    response = await api_session.post(
        "/api/v1/auth/signin",
        json=data_payload.model_dump(),
        cookies={"access_token": access_token},
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_success_terminate_all_sessions(api_session: AsyncClient, db: AsyncSession):
    exists_user_data = {"email": "some@example.com", "password": "somepass"}
    for _ in range(3):
        response = await api_session.post("/api/v1/auth/signin", json=exists_user_data)

    tokens = TokensResponse(**response.json())
    exists_user = await UserService.get(
        db, attribute="email", attribute_value=exists_user_data.get("email")
    )
    statement = select(UserRefreshTokens).where(UserRefreshTokens.user_id == exists_user.id)
    refresh_tokens = await db.execute(statement)
    assert len(refresh_tokens.all()) > 1

    response = await api_session.post(
        "/api/v1/auth/verify", cookies={"access_token": tokens.data.access_token}
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == VerifyTokenResponse().model_dump()

    response = await api_session.post(
        "/api/v1/auth/logout_all", cookies={"access_token": tokens.data.access_token}
    )
    assert response.status_code == HTTPStatus.OK
    assert response.cookies.get("access_token") is None
    refresh_tokens = await db.execute(statement)
    assert len(refresh_tokens.all()) == 0

    response = await api_session.post(
        "/api/v1/auth/verify", cookies={"access_token": tokens.data.access_token}
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == VerifyTokenResponse(data={"access": False}).model_dump()
