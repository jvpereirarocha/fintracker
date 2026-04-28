import bcrypt

from app.domain.abstractions.password_handler import PasswordHandlerAbstraction


class AdapterPasswordHandler(PasswordHandlerAbstraction):
    @classmethod
    def _encoded_password(cls, password: str) -> bytes:
        return password.encode("utf-8")

    @classmethod
    def _get_password_hash(cls, password_as_bytes: bytes) -> bytes:
        salt = bcrypt.gensalt()
        generated_hash = bcrypt.hashpw(password=password_as_bytes, salt=salt)
        return generated_hash

    def verify_password(self, raw_password: str, hashed_password: bytes) -> bool:
        return bcrypt.checkpw(
            password=self._encoded_password(password=raw_password), hashed_password=hashed_password
        )

    def encrypted_password(self, password: str) -> bytes:
        password_as_bytes = self._encoded_password(password=password)
        password_hash = self._get_password_hash(password_as_bytes=password_as_bytes)
        return password_hash
