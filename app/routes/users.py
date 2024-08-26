from datetime import datetime
from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from app.database import User
from app.dependencies import get_session
from app.domain.entities.users import UserEntity
from app.schemas.users import CreateUser, UserPublic

users_router = APIRouter(
    prefix="/users",
    dependencies=[Depends(get_session)]
)


@users_router.post(
    "/",
    response_model=UserPublic,
    status_code=HTTPStatus.CREATED,
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


@users_router.get("/", response_model=list[UserPublic], status_code=HTTPStatus.OK)
async def get_users():
    session = await get_session()
    all_users = session.scalars(
        select(User.email, User.username)
    )
    if not all_users:
        return []

    public_users_list = []
    for user in all_users:
        user_public = UserPublic(
            username=user.username,
            email=user.email,
        )
        public_users_list.append(user_public)

    return public_users_list


@users_router.post("/login", response_model=PublicToken, status_code=HTTPStatus.OK)


@users_router.get(
    "/test",
)
def test_endpoint():
    return {"message": "The API is working :)"}
