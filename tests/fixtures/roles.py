import pytest_asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from src.v1.roles.models import Role

data = [
    {"id": 96610, "name": "Admin"},
    {"id": 96612, "name": "Moderator"},
    {"id": 96614, "name": "User"},
    {"id": 96616, "name": "Owner"},
    {"id": 96618, "name": "DevOps"}
]
data_id = [i.get("id") for i in data]
data_name = [n.get("name") for n in data]

@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_test_role(db: AsyncSession):
    for d in data:
        role = Role(id=d.get("id"), name=d.get("name"))
        db.add(role)
        await db.commit()