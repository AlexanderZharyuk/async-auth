import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.v1.roles.service import RoleService
from src.v1.users.service import UserService

data = {"user_id": "c94e5b5d-7992-466e-bebe-da86d6ddfa82", "role_id": 96606}

@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_test_role_to_users(db: AsyncSession):
    user = await UserService.get_by_id(db_session=db, user_id=data.get("user_id"))
    role = await RoleService.get_by_id(session=db, role_id=data.get("role_id"))
    user.roles.append(role)
    await db.commit()
