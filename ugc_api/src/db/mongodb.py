# stdlib


# stdlib
import logging

# thirdparty
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import OperationFailure

# project
from core.config import settings
from documents.movie import Movie

logger = logging.getLogger(__name__)


async def init_mongodb() -> AsyncIOMotorClient:
    client: AsyncIOMotorClient = AsyncIOMotorClient(settings.mongo_dns)
    await init_beanie(
        database=client.get_database(settings.mongo_db),
        document_models=[
            Movie,
        ]
    )
    try:
        admin_db = client.get_database("admin")
        await admin_db.command(
            "shardCollection",
            f"{settings.mongo_db}.{Movie.Settings.name}",
            key={"id": "hashed"}
        )
    except OperationFailure as e:
        logger.error(f"Ошибка настройки шардирования коллекций: {e}")
    return client
