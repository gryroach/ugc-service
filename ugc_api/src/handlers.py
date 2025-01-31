# stdlib
from collections.abc import Callable, Coroutine
from typing import Any

# thirdparty
from fastapi import Request
from pymongo.errors import DuplicateKeyError
from starlette import status
from starlette.responses import JSONResponse, Response

# project
from exceptions.auth_exceptions import AuthError
from services.repositories.base import DocumentNotFoundException


async def auth_exception_handler(_: Request, exc: AuthError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": str(exc)},
    )


async def document_not_found_exception_handler(_: Request, exc: DocumentNotFoundException) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


async def document_duplicate_exception_handler(_: Request, __: DuplicateKeyError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Document already exists"},
    )


exception_handlers: dict[int | type[Exception], Callable[[Request, Any], Coroutine[Any, Any, Response]]] | None = {
    AuthError: auth_exception_handler,
    DocumentNotFoundException: document_not_found_exception_handler,
    DuplicateKeyError: document_duplicate_exception_handler,
}
