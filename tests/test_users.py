"""Users API tests."""
import pytest

from tests.fixtures.users import user_data


@pytest.mark.asyncio
async def test_user_success(client):
    user_id = user_data["id"]
    response = await client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 200

    data = response.json()["data"]
    assert data["id"] == user_data["id"]
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert data["username"] == user_data["username"]
    assert data["last_login"] is None
    assert data["created_at"] is not None
    assert data["updated_at"] is None
    assert data["roles"] == []
