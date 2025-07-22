from fastapi.testclient import TestClient
from app.app_factory import create_app

app = create_app()
client = TestClient(app)


def test_healthcheck():
    response = client.get("/api/healthcheck")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "house-scraper-api"
