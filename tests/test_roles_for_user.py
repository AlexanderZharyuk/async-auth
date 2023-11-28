import random
import uuid
from http import HTTPStatus

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.v1.roles.exceptions import RoleAlreadyExistsError, RoleNotFound
from src.v1.roles.schemas import SeveralRolesResponse
from src.v1.users.exceptions import UserNotFoundError
from src.v1.users.schemas import UserHasRole, UserResponse
from tests.fixtures.roles_to_users import role_to_user, role_user_data
from tests.utils.check_role import check_create_role


@pytest.mark.parametrize("user_id", [role_user_data["id"]])
@pytest.mark.asyncio
async def test_get_user_roles_user_exist(api_session: AsyncClient, user_id: str):
    response = await api_session.get(f"/api/v1/users/{user_id}/roles")
    assert response.status_code == HTTPStatus.OK
    assert SeveralRolesResponse.model_validate(response.json())


@pytest.mark.parametrize("user_id", [uuid.uuid4()])
@pytest.mark.asyncio
async def test_get_roles_user_not_exist(api_session: AsyncClient, user_id: str):
    response = await api_session.get(f"/api/v1/users/{user_id}/roles")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert UserNotFoundError(response.json())


@pytest.mark.parametrize(
    "user_id, role_id", [(role_user_data["id"], role_to_user["id"])]
)
@pytest.mark.asyncio
async def test_add_role_to_user_success(
    api_session: AsyncClient, db: AsyncSession, user_id: str, role_id: int
):
    request_data = {"role_id": role_id}
    response = await api_session.post(f"/api/v1/users/{user_id}/roles", json=request_data)
    role = await check_create_role(db=db, user_id=user_id, role_id=role_id)
    assert response.status_code == HTTPStatus.OK
    assert UserResponse.model_validate(response.json())
    assert role is not None


@pytest.mark.parametrize("user_id, role_id", [(uuid.uuid4(), role_to_user["id"])])
@pytest.mark.asyncio
async def test_add_user_role_user_not_exist(
    api_session: AsyncClient, db: AsyncSession, user_id: str, role_id: int
):
    request_data = {"role_id": role_id}
    response = await api_session.post(f"/api/v1/users/{user_id}/roles", json=request_data)
    role = await check_create_role(db=db, user_id=user_id, role_id=role_id)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert UserNotFoundError(response.json())
    assert role is None


@pytest.mark.parametrize("user_id, role_id", [(role_user_data["id"], random.randint(1, 100))])
@pytest.mark.asyncio
async def test_add_user_role_role_not_exist(
    api_session: AsyncClient, db: AsyncSession, user_id: str, role_id: int
):
    request_data = {"role_id": role_id}
    response = await api_session.post(f"/api/v1/users/{user_id}/roles", json=request_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert RoleNotFound(response.json())
    role = await check_create_role(db=db, user_id=user_id, role_id=role_id)
    assert role is None


@pytest.mark.parametrize(
    "user_id, role_id", [(role_user_data["id"], role_to_user["id"])]
)
@pytest.mark.asyncio
async def test_add_user_role_role_already_exist(
    api_session: AsyncClient,
    db: AsyncSession,
    user_id: str,
    role_id: int,
):
    request_data = {"role_id": role_id}
    response = await api_session.post(f"/api/v1/users/{user_id}/roles", json=request_data)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert RoleAlreadyExistsError(response.json())
    role = await check_create_role(db=db, user_id=user_id, role_id=role_id)
    assert role.id == role_to_user["id"]
    assert role.name == role_to_user["name"]


@pytest.mark.parametrize(
    "user_id, role_id", [(role_user_data["id"], role_to_user["id"])]
)
@pytest.mark.asyncio
async def test_delete_user_role_success(
    api_session: AsyncClient, db: AsyncSession, user_id: str, role_id: int
):
    response = await api_session.delete(f"/api/v1/users/{user_id}/roles/{role_id}")
    assert response.status_code == HTTPStatus.OK
    assert UserResponse.model_validate(response.json())
    role = await check_create_role(db=db, user_id=user_id, role_id=role_id)
    assert role is None


@pytest.mark.parametrize("user_id, role_id", [(uuid.uuid4(), role_to_user["id"])])
@pytest.mark.asyncio
async def test_delete_user_role_user_not_exist(
    api_session: AsyncClient, user_id: str, role_id: int
):
    response = await api_session.delete(f"/api/v1/users/{user_id}/roles/{role_id}")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert UserNotFoundError(response.json())


@pytest.mark.parametrize("user_id, role_id", [(role_user_data["id"], random.randint(1, 100))])
@pytest.mark.asyncio
async def test_delete_user_role_role_not_exist(
    api_session: AsyncClient, user_id: str, role_id: int
):
    response = await api_session.delete(f"/api/v1/users/{user_id}/roles/{role_id}")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert RoleNotFound(response.json())


@pytest.mark.parametrize(
    "user_id, role_id", [(role_user_data["id"], role_to_user["id"])]
)
@pytest.mark.asyncio
async def test_user_has_role_success(api_session: AsyncClient, user_id: str, role_id: int):
    response = await api_session.get(f"/api/v1/users/{user_id}/roles/{role_id}")
    assert response.status_code == HTTPStatus.OK
    assert UserHasRole.model_validate(response.json())


@pytest.mark.parametrize("user_id, role_id", [(uuid.uuid4(), role_to_user["id"])])
@pytest.mark.asyncio
async def test_user_has_role_user_not_exist(api_session: AsyncClient, user_id: str, role_id: int):
    response = await api_session.get(f"/api/v1/users/{user_id}/roles/{role_id}")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert UserNotFoundError(response.json())
