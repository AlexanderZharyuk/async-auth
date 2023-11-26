import pytest

from httpx import AsyncClient

from src.main import app
from src.v1.roles.schemas import SeveralRolesResponse


@pytest.mark.asyncio
async def test_get_roles(api_session):
    response = await api_session.get("/api/v1/roles/")
    assert response.status_code == 200
    assert SeveralRolesResponse.model_validate(response.json())