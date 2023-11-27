import pytest

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tests.fixtures.roles import data_id, data_name
from src.v1.roles.models import Role
from src.v1.roles.schemas import SeveralRolesResponse, SingleRoleResponse
from src.v1.roles.exceptions import RoleAlreadyExistsError, RoleNotFound


@pytest.mark.asyncio
async def test_get(api_session: AsyncClient):
    response = await api_session.get("/api/v1/roles/")
    assert response.status_code == 200
    assert SeveralRolesResponse.model_validate(response.json())


@pytest.mark.parametrize("name", ["Tester"])
@pytest.mark.asyncio
async def test_create(api_session: AsyncClient, db: AsyncSession, name: str):
    request_data = {
        "name": name
    }
    response = await api_session.post(
        "/api/v1/roles/",
        json=request_data
    )
    statement = select(Role).where(Role.name == name)
    query = await db.execute(statement)
    role = query.scalar_one_or_none()
    assert response.status_code == 201
    assert SingleRoleResponse.model_validate(response.json())
    assert role != None


@pytest.mark.parametrize("name", ["Tester"])
@pytest.mark.asyncio
async def test_save_role_that_exists(api_session: AsyncClient, name: str):
    request_data = {
        "name": name
    }
    response = await api_session.post(
        "/api/v1/roles/",
        json=request_data
    )
    assert response.status_code == 400
    assert RoleAlreadyExistsError(response.json())


@pytest.mark.parametrize("id", data_id)
@pytest.mark.parametrize("name", data_name)
@pytest.mark.asyncio
async def test_update(api_session: AsyncClient, db: AsyncSession, id: int, name: str):
    name = f"{name}_{id}"
    request_data = {
        "name": name
    }
    response = await api_session.patch(
        f"/api/v1/roles/{id}",
        json=request_data
    )
    statement = select(Role).where(Role.name == name)
    query = await db.execute(statement)
    role = query.scalar_one_or_none()
    assert response.status_code == 200
    assert SingleRoleResponse.model_validate(response.json())
    assert role != None


@pytest.mark.parametrize("id, name", [(96620, "Tester")])
@pytest.mark.asyncio
async def test_update_role_that_not_exist(api_session: AsyncClient, id: int, name: str):
    request_data = {
        "name": name
    }
    response = await api_session.patch(
        f"/api/v1/roles/{id}",
        json=request_data
    )
    assert response.status_code == 404
    assert RoleNotFound(response.json())


@pytest.mark.parametrize("id", data_id)
@pytest.mark.asyncio
async def test_delete(api_session: AsyncClient, db: AsyncSession, id: int):
    response = await api_session.delete(f"/api/v1/roles/{id}")
    role = await db.get(Role, id)
    assert response.status_code == 200
    assert role == None


@pytest.mark.parametrize("id", [96620])
@pytest.mark.asyncio
async def test_delete_role_that_not_exist(api_session: AsyncClient, id: int):
    response = await api_session.delete(f"/api/v1/roles/{id}")
    assert response.status_code == 404
    assert RoleNotFound(response.json())
