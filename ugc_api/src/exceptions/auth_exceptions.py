# project
from exceptions.base import CustomException


class AuthError(CustomException):
    """Базовое исключение для всех ошибок аутентификации."""

    pass
