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
from documents.reaction import ContentType, LikeValue, Reaction as ReactionDocument
from schemas.auth import JwtToken
from schemas.reaction import Reaction, ReactionRequest, ReactionResponse
from services.jwt_token import JWTBearer
from services.reactions import remove_user_reaction, update_user_reaction
from services.repositories.movies import MovieRepository
from services.repositories.reactions import ReactionRepository
from services.repositories.reviews import ReviewRepository

router = APIRouter()


class ReactionOrderBy(StrEnum):
    content_type = "content_type"
    value = "value"
    created_at = "created_at"
    updated_at = "updated_at"


class ReactionSortParams(BaseModel):
    order_by: ReactionOrderBy = ReactionOrderBy.created_at
    direction: SortDirection = SortDirection.ASCENDING


@router.get(
    "/",
    response_model=list[Reaction],
    status_code=status.HTTP_200_OK,
    description="Получение списка реакций",
    summary="Получение списка реакций",
)
async def get_reactions(
    reaction_repo: Annotated[ReactionRepository, Depends()],
    pagination_params: Annotated[PaginationParams, Depends()],
    sort_params: Annotated[ReactionSortParams, Depends()],
    target_id: Annotated[UUID | None, Query(description="Фильтр по фильму или рецензии")] = None,
    user_id: Annotated[UUID | None, Query(description="Фильтр по пользователю")] = None,
    content_type: Annotated[ContentType | None, Query(description="Фильтр по типу контента")] = None,
    value: Annotated[LikeValue | None, Query(description="Фильтр по значению реакции")] = None,
) -> list[ReactionDocument]:
    filters = {
        "target_id": target_id,
        "user_id": user_id,
        "content_type": content_type,
        "value": value,
    }
    return await reaction_repo.list(
        skip=pagination_params.page_number - 1,
        limit=pagination_params.page_size,
        sort_field=sort_params.order_by,
        sort_order=sort_params.direction,
        filters=filters,
    )


@router.post(
    "/",
    response_model=ReactionResponse,
    status_code=status.HTTP_200_OK,
    description="Поставить лайк или дизлайк контенту",
    summary="Оценить контент",
)
async def evaluate_content(
    token_payload: Annotated[JwtToken, Depends(JWTBearer())],
    reaction_request: ReactionRequest,
    movie_repo: Annotated[MovieRepository, Depends()],
    review_repo: Annotated[ReviewRepository, Depends()],
) -> ReactionResponse:
    if reaction_request.content_type == ContentType.movie:
        repo = movie_repo  # type: ignore
    elif reaction_request.content_type == ContentType.review:
        repo = review_repo  # type: ignore
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid content type")

    await repo.get(reaction_request.target_id)
    if reaction_request.like_value is None:
        await remove_user_reaction(
            target_id=reaction_request.target_id,
            content_type=reaction_request.content_type,
            user_id=token_payload.user,
            repo=repo,
        )
        return ReactionResponse(success=True)

    await update_user_reaction(
        target_id=reaction_request.target_id,
        content_type=reaction_request.content_type,
        like_value=reaction_request.like_value,
        user_id=token_payload.user,
        repo=repo,
    )
    return ReactionResponse(success=True)
