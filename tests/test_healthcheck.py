"""General tests."""
import pytest


@pytest.mark.asyncio
async def test_healthcheck(client):
    response = await client.get("/api/v1/healthcheck/")
    assert response.status_code == 200
    assert response.json() == {"status": "OK", "message": "Service is available right now."}
