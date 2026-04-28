from abc import ABC, abstractmethod


class PasswordHandlerAbstraction(ABC):
    @abstractmethod
    def encrypted_password(self, password: str) -> bytes:
        pass

    @abstractmethod
    def verify_password(self, raw_password: str, hashed_password: bytes) -> bool:
        pass
