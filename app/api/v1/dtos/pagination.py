from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class Pagination(BaseModel, Generic[T]):
    items: list[T]
    page: int
    total_count: int = Field(alias="totalItems")
    total_of_pages: int = Field(alias="totalOfPages")
    items_per_page: int = Field(alias="itemsPerPage")
    prev: int | None
    next_page: int | None = Field(alias="next")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
