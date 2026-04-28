from dataclasses import dataclass
from enum import StrEnum, auto


class TokenType(StrEnum):
    BEARER = auto()
    ACCESS = auto()


@dataclass(frozen=True)
class LoginCredentials:
    username: str
    password: str


@dataclass(frozen=True)
class UserLogin:
    username: str
    email: str
    password_hash: bytes


@dataclass(frozen=True)
class PublicToken:
    access_token: str
    token_type: str


@dataclass(frozen=True)
class JWTPayload:
    sub: str
    exp: int


@dataclass(frozen=True)
class SavedUser:
    username: str
    email: str
