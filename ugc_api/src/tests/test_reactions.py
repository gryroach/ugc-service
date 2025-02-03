from http import HTTPStatus

from fastapi.testclient import TestClient

MOVIE_ID = "22222222-2222-2222-2222-222222222222"
USER_ID = "11111111-1111-1111-1111-111111111111"


def test_create_reaction(client: TestClient, headers: dict[str, str]) -> None:
    """Тест создания реакции."""
    request_data = {"content_type": "movie", "target_id": MOVIE_ID, "value": 1}

    response = client.post(
        "/api-ugc/v1/reactions/",
        headers=headers,
        json=request_data,
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["success"] is True


def test_get_reactions(client: TestClient, headers: dict[str, str]) -> None:
    """Тест получения списка реакций."""
    response = client.get(
        "/api-ugc/v1/reactions/",
        headers=headers,
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_remove_reaction(client: TestClient, headers: dict[str, str]) -> None:
    """Тест удаления реакции."""
    request_data = {
        "content_type": "movie",
        "target_id": MOVIE_ID,
        "value": None,
    }

    response = client.post(
        "/api-ugc/v1/reactions/",
        headers=headers,
        json=request_data,
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["success"] is True
