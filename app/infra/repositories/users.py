from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy import select

from app.database import User
from app.domain.abstractions.repositories import AbstractUserRepository


class AdapterUserRepo(AbstractUserRepository):
    def __init__(self, session: SQLAlchemySession) -> None:
        self.session = session

    def get_user_id_by_username(self, username) -> int:
        query = select(User.user_id).where(User.username == username)
        result = self.session.execute(statement=query)
        return result.scalar() or 0