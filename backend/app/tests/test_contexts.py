import pytest
from httpx import AsyncClient

ADMIN_UID = "MwCKifPTobV7VFb2KwKg7uYbMuX2"

@pytest.mark.asyncio
async def test_get_contexts(client: AsyncClient, mock_auth):
    """Tests fetching the ML context list."""
    mock_auth.return_value = {"uid": ADMIN_UID}
    headers = {"Authorization": "Bearer mock-admin-token"}
    
    response = await client.get("/api/v1/contexts/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_unauthorized_context_access(client: AsyncClient):
    """Tests security gatekeeper."""
    response = await client.get("/api/v1/contexts/")
    assert response.status_code == 401