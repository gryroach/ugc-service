# stdlib
from collections.abc import Callable

# thirdparty
from fastapi import Request, status
from fastapi.responses import ORJSONResponse


async def request_id_require(
    request: Request,
    call_next: Callable,
) -> ORJSONResponse:
    request_id = request.headers.get("X-Request-Id")
    if not request_id:
        return ORJSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "X-Request-Id is required"},
        )
    response = await call_next(request)
    return response
