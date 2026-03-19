import pytest
from httpx import AsyncClient

# We use the seeded UIDs from your database for realistic testing
ADMIN_UID = "MwCKifPTobV7VFb2KwKg7uYbMuX2"
MANAGER_UID = "Kacju0gUqTN2ceNjZuaeM93HMXn2" # Arjun

# Global variable to store a fetched recipient ID for later tests
test_recipient_id = None

@pytest.mark.asyncio
async def test_get_all_recipients_as_admin(client: AsyncClient, mock_auth):
    """Test that a SUPER_ADMIN can fetch all recipients."""
    global test_recipient_id
    
    mock_auth.return_value = {"uid": ADMIN_UID}
    headers = {"Authorization": "Bearer mock-admin-token"}
    
    response = await client.get("/api/v1/recipients/", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    
    # Grab the first recipient in the database to use for the next tests
    if len(data) > 0:
        test_recipient_id = data[0]["recipient_id"]
        
    print("\n✅ Admin successfully fetched all Recipients.")


@pytest.mark.asyncio
async def test_manager_cannot_access_recipients(client: AsyncClient, mock_auth):
    """Test the RBAC Gatekeeper: STATION_MANAGER must be blocked with a 403."""
    mock_auth.return_value = {"uid": MANAGER_UID}
    headers = {"Authorization": "Bearer mock-manager-token"}
    
    response = await client.get("/api/v1/recipients/", headers=headers)
    
    # The Gatekeeper should return 403 Forbidden because it is SUPER_ADMIN only
    assert response.status_code == 403
    print("\n✅ Gatekeeper successfully blocked Station Manager access.")


@pytest.mark.asyncio
async def test_get_single_recipient_as_admin(client: AsyncClient, mock_auth):
    """Test fetching a specific recipient."""
    global test_recipient_id
    if not test_recipient_id:
        pytest.skip("No recipient found in the database to test GET by ID.")
        
    mock_auth.return_value = {"uid": ADMIN_UID}
    headers = {"Authorization": "Bearer mock-admin-token"}
    
    response = await client.get(f"/api/v1/recipients/{test_recipient_id}", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["recipient_id"] == test_recipient_id
    print("\n✅ Admin successfully fetched the single Recipient.")


@pytest.mark.asyncio
async def test_update_recipient_as_admin(client: AsyncClient, mock_auth):
    """Test partial updates (PATCH) on the recipient."""
    global test_recipient_id
    if not test_recipient_id:
        pytest.skip("No recipient found in the database to test PATCH.")
        
    mock_auth.return_value = {"uid": ADMIN_UID}
    headers = {"Authorization": "Bearer mock-admin-token"}
    
    # We only send the field we want to change
    update_payload = {
        "floor_number": "Level 10"
    }
    
    response = await client.patch(f"/api/v1/recipients/{test_recipient_id}", json=update_payload, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["floor_number"] == "Level 10"
    print("\n✅ Recipient successfully updated by Admin.")