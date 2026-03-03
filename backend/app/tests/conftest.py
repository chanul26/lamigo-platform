import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.core.database import engine


# ==============================================================================
# CLIENT FIXTURE
# Provides a real async HTTP client that talks directly to the FastAPI app
# in-memory, without needing a live server running.
# ==============================================================================
@pytest_asyncio.fixture
async def client():
    """
    Async HTTP client for making requests to the FastAPI app.
    Uses ASGITransport for HTTPX 0.28+ compatibility.
    Scope: per-test (default). Each test gets a fresh client.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ==============================================================================
# FIREBASE AUTH MOCK FIXTURE
# Patches the Firebase Admin SDK token verifier so tests never hit Google's
# servers. Tests can control exactly what token payload gets returned.
#
# Usage in a test:
#   mock_auth.return_value = {"uid": "SOME_UID_FROM_SEED_DATA"}
# ==============================================================================
@pytest.fixture
def mock_auth():
    """
    Mocks Firebase token verification at the security layer.
    Prevents any real network call to Google during testing.
    """
    with patch("app.core.security.auth.verify_id_token") as mock:
        yield mock


# ==============================================================================
# DATABASE SESSION FIXTURE
# Opens a direct SQLAlchemy async session for tests that need to inspect
# or verify data in PostgreSQL without going through the API layer.
#
# Note: This hits the REAL database configured in your .env file.
# It is intentional — we test against the seeded Apex Dispatch data.
# ==============================================================================
@pytest_asyncio.fixture
async def db_session():
    """
    Provides a live async database session for direct PostgreSQL queries.
    Session is closed automatically after each test via the context manager.
    """
    async with AsyncSession(engine) as session:
        yield session
