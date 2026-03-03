from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

# Import your custom modules
from app.core.security import verify_firebase_token
from app.services import auth_service
from app.schemas.user import CurrentUserResponse
from app.core.database import SessionLocal
# --- Database Dependency ---
# (If you already have this in a deps.py file, you can import it instead)
async def get_db():
    async with SessionLocal() as session:
        yield session

# Create the router for Auth endpoints
router = APIRouter()

@router.get("/me", response_model=CurrentUserResponse)
async def get_current_user_profile(
    # 1. The Padlock: Intercepts the header, verifies with Google, returns the payload
    token_payload: dict = Depends(verify_firebase_token),
    
    # 2. The Database: Opens a secure, temporary connection to PostgreSQL
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves the profile of the currently logged-in user.
    Requires a valid Firebase Bearer token in the Authorization header.
    """
    # Extract the uid from the verified Firebase payload
    uid = token_payload.get("uid")
    
    if not uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload is missing UID."
        )

    # 3. The Brain: Look up the user in PostgreSQL and format the data
    user_profile = await auth_service.get_current_db_user(uid=uid, db=db)
    
    # FastAPI and Pydantic will automatically look at the 'role' in user_profile
    # and use the correct schema (SuperAdmin, StationManager, or Driver) to format the JSON!
    return user_profile