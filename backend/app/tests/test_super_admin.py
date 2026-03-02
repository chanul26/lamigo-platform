import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.sql_models import SuperAdmin
from app.core.database import engine

# ==============================================================================
# LAYER 1: Direct Database Verification
# Confirms the SuperAdmin record exists in PostgreSQL before testing the API.
# ==============================================================================
@pytest.mark.asyncio
async def test_super_admin_exists_in_db():
    """
    Directly queries the super_admins table to verify the seeded
    record exists with the correct email. No API or HTTP involved.
    """
    ADMIN_UID = "MwCKifPTobV7VFb2KwKg7uYbMuX2"

    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(SuperAdmin).where(SuperAdmin.admin_id == ADMIN_UID)
        )
        admin = result.scalar_one_or_none()

        assert admin is not None, "SuperAdmin record not found in DB. Did you run create_super_admin.py?"
        assert admin.email == "lamigo.sdgp@gmail.com"
        assert admin.role.value == "SUPER_ADMIN"
        print(f"\n✅ SuperAdmin '{admin.name}' verified in DB.")


# ==============================================================================
# LAYER 2: API Endpoint Verification
# Confirms the /me endpoint returns the correct SuperAdmin payload.
# ==============================================================================
@pytest.mark.asyncio
async def test_super_admin_me_endpoint(client, mock_auth):
    """
    Mocks a valid Firebase token for the SuperAdmin UID and verifies
    the /me endpoint returns the correct admin profile from the DB.
    """
    ADMIN_UID = "MwCKifPTobV7VFb2KwKg7uYbMuX2"
    mock_auth.return_value = {"uid": ADMIN_UID}

    headers = {"Authorization": "Bearer mock-token-admin"}
    response = await client.get("/api/v1/auth/me", headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert data["role"] == "SUPER_ADMIN"
    assert data["email"] == "lamigo.sdgp@gmail.com"
    assert data["name"] == "LamiGo System Admin"

    # SuperAdmin response must NOT expose branch or phone (those are staff fields)
    assert "branch_id" not in data
    assert "phone_number" not in data

    print("\n✅ SuperAdmin /me endpoint verified successfully.")
