# stdlib
from enum import StrEnum
from typing import Annotated
from uuid import UUID

# thirdparty
from beanie.odm.enums import SortDirection
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from starlette import status

# project
from api.v1.pagination import PaginationParams
from documents.review import Review as ReviewDocument
from schemas.auth import JwtToken
from schemas.review import CreateReview, CreateReviewData, Review
from services.jwt_token import JWTBearer
from services.repositories.reviews import ReviewRepository

router = APIRouter()


class ReviewOrderBy(StrEnum):
    title = "title"  # type: ignore
    rating = "rating"
    created_at = "created_at"


class ReviewSortParams(BaseModel):
    order_by: ReviewOrderBy = ReviewOrderBy.title
    direction: SortDirection = SortDirection.ASCENDING


@router.get(
    "/",
    response_model=list[Review],
    status_code=status.HTTP_200_OK,
    description="Получение списка рецензий",
    summary="Получение списка рецензий",
)
async def get_reviews(
    review_repo: Annotated[ReviewRepository, Depends()],
    pagination_params: Annotated[PaginationParams, Depends()],
    sort_params: Annotated[ReviewSortParams, Depends()],
    movie_id: Annotated[UUID | None, Query(description="Фильтр по фильму")] = None,
    user_id: Annotated[UUID | None, Query(description="Фильтр по пользователю")] = None,
    rating__gte: Annotated[int | None, Query(description="Фильтр по рейтингу рецензии (больше или равно)")] = None,
    rating__lte: Annotated[int | None, Query(description="Фильтр по рейтингу рецензии (меньше или равно)")] = None,
) -> list[ReviewDocument]:
    filters = {
        "movie_id": movie_id,
        "user_id": user_id,
        "rating__gte": rating__gte,
        "rating__lte": rating__lte,
    }
    return await review_repo.list(
        skip=pagination_params.page_number - 1,
        limit=pagination_params.page_size,
        sort_field=sort_params.order_by,
        sort_order=sort_params.direction,
        filters=filters,
    )


@router.get(
    "/{review_id}",
    response_model=Review,
    status_code=status.HTTP_200_OK,
    description="Получение рецензии",
    summary="Получение рецензии",
)
async def get_review(
    review_id: UUID,
    review_repo: Annotated[ReviewRepository, Depends()],
) -> Review:
    review = await review_repo.get(document_id=review_id)
    return Review(**review.model_dump())


@router.post(
    "/",
    response_model=Review,
    status_code=status.HTTP_201_CREATED,
    description="Создание рецензии",
    summary="Создание рецензии",
)
async def create_review(
    review_data: CreateReviewData,
    token_payload: Annotated[JwtToken, Depends(JWTBearer())],
    review_repo: Annotated[ReviewRepository, Depends()],
) -> Review:
    review = await review_repo.create(CreateReview(**review_data.model_dump(), user_id=token_payload.user))
    return Review(**review.model_dump())


@router.delete(
    "/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Удаление рецензии пользователя",
    summary="Удаление рецензии",
)
async def delete_review(
    review_id: UUID,
    token_payload: Annotated[JwtToken, Depends(JWTBearer())],
    review_repo: Annotated[ReviewRepository, Depends()],
) -> None:
    review = await review_repo.get(document_id=review_id)
    if review.user_id != token_payload.user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can delete only your review",
        )
    await review.delete()
