import os

import numpy as np
from tqdm import tqdm

from constants import BATCH_SIZE, OUTPUT_DIR, TEST_RANGE

os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_data_batches():
    """
    Генерирует данные и сохраняет их в `.npy` файлы.
    """
    total_batches = TEST_RANGE // BATCH_SIZE

    for i in tqdm(range(total_batches), desc="Generating batches"):
        user_ids = np.random.randint(1, 1000000, size=BATCH_SIZE)
        movie_ids = np.random.randint(1, 10000, size=BATCH_SIZE)

        # Сохраняем массивы в файл
        np.save(os.path.join(OUTPUT_DIR, f"user_ids_batch_{i}.npy"), user_ids)
        np.save(
            os.path.join(OUTPUT_DIR, f"movie_ids_batch_{i}.npy"), movie_ids
        )

    print(
        f"Data generation complete. Saved {total_batches} batches in '{OUTPUT_DIR}'."
    )


if __name__ == "__main__":
    generate_data_batches()
