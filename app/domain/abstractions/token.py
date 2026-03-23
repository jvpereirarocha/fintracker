from abc import ABC, abstractmethod
from datetime import timedelta

from app.domain.value_objects.auth import JWTPayload, PublicToken


class TokenProviderAbstraction(ABC):
    @abstractmethod
    def encode_token(self, username: str, token_expiration: timedelta | None = None) -> PublicToken:
        ...

    @abstractmethod
    def decode_token(self, *args, **kwargs) -> JWTPayload:
        ...