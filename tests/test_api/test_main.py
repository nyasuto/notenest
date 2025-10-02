"""Main API tests"""

from fastapi.testclient import TestClient

from web.api.main import app

client = TestClient(app)


def test_root() -> None:
    """ルートエンドポイントのテスト"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "NoteNest API"
    assert data["version"] == "0.1.0"


def test_health() -> None:
    """ヘルスチェックのテスト"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
