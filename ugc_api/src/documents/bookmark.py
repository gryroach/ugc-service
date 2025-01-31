# stdlib
from datetime import datetime
from uuid import UUID, uuid4

# thirdparty
from beanie import Document
from pydantic import Field


class Bookmark(Document):
    id: UUID = Field(default_factory=uuid4)  # type: ignore
    movie_id: UUID
    user_id: UUID
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "bookmarks"
