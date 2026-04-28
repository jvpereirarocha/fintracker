from app.domain.exceptions.base import BaseDomainException, ExceptionType


class InvalidCredentialsException(BaseDomainException):
    def __init__(self, message: str) -> None:
        super().__init__(
            message=message, name="InvalidCredentials", type=ExceptionType.UNAUTHORIZED
        )


class AuthorizationHeaderMissingException(BaseDomainException):
    def __init__(self, message: str) -> None:
        super().__init__(
            message=message, name="AuthorizationHeaderMissing", type=ExceptionType.UNAUTHORIZED
        )


class InvalidTokenException(BaseDomainException):
    def __init__(self, message: str) -> None:
        super().__init__(message=message, name="InvalidToken", type=ExceptionType.UNAUTHORIZED)


class TokenExpiredException(BaseDomainException):
    def __init__(self, message: str) -> None:
        super().__init__(message=message, name="TokenExpired", type=ExceptionType.UNAUTHORIZED)


class PasswordsDontMatchException(BaseDomainException):
    def __init__(self, message: str) -> None:
        super().__init__(message=message, name="PasswordsDontMatch", type=ExceptionType.BAD_REQUEST)
