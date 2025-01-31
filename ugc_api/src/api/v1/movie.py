# stdlib
from enum import StrEnum
from typing import Annotated
from uuid import UUID

# thirdparty
from beanie.odm.enums import SortDirection
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from starlette import status

# project
from api.v1.pagination import PaginationParams
from documents.movie import Movie as MovieDocument
from schemas.movie import CreateMovie, Movie, MovieDetail
from services.jwt_token import JWTBearer
from services.repositories.movies import MovieRepository

router = APIRouter()


class MovieOrderBy(StrEnum):
    rating = "rating"
    created_at = "created_at"


class MovieSortParams(BaseModel):
    order_by: MovieOrderBy = MovieOrderBy.rating
    direction: SortDirection = SortDirection.ASCENDING


@router.get(
    "/",
    response_model=list[Movie],
    status_code=status.HTTP_200_OK,
    description="Получение списка фильмов",
    summary="Получение списка фильмов",
)
async def get_movies(
    movie_repo: Annotated[MovieRepository, Depends()],
    pagination_params: Annotated[PaginationParams, Depends()],
    sort_params: Annotated[MovieSortParams, Depends()],
    rating__gte: Annotated[int | None, Query(description="Фильтр по рейтингу фильма (больше или равно)")] = None,
    rating__lte: Annotated[int | None, Query(description="Фильтр по рейтингу фильма (меньше или равно)")] = None,
) -> list[MovieDocument]:
    filters = {
        "rating__gte": rating__gte,
        "rating__lte": rating__lte,
    }
    return await movie_repo.list(
        skip=pagination_params.page_number - 1,
        limit=pagination_params.page_size,
        sort_field=sort_params.order_by,
        sort_order=sort_params.direction,
        filters=filters,
    )


@router.get(
    "/{movie_id}",
    response_model=MovieDetail,
    status_code=status.HTTP_200_OK,
    description="Получение детальной информации о фильме",
    summary="Получение фильма",
)
async def get_review(
    movie_id: UUID,
    movie_repo: Annotated[MovieRepository, Depends()],
) -> MovieDetail:
    movie = await movie_repo.get_detail_info(document_id=movie_id)
    return MovieDetail(**movie.model_dump())


@router.post(
    "/",
    response_model=Movie,
    status_code=status.HTTP_201_CREATED,
    description="Создание записи фильма",
    summary="Создание записи фильма",
    dependencies=[Depends(JWTBearer())],
)
async def create_reviews(
    movie_data: CreateMovie,
    movie_repo: Annotated[MovieRepository, Depends()],
) -> Movie:
    movie = await movie_repo.create(movie_data)
    return Movie(**movie.model_dump())
