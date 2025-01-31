# stdlib
from enum import StrEnum
from typing import Annotated
from uuid import UUID

# thirdparty
from beanie.odm.enums import SortDirection
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from starlette import status

# project
from api.v1.pagination import PaginationParams
from documents.bookmark import Bookmark as BookmarkDocument
from schemas.auth import JwtToken
from schemas.bookmark import (
    Bookmark,
    BookmarkCreateRequest,
    BookmarkCreateResponse,
    CreateBookmark,
)
from services.jwt_token import JWTBearer
from services.repositories.bookmarks import BookmarkRepository
from services.repositories.movies import MovieRepository

router = APIRouter()


class BookmarkOrderBy(StrEnum):
    created_at = "created_at"


class BookmarkSortParams(BaseModel):
    order_by: BookmarkOrderBy = BookmarkOrderBy.created_at
    direction: SortDirection = SortDirection.ASCENDING


@router.get(
    "/",
    response_model=list[Bookmark],
    status_code=status.HTTP_200_OK,
    description="Получение списка закладок пользователя",
    summary="Получение списка закладок",
)
async def get_bookmarks(
    bookmark_repo: Annotated[BookmarkRepository, Depends()],
    token_payload: Annotated[JwtToken, Depends(JWTBearer())],
    pagination_params: Annotated[PaginationParams, Depends()],
    sort_params: Annotated[BookmarkSortParams, Depends()],
) -> list[BookmarkDocument]:
    return await bookmark_repo.list(
        skip=pagination_params.page_number - 1,
        limit=pagination_params.page_size,
        sort_field=sort_params.order_by,
        sort_order=sort_params.direction,
        filters={"user_id": token_payload.user},
    )


@router.get(
    "/{bookmark_id}",
    response_model=Bookmark,
    status_code=status.HTTP_200_OK,
    description="Получение закладки пользователя",
    summary="Получение закладки",
)
async def get_bookmark(
    bookmark_id: UUID,
    bookmark_repo: Annotated[BookmarkRepository, Depends()],
    token_payload: Annotated[JwtToken, Depends(JWTBearer())],
) -> Bookmark:
    bookmark = await bookmark_repo.get(document_id=bookmark_id, filters={"user_id": token_payload.user})
    return Bookmark(**bookmark.model_dump())


@router.post(
    "/",
    response_model=BookmarkCreateResponse,
    status_code=status.HTTP_201_CREATED,
    description="Создание закладки для пользователя",
    summary="Создание закладки",
)
async def create_bookmark(
    bookmark_data: BookmarkCreateRequest,
    token_payload: Annotated[JwtToken, Depends(JWTBearer())],
    bookmark_repo: Annotated[BookmarkRepository, Depends()],
    movie_repo: Annotated[MovieRepository, Depends()],
) -> BookmarkCreateResponse:
    await movie_repo.get(bookmark_data.movie_id)
    bookmark = await bookmark_repo.get_or_create(
        CreateBookmark(**bookmark_data.model_dump(), user_id=token_payload.user)
    )
    return BookmarkCreateResponse(**bookmark.model_dump())


@router.delete(
    "/{bookmark_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Удаление закладки у пользователя",
    summary="Удаление закладки",
)
async def delete_bookmark(
    bookmark_id: UUID,
    token_payload: Annotated[JwtToken, Depends(JWTBearer())],
    bookmark_repo: Annotated[BookmarkRepository, Depends()],
) -> None:
    bookmark = await bookmark_repo.get(document_id=bookmark_id, filters={"user_id": token_payload.user})
    await bookmark.delete()
