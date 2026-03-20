from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class SaveCategory:
    name: str
    description: str
    updated_at: datetime = datetime.now()

@dataclass(frozen=True)
class PartialUpdateCategory:
    name: str | None
    description: str | None
    updated_at: datetime = datetime.now()


@dataclass(frozen=True)
class CategoryEntity:
    category_id: int
    name: str
    description: str