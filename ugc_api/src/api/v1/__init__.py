# thirdparty
from fastapi import APIRouter

from api.v1.bookmark import router as bookmark_router
from api.v1.movie import router as movie_router
from api.v1.reactions import router as reactions_router
from api.v1.review import router as review_router

api_router = APIRouter()

api_router.include_router(bookmark_router, prefix="/bookmarks", tags=["bookmarks"])
api_router.include_router(movie_router, prefix="/movies", tags=["movies"])
api_router.include_router(reactions_router, prefix="/reactions", tags=["reactions"])
api_router.include_router(review_router, prefix="/reviews", tags=["reviews"])
