from datetime import datetime
from http import HTTPStatus
from uuid import UUID

import pytest
from documents.bookmark import Bookmark as BookmarkDocument


def test_create_bookmark(client, headers, mock_bookmark_repo, mock_movie_repo):
    """Тест создания закладки."""
    movie_id = "22222222-2222-2222-2222-222222222222"
    user_id = "11111111-1111-1111-1111-111111111111"

    # Создаем запрос с правильной схемой
    request_data = {"movie_id": movie_id}

    print("\nSending request...")
    print(f"URL: /api-ugc/v1/bookmarks/")
    print(f"Headers: {headers}")
    print(f"Request data: {request_data}")

    # Выполнение
    response = client.post(
        "/api-ugc/v1/bookmarks/",
        headers={**headers, "X-Request-Id": "test-request-id"},
        json=request_data,
    )

    # Отладочная информация
    print("\nGot response:")
    print(f"Status code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Response body: {response.text}")
    if response.status_code == 422:
        print("\nValidation errors:")
        for error in response.json()["detail"]:
            print(f"- {error}")

    # Проверка
    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data["movie_id"] == movie_id
    assert "created_at" in data

    bookmark = BookmarkDocument.find_one(
        {"movie_id": UUID(movie_id), "user_id": UUID(user_id)}
    )
    assert bookmark is not None
