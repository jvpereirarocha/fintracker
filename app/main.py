from datetime import datetime
from fastapi import FastAPI
from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from app.database import User
from app.dependencies import get_session
from app.domain.entities.users import UserEntity
from app.schemas.users import CreateUser, UserPublic


app = FastAPI(title="Fintracker API")


users_router = APIRouter(
    prefix="/users",
    dependencies=[Depends(get_session)]
)


@users_router.post(
    "/",
    response_model=UserPublic,
)
async def create_user(user_schema: CreateUser):
    session = await get_session()
    user_already_exists = session.scalar(
        select(User).where(
            (User.email == user_schema.email)
            |
            (User.username == user_schema.username)
        )
    )
    if user_already_exists:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="User already exists"
        )
    user_entity = UserEntity.new_user(
        user_schema=user_schema
    )
    db_user = User(
        email=user_entity.email,
        password=user_entity.hashed_password,
        username=user_entity.username,
        transactions=[],
        updated_at=datetime.now()
    )
    session.add(db_user)
    session.commit()
    user_public = UserPublic(
        username=db_user.username,
        email=db_user.email
    )
    return user_public


app.include_router(router=users_router)
