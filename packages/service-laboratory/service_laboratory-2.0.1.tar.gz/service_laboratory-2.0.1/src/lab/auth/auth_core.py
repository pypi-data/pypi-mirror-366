from datetime import datetime, timedelta
from typing import Any

import bcrypt
import jwt
from pydantic import BaseModel

from ..settings import settings

DEFAULT_TIME_DELTA = timedelta(days=30)
ALGORITHM = "HS256"


class Token(BaseModel):
    exp: datetime
    sub: str
    payload: Any


def decode_jwt_token(
    token: str,
) -> Token:
    return Token(
        **jwt.decode(
            token,
            settings.secret_key,
            algorithms=[ALGORITHM],
        )
    )


def encode_jwt_token(
    payload,
    expiration: timedelta = DEFAULT_TIME_DELTA,
) -> str:
    token = Token(
        exp=datetime.now() + expiration,
        sub="auth",
        payload=payload,
    )
    return jwt.encode(
        {
            "exp": token.exp,
            "sub": token.sub,
            "payload": token.payload,
        },
        settings.secret_key,
        algorithm=ALGORITHM,
    )


def hash_password(
    password: str,
) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")


def check_password(
    password: str,
    hashed_password: str,
) -> bool:
    try:
        if bcrypt.checkpw(
            password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        ):
            return True
    except ValueError:
        return False

    return False
