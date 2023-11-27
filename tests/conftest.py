import asyncio

import pytest

pytest_plugins = (
    "tests.fixtures.core",
    "tests.fixtures.users",
    "tests.fixtures.roles",
    "tests.fixtures.roles_to_users",
)


@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()
