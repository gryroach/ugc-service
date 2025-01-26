from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from core.config import settings
from documents.movie import Movie


async def init_mongodb() -> AsyncIOMotorClient:
    client = AsyncIOMotorClient(settings.mongo_dns)
    await init_beanie(
        database=client.db_name,
        document_models=[
            Movie,
        ]
    )

    # Шардирование коллекции после инициализации
    await getattr(client, settings.mongo_db).command(
        "shardCollection",
        f"{settings.mongo_db}.{Movie.Settings.name}",
        key={"id": "hashed"}
    )
    return client