from fastapi import Request
from app.database import Session
from app.middleware import get_user_info
from app.schemas.auth import JWTPayload


async def get_session():
    with Session() as session:
        return session


async def get_current_user(request: Request):
    user_info = await get_user_info(request=request)
    return user_info
