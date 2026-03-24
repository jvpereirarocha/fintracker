from datetime import datetime, timedelta, timezone

from fastapi import Request
import jwt

from app.config import Settings
from app.domain.abstractions.token import TokenProviderAbstraction
from app.domain.exceptions.auth import AuthorizationHeaderMissingException, InvalidTokenException, TokenExpiredException
from app.domain.value_objects.auth import JWTPayload, PublicToken


settings = Settings() # type: ignore


class TokenProvider(TokenProviderAbstraction):
    def _build_token_payload(
        self,
        username: str,
        expiration_date: datetime
    ) -> dict:
        return {
            "sub": username,
            "name": f"{username}'s token",
            "exp": expiration_date,
            "iat": datetime.now(tz=timezone.utc)
        }

    def encode_token(self, username: str, token_expiration: timedelta | None = None) -> PublicToken:
        if not token_expiration:
            token_expiration = timedelta(minutes=45)
        
        expiration_date = datetime.now(tz=timezone.utc) + token_expiration
        data = self._build_token_payload(username=username, expiration_date=expiration_date)
        encoded_jwt = jwt.encode(
            payload=data,
            key=settings.JWT_SECRET_KEY,
            algorithm=settings.ALGORITHM # type: ignore
        )
        return PublicToken(
            access_token=encoded_jwt,
            token_type=settings.TOKEN_TYPE
        )
    
    def decode_token(self, request: Request) -> JWTPayload:
        auth = request.headers.get("Authorization")
        if not auth:
            raise AuthorizationHeaderMissingException(
                message="Authorization header is missing"
            )
        try:
            token = auth.split()[1]
            payload = jwt.decode(
                jwt=token,
                key=settings.JWT_SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            token_is_expired = self._token_is_expired(
                expiration_time=payload.get("exp")
            )
            if token_is_expired:
                raise TokenExpiredException(message="Token is expired")
            return JWTPayload(
                sub=payload['sub'],
                exp=payload['exp']
            )
        except jwt.InvalidTokenError:
            raise InvalidTokenException(
                message="Token is invalid"
            )
        
    def _token_is_expired(self, expiration_time: int) -> bool:
        expiration_token_datetime = datetime.fromtimestamp(expiration_time)
        return expiration_token_datetime < datetime.now()