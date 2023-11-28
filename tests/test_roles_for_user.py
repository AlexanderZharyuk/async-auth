import pytest

from http import HTTPStatus
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.v1.roles.exceptions import RoleAlreadyExistsError, RoleNotFound
from src.v1.roles.schemas import SeveralRolesResponse
from src.v1.users.exceptions import UserNotFoundError
from src.v1.users.schemas import UserHasRole, UserResponse
from tests.utils.check_role import check_create_role


@pytest.mark.parametrize("id", ["c94e5b5d-7992-466e-bebe-da86d6ddfa82"])
@pytest.mark.asyncio
async def test_get_user_roles_user_exist(api_session: AsyncClient, id: str):
    response = await api_session.get(f"/api/v1/users/{id}/roles")
    assert response.status_code == HTTPStatus.OK
    assert SeveralRolesResponse.model_validate(response.json())


@pytest.mark.parametrize("id", ["e460707d-4ff9-4e75-a0d7-1a02ae7db45f"])
@pytest.mark.asyncio
async def test_get_roles_user_not_exist(api_session: AsyncClient, id: str):
    response = await api_session.get(f"/api/v1/users/{id}/roles")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert UserNotFoundError(response.json())


@pytest.mark.parametrize("user_id, role_id", [("c94e5b5d-7992-466e-bebe-da86d6ddfa82", 96608)])
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


@pytest.mark.parametrize("user_id, role_id", [("e460707d-4ff9-4e75-a0d7-1a02ae7db45f", 96608)])
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


@pytest.mark.parametrize("user_id, role_id", [("c94e5b5d-7992-466e-bebe-da86d6ddfa82", 96600)])
@pytest.mark.asyncio
async def test_add_user_role_role_not_exist(
    api_session: AsyncClient, db: AsyncSession, user_id: str, role_id: int
):
    request_data = {"role_id": role_id}
    response = await api_session.post(f"/api/v1/users/{user_id}/roles", json=request_data)
    role = await check_create_role(db=db, user_id=user_id, role_id=role_id)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert RoleNotFound(response.json())
    assert role is None


@pytest.mark.parametrize("user_id, role_id", [("c94e5b5d-7992-466e-bebe-da86d6ddfa82", 96606)])
@pytest.mark.asyncio
async def test_add_user_role_role_already_exist(
    api_session: AsyncClient, db: AsyncSession, user_id: str, role_id: int
):
    request_data = {"role_id": role_id}
    response = await api_session.post(f"/api/v1/users/{user_id}/roles", json=request_data)
    role = await check_create_role(db=db, user_id=user_id, role_id=role_id)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert RoleAlreadyExistsError(response.json())
    assert role is None


@pytest.mark.parametrize("user_id, role_id", [("c94e5b5d-7992-466e-bebe-da86d6ddfa82", 96608)])
@pytest.mark.asyncio
async def test_delete_user_role_success(
    api_session: AsyncClient, db: AsyncSession, user_id: str, role_id: int
):
    response = await api_session.delete(f"/api/v1/users/{user_id}/roles/{role_id}")
    role = await check_create_role(db=db, user_id=user_id, role_id=role_id)
    assert response.status_code == HTTPStatus.OK
    assert UserResponse.model_validate(response.json())
    assert role is None


@pytest.mark.parametrize("user_id, role_id", [("e460707d-4ff9-4e75-a0d7-1a02ae7db45f", 96608)])
@pytest.mark.asyncio
async def test_delete_user_role_user_not_exist(
    api_session: AsyncClient, user_id: str, role_id: int
):
    response = await api_session.delete(f"/api/v1/users/{user_id}/roles/{role_id}")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert UserNotFoundError(response.json())


@pytest.mark.parametrize("user_id, role_id", [("c94e5b5d-7992-466e-bebe-da86d6ddfa82", 96600)])
@pytest.mark.asyncio
async def test_delete_user_role_role_not_exist(
    api_session: AsyncClient, user_id: str, role_id: int
):
    response = await api_session.delete(f"/api/v1/users/{user_id}/roles/{role_id}")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert RoleNotFound(response.json())


@pytest.mark.parametrize("user_id, role_id", [("c94e5b5d-7992-466e-bebe-da86d6ddfa82", 96606)])
@pytest.mark.asyncio
async def test_user_has_role_success(api_session: AsyncClient, user_id: str, role_id: int):
    response = await api_session.get(f"/api/v1/users/{user_id}/roles/{role_id}")
    assert response.status_code == HTTPStatus.OK
    assert UserHasRole.model_validate(response.json())


@pytest.mark.parametrize("user_id, role_id", [("e460707d-4ff9-4e75-a0d7-1a02ae7db45f", 96606)])
@pytest.mark.asyncio
async def test_user_has_role_user_not_exist(api_session: AsyncClient, user_id: str, role_id: int):
    response = await api_session.get(f"/api/v1/users/{user_id}/roles/{role_id}")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert UserNotFoundError(response.json())
