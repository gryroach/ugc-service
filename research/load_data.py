import asyncio
import os

import asyncpg
import numpy as np
from joblib import Parallel, delayed
from motor.motor_asyncio import AsyncIOMotorClient
from tqdm import tqdm

from constants import (
    INPUT_DIR,
    MONGO_URI,
    NUM_WORKERS,
    POSTGRES_DSN,
    TEST_RANGE,
)


async def write_postgres_batch(user_ids, movie_ids):
    """
    Асинхронная запись в PostgreSQL.
    """
    conn = await asyncpg.connect(POSTGRES_DSN)
    await conn.executemany(
        "INSERT INTO likes (user_id, movie_id) VALUES ($1, $2);",
        zip(user_ids, movie_ids),
    )
    await conn.close()


async def write_mongo_batch(user_ids, movie_ids):
    """
    Асинхронная запись в MongoDB с преобразованием np.int64 в обычный int.
    """
    client = AsyncIOMotorClient(MONGO_URI)
    db = client.test_db
    likes = db.likes
    # Преобразуем np.int64 в int
    data = [
        {"user_id": int(uid), "movie_id": int(mid)}
        for uid, mid in zip(user_ids, movie_ids)
    ]
    await likes.insert_many(data)
    client.close()


def process_batch(file_index, write_function):
    """
    Загружает данные из `.npy` и записывает их в базу данных.
    """
    user_ids = np.load(
        os.path.join(INPUT_DIR, f"user_ids_batch_{file_index}.npy")
    )
    movie_ids = np.load(
        os.path.join(INPUT_DIR, f"movie_ids_batch_{file_index}.npy")
    )
    # Преобразуем np.int64 в int перед отправкой в MongoDB
    user_ids = user_ids.astype(int)
    movie_ids = movie_ids.astype(int)

    asyncio.run(write_function(user_ids, movie_ids))


def parallel_data_loading(total_batches, write_function):
    """
    Параллельно обрабатывает батчи данных.
    """
    Parallel(n_jobs=NUM_WORKERS)(
        delayed(process_batch)(i, write_function)
        for i in tqdm(range(total_batches), desc="Loading batches")
    )


async def initialize_postgres():
    """
    Создаёт таблицу likes в PostgreSQL, если она не существует.
    """
    conn = await asyncpg.connect(POSTGRES_DSN)
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS likes (
            user_id INT NOT NULL,
            movie_id INT NOT NULL
        );
        """
    )
    await conn.close()


async def initialize_mongo():
    """
    Создает.
    """
    client = AsyncIOMotorClient(MONGO_URI)
    db = client.test_db
    client.close()


async def initialize_databases():
    """
    Инициализирует базы данных (PostgreSQL и MongoDB).
    """
    await asyncio.gather(initialize_postgres(), initialize_mongo())


async def get_mongo_record_count():
    """
    Запрос на подсчёт количества документов в коллекции MongoDB.
    """
    client = AsyncIOMotorClient(MONGO_URI)
    db = client.test_db
    count = await db.likes.count_documents({})
    client.close()
    return count


async def get_postgres_record_count():
    """
    Запрос на подсчёт количества записей в таблице PostgreSQL.
    """
    conn = await asyncpg.connect(POSTGRES_DSN)
    result = await conn.fetchval("SELECT COUNT(*) FROM likes;")
    await conn.close()
    return result


if __name__ == "__main__":
    print("Initializing databases...")
    asyncio.run(initialize_databases())
    print("Testing existing data in PostgreSQL and MongoDB...")
    postgres_count = asyncio.run(get_postgres_record_count())
    mongo_count = asyncio.run(get_mongo_record_count())
    print(postgres_count)
    print(mongo_count)
    total_batches = len(
        [f for f in os.listdir(INPUT_DIR) if f.startswith("user_ids")]
    )
    if postgres_count < TEST_RANGE:
        print("Loading data into PostgreSQL...")
        parallel_data_loading(total_batches, write_postgres_batch)
    if mongo_count < TEST_RANGE:
        print("Loading data into MongoDB...")
        parallel_data_loading(total_batches, write_mongo_batch)
