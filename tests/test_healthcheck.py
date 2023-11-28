"""General tests."""
from http import HTTPStatus

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_healthcheck(api_session: AsyncClient):
    response = await api_session.get("/api/v1/healthcheck/")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"status": "OK", "message": "Service is available right now."}
