from app.domain.abstractions.usecases import AbstractUseCase
from app.domain.abstractions.password_handler import PasswordHandlerAbstraction
from app.domain.abstractions.repositories import AbstractUserRepository
from app.domain.entities.users import SignUpUser, UserEntity
from app.domain.exceptions.users import UserAlreadyExistsException
from app.domain.value_objects.auth import SavedUser


class SignUpUseCase(AbstractUseCase):
    def __init__(self, user_repo: AbstractUserRepository, password_handler: PasswordHandlerAbstraction):
        self.user_repo = user_repo
        self.password_handler = password_handler

    async def execute(
        self,
        create_user: SignUpUser
    ) -> SavedUser:
        
        user_already_exists = self.user_repo.user_already_exists(
            username=create_user.username,
            email=create_user.email
        )
        if user_already_exists:
            raise UserAlreadyExistsException(
                message=f"User with these infos already exists"
            )
        hashed_password = self.password_handler.encrypted_password(
            password=create_user.password
        )
        user = UserEntity(
            username=create_user.username,
            email=create_user.email,
            password_hash=hashed_password
        )
        saved_user = self.user_repo.save(user=user)
        return saved_user
