import pytest_asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from src.v1.roles.models import Role

data = [
    {"id": 96606, "name": "Test_1"},
    {"id": 96608, "name": "Test_2"},
    {"id": 96610, "name": "Admin"},
    {"id": 96612, "name": "Moderator"},
    {"id": 96614, "name": "User"},
    {"id": 96616, "name": "Owner"},
    {"id": 96618, "name": "DevOps"}
]
data_id = [i.get("id") for i in data[2:]]
data_name = [n.get("name") for n in data[2:]]

@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_test_role(db: AsyncSession):
    for d in data:
        role = Role(**d)
        db.add(role)
        await db.commit()