from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.dependencies.base import get_db
from app.infra.auth.password_handler import AdapterPasswordHandler
from app.infra.auth.token import TokenProvider
from app.infra.repositories.users import AdapterUserRepo
from app.usecases.auth.login import LoginUseCase
from app.usecases.auth.create_user import SignUpUseCase


async def get_login_use_case(
    db: Session = Depends(get_db)
) -> LoginUseCase:
    user_repo = AdapterUserRepo(session=db)
    password_handler = AdapterPasswordHandler()
    token_provider = TokenProvider()
    return LoginUseCase(
        user_repo=user_repo,
        password_handler=password_handler,
        token_provider=token_provider
    )


async def get_sign_up_use_case(
    db: Session = Depends(get_db)
) -> SignUpUseCase:
    user_repo = AdapterUserRepo(session=db)
    password_handler = AdapterPasswordHandler()
    return SignUpUseCase(
        user_repo=user_repo,
        password_handler=password_handler,
    )