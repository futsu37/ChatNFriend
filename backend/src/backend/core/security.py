import jwt
from backend.core.config import settings
from datetime import datetime, UTC, timedelta
from typing import Any
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher
from pwdlib import PasswordHash

ALGORITHM = "HS256"

password_hash = PasswordHash(
    (
        BcryptHasher(),
        Argon2Hasher()
    )
)

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify(plain_password: str, hashed_password: str
) -> tuple[bool, str | None]:
    return password_hash.verify_and_update(plain_password,hashed_password)

def create_access_token(sub: str | Any) -> str:
    expire_token_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(UTC) + expire_token_delta
    to_encode = {"sub":str(sub),"exp":expire}
    token = jwt.encode(to_encode,settings.SECRET_KEY,algorithm=ALGORITHM)
    return token