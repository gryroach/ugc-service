# stdlib
import logging

# thirdparty
from beanie import Document, init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import OperationFailure

# project
from core.config import settings
from documents.bookmark import Bookmark
from documents.movie import Movie
from documents.reaction import Reaction
from documents.review import Review

logger = logging.getLogger(__name__)

COLLECTIONS: list[type[Document]] = [
    Movie,
    Reaction,
    Review,
    Bookmark,
]


async def init_mongodb() -> AsyncIOMotorClient:
    client: AsyncIOMotorClient = AsyncIOMotorClient(settings.mongo_dns)

    try:
        admin_db = client.get_database("admin")
        for collection in COLLECTIONS:
            collection_name = collection.Settings.name
            await admin_db.command(
                "shardCollection",
                f"{settings.mongo_db}.{collection_name}",
                key={"id": "hashed"},
            )
            logger.info(f"Шардирование коллекции {collection_name} настроено.")
    except OperationFailure as e:
        logger.error(f"Ошибка настройки шардирования коллекций: {e}")

    await init_beanie(
        database=client.get_database(settings.mongo_db),
        document_models=COLLECTIONS,
    )

    return client
