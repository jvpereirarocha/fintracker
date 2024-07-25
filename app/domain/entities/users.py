from dataclasses import dataclass, field
from typing import Self
import bcrypt

from app.schemas.users import CreateUser


@dataclass
class UserEntity:
    user_id: int = field(init=False)
    username: str
    hashed_password: bytes
    email: str

    @classmethod
    def _change_password_to_bytes(cls, password: str) -> bytes:
        return bytes(password.encode('utf-8'))
    
    @classmethod
    def _hash_password(cls, password_as_bytes: bytes) -> bytes:
        return bcrypt.hashpw(password_as_bytes, bcrypt.gensalt())

    @classmethod
    def encrypted_password(cls, password: str) -> bytes:
        password_bytes: bytes = cls._change_password_to_bytes(
            password=password
        )
        hashed_password = cls._hash_password(
            password_as_bytes=password_bytes
        )
        return hashed_password
    
    @classmethod
    def new_user(cls, user_schema: CreateUser) -> Self:
        return cls(
            username=user_schema.username,
            hashed_password=cls.encrypted_password(
                password=user_schema.password
            ),
            email=user_schema.email
        )