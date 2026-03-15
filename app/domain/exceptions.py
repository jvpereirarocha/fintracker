class BaseException(Exception):
    def __init__(self, message: str, *args):
        self.message = message
        super().__init__(*args)

    def __repr__(self):
        return f"{self.message}"

class InvalidMonth(BaseException):
    def __init__(self, message, *args):
        super().__init__(message, *args)