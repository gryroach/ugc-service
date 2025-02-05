# stdlib
from datetime import datetime
from uuid import UUID, uuid4

# thirdparty
from bson import Binary
from pymongo.results import UpdateResult

# project
from documents.reaction import ContentType, LikeValue, Reaction
from schemas.reaction import CreateReaction, UpdateReaction
from services.repositories.base import BaseRepository


class ReactionRepository(BaseRepository[Reaction, CreateReaction, UpdateReaction]):
    def __init__(self) -> None:
        super().__init__(Reaction)

    @staticmethod
    async def upsert(
        target_id: UUID,
        content_type: ContentType,
        user_id: UUID,
        value: LikeValue = LikeValue.like,
    ) -> tuple[bool, bool]:
        current_time = datetime.now()

        existing_record = await Reaction.get_motor_collection().find_one(
            {
                "content_type": content_type,
                "target_id": Binary.from_uuid(target_id),
                "user_id": Binary.from_uuid(user_id),
            }
        )

        if existing_record and existing_record.get("value") == value:
            return False, False

        result: UpdateResult = await Reaction.get_motor_collection().update_one(
            {
                "content_type": content_type,
                "target_id": Binary.from_uuid(target_id),
                "user_id": Binary.from_uuid(user_id),
            },
            {
                "$set": {"value": value, "updated_at": current_time},
                "$setOnInsert": {
                    "_id": Binary.from_uuid(uuid4()),
                    "created_at": current_time,
                },
            },
            upsert=True,
        )
        updated = result.modified_count > 0
        created = result.upserted_id is not None
        return updated, created

    @staticmethod
    async def remove_value(
        target_id: UUID,
        content_type: ContentType,
        user_id: UUID,
    ) -> LikeValue | int:
        doc = await Reaction.find_one(
            Reaction.content_type == content_type,
            Reaction.target_id == target_id,
            Reaction.user_id == user_id,
        )
        old_value = 0
        if doc:
            old_value = doc.value
            await doc.delete()
        return old_value


def get_reaction_repository() -> ReactionRepository:
    return ReactionRepository()
