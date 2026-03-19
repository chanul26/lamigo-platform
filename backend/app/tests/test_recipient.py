import pytest
from httpx import AsyncClient

# We use the seeded UIDs from your database for realistic testing
ADMIN_UID = "MwCKifPTobV7VFb2KwKg7uYbMuX2"
MANAGER_UID = "Kacju0gUqTN2ceNjZuaeM93HMXn2" # Arjun
DRIVER_UID = "uC2V93X7znQOfrHxtAOt8WkIVFl2"  # Kasun

# Global variable to store the created recipient ID for later tests
created_recipient_id = None

@pytest.mark.asyncio
async def test_create_recipient_as_admin(client: AsyncClient, mock_auth):
    """Test that a SUPER_ADMIN can successfully create a recipient."""
    global created_recipient_id
    
    mock_auth.return_value = {"uid": ADMIN_UID}
    headers = {"Authorization": "Bearer mock-admin-token"}
    
    payload = {
        "name": "Kamal Perera",
        "phone_number": "+94771234567",
        "address": "123 Galle Road, Colombo 03",
        "location_type": "HOME",
        "floor_number": "Ground",
        "gps_lat": 6.9055,
        "gps_lng": 79.8510
    }
    
    response = await client.post("/api/v1/recipients/", json=payload, headers=headers)
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Kamal Perera"
    assert data["is_location_verified"] is False
    assert "recipient_id" in data
    
    # Save the ID for the next tests
    created_recipient_id = data["recipient_id"]
    print("\n✅ Admin successfully created a Recipient.")


@pytest.mark.asyncio
async def test_driver_cannot_create_recipient(client: AsyncClient, mock_auth):
    """Test the RBAC Gatekeeper: DRIVERs must be blocked with a 403."""
    mock_auth.return_value = {"uid": DRIVER_UID}
    headers = {"Authorization": "Bearer mock-driver-token"}
    
    payload = {
        "name": "Unauthorized User",
        "phone_number": "+94770000000",
        "address": "Hidden Location",
        "gps_lat": 0.0,
        "gps_lng": 0.0
    }
    
    response = await client.post("/api/v1/recipients/", json=payload, headers=headers)
    
    # The Gatekeeper should return 403 Forbidden
    assert response.status_code == 403
    print("\n✅ Gatekeeper successfully blocked Driver access.")


@pytest.mark.asyncio
async def test_get_recipient_as_manager(client: AsyncClient, mock_auth):
    """Test that a STATION_MANAGER can fetch the created recipient."""
    global created_recipient_id
    
    mock_auth.return_value = {"uid": MANAGER_UID}
    headers = {"Authorization": "Bearer mock-manager-token"}
    
    response = await client.get(f"/api/v1/recipients/{created_recipient_id}", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["recipient_id"] == created_recipient_id
    assert data["name"] == "Kamal Perera"
    print("\n✅ Station Manager successfully fetched the Recipient.")


@pytest.mark.asyncio
async def test_update_recipient(client: AsyncClient, mock_auth):
    """Test partial updates (PATCH) on the recipient."""
    global created_recipient_id
    
    mock_auth.return_value = {"uid": ADMIN_UID}
    headers = {"Authorization": "Bearer mock-admin-token"}
    
    # We only send the fields we want to change
    update_payload = {
        "is_location_verified": True,
        "phone_number": "+94779999999"
    }
    
    response = await client.patch(f"/api/v1/recipients/{created_recipient_id}", json=update_payload, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_location_verified"] is True
    assert data["phone_number"] == "+94779999999"
    assert data["name"] == "Kamal Perera" # Ensure original data wasn't wiped out
    print("\n✅ Recipient successfully updated.")