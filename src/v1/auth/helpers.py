import hashlib
from datetime import datetime, timedelta

from jose import jwt, JWTError
from passlib.hash import pbkdf2_sha256
from pydantic import UUID4

from src.db.redis import BlacklistSignatureStorage
from src.core.config import settings
from src.v1.auth.schemas import JWTTokens
from src.v1.auth.exceptions import UnauthorizedError, InvalidTokenError


# TODO(alexander.zharyuk): Improve generation. Maybe add some salt?
def hash_password(password: str) -> str:
    """Generates a hashed version of the provided password."""
    return pbkdf2_sha256.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify hash password"""
    return pbkdf2_sha256.verify(password, hashed_password)


def generate_user_signature(username: str) -> str:
    """Create user signature based on his username and current timestamp"""
    signature = username + str(datetime.now().timestamp())
    hashed_signature = hashlib.sha256(signature.encode())
    return hashed_signature.hexdigest()


def generate_jwt(payload: dict, access_jti: str, refresh_jti: UUID4) -> JWTTokens:
    """Generate JWT-pair"""
    access_token_expire_date = datetime.now() + timedelta(
        seconds=settings.jwt_access_expire_time_in_seconds
    )
    refresh_token_expire_date = datetime.now() + timedelta(
        seconds=settings.jwt_refresh_expire_time_in_seconds
    )
    access_token_payload = {"exp": access_token_expire_date, **payload}
    refresh_token_payload = {"exp": refresh_token_expire_date}

    access_token = jwt.encode(
        access_token_payload,
        algorithm=settings.jwt_algorithm,
        key=settings.jwt_secret_key,
        headers={"jti": access_jti},
    )
    refresh_token = jwt.encode(
        refresh_token_payload,
        algorithm=settings.jwt_algorithm,
        key=settings.jwt_secret_key,
        headers={"jti": str(refresh_jti)},
    )
    return JWTTokens(access_token=access_token, refresh_token=refresh_token)


def decode_jwt(token: str) -> dict:
    """Decode access / refresh tokens payload"""
    return jwt.decode(
            token, 
            key=settings.jwt_secret_key, 
            algorithms=[settings.jwt_algorithm]
        )


async def validate_jwt(blacklist_tokens_storage: BlacklistSignatureStorage, token: str):
    """Validate that token is not in blacklists"""
    try:
        token_payload = decode_jwt(token)
    except JWTError:
        raise InvalidTokenError()
    token_headers = jwt.get_unverified_header(token)

    user_id = token_payload.get("user_id")
    token_signature = token_headers.get("jti")

    if token_signature == await blacklist_tokens_storage.get(user_id):
        raise UnauthorizedError()
