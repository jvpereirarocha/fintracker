from fastapi import Request

from app.database import Session
from app.middleware import get_user_info


async def get_current_user(request: Request):
    user_info = await get_user_info(request=request)
    request.state.user = user_info
    return user_info

def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()