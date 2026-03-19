from typing import Protocol, Any


class AbstractRepository(Protocol):
    pass


class AbstractTransactionRepository(AbstractRepository):
    
    def fetch_all(self, *args, **kwargs) -> Any: ...
    
    def fetch_one(self, *args, **kwargs) -> Any: ...

    def save(self, *args, **kwargs) -> Any: ...

    def update(self, *args, **kwargs) -> Any: ...

    def delete(self, *args, **kwargs) -> Any: ...


class AbstractUserRepository(AbstractRepository):
    
    def get_user_id_by_username(self, username: str) -> int | None: ...

    def save(self, *args, **kwargs) -> Any: ...


class AbstractCategoryRepository(AbstractRepository):
    
    def get_category_id_by_name(self, name: str) -> int | None: ...

    def save(self, *args, **kwargs) -> Any: ...

