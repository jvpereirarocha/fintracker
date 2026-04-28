from app.domain.abstractions.password_handler import PasswordHandlerAbstraction
from app.domain.abstractions.repositories import AbstractUserRepository
from app.domain.abstractions.token import TokenProviderAbstraction
from app.domain.abstractions.usecases import AbstractUseCase
from app.domain.exceptions.auth import InvalidCredentialsException
from app.domain.exceptions.users import UserNotFoundException
from app.domain.value_objects.auth import LoginCredentials, PublicToken


class LoginUseCase(AbstractUseCase):
    def __init__(
        self,
        user_repo: AbstractUserRepository,
        password_handler: PasswordHandlerAbstraction,
        token_provider: TokenProviderAbstraction,
    ) -> None:
        self.user_repo = user_repo
        self.password_handler = password_handler
        self.token_provider = token_provider

    async def execute(self, credentials: LoginCredentials) -> PublicToken:
        user_id = self.user_repo.get_user_id_by_username(username=credentials.username)
        if not user_id:
            raise UserNotFoundException(message=f"User with {credentials.username} was not found")
        user = self.user_repo.get_user_password_by_id(user_id=user_id)
        user_authenticated = self.password_handler.verify_password(
            raw_password=credentials.password, hashed_password=user.password_hash
        )
        if not user_authenticated:
            raise InvalidCredentialsException(
                message=f"User {credentials.username} with invalid credentials"
            )

        token = self.token_provider.encode_token(
            username=user.username,
        )
        return token
