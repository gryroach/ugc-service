# stdlib
import asyncio
from uuid import UUID

# thirdparty
from bson import Binary

# project
from documents.bookmark import Bookmark
from documents.reaction import ContentType, LikeValue, Reaction
from documents.review import Review
from services.repositories.base import RatingRepository
from services.repositories.reactions import get_reaction_repository


async def remove_user_reaction(
    target_id: UUID,
    content_type: ContentType,
    user_id: UUID,
    repo: RatingRepository,
) -> None:
    """
    Удаление реакции пользователя и откат рейтинга оцененной сущности.
    """
    reaction_repo = get_reaction_repository()
    value = await reaction_repo.remove_value(
        target_id=target_id,
        content_type=content_type,
        user_id=user_id,
    )
    await repo.update_rating_count(document_id=target_id, like_value=-value)


async def update_user_reaction(
    target_id: UUID,
    content_type: ContentType,
    user_id: UUID,
    value: LikeValue,
    repo: RatingRepository,
) -> None:
    """
    Создание/обновление реакции пользователя и обновление рейтинга оцениваемой сущности.
    """
    reaction_repo = get_reaction_repository()
    updated, created = await reaction_repo.upsert(
        target_id=target_id,
        content_type=content_type,
        value=value,
        user_id=user_id,
    )
    if created:
        await repo.update_rating_count(target_id, value)
    if updated:
        await repo.update_rating_count(target_id, value * 2)


async def get_movie_statistics(movie_id: UUID) -> dict[str, int]:
    """
    Получение агрегированных данных для определенного фильма.
    """
    likes_pipeline = [
        {
            "$match": {
                "target_id": Binary.from_uuid(movie_id),
                "content_type": ContentType.movie,
            }
        },
        {
            "$group": {
                "_id": None,
                "likes_count": {
                    "$sum": {
                        "$cond": [{"$eq": ["$value", LikeValue.like]}, 1, 0]
                    }
                },
                "dislikes_count": {
                    "$sum": {
                        "$cond": [{"$eq": ["$value", LikeValue.dislike]}, 1, 0]
                    }
                },
                "total": {"$sum": 1},
            }
        },
    ]
    # Запуск всех запросов конкурентно
    likes_data, bookmarks_count, reviews_count = await asyncio.gather(
        Reaction.aggregate(likes_pipeline).to_list(),
        Bookmark.find(Bookmark.movie_id == movie_id).count(),
        Review.find(Review.movie_id == movie_id).count(),
    )
    likes_stats = likes_data[0] if likes_data else {}

    return {
        "likes_count": likes_stats.get("likes_count", 0),
        "dislikes_count": likes_stats.get("dislikes_count", 0),
        "reactions_count": likes_stats.get("total", 0),
        "bookmarks_count": bookmarks_count,
        "reviews_count": reviews_count,
    }
