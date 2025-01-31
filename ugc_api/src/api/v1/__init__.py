# thirdparty
from fastapi import APIRouter

from .bookmark import router as bookmark_router
from .movie import router as movie_router
from .reactions import router as reaction_router
from .review import router as review_router

api_router = APIRouter()

api_router.include_router(
    movie_router,
    prefix="/movies",
    tags=["Фильмы"],
)
api_router.include_router(
    review_router,
    prefix="/reviews",
    tags=["Рецензии"],
)
api_router.include_router(
    bookmark_router,
    prefix="/bookmarks",
    tags=["Закладки"],
)
api_router.include_router(
    reaction_router,
    prefix="/reactions",
    tags=["Реакции"],
)
