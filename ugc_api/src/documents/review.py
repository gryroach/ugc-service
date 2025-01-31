# stdlib
from datetime import datetime
from uuid import UUID, uuid4

# thirdparty
from beanie import Document
from pydantic import Field, field_validator


class Review(Document):
    id: UUID = Field(default_factory=uuid4)  # type: ignore
    movie_id: UUID
    user_id: UUID
    title: str
    review_text: str
    rating: int = 0
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "reviews"

    @field_validator("review_text", "title")
    @classmethod
    def not_empty_review(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Review cannot be empty or contain only whitespace")
        return value
