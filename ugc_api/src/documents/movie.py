from uuid import UUID, uuid4
from beanie import Document
from pydantic import Field


class Movie(Document):
    id: UUID = Field(default_factory=uuid4)

    class Settings:
        name = "movies"
