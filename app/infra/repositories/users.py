from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session as SQLAlchemySession

from app.domain.abstractions.repositories import AbstractUserRepository
from app.domain.entities.users import UserEntity
from app.domain.value_objects.auth import SavedUser, UserLogin
from app.infra.database.orm_user import User


class AdapterUserRepo(AbstractUserRepository):
    def __init__(self, session: SQLAlchemySession) -> None:
        self.session = session

    def get_user_id_by_username(self, username) -> int:
        query = select(User.user_id).where(User.username == username)
        result = self.session.execute(statement=query)
        return result.scalar() or 0

    def get_user_password_by_id(self, user_id: int) -> UserLogin:
        query = select(User).where(User.user_id == user_id)
        result = self.session.execute(statement=query)
        user_dao = result.scalars().first()
        user = UserLogin(
            username=user_dao.username,
            email=user_dao.email,
            password_hash=user_dao.password_hash,
        )
        return user

    def user_already_exists(self, username: str, email: str) -> bool:
        user_found = self.session.scalar(
            select(User).where((User.email == email) | (User.username == username))
        )
        return bool(user_found)

    def save(self, user: UserEntity) -> SavedUser:
        user_dao = User(
            email=user.email,
            username=user.username,
            password_hash=user.password_hash,
            updated_at=datetime.now(),
        )
        self.session.add(user_dao)
        self.session.commit()
        self.session.refresh(user_dao)
        return SavedUser(username=user_dao.username, email=user.email)
