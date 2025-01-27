# stdlib
import logging
from typing import Any

# thirdparty
import jwt
from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# project
from core.config import settings
from exceptions.auth_exceptions import AuthError

logger = logging.getLogger(__name__)


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True) -> None:
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict[str, Any] | None:  # type: ignore
        credentials: HTTPAuthorizationCredentials | None = await super().__call__(request)
        if credentials is None:
            return None

        return self.verify_jwt(credentials.credentials)

    @staticmethod
    def verify_jwt(jwt_token: str) -> dict[str, Any]:
        try:
            return jwt.decode(
                jwt_token,
                settings.jwt_public_key,
                algorithms=[settings.jwt_algorithm],
                options={"verify_exp": False},
            )
        except jwt.exceptions.PyJWTError:
            raise AuthError("JWT token error")
