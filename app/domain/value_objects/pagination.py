from dataclasses import dataclass


@dataclass(frozen=True)
class PaginationParams:
    page: int
    page_size: int
        
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size