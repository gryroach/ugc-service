# stdlib
from uuid import UUID

# project
from documents.movie import Movie
from schemas.movie import AdditionalInfo, CreateMovie, MovieDetail, UpdateMovie
from services.reactions import get_movie_statistics
from services.repositories.base import RatingRepository


class MovieRepository(RatingRepository[Movie, CreateMovie, UpdateMovie]):
    def __init__(self) -> None:
        super().__init__(Movie)

    async def get_detail_info(self, document_id: UUID) -> MovieDetail:
        movie = await self.get(document_id)
        movie_info = await get_movie_statistics(document_id)
        return MovieDetail(**movie.model_dump(), additional_info=AdditionalInfo(**movie_info))
