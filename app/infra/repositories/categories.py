from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy import select, func

from app.database import Category
from app.domain.abstractions.repositories import AbstractCategoryRepository


class AdapterCategoryRepo(AbstractCategoryRepository):
    def __init__(self, session: SQLAlchemySession) -> None:
        self.session = session

    def get_category_id_by_name(self, name: str) -> int:
        query = select(Category.category_id).where(func.lower(Category.name) == name.lower())
        result = self.session.execute(statement=query)
        return result.scalar() or 0