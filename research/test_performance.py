import random
import statistics
import time
from concurrent.futures import ThreadPoolExecutor

import matplotlib.pyplot as plt
import psycopg2
from pymongo import ASCENDING, MongoClient

from constants import (
    MONGO_URI,
    NUM_OPERATIONS_PER_WAVE,
    NUM_THREADS,
    NUM_WAVES,
    POSTGRES_DSN,
)


def postgres_get_liked_movies(user_id, conn):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT movie_id FROM likes WHERE user_id = %s", (user_id,)
        )
        return cur.fetchall()


def postgres_get_movie_likes(movie_id, conn):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) FROM likes WHERE movie_id = %s", (movie_id,)
        )
        return cur.fetchone()[0]


def postgres_add_like(user_id, movie_id, conn):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO likes (user_id, movie_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            (user_id, movie_id),
        )
        conn.commit()


def postgres_get_sample_data(limit, conn):
    offset = random.randint(0, max(1, 10000 - limit))
    with conn.cursor() as cur:
        cur.execute(
            "SELECT user_id, movie_id FROM likes OFFSET %s LIMIT %s",
            (offset, limit),
        )
        return cur.fetchall()


def mongo_get_liked_movies(user_id, collection):
    return list(
        collection.find({"user_id": user_id}, {"movie_id": 1, "_id": 0})
    )


def mongo_get_movie_likes(movie_id, collection):
    return collection.count_documents({"movie_id": movie_id})


def mongo_add_like(user_id, movie_id, collection):
    collection.insert_one({"user_id": user_id, "movie_id": movie_id})


def mongo_get_sample_data(limit, collection):
    return list(
        collection.find({}, {"user_id": 1, "movie_id": 1, "_id": 0}).limit(
            limit
        )
    )


def create_mongo_indexes(collection):
    collection.create_index(
        [("user_id", ASCENDING)],
        name="user_id_index",
        unique=False,
        background=True,
    )
    collection.create_index(
        [("movie_id", ASCENDING)],
        name="movie_id_index",
        unique=False,
        background=True,
    )
    print("Индексы для MongoDB созданы (если они не существовали).")


def create_postgres_indexes(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_user_id ON likes(user_id);
        """
        )
        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_movie_id ON likes(movie_id);
        """
        )
        conn.commit()
        print("Индексы для PostgreSQL созданы (если они не существовали).")


def benchmark_operation(func, args):
    start_time = time.time()
    func(*args)
    return time.time() - start_time


def run_benchmark():
    postgres_conn = psycopg2.connect(POSTGRES_DSN)
    mongo_client = MongoClient(MONGO_URI)
    mongo_collection = mongo_client.test_db.likes
    create_postgres_indexes(postgres_conn)
    create_mongo_indexes(mongo_collection)
    postgres_read_results = []
    mongo_read_results = []
    postgres_write_results = []
    mongo_write_results = []
    postgres_sample_data = postgres_get_sample_data(
        NUM_OPERATIONS_PER_WAVE, postgres_conn
    )
    mongo_sample_data = mongo_get_sample_data(
        NUM_OPERATIONS_PER_WAVE, mongo_collection
    )
    user_ids_postgres, movie_ids_postgres = zip(*postgres_sample_data)
    user_ids_mongo = [data["user_id"] for data in mongo_sample_data]
    movie_ids_mongo = [data["movie_id"] for data in mongo_sample_data]
    for wave in range(NUM_WAVES):
        print(f"Запуск волны {wave + 1} из {NUM_WAVES}...")
        with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
            postgres_read_times = list(
                executor.map(
                    lambda user_id: benchmark_operation(
                        postgres_get_liked_movies, (user_id, postgres_conn)
                    ),
                    user_ids_postgres,
                )
            )
            postgres_read_results.append(statistics.mean(postgres_read_times))
            mongo_read_times = list(
                executor.map(
                    lambda user_id: benchmark_operation(
                        mongo_get_liked_movies, (user_id, mongo_collection)
                    ),
                    user_ids_mongo,
                )
            )
            mongo_read_results.append(statistics.mean(mongo_read_times))
        with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
            postgres_write_times = list(
                executor.map(
                    lambda args: benchmark_operation(
                        postgres_add_like, args + (postgres_conn,)
                    ),
                    zip(user_ids_postgres, movie_ids_postgres),
                )
            )
            postgres_write_results.append(
                statistics.mean(postgres_write_times)
            )
            mongo_write_times = list(
                executor.map(
                    lambda args: benchmark_operation(mongo_add_like, args),
                    zip(
                        user_ids_mongo,
                        movie_ids_mongo,
                        [mongo_collection] * NUM_OPERATIONS_PER_WAVE,
                    ),
                )
            )
            mongo_write_results.append(statistics.mean(mongo_write_times))

    postgres_conn.close()
    mongo_client.close()

    plt.figure(figsize=(12, 8))

    plt.subplot(2, 1, 1)
    plt.plot(
        range(1, NUM_WAVES + 1),
        postgres_read_results,
        label="PostgreSQL (чтение)",
        marker="o",
    )
    plt.plot(
        range(1, NUM_WAVES + 1),
        mongo_read_results,
        label="MongoDB (чтение)",
        marker="o",
    )
    plt.xlabel("Номер волны")
    plt.ylabel("Среднее время (сек)")
    plt.title("Сравнение скорости чтения")
    plt.legend()
    plt.grid()

    plt.subplot(2, 1, 2)
    plt.plot(
        range(1, NUM_WAVES + 1),
        postgres_write_results,
        label="PostgreSQL (запись)",
        marker="o",
    )
    plt.plot(
        range(1, NUM_WAVES + 1),
        mongo_write_results,
        label="MongoDB (запись)",
        marker="o",
    )
    plt.xlabel("Номер волны")
    plt.ylabel("Среднее время (сек)")
    plt.title("Сравнение скорости записи")
    plt.legend()
    plt.grid()

    plt.tight_layout()
    plt.savefig("benchmark_results.png")
    plt.show()


if __name__ == "__main__":
    run_benchmark()
