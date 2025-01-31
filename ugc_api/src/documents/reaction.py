# stdlib
from datetime import datetime
from enum import IntEnum, StrEnum
from uuid import UUID, uuid4

# thirdparty
from beanie import Document
from pydantic import Field


class ContentType(StrEnum):
    movie = "movie"
    review = "review"


class LikeValue(IntEnum):
    like = 1
    dislike = -1


class Reaction(Document):
    id: UUID = Field(default_factory=uuid4)  # type: ignore
    content_type: ContentType = ContentType.movie
    value: LikeValue = LikeValue.like
    user_id: UUID
    target_id: UUID
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "reactions"
