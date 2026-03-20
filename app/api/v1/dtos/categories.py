from dataclasses import Field

from pydantic import BaseModel, ConfigDict

from app.api.v1.dtos.pagination import Pagination


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category_id: int
    name: str 
    description: str


class SaveTransactionDTO(BaseModel):
    name: str
    description: str


class PaginatedCategories(Pagination[CategoryResponse]):
    items: list[CategoryResponse] = Field(alias="categories")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
