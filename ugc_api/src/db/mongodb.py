# stdlib
import logging

# thirdparty
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import OperationFailure

# project
from core.config import settings
from documents.bookmark import Bookmark
from documents.movie import Movie
from documents.reaction import Reaction
from documents.review import Review

logger = logging.getLogger(__name__)


async def init_mongodb() -> AsyncIOMotorClient:
    client: AsyncIOMotorClient = AsyncIOMotorClient(settings.mongo_dns)

    try:
        admin_db = client.get_database("admin")
        await admin_db.command(
            "shardCollection",
            f"{settings.mongo_db}.{Movie.Settings.name}",
            key={"id": "hashed"},
        )
        await admin_db.command(
            "shardCollection",
            f"{settings.mongo_db}.{Reaction.Settings.name}",
            key={"id": "hashed"},
        )
        await admin_db.command(
            "shardCollection",
            f"{settings.mongo_db}.{Review.Settings.name}",
            key={"id": "hashed"},
        )
        await admin_db.command(
            "shardCollection",
            f"{settings.mongo_db}.{Bookmark.Settings.name}",
            key={"id": "hashed"},
        )
    except OperationFailure as e:
        logger.error(f"Ошибка настройки шардирования коллекций: {e}")

    await init_beanie(
        database=client.get_database(settings.mongo_db),
        document_models=[
            Movie,
            Reaction,
            Review,
            Bookmark,
        ],
    )

    return client
