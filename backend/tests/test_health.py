from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import RATE_LIMIT_REQUESTS, app


@pytest.fixture(scope="module")
def client() -> Iterator[TestClient]:
    with TestClient(app) as c:
        yield c


def test_health(client: TestClient) -> None:
    response = client.get("/health", headers={"x-forwarded-for": "203.0.113.1"})
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_rate_limit_returns_429_after_threshold(client: TestClient) -> None:
    headers = {"x-forwarded-for": "203.0.113.2"}
    for _ in range(RATE_LIMIT_REQUESTS):
        assert client.get("/health", headers=headers).status_code == 200
    assert client.get("/health", headers=headers).status_code == 429


def test_login_success() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "wrong"},
    )

    assert response.status_code == 401


def test_me_requires_token() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_me_with_valid_token() -> None:
    client = TestClient(app)

    login = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    token = login.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["username"] == "admin"