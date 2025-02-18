from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select

from app.config import Settings
from app.database import User
from app.dependencies import get_session
from app.domain.entities.users import UserEntity
from app.domain.value_objects.token import Token
from app.schemas.users import CreateUser, UserPublic, LoginUser
from app.schemas.auth import PublicToken


users_router = APIRouter(prefix="/users", dependencies=[Depends(get_session)])

settings = Settings()  # type: ignore


@users_router.post(
    "/register",
    response_model=UserPublic,
    status_code=HTTPStatus.CREATED,
)
async def create_user(user_schema: CreateUser):
    session = await get_session()
    user_already_exists = session.scalar(
        select(User).where(
            (User.email == user_schema.email) | (User.username == user_schema.username)
        )
    )
    if user_already_exists:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="User already exists"
        )
    user_entity = UserEntity.new_user(user_schema=user_schema)
    db_user = User(
        email=user_entity.email,
        password_hash=user_entity.password_hash,
        password_salt=user_entity.password_salt,
        username=user_entity.username,
        transactions=[],
        updated_at=datetime.now(),
    )
    session.add(db_user)
    session.commit()
    user_public = UserPublic(username=db_user.username, email=db_user.email)
    return user_public


@users_router.get("/", response_model=list[UserPublic], status_code=HTTPStatus.OK)
async def get_users():
    session = await get_session()
    statement = select(User.email.label("email"), User.username.label("username"))
    query = session.execute(statement=statement)
    all_users = query.all()
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
async def login(user: LoginUser) -> PublicToken:
    session = await get_session()
    db_user = session.scalar(select(User).where((User.username == user.username)))
    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="User doesn't exist"
        )

    user_authenticated = UserEntity.verify_password(
        plain_text_password=user.password,
        password_hash=db_user.password_hash,
    )

    if not user_authenticated:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid user credentials"
        )

    access_token = Token.create_token(
        username=user.username, token_expiration_time=timedelta(minutes=30)
    )
    return PublicToken(accessToken=access_token, tokenType=settings.TOKEN_TYPE)


@users_router.get(
    "/test",
)
def test_endpoint():
    return {"message": "The API is working :)"}
