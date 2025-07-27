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


@pytest.mark.asyncio
async def test_rentals_search_limit_offset():
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/rentals/?limit=2&offset=0")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) <= 2


@pytest.mark.asyncio
async def test_rentals_search_property_type():
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/rentals/?property_type=appartamento")
        assert response.status_code == 200
        for rental in response.json():
            assert rental.get("property_type") == "appartamento"


@pytest.mark.asyncio
async def test_rentals_search_tenant_preference():
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/rentals/?tenant_preference=ragazza")
        assert response.status_code == 200
        for rental in response.json():
            assert rental.get("tenant_preference") == "ragazza"
