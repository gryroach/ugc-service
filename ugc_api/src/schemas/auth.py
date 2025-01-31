# stdlib
from uuid import UUID

# thirdparty
from pydantic import BaseModel


class JwtToken(BaseModel):
    user: UUID
    session_version: int
    iat: int
    exp: int
    role: str
    type: str
