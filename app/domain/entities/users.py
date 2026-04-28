from dataclasses import dataclass


@dataclass(frozen=True)
class SignUpUser:
    username: str
    email: str
    password: str


@dataclass
class UserEntity:
    username: str
    email: str
    password_hash: bytes
