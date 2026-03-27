import pytest

# ==============================================================================
# Station Manager — Southern Coastal Hub
# Arjun Rathnayake | UID: Kacju0gUqTN2ceNjZuaeM93HMXn2
# ==============================================================================
@pytest.mark.asyncio
async def test_manager_arjun_profile(client, mock_auth):
    """
    Verifies the Southern Hub manager's profile is returned correctly.
    Arjun is a STATION_MANAGER with phone-based Firebase auth.
    """
    ARJUN_UID = "Kacju0gUqTN2ceNjZuaeM93HMXn2"
    mock_auth.return_value = {"uid": ARJUN_UID}

    headers = {"Authorization": "Bearer mock-token-arjun"}
    response = await client.get("/api/v1/auth/me", headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert data["full_name"] == "Arjun Rathnayake"
    assert data["role"] == "STATION_MANAGER"
    assert data["phone_number"] == "+94713230532"
    assert data["is_active"] is True

    # Manager response must NOT expose driver-only fields
    assert "vehicle_type" not in data
    assert "license_number" not in data

    print("\n✅ Arjun (Manager - Southern Hub) profile verified.")


# ==============================================================================
# Station Manager — Western Metro Station
# Dilshan Perera | UID: D2yYxq6ajMXCreAZdmbKDX4GDvn2
# ==============================================================================
@pytest.mark.asyncio
async def test_manager_dilshan_profile(client, mock_auth):
    """
    Verifies the Western Hub manager's profile is returned correctly.
    Dilshan is the second seeded STATION_MANAGER.
    """
    DILSHAN_UID = "D2yYxq6ajMXCreAZdmbKDX4GDvn2"
    mock_auth.return_value = {"uid": DILSHAN_UID}

    headers = {"Authorization": "Bearer mock-token-dilshan"}
    response = await client.get("/api/v1/auth/me", headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert data["full_name"] == "Dilshan Perera"
    assert data["role"] == "STATION_MANAGER"
    assert data["phone_number"] == "+94774384919"
    assert data["is_active"] is True

    print("\n✅ Dilshan (Manager - Western Metro) profile verified.")
