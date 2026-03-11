from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

# Import your custom modules
from app.core.database import get_db
from app.core.security import verify_firebase_token
from app.services import auth_service
from app.schemas.user import CurrentUserResponse, LoginRequest

# --- ADDED: Import our new centralized dependency chain ---
from app.api.deps import get_current_user

# Create the router for Auth endpoints
router = APIRouter()

@router.get("/me", response_model=CurrentUserResponse)
async def get_current_user_profile(
    # --- CHANGED: Replaced the manual verify_firebase_token and db session ---
    # The new Gatekeeper handles the token verification, DB lookup, and error throwing natively!
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieves the profile of the currently logged-in user.
    Requires a valid Firebase Bearer token in the Authorization header.
    """
    # --- CHANGED: Deleted all the repetitive manual UID extraction and DB querying ---
    
    # FastAPI and Pydantic will automatically look at the 'role' in current_user
    # and use the correct schema (SuperAdmin, StationManager, or Driver) to format the JSON!
    return current_user


@router.post("/login", response_model=CurrentUserResponse)
async def login_user(
    # The optional JSON body payload from the frontend
    login_data: LoginRequest,
    
    # 1. The Padlock
    token_payload: dict = Depends(verify_firebase_token),
    
    # 2. The Database
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticates a user and performs login database writes.
    Saves the device FCM token for mobile push notifications.
    Should be called EXACTLY ONCE by the frontend after a successful Firebase login.
    """
    # NOTE: We keep the manual extraction here because this is a WRITE operation.
    # It specifically needs the raw DB session to update the FCM token and last_access_at timestamp.
    uid = token_payload.get("uid")
    
    if not uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload is missing UID."
        )

    # Call the new write-enabled service function
    user_profile = await auth_service.process_user_login(
        uid=uid, 
        db=db, 
        fcm_token=login_data.fcm_token
    )
    
    return user_profile


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout_user(
    # 1. The Padlock
    token_payload: dict = Depends(verify_firebase_token),
    
    # 2. The Database
    db: AsyncSession = Depends(get_db)
):
    """
    Securely logs out the user.
    Clears their FCM push notification token from the database and revokes active Firebase sessions.
    """
    # NOTE: We keep the manual extraction here as well to handle 
    # the specific database write operation of clearing the fcm_token.
    uid = token_payload.get("uid")
    
    if not uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload is missing UID."
        )

    # Call the service function to handle the database and Firebase teardown
    await auth_service.process_user_logout(uid=uid, db=db)
    
    return {"message": "Successfully logged out. Push notifications disabled."}