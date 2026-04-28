from enum import StrEnum, auto


class ExceptionType(StrEnum):
    BAD_REQUEST = auto()
    UNAUTHORIZED = auto()
    FORBIDDEN = auto()
    NOT_FOUND = auto()
    INTERNAL_SERVER_ERROR = auto()


class BaseDomainException(Exception):
    def __init__(self, message: str, name: str, type: ExceptionType):
        self.message = message
        self.name = name
        self.type = type
        super().__init__(self.message)
