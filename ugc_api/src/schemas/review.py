# stdlib
from datetime import datetime
from uuid import UUID

# thirdparty
from pydantic import BaseModel


class Review(BaseModel):
    id: UUID
    movie_id: UUID
    user_id: UUID
    title: str
    review_text: str
    rating: int
    created_at: datetime


class CreateReview(BaseModel):
    movie_id: UUID
    user_id: UUID
    title: str
    review_text: str


class UpdateReview(BaseModel):
    movie_id: UUID
    user_id: UUID
    title: str
    review_text: str


class CreateReviewData(BaseModel):
    movie_id: UUID
    title: str
    review_text: str
