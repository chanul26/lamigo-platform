from typing import List
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

# Import your core modules
from app.core.database import get_db
from app.core.security import verify_firebase_token
from app.services import auth_service
from app.models.enums import UserRole

async def get_current_user(
    # Link 1: The Firebase Padlock
    token_payload: dict = Depends(verify_firebase_token),
    # Link 2: The Database Connection
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Base dependency that fetches the user profile from the database 
    using the verified Firebase UID. 
    It automatically blocks deactivated users or missing profiles.
    """
    uid = token_payload.get("uid")
    
    if not uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload is missing UID."
        )
    
    # Let the auth_service handle the database lookups and active/inactive checks
    user_profile = await auth_service.get_current_db_user(uid=uid, db=db)
    
    return user_profile


class RoleChecker:
    """
    Enterprise Role-Based Access Control (RBAC) Gatekeeper.
    
    Usage on endpoints: 
    user_profile = Depends(RoleChecker([UserRole.SUPER_ADMIN, UserRole.STATION_MANAGER]))
    """
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles

    async def __call__(self, user: dict = Depends(get_current_user)) -> dict:
        """
        This is called automatically by FastAPI. It receives the user from 
        `get_current_user` and checks if their role is in the allowed list.
        """
        user_role = user.get("role")
        
        if user_role not in self.allowed_roles:
            # Format a clean error message showing exactly who is allowed in
            allowed_list = [role.value for role in self.allowed_roles]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access Denied. This action requires one of the following roles: {allowed_list}"
            )
        
        # If they pass the check, hand the fully validated user profile to the endpoint route!
        return user