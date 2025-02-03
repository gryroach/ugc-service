from collections.abc import Callable
from http import HTTPStatus
from uuid import UUID

from documents.bookmark import Bookmark as BookmarkDocument
from fastapi.testclient import TestClient
from services.repositories.bookmarks import BookmarkRepository
from services.repositories.movies import MovieRepository

MOVIE_ID = "22222222-2222-2222-2222-222222222222"
USER_ID = "11111111-1111-1111-1111-111111111111"


def test_create_bookmark(
    client: TestClient,
    headers: dict[str, str],
    mock_bookmark_repo: Callable[[], BookmarkRepository],
    mock_movie_repo: Callable[[], MovieRepository],
) -> None:
    """Тест создания закладки."""
    request_data = {"movie_id": MOVIE_ID}

    response = client.post(
        "/api-ugc/v1/bookmarks/",
        headers={**headers, "X-Request-Id": "test-request-id"},
        json=request_data,
    )

    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data["movie_id"] == MOVIE_ID
    assert "created_at" in data

    bookmark = BookmarkDocument.find_one(
        {"movie_id": UUID(MOVIE_ID), "user_id": UUID(USER_ID)}
    )
    assert bookmark is not None


def test_get_bookmarks(
    client: TestClient,
    headers: dict[str, str],
    mock_bookmark_repo: Callable[[], BookmarkRepository],
) -> None:
    """Тест получения списка закладок."""
    response = client.get(
        "/api-ugc/v1/bookmarks/",
        headers=headers,
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert isinstance(data, list)


def test_delete_bookmark(
    client: TestClient,
    headers: dict[str, str],
    mock_bookmark_repo: Callable[[], BookmarkRepository],
) -> None:
    """Тест удаления закладки."""
    response = client.delete(
        "/api-ugc/v1/bookmarks/33333333-3333-3333-3333-333333333333",
        headers=headers,
    )

    assert response.status_code == HTTPStatus.NO_CONTENT
