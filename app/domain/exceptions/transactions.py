from app.domain.exceptions.base import BaseDomainException, ExceptionType


class TransactionNotFoundException(BaseDomainException):
    def __init__(self, message: str = "Transaction not found"):
        super().__init__(message=message, name="TransactionNotFound", type=ExceptionType.NOT_FOUND)


class TransactionAlreadyExistsException(BaseDomainException):
    def __init__(self, message: str = "Transaction already exists"):
        super().__init__(
            message=message, name="TransactionAlreadyExists", type=ExceptionType.BAD_REQUEST
        )


class InvalidFormatDateException(BaseDomainException):
    def __init__(self, message: str) -> None:
        super().__init__(message=message, name="InvalidDateFormat", type=ExceptionType.BAD_REQUEST)


class InvalidTransactionStatusException(BaseDomainException):
    def __init__(self, message: str) -> None:
        super().__init__(
            message=message, name="InvalidTransactionStatus", type=ExceptionType.BAD_REQUEST
        )


class InvalidFormatCurrencyException(BaseDomainException):
    def __init__(self, message: str) -> None:
        super().__init__(
            message=message, name="InvalidFormatCurrency", type=ExceptionType.BAD_REQUEST
        )


class DueDateNotProvidedException(BaseDomainException):
    def __init__(self, message: str) -> None:
        super().__init__(message=message, name="DueDateNotProvided", type=ExceptionType.BAD_REQUEST)
