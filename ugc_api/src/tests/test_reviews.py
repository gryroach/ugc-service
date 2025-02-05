# stdlib
from collections.abc import Callable
from http import HTTPStatus

# thirdparty
from fastapi.testclient import TestClient

# project
from services.repositories.movies import MovieRepository

MOVIE_ID = "22222222-2222-2222-2222-222222222222"
USER_ID = "11111111-1111-1111-1111-111111111111"
REVIEW_ID = "44444444-4444-4444-4444-444444444444"


def test_create_review(
    client: TestClient,
    headers: dict[str, str],
    mock_movie_repo: Callable[[], MovieRepository],
) -> None:
    """Тест создания рецензии."""
    request_data = {
        "movie_id": MOVIE_ID,
        "title": "Test Review",
        "review_text": "Great movie!",
    }

    response = client.post(
        "/api-ugc/v1/reviews/",
        headers=headers,
        json=request_data,
    )

    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data["title"] == request_data["title"]
    assert data["review_text"] == request_data["review_text"]


def test_get_reviews(client: TestClient, headers: dict[str, str]) -> None:
    """Тест получения списка рецензий."""
    response = client.get(
        "/api-ugc/v1/reviews/",
        headers=headers,
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_delete_review(client: TestClient, headers: dict[str, str]) -> None:
    """Тест удаления рецензии."""
    response = client.delete(
        f"/api-ugc/v1/reviews/{REVIEW_ID}",
        headers=headers,
    )

    assert response.status_code == HTTPStatus.NO_CONTENT
