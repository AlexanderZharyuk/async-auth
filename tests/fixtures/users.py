import uuid

import pytest_asyncio
from faker import Faker

from src.v1.auth.helpers import hash_password
from src.v1.users.models import User

fake = Faker()

user_password = fake.password()
user_data = {
    "id": str(uuid.uuid4()),
    "username": fake.profile(fields=["username"])["username"],
    "full_name": fake.name(),
    "email": fake.email(),
    "password": hash_password(user_password),
    "is_superuser": False,
}


@pytest_asyncio.fixture(scope="session", autouse=True)
async def load_data(db):
    user = User(**user_data)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
