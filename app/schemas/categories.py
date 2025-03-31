from typing import Optional
from pydantic import BaseModel, ConfigDict


class NewCategorySchema(BaseModel):
    name: str
    description: str


class UpdateCategorySchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class NewCategoryResponse(BaseModel):
    detail: str = "New category created successfully"
    status_code: int = 201


class CategorySchemaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category_id: int
    name: str 
    description: str


class AllCategoriesResponse(BaseModel):
    results: list[CategorySchemaResponse]
