"""
LamiGo Authentication Endpoints
Handles user authentication via Firebase

Note: Primary authentication is handled by Firebase on the frontend.
These endpoints are for server-side token verification and user management.
"""

from fastapi import APIRouter, HTTPException, status

router = APIRouter()


@router.post("/verify-token")
def verify_firebase_token(token: str):
    """
    Verify a Firebase ID token.
    
    This endpoint is used by the frontend to verify tokens
    and get user information from the backend.
    
    TODO: Implement Firebase token verification
    """
    return {
        "status": "placeholder",
        "message": "Firebase token verification not yet implemented",
    }


@router.get("/me")
def get_current_user():
    """
    Get the current authenticated user's information.
    
    TODO: Implement with Firebase Auth dependency
    """
    return {
        "status": "placeholder",
        "message": "Current user endpoint not yet implemented",
    }


@router.post("/logout")
def logout():
    """
    Handle user logout (server-side cleanup if needed).
    
    Note: Primary logout is handled by Firebase on the frontend.
    This endpoint can be used for server-side session cleanup.
    """
    return {
        "status": "success",
        "message": "Logged out successfully",
    }
