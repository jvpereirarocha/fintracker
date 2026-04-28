from app.domain.exceptions.base import BaseDomainException, ExceptionType


class CategoryNotFoundException(BaseDomainException):
    def __init__(self, message: str = "Category not found"):
        super().__init__(message=message, name="CategoryNotFound", type=ExceptionType.NOT_FOUND)


class CategoryAlreadyExistsException(BaseDomainException):
    def __init__(self, message: str = "Category already exists"):
        super().__init__(
            message=message, name="CategoryAlreadyExists", type=ExceptionType.BAD_REQUEST
        )
