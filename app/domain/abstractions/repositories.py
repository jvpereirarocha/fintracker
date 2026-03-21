from datetime import date
from decimal import Decimal
from typing import Protocol, Any, Literal

from app.domain.entities.categories import CategoryEntity, PartialUpdateCategory
from app.domain.value_objects.dashboard import DashboardValues


class AbstractRepository(Protocol):
    pass


class AbstractTransactionRepository(AbstractRepository):
    
    def fetch_all(self, *args, **kwargs) -> Any: ...
    
    def fetch_one(self, *args, **kwargs) -> Any: ...

    def save(self, *args, **kwargs) -> Any: ...

    def update(self, *args, **kwargs) -> Any: ...

    def delete(self, *args, **kwargs) -> Any: ...

    def exists(self, transaction_id: int) -> bool: ...

    def get_sum_of_transactions_by_interval(
        self,
        user_id: int,
        start_date: date,
        end_date: date,
    ) -> DashboardValues: ...


class AbstractUserRepository(AbstractRepository):
    
    def get_user_id_by_username(self, username: str) -> int | None: ...

    def save(self, *args, **kwargs) -> Any: ...


class AbstractCategoryRepository(AbstractRepository):
    
    def get_category_id_by_name(self, name: str) -> int: ...

    def get_category_by_id(self, category_id: int) -> CategoryEntity | None: ...

    def save(self, *args, **kwargs) -> Any: ...

    def fetch_all(self, *args, **kwargs) -> Any: ...

    def fetch_one(self, *args, **kwargs) -> Any: ...

    def update(self, category_id: int, edit_category: PartialUpdateCategory) -> CategoryEntity: ...

    def delete(self, category_id: int) -> None: ...

