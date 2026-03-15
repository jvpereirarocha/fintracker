from typing import Protocol


class AbstractRepository(Protocol):
    pass


class AbstractTransactionRepository(AbstractRepository):
    
    def fetch_all(self, *args, **kwargs): ...
    
    def fetch_one(self, *args, **kwargs): ...

    def save(self, *args, **kwargs): ...