from abc import ABC, abstractmethod

class AbstractUseCase(ABC):
    async def execute(self, *args, **kwargs) -> any: ...