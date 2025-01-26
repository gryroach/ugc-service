from fastapi import Request
from starlette import status
from starlette.responses import JSONResponse

from exceptions.auth_exceptions import AuthError


async def auth_exception_handler(_: Request, exc: AuthError):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": str(exc)},
    )


exception_handlers = {
    AuthError: auth_exception_handler,
}
