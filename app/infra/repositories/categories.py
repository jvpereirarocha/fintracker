from typing import Sequence

from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy import select, func

from app.database import Category
from app.domain.abstractions.repositories import AbstractCategoryRepository
from app.domain.entities.categories import CategoryEntity, PartialUpdateCategory, SaveCategory


class AdapterCategoryRepo(AbstractCategoryRepository):
    def __init__(self, session: SQLAlchemySession) -> None:
        self.session = session

    def get_category_id_by_name(self, name: str) -> int:
        query = select(Category.category_id).where(func.lower(Category.name) == name.lower())
        result = self.session.execute(statement=query)
        return result.scalar() or 0
    
    def get_category_by_id(self, category_id: int) -> Category | None: # type: ignore
        query = select(Category).where(Category.category_id == category_id)
        result = self.session.execute(statement=query)
        return result.scalar_one_or_none()
    
    def fetch_one(self, category_id: int) -> CategoryEntity:
        category_dao = self.get_category_by_id(category_id=category_id)
        if not category_dao:
            raise ValueError("Category not found")
        
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
        query = (
            select(Category)
        )
        count_query = (
            select(func.count())
            .select_from(query.subquery())
        )
        total_result = self.session.execute(statement=count_query)
        total_count = total_result.scalar() or 0
        query = (
            query
            .order_by(Category.category_id.asc())
            .limit(limit=limit)
            .offset(offset=offset)
        )
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
            name=new_category.name,
            description=new_category.description,
            updated_at=new_category.updated_at,
        )
        self.session.add(category)
        self.session.commit()
        self.session.refresh(category)
        return CategoryEntity(category_id=category.category_id, name=category.name, description=category.description)

    def update(self, category_id: int, edit_category: PartialUpdateCategory) -> CategoryEntity:
        category = self.get_category_by_id(category_id=category_id)
        if not category:
            raise ValueError("Category not found")
        
        category.name = edit_category.name or category.name
        category.description = edit_category.description or category.description
        category.updated_at = edit_category.updated_at
        self.session.commit()
        self.session.refresh(category)
        return CategoryEntity(
            category_id=category.category_id,
            name=category.name,
            description=category.description
        )
    
    def delete(self, category_id: int) -> None:
        category = self.get_category_by_id(category_id=category_id)
        if not category:
            raise ValueError("Category not found")
        
        self.session.delete(category)
        self.session.commit()
        return None