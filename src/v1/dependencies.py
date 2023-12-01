from fastapi import Depends
from fastapi.security import APIKeyCookie

from src.core.config import settings
from src.db.postgres import DatabaseSession
from src.v1.auth.exceptions import UnauthorizedError
from src.v1.auth.helpers import decode_jwt
from src.v1.users.models import User
from src.v1.users.service import UserService

cookie_scheme = APIKeyCookie(name=settings.sessions_cookie_name)


async def get_current_user(
    db: DatabaseSession, token: str | None = Depends(cookie_scheme)
) -> User:
    """Get current user"""
    token_payload = decode_jwt(token)
    return await UserService.get(
        db_session=db, attribute="id", attribute_value=token_payload.get("user_id")
    )


def require_roles(allowed_roles: list[str]):
    """Check user roles for route"""

    async def check_user_roles(user: User = Depends(get_current_user)) -> User:
        if user.is_superuser:
            return user
        user_roles = set([role.name for role in user.roles])
        if set(allowed_roles).intersection(user_roles):
            return user
        else:
            raise UnauthorizedError

    return check_user_roles
