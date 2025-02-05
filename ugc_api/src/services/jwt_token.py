# stdlib
import logging

# thirdparty
import jwt
from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import ValidationError

# project
from core.config import settings
from exceptions.auth_exceptions import AuthError
from schemas.auth import JwtToken

logger = logging.getLogger(__name__)


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True) -> None:
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> JwtToken | None:  # type: ignore
        credentials: HTTPAuthorizationCredentials | None = await super().__call__(request)
        if credentials is None:
            return None

        return self.verify_jwt(credentials.credentials)

    @staticmethod
    def verify_jwt(jwt_token: str) -> JwtToken:
        try:
            token = jwt.decode(
                jwt_token,
                settings.jwt_public_key,
                algorithms=[settings.jwt_algorithm],
                options={'verify_exp': False},
            )
            return JwtToken(
                user=token.get('user'),
                session_version=token.get('session_version'),
                iat=token.get('iat'),
                exp=token.get('exp'),
                role=token.get('role'),
                type=token.get('type'),
            )
        except (jwt.exceptions.PyJWTError, ValidationError) as err:
            raise AuthError('JWT token error') from err
