from collections.abc import AsyncGenerator, Callable, Generator
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, patch
from uuid import UUID

import beanie
import mongomock_motor
import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorDatabase

from documents.bookmark import Bookmark
from documents.movie import Movie
from documents.reaction import Reaction
from documents.review import Review
from main import app
from schemas.bookmark import CreateBookmark
from services.repositories.bookmarks import BookmarkRepository
from services.repositories.movies import MovieRepository

pytestmark = pytest.mark.asyncio(scope="session")


@pytest.fixture
async def mock_mongodb() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    client = mongomock_motor.AsyncMongoMockClient()
    db = client.get_database("test_db")

    await beanie.init_beanie(database=db, document_models=[Bookmark, Movie, Review, Reaction])

    movie = Movie(
        id=UUID("22222222-2222-2222-2222-222222222222"),
        title="Test Movie",
        rating=8,
        created_at=datetime(2024, 1, 1),
    )
    await movie.insert()

    bookmark = Bookmark(
        id=UUID("33333333-3333-3333-3333-333333333333"),
        user_id=UUID("11111111-1111-1111-1111-111111111111"),
        movie_id=UUID("22222222-2222-2222-2222-222222222222"),
        created_at=datetime(2024, 1, 1),
    )
    await bookmark.insert()

    review = Review(
        id=UUID("44444444-4444-4444-4444-444444444444"),
        user_id=UUID("11111111-1111-1111-1111-111111111111"),
        movie_id=UUID("22222222-2222-2222-2222-222222222222"),
        title="Test Review",
        review_text="Great movie!",
        rating=9,
        created_at=datetime(2024, 1, 1),
    )
    await review.insert()

    reaction = Reaction(
        id=UUID("55555555-5555-5555-5555-555555555555"),
        user_id=UUID("11111111-1111-1111-1111-111111111111"),
        target_id=UUID("22222222-2222-2222-2222-222222222222"),
        content_type="movie",
        value=1,
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 1, 1),
    )
    await reaction.insert()

    yield db

    await db[Movie.get_collection_name()].delete_many({})
    await db[Bookmark.get_collection_name()].delete_many({})
    await db[Review.get_collection_name()].delete_many({})
    await db[Reaction.get_collection_name()].delete_many({})


@pytest.fixture
def mock_jwt_bearer() -> Generator[AsyncMock, None, None]:
    class TokenPayload:
        def __init__(self, user: UUID) -> None:
            self.user = user

    with patch("services.jwt_token.JWTBearer.__call__") as mock:

        async def get_token_payload(request: Request) -> TokenPayload:
            token = request.headers["Authorization"].split()[1]
            if token == "test_token":
                return TokenPayload(UUID("11111111-1111-1111-1111-111111111111"))
            elif "33333333-3333-3333-3333-333333333333" in token:
                return TokenPayload(UUID("33333333-3333-3333-3333-333333333333"))
            return TokenPayload(UUID("11111111-1111-1111-1111-111111111111"))

        mock.side_effect = get_token_payload
        yield mock


@pytest.fixture
def mock_bookmark_doc() -> AsyncMock:
    mock_doc = AsyncMock()
    mock_doc.model_dump.return_value = {
        "id": str(UUID("33333333-3333-3333-3333-333333333333")),
        "user_id": str(UUID("11111111-1111-1111-1111-111111111111")),
        "movie_id": str(UUID("22222222-2222-2222-2222-222222222222")),
        "created_at": datetime(2024, 1, 1).isoformat(),
    }
    return mock_doc


@pytest.fixture
def mock_bookmark_repo(
    mock_bookmark_doc: AsyncMock,
) -> Callable[[], BookmarkRepository]:
    class MockBookmarkRepo(BookmarkRepository):
        def __init__(self) -> None:
            super().__init__()

        async def get_or_create(self, create_bookmark: CreateBookmark) -> Bookmark:
            result = Bookmark.parse_obj(mock_bookmark_doc.model_dump.return_value)
            return result

    def get_repo() -> BookmarkRepository:
        return MockBookmarkRepo()

    return get_repo


@pytest.fixture
def mock_movie_repo() -> Callable[[], MovieRepository]:
    class MockMovieRepo(MovieRepository):
        def __init__(self) -> None:
            super().__init__()

        async def get(self, document_id: UUID, filters: dict[Any, Any] | None = None) -> Movie:
            result = {
                "id": str(document_id),
                "title": "Test Movie",
                "rating": 8,
                "created_at": datetime(2024, 1, 1),
            }
            return Movie.parse_obj(result)

    def get_repo() -> MovieRepository:
        return MockMovieRepo()

    return get_repo


@pytest.fixture
async def client(
    mock_mongodb: AsyncIOMotorDatabase,
    mock_jwt_bearer: AsyncMock,
    mock_bookmark_repo: Callable[[], BookmarkRepository],
    mock_movie_repo: Callable[[], MovieRepository],
) -> AsyncGenerator[TestClient, None]:
    app.dependency_overrides.clear()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        yield

    original_lifespan = app.router.lifespan_context
    app.router.lifespan_context = lifespan

    test_client = TestClient(app)
    yield test_client

    app.router.lifespan_context = original_lifespan
    app.dependency_overrides.clear()


@pytest.fixture
def headers() -> dict[str, str]:
    return {
        "Authorization": "Bearer test_token",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Request-Id": "test-request-id",
    }


@pytest.fixture
def mock_review_doc() -> AsyncMock:
    mock_doc = AsyncMock()
    mock_doc.model_dump.return_value = {
        "id": str(UUID("44444444-4444-4444-4444-444444444444")),
        "user_id": str(UUID("11111111-1111-1111-1111-111111111111")),
        "movie_id": str(UUID("22222222-2222-2222-2222-222222222222")),
        "text": "Test review",
        "rating": 9,
        "created_at": datetime(2024, 1, 1).isoformat(),
    }
    return mock_doc


@pytest.fixture
def mock_reaction_doc() -> AsyncMock:
    mock_doc = AsyncMock()
    mock_doc.model_dump.return_value = {
        "id": str(UUID("55555555-5555-5555-5555-555555555555")),
        "user_id": str(UUID("11111111-1111-1111-1111-111111111111")),
        "movie_id": str(UUID("22222222-2222-2222-2222-222222222222")),
        "type": "like",
        "created_at": datetime(2024, 1, 1).isoformat(),
    }
    return mock_doc
