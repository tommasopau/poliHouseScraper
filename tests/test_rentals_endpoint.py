from fastapi.testclient import TestClient
from app.app_factory import create_app

app = create_app()
client = TestClient(app)


def test_rentals_search_empty():
    response = client.get("/api/rentals/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
