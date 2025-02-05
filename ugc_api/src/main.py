# stdlib
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

# thirdparty
import sentry_sdk
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

# project
from api.v1 import api_router as api_v1_router
from core.config import settings
from db.mongodb import init_mongodb
from handlers import exception_handlers
from middlewares.request_id import request_id_require

if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=str(settings.sentry_dsn),
        traces_sample_rate=1.0,
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    client = await init_mongodb()
    yield
    client.close()


app = FastAPI(
    title=settings.project_name,
    description="API сервис для работы с закладками, лайками и рецензиями",
    version="1.0.0",
    docs_url="/api-ugc/openapi",
    openapi_url="/api-ugc/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
    exception_handlers=exception_handlers,  # type: ignore
)

app.middleware("http")(request_id_require)

app.include_router(api_v1_router, prefix="/api-ugc/v1")
