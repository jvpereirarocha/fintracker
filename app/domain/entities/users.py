from dataclasses import dataclass, field
from typing import Self
import bcrypt

from app.schemas.users import CreateUser


@dataclass
class UserEntity:
    user_id: int = field(init=False)
    username: str
    email: str
    password_hash: bytes
    password_salt: bytes

    @classmethod
    def _change_password_to_bytes(cls, password: str) -> bytes:
        return password.encode('utf-8')

    @classmethod
    def _get_hash_and_salt_password(cls, password_as_bytes: bytes) -> tuple[bytes, bytes]:
        salt = bcrypt.gensalt()
        generated_hash = bcrypt.hashpw(password_as_bytes, salt=salt)
        return generated_hash, salt

    @classmethod
    def encrypted_password(cls, password: str) -> tuple[bytes, bytes]:
        password_bytes: bytes = cls._change_password_to_bytes(
            password=password
        )
        password_hash, password_salt = cls._get_hash_and_salt_password(
            password_as_bytes=password_bytes
        )
        return password_hash, password_salt

    @classmethod
    def verify_password(cls, plain_text_password: str, password_hash: bytes) -> bool:
        return bcrypt.checkpw(
            password=plain_text_password.encode('utf-8'),
            hashed_password=password_hash
        )

    @classmethod
    def new_user(cls, user_schema: CreateUser) -> Self:
        password_hash, password_salt = cls.encrypted_password(
            password=user_schema.password,
        )
        return cls(
            username=user_schema.username,
            email=user_schema.email,
            password_hash=password_hash,
            password_salt=password_salt,
        )
