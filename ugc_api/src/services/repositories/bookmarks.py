# project
from documents.bookmark import Bookmark
from schemas.bookmark import CreateBookmark, UpdateBookmark
from services.repositories.base import BaseRepository


class BookmarkRepository(BaseRepository[Bookmark, CreateBookmark, UpdateBookmark]):
    def __init__(self) -> None:
        super().__init__(Bookmark)

    async def get_or_create(self, obj_in: CreateBookmark) -> Bookmark:
        existing_bookmark = await self.model.find_one({"movie_id": obj_in.movie_id, "user_id": obj_in.user_id})
        if existing_bookmark is not None:
            return existing_bookmark
        return await super().create(obj_in)
