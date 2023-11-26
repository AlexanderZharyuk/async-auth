import asyncio
import pytest
import pytest_asyncio

from httpx import AsyncClient

from src.main import app

@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session", autouse=True)
async def api_session():
    client = AsyncClient(app=app, base_url="http://api_test")
    yield client
    await client.aclose()
