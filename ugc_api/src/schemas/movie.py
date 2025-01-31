# stdlib
from datetime import datetime
from uuid import UUID

# thirdparty
from pydantic import BaseModel


class Movie(BaseModel):
    id: UUID
    title: str
    rating: int
    created_at: datetime


class AdditionalInfo(BaseModel):
    reactions_count: int
    likes_count: int
    dislikes_count: int
    bookmarks_count: int
    reviews_count: int


class MovieDetail(BaseModel):
    id: UUID
    title: str
    rating: int
    created_at: datetime
    additional_info: AdditionalInfo


class CreateMovie(BaseModel):
    id: UUID
    title: str
    rating: int


class UpdateMovie(BaseModel):
    title: str
    rating: int
