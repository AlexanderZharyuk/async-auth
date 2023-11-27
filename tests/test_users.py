"""Users API tests."""
import uuid
from http import HTTPStatus

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.v1.auth.helpers import verify_password
from src.v1.users.exceptions import UserExceptionCodes
from src.v1.users.models import User
from tests.fixtures.users import user_data, user_password, logins, conflict_user_data


@pytest.mark.asyncio
async def test_get_user_success(api_session: AsyncClient):
    user_id = user_data["id"]
    response = await api_session.get(f"/api/v1/users/{user_id}")
    assert response.status_code == HTTPStatus.OK

    data = response.json()["data"]
    assert data["id"] == user_data["id"]
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert data["username"] == user_data["username"]
    assert data["last_login"] is None
    assert data["created_at"] is not None
    assert data["updated_at"] is None
    assert data["roles"] == [{"id": 10000, "name": "UserTestRole"}]


@pytest.mark.asyncio
async def test_get_user_failed(api_session: AsyncClient):
    response = await api_session.get(f"/api/v1/users/{uuid.uuid4()}")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {
        "detail": {"code": UserExceptionCodes.USER_NOT_FOUND, "message": "User is not exists."}
    }


@pytest.mark.asyncio
async def test_get_user_login_history_success(api_session: AsyncClient):
    user_id = user_data["id"]
    response = await api_session.get(f"/api/v1/users/{user_id}/history")
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()["data"]) == len(logins)


@pytest.mark.parametrize("page, per_page", [(1, 10), (2, 2), (3, 3)])
@pytest.mark.asyncio
async def test_get_user_login_history_paginated(
    api_session: AsyncClient, page: int, per_page: int
):
    user_id = user_data["id"]
    response = await api_session.get(
        f"/api/v1/users/{user_id}/history?page={page}&per_page={per_page}"
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()["data"]) == per_page


@pytest.mark.parametrize(
    "update_data",
    [
        {
            "username": "new_username",
            "current_password": user_password,
        },
        {
            "full_name": "new_full_name",
            "current_password": user_password,
        },
        {
            "email": "new@example.com",
            "current_password": user_password,
        },
        {
            "username": "username",
            "full_name": "full_name",
            "email": "email@example.com",
            "current_password": user_password,
        },
    ],
)
@pytest.mark.asyncio
async def test_update_user_params_success(api_session: AsyncClient, update_data):
    user_id = user_data["id"]
    response = await api_session.patch(f"/api/v1/users/{user_id}", json=update_data)
    assert response.status_code == HTTPStatus.OK
    assert response.json()["data"]["id"] == user_id

    update_data.pop("current_password", None)
    for key, value in update_data.items():
        assert response.json()["data"][key] == value

    response = await api_session.get(f"/api/v1/users/{user_id}")
    assert response.status_code == HTTPStatus.OK
    for key, value in update_data.items():
        assert response.json()["data"][key] == value


@pytest.mark.parametrize(
    "update_data",
    [
        {
            "username": conflict_user_data["username"],
            "current_password": user_password,
        },
        {
            "email": conflict_user_data["email"],
            "current_password": user_password,
        },
    ],
)
@pytest.mark.asyncio
async def test_update_user_params_failed(api_session: AsyncClient, update_data):
    user_id = user_data["id"]
    response = await api_session.patch(f"/api/v1/users/{user_id}", json=update_data)
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        "detail": {
            "code": UserExceptionCodes.USER_PARAMS_CONFLICT,
            "message": "Username or email is already taken.",
        }
    }


@pytest.mark.asyncio
async def test_update_user_password_success(api_session: AsyncClient, db: AsyncSession):
    user_id = user_data["id"]
    update_data = {
        "current_password": user_password,
        "password": "new_password",
        "repeat_password": "new_password",
    }
    response = await api_session.patch(f"/api/v1/users/{user_id}", json=update_data)
    assert response.status_code == HTTPStatus.OK

    user = await db.get(User, user_id)
    assert verify_password(update_data["password"], user.password)


@pytest.mark.parametrize(
    "update_data",
    [
        {
            "current_password": "fake_password",
            "password": "new_password",
            "repeat_password": "new_password",
        },
        {
            "current_password": user_password,
            "password": "new_password",
            "repeat_password": "new_password2",
        },
    ],
)
@pytest.mark.asyncio
async def test_update_user_password_failed(api_session: AsyncClient, update_data):
    user_id = user_data["id"]
    response = await api_session.patch(f"/api/v1/users/{user_id}", json=update_data)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
