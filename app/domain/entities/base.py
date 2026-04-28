from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass()
class PagedResponse(Generic[T]):
    items: list[T]
    page: int
    total_count: int
    items_per_page: int

    @property
    def total_of_pages(self) -> int:
        if self.total_count == 0:
            return 1
        return (self.total_count + self.items_per_page - 1) // self.items_per_page

    @property
    def next_page(self) -> int | None:
        if self.page < self.total_of_pages:
            return self.page + 1
        return None

    @property
    def prev(self) -> int | None:
        if self.page > 1:
            return self.page - 1

        return None
