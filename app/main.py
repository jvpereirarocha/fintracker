from fastapi import FastAPI
from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from app.database import User
from app.dependencies import get_db
from app.domain.entities.users import UserEntity
from app.schemas.users import CreateUser, UserPublic


app = FastAPI(title="Fintracker API")


users_router = APIRouter(
    prefix="/users",
    dependencies=[Depends(get_db)]
)


@users_router.post(
    "/",
    response_model=UserPublic,
)
async def create_user(user_schema: CreateUser):
    breakpoint()
    db = await get_db()
    user_already_exists = db.scalar(
        select(User).where(
            User.email == user_schema.email
            |
            User.username == user_schema.username
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
        username=user_entity.username
    )
    db.add(db_user)
    db.commit()
    db.refresh()
    user_public = UserPublic(
        username=db_user.username,
        email=db_user.email
    )
    return {"message": "User created!", "user": user_public}


app.include_router(router=users_router)
