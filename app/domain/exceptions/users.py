from app.domain.exceptions.base import BaseDomainException, ExceptionType


class UserNotFoundException(BaseDomainException):
    def __init__(self, message: str = "User not found"):
        super().__init__(
            message=message,
            name="UserNotFound",
            type=ExceptionType.NOT_FOUND
        )


class UserAlreadyExistsException(BaseDomainException):
    def __init__(self, message: str = "User already exists"):
        super().__init__(
            message=message,
            name="UserAlreadyExists",
            type=ExceptionType.BAD_REQUEST
        )