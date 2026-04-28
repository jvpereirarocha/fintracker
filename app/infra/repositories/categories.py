from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session as SQLAlchemySession

from app.domain.abstractions.repositories import AbstractCategoryRepository
from app.domain.entities.categories import (
    CategoryEntity,
    PartialUpdateCategory,
    SaveCategory,
)
from app.infra.database.orm_category import Category


class AdapterCategoryRepo(AbstractCategoryRepository):
    def __init__(self, session: SQLAlchemySession) -> None:
        self.session = session

    def _get_category_dao(self, category_id: int) -> Category:
        """
        It doesn't check if the category exists

        We must handle it in the use case level

        :param category_id: int
        :return: Category
        """
        query = select(Category).where(Category.category_id == category_id)
        result = self.session.execute(statement=query)
        category = result.scalar_one()
        return category

    def get_category_id_by_name(self, name: str) -> int:
        query = select(Category.category_id).where(func.lower(Category.name) == name.lower())
        result = self.session.execute(statement=query)
        return result.scalar() or 0

    def get_category_by_id(self, category_id: int) -> CategoryEntity | None:  # type: ignore
        query = select(Category).where(Category.category_id == category_id)
        result = self.session.execute(statement=query)
        category_dao = result.scalar_one_or_none()
        if not category_dao:
            return None
        return CategoryEntity(
            category_id=category_dao.category_id,
            name=category_dao.name,
            description=category_dao.description,
        )

    def fetch_all(
        self,
        limit: int,
        offset: int,
    ) -> tuple[list[CategoryEntity], int]:
        query = select(Category)
        count_query = select(func.count()).select_from(query.subquery())
        total_result = self.session.execute(statement=count_query)
        total_count = total_result.scalar() or 0
        query = query.order_by(Category.category_id.asc()).limit(limit=limit).offset(offset=offset)
        results = self.session.execute(statement=query)
        categories: Sequence[Category] = results.scalars().all()
        category_entities = [
            CategoryEntity(
                category_id=category.category_id,
                name=category.name,
                description=category.description,
            )
            for category in categories
        ]
        return category_entities, total_count

    def save(self, new_category: SaveCategory) -> CategoryEntity:
        category = Category(
            name=new_category.name.capitalize(),
            description=new_category.description,
            updated_at=new_category.updated_at,
        )
        self.session.add(category)
        self.session.commit()
        self.session.refresh(category)
        return CategoryEntity(
            category_id=category.category_id,
            name=category.name,
            description=category.description,
        )

    def update(self, category_id: int, edit_category: PartialUpdateCategory) -> CategoryEntity:
        category = self._get_category_dao(category_id=category_id)
        category_name = edit_category.name or category.name
        category.name = category_name.capitalize()
        category.description = edit_category.description or category.description
        category.updated_at = edit_category.updated_at
        self.session.commit()
        self.session.refresh(category)
        return CategoryEntity(
            category_id=category.category_id,
            name=category.name,
            description=category.description,
        )

    def delete(self, category_id: int) -> None:
        category = self._get_category_dao(category_id=category_id)
        self.session.delete(category)
        self.session.commit()
        return None
