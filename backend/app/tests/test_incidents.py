import pytest
from httpx import AsyncClient

ADMIN_UID = "MwCKifPTobV7VFb2KwKg7uYbMuX2"

@pytest.mark.asyncio
async def test_get_incidents(client: AsyncClient, mock_auth):
    mock_auth.return_value = {"uid": ADMIN_UID}
    headers = {"Authorization": "Bearer mock-admin-token"}
    
    response = await client.get("/api/v1/incidents/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_unauthorized_incident_access(client: AsyncClient):
    response = await client.get("/api/v1/incidents/")
    assert response.status_code == 401