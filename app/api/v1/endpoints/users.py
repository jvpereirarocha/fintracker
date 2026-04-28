from http import HTTPStatus

from fastapi import APIRouter, Depends

from app.api.dependencies.auth import get_login_use_case, get_sign_up_use_case
from app.api.v1.dtos.auth import (
    CreateUserDTO,
    PublicTokenResponse,
    UserCredentialsDTO,
    UserPublicResponse,
)
from app.domain.entities.users import SignUpUser
from app.domain.value_objects.auth import LoginCredentials
from app.usecases.auth.create_user import SignUpUseCase
from app.usecases.auth.login import LoginUseCase

users_router = APIRouter(prefix="/users")


@users_router.post(
    path="/register", response_model=UserPublicResponse, status_code=HTTPStatus.CREATED
)
async def create_user(
    new_user: CreateUserDTO, use_case: SignUpUseCase = Depends(get_sign_up_use_case)
):
    sign_up = SignUpUser(
        username=new_user.username,
        password=new_user.password,
        email=new_user.email,  # type: ignore
    )
    return await use_case.execute(create_user=sign_up)


@users_router.post(path="/login", response_model=PublicTokenResponse, status_code=HTTPStatus.OK)
async def login(
    user_credentials: UserCredentialsDTO,
    use_case: LoginUseCase = Depends(get_login_use_case),
):
    user = LoginCredentials(username=user_credentials.username, password=user_credentials.password)
    return await use_case.execute(credentials=user)
