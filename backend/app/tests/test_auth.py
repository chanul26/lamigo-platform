import pytest
@pytest.mark.asyncio
async def test_unauthorized_no_token(client):
    """
    Hitting a protected endpoint with no Bearer token must return 401.
    This is the fundamental security gate check.
    """
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401