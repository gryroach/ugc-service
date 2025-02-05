from http import HTTPStatus
from uuid import UUID

from fastapi.testclient import TestClient

from documents.bookmark import Bookmark as BookmarkDocument

UNPROCESSABLE_ENTITY = 422


def test_create_bookmark(client: TestClient, headers: dict[str, str]) -> None:
    """Тест создания закладки."""
    movie_id = "22222222-2222-2222-2222-222222222222"
    user_id = "11111111-1111-1111-1111-111111111111"

    request_data = {"movie_id": movie_id}

    response = client.post(
        "/api-ugc/v1/bookmarks/",
        headers={**headers, "X-Request-Id": "test-request-id"},
        json=request_data,
    )

    print("\nGot response:")
    print(f"Status code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Response body: {response.text}")
    if response.status_code == UNPROCESSABLE_ENTITY:
        print("\nValidation errors:")
        for error in response.json()["detail"]:
            print(f"- {error}")

    # Проверка
    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data["movie_id"] == movie_id
    assert "created_at" in data

    bookmark = BookmarkDocument.find_one({"movie_id": UUID(movie_id), "user_id": UUID(user_id)})
    assert bookmark is not None
