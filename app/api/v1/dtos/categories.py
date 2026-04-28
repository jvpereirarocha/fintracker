from pydantic import BaseModel, ConfigDict, Field

from app.api.v1.dtos.pagination import Pagination


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category_id: int = Field(serialization_alias="categoryId")
    name: str
    description: str


class SaveCategoryDTO(BaseModel):
    name: str
    description: str


class UpdatePartialCategoryDTO(BaseModel):
    name: str | None = None
    description: str | None = None


class PaginatedCategories(Pagination[CategoryResponse]):
    items: list[CategoryResponse] = Field(alias="results")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
