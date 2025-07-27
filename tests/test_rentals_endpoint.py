import pytest
from httpx import AsyncClient, ASGITransport
from app.app_factory import create_app


@pytest.mark.asyncio
async def test_rentals_search_empty():
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/rentals/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
