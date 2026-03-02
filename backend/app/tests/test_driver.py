import pytest

@pytest.mark.asyncio
async def test_driver_kasun_profile(client, mock_auth):
    """
    Verifies that a Driver (Kasun Mendis) gets a complete profile back
    including both base User fields AND flat Driver operational fields.
    """
    KASUN_UID = "uC2V93X7znQOfrHxtAOt8WkIVFl2"
    mock_auth.return_value = {"uid": KASUN_UID}

    headers = {"Authorization": "Bearer mock-token-kasun"}
    response = await client.get("/api/v1/auth/me", headers=headers)

    assert response.status_code == 200
    data = response.json()

    # Base user fields
    assert data["full_name"] == "Kasun Mendis"
    assert data["role"] == "DRIVER"
    assert data["phone_number"] == "+94703595518"

    # Driver-specific fields are flat at root, NOT nested under "driver_profile"
    assert data["vehicle_type"] == "MOTORCYCLE"
    assert data["vehicle_number"] == "WP GA-1111"
    assert data["license_number"] == "L-SOUTH-001"

    print("✅ Successfully verified Kasun (Driver) flat profile.")
