import hashlib
from datetime import datetime

from passlib.hash import pbkdf2_sha256


# TODO(alexander.zharyuk): Improve generation. Maybe add some salt?
def hash_password(password: str) -> str:
    """Generates a hashed version of the provided password."""
    return pbkdf2_sha256.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify hash password"""
    return pbkdf2_sha256.verify(password, hashed_password)


async def generate_user_signature(username: str) -> str:
    """Create user signature based on his username and current timestamp"""
    signature = username + str(datetime.now().timestamp())
    hashed_signature = hashlib.sha256(signature.encode())
    return hashed_signature.hexdigest()
