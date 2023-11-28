import uuid

import pytest_asyncio
from faker import Faker

from src.v1.auth.helpers import hash_password
from src.v1.roles.models import Role
from src.v1.users.models import User, UserLogin

fake = Faker()

user_password = fake.password()
user_data = {
    "id": "c94e5b5d-7992-466e-bebe-da86d6ddfa82",
    "username": fake.profile(fields=["username"])["username"],
    "full_name": fake.name(),
    "email": fake.email(),
    "password": hash_password(user_password),
}

role = {"id": 10000, "name": "UserTestRole"}

logins = [
    {
        "ip": fake.ipv4_public(),
        "user_agent": fake.user_agent(),
        "user_id": user_data["id"],
    }
    for _ in range(10)
]

conflict_user_data = {
    "id": str(uuid.uuid4()),
    "username": fake.profile(fields=["username"])["username"],
    "full_name": fake.name(),
    "email": fake.email(),
    "password": hash_password(user_password),
}


@pytest_asyncio.fixture(scope="session", autouse=True)
async def load_data(db):
    user = User(**user_data)
    db.add(user)
    await db.commit()
    await db.refresh(user)

    user_role = Role(**role)
    db.add(user_role)
    await db.commit()
    await db.refresh(user_role)

    user.roles.append(user_role)
    await db.commit()

    db.add_all([UserLogin(**login) for login in logins])
    await db.commit()

    conflict_user = User(**conflict_user_data)
    db.add(conflict_user)
    await db.commit()
