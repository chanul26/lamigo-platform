import pytest
from httpx import AsyncClient

# Seeded UIDs from your database
ADMIN_UID = "MwCKifPTobV7VFb2KwKg7uYbMuX2"
MANAGER_UID = "Kacju0gUqTN2ceNjZuaeM93HMXn2"  # Arjun Rathnayake

@pytest.mark.asyncio
async def test_create_package_as_manager(client: AsyncClient, mock_auth):
    """
    Tests that a Station Manager can successfully create a package
    and that the system auto-assigns their branch_id.
    """
    # Authenticate as Arjun (Station Manager)
    mock_auth.return_value = {"uid": MANAGER_UID}
    headers = {"Authorization": "Bearer mock-manager-token"}
    
    payload = {
        "weight": 2.5,
        "is_cod": True,
        "cod_amount": 1500.00,
        "delivery_charge": 300.00,
        "sender_name": "Tech Store LK",
        "sender_phone": "+94771234567",
        "sender_address": "Galle Road, Colombo 03",
        "recipient_name": "Nimal Perera",
        "recipient_phone": "+94719876543",
        "address": "123 Beach Road, Mount Lavinia",
        "location_type": "HOME",
        "floor_number": "Ground",
        "gps_lat": 6.8398,
        "gps_lng": 79.8654
    }
    
    response = await client.post("/api/v1/packages/", json=payload, headers=headers)
    
    assert response.status_code == 201
    data = response.json()
    
    # Verify the backend auto-generated the tracking ID and nested the recipient
    assert "LMG-" in data["tracking_id"]
    assert data["recipient"]["phone_number"] == "+94719876543"

@pytest.mark.asyncio
async def test_create_package_as_admin_forbidden(client: AsyncClient, mock_auth):
    """
    Tests the IDOR protection: Super Admins should be blocked from creating
    packages because they do not have a physical branch assigned to them.
    """
    # Authenticate as Super Admin
    mock_auth.return_value = {"uid": ADMIN_UID}
    headers = {"Authorization": "Bearer mock-admin-token"}
    
    # We send a minimal payload just to trigger the endpoint
    payload = {
        "weight": 1.0, "is_cod": False, "delivery_charge": 100, 
        "sender_name": "Test", "recipient_name": "Test", "recipient_phone": "123", 
        "address": "Test", "gps_lat": 0, "gps_lng": 0
    }
    
    response = await client.post("/api/v1/packages/", json=payload, headers=headers)
    
    # The Gatekeeper must block this with a 403 Forbidden
    assert response.status_code == 403
    assert "profile does not have an assigned branch" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_packages(client: AsyncClient, mock_auth):
    """
    Tests that authenticated users can fetch the package dashboard list.
    """
    mock_auth.return_value = {"uid": MANAGER_UID}
    headers = {"Authorization": "Bearer mock-manager-token"}
    
    response = await client.get("/api/v1/packages/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)