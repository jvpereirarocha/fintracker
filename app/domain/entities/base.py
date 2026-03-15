from dataclasses import dataclass
from typing import Generic, TypeVar, List


T = TypeVar("T")


@dataclass()
class PagedResponse(Generic[T]):
    items: List[T]
    page: int
    total_count: int
    items_per_page: int

    @property
    def total_of_pages(self) -> int:
        number_of_pages = (self.total_count + self.items_per_page - 1) // self.items_per_page
        if number_of_pages < 1:
            return 1
        return number_of_pages
    
    @property
    def next(self) -> int | None:
        if self.page == 1:
            return None
        return self.page - 1
    
    @property
    def prev(self) -> int | None:
        if self.page < self.total_of_pages:
            return self.page + 1
        
        return None