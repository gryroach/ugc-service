# stdlib
from uuid import UUID, uuid4

# thirdparty
from beanie import Document
from pydantic import Field


class Movie(Document):
    id: UUID = Field(default_factory=uuid4)  # type: ignore

    class Settings:
        name = "movies"
