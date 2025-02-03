from http import HTTPStatus

from fastapi.testclient import TestClient

MOVIE_ID = "22222222-2222-2222-2222-222222222222"
USER_ID = "11111111-1111-1111-1111-111111111111"


def test_get_movies(client: TestClient, headers: dict[str, str]) -> None:
    """Тест получения списка фильмов."""
    response = client.get(
        "/api-ugc/v1/movies/",
        headers=headers,
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_movie_detail(client: TestClient, headers: dict[str, str]) -> None:
    """Тест получения детальной информации о фильме."""
    response = client.get(
        f"/api-ugc/v1/movies/{MOVIE_ID}",
        headers=headers,
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["id"] == MOVIE_ID
    assert "additional_info" in data


def test_create_movie(client: TestClient, headers: dict[str, str]) -> None:
    """Тест создания фильма."""
    new_movie_id = "33333333-3333-3333-3333-333333333333"
    request_data = {"id": new_movie_id, "title": "New Test Movie", "rating": 8}

    response = client.post(
        "/api-ugc/v1/movies/",
        headers=headers,
        json=request_data,
    )

    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data["title"] == request_data["title"]
    assert data["rating"] == request_data["rating"]
