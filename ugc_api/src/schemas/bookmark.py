# stdlib
from datetime import datetime
from uuid import UUID

# thirdparty
from pydantic import BaseModel


class Bookmark(BaseModel):
    id: UUID
    movie_id: UUID
    user_id: UUID
    created_at: datetime


class CreateBookmark(BaseModel):
    movie_id: UUID
    user_id: UUID


class UpdateBookmark(CreateBookmark):
    pass


class BookmarkCreateRequest(BaseModel):
    movie_id: UUID


class BookmarkCreateResponse(BaseModel):
    movie_id: UUID
    created_at: datetime
