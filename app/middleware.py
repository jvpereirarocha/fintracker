from datetime import datetime, time
from http import HTTPStatus
from fastapi import Request
import jwt
from fastapi.exceptions import HTTPException
from app.config import Settings
from app.schemas.auth import JWTPayload

settings = Settings()  # type: ignore


def check_if_token_is_expired(expiration_time: int) -> bool:
    expiration_token_datetime = datetime.fromtimestamp(expiration_time)
    return expiration_token_datetime < datetime.now()


async def get_user_info(request: Request) -> JWTPayload:
    auth = request.headers.get("Authorization")
    if not auth:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Authorization header is missing",
        )

    try:
        token = auth.split()[1]
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_is_expired = check_if_token_is_expired(expiration_time=payload.get("exp"))
        if token_is_expired:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="Token is expired"
            )
        return JWTPayload(**payload)
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="Token is invalid"
        )
