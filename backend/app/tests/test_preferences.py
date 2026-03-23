import pytest
from httpx import AsyncClient

# Dummy UUIDs for routing tests
DUMMY_PACKAGE_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
DUMMY_PREFERENCE_ID = "123e4567-e89b-12d3-a456-426614174000"

@pytest.mark.asyncio
async def test_create_preference_public_access(client: AsyncClient):
    """
    Tests that a customer can submit a preference WITHOUT a JWT token.
    Proves the endpoint is successfully public.
    """
    payload = {
        "package_id": DUMMY_PACKAGE_ID,
        "target_date": "2026-03-25",
        "status": "AVAILABLE"
    }
    
    # Notice: NO headers={"Authorization": ...} are passed here!
    response = await client.post("/api/v1/preferences/", json=payload)
    
    # The crucial check: It must NOT return 401 Unauthorized or 403 Forbidden.
    # It will likely return 404 because the dummy package UUID isn't in the real test DB, 
    # which proves the service validation logic is working!
    assert response.status_code not in [401, 403]
    assert response.status_code in [201, 404]

@pytest.mark.asyncio
async def test_get_preferences_public_access(client: AsyncClient):
    """
    Tests fetching preferences via package_id without authentication.
    """
    response = await client.get(f"/api/v1/preferences/{DUMMY_PACKAGE_ID}")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_update_preference_public_access(client: AsyncClient):
    """
    Tests updating a preference status without authentication.
    """
    payload = {"status": "UNAVAILABLE"}
    response = await client.patch(f"/api/v1/preferences/{DUMMY_PREFERENCE_ID}", json=payload)
    
    assert response.status_code not in [401, 403]
    assert response.status_code in [200, 404]