import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from inspect import signature
from unittest.mock import AsyncMock, patch
from uuid import UUID

import beanie
import mongomock_motor
import pytest
from documents.bookmark import Bookmark
from documents.movie import Movie
from fastapi.testclient import TestClient
from main import app
from services.repositories.bookmarks import BookmarkRepository
from services.repositories.movies import MovieRepository

pytestmark = pytest.mark.asyncio(scope="session")


@pytest.fixture
async def mock_mongodb():
    client = mongomock_motor.AsyncMongoMockClient()
    db = client.get_database("test_db")

    await beanie.init_beanie(database=db, document_models=[Bookmark, Movie])

    movie = Movie(
        id=UUID("22222222-2222-2222-2222-222222222222"),
        title="Test Movie",
        rating=8,
        created_at=datetime(2024, 1, 1),
    )
    await movie.insert()

    yield db

    await db[Movie.get_collection_name()].delete_many({})
    await db[Bookmark.get_collection_name()].delete_many({})


@pytest.fixture
def mock_jwt_bearer():
    class TokenPayload:
        def __init__(self, user):
            self.user = user

    with patch("services.jwt_token.JWTBearer.__call__") as mock:
        mock.return_value = TokenPayload(
            UUID("11111111-1111-1111-1111-111111111111")
        )
        yield mock


@pytest.fixture
def mock_bookmark_doc():
    mock_doc = AsyncMock()
    mock_doc.model_dump.return_value = {
        "id": str(UUID("33333333-3333-3333-3333-333333333333")),
        "user_id": str(UUID("11111111-1111-1111-1111-111111111111")),
        "movie_id": str(UUID("22222222-2222-2222-2222-222222222222")),
        "created_at": datetime(2024, 1, 1).isoformat(),
    }
    return mock_doc


@pytest.fixture
def mock_bookmark_repo(mock_bookmark_doc):
    print("\nCreating bookmark repo mock...")

    class MockBookmarkRepo(BookmarkRepository):
        def __init__(self):
            super().__init__()
            print(f"Initialized MockBookmarkRepo with model: {self.model}")

        async def get_or_create(self, create_bookmark):
            print(f"\nCalling get_or_create with: {create_bookmark}")
            result = mock_bookmark_doc.return_value
            print(f"Returning: {result.model_dump()}")
            return result

    def get_repo():
        return MockBookmarkRepo()

    get_repo.__signature__ = signature(lambda: None)

    return get_repo


@pytest.fixture
def mock_movie_repo():
    print("\nCreating movie repo mock...")

    class MockMovieRepo(MovieRepository):
        def __init__(self):
            super().__init__()
            print(f"Initialized MockMovieRepo with model: {self.model}")

        async def get(self, movie_id: str):
            print(f"\nCalling get with movie_id: {movie_id}")
            result = {
                "id": movie_id,
                "title": "Test Movie",
                "rating": 8,
                "created_at": datetime(2024, 1, 1),
            }
            print(f"Returning: {result}")
            return result

    def get_repo():
        return MockMovieRepo()

    get_repo.__signature__ = signature(lambda: None)

    return get_repo


@pytest.fixture
async def client(
    mock_mongodb, mock_jwt_bearer, mock_bookmark_repo, mock_movie_repo
):
    app.dependency_overrides.clear()

    @asynccontextmanager
    async def lifespan(app):
        print("Starting up")
        yield
        print("Shutting down")

    original_lifespan = app.router.lifespan_context
    app.router.lifespan_context = lifespan

    test_client = TestClient(app)
    yield test_client

    app.router.lifespan_context = original_lifespan
    app.dependency_overrides.clear()


@pytest.fixture
def headers():
    return {
        "Authorization": "Bearer test_token",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Request-Id": "test-request-id",
    }


@pytest.fixture
def mock_review_doc():
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
def mock_reaction_doc():
    mock_doc = AsyncMock()
    mock_doc.model_dump.return_value = {
        "id": str(UUID("55555555-5555-5555-5555-555555555555")),
        "user_id": str(UUID("11111111-1111-1111-1111-111111111111")),
        "movie_id": str(UUID("22222222-2222-2222-2222-222222222222")),
        "type": "like",
        "created_at": datetime(2024, 1, 1).isoformat(),
    }
    return mock_doc
