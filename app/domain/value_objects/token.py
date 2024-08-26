from enum import StrEnum, auto
from datetime import timedelta
from typing import Optional
import jwt
from app.config import Settings
from app.schemas.users import PublicToken


settings = Settings() # type: ignore


class TokenType(StrEnum):
    BEARER = auto()
    ACCESS = auto()


class Token:
    def __init__(self) -> None:
        pass

    @classmethod
    def create_token(
        cls,
        username: str,
        token_expiration_time: timedelta
    ) -> str:
        data = {"sub": username, "exp": token_expiration_time}
        encoded_jwt = jwt.encode(payload=data, key=settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @classmethod
    def get_token(cls, username: str, token_expiration_time: timedelta = timedelta(minutes=10)) -> PublicToken:
        token_content = cls.create_token(
            username=username,
            token_expiration_time=token_expiration_time
        )
        return PublicToken(access_token=token_content, token_type=TokenType.BEARER)
