from dataclasses import dataclass


@dataclass(frozen=True)
class SaveCategory:
    name: str
    description: str


@dataclass(frozen=True)
class CategoryEntity:
    category_id: int
    name: str
    description: str