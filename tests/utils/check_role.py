from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.v1.roles.models import Role, roles_to_users


async def check_create_role(db: AsyncSession, user_id: str, role_id: int) -> Role | None:
    statement = (
        select(Role)
        .join(roles_to_users)
        .filter(roles_to_users.c.user_id == user_id)
        .filter(roles_to_users.c.role_id == role_id)
    )
    query = await db.execute(statement)
    role = query.scalar_one_or_none()
    return role
