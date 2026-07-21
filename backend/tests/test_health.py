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
