import uuid

import pytest_asyncio
from faker import Faker

from src.v1.auth.helpers import hash_password
from src.v1.roles.models import Role
from src.v1.users.models import User

fake = Faker()

role_user_password = fake.password()
role_user_data = {
    "id": str(uuid.uuid4()),
    "username": fake.profile(fields=["username"])["username"],
    "full_name": fake.name(),
    "email": fake.email(),
    "password": hash_password(role_user_password),
}

role_to_user = {"id": 99000, "name": "RoleTest"}


@pytest_asyncio.fixture(scope="session", autouse=True)
async def load_data_roles_to_users(db):
    user = User(**role_user_data)
    db.add(user)
    await db.commit()
    await db.refresh(user)

    user_role = Role(**role_to_user)
    db.add(user_role)
    await db.commit()
    await db.refresh(user_role)
