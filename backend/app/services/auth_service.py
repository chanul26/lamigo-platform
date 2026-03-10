from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from firebase_admin import auth as firebase_auth

# Import your SQLAlchemy models and Enums
from app.models.sql_models import SuperAdmin, User, Driver
from app.models.enums import UserRole

async def get_current_db_user(uid: str, db: AsyncSession) -> dict:
    """
    Takes a verified Firebase UID and searches the PostgreSQL database.
    Returns the profile as a dictionary to be validated by Pydantic.
    (Read-only, no database commits are performed here).
    """
    
    # ---------------------------------------------------------
    # 1. Check SuperAdmin Table (NextJS / Swagger UI)
    # ---------------------------------------------------------
    admin_query = await db.execute(select(SuperAdmin).where(SuperAdmin.admin_id == uid))
    admin = admin_query.scalar_one_or_none()
    
    if admin:
        return {
            "user_id": admin.admin_id,
            "email": admin.email,
            "name": admin.name,
            "role": admin.role
        }

    # ---------------------------------------------------------
    # 2. Check Core Users Table (Managers & Drivers)
    # ---------------------------------------------------------
    user_query = await db.execute(select(User).where(User.user_id == uid))
    user = user_query.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is not registered in the LamiGo system."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated."
        )

    # Base dictionary containing shared user fields
    user_data = {
        "user_id": user.user_id,
        "branch_id": user.branch_id,
        "phone_number": user.phone_number,
        "role": user.role,
        "full_name": user.full_name,
        "preferred_name": user.preferred_name,
        "email": user.email,
        "is_active": user.is_active,
        # NOTICE: fcm_token has been completely removed from here!
    }

    # ---------------------------------------------------------
    # 3. Handle Specific Roles (Station Manager)
    # ---------------------------------------------------------
    if user.role == UserRole.STATION_MANAGER:
        return user_data

    # ---------------------------------------------------------
    # 4. Handle Specific Roles (Driver)
    # ---------------------------------------------------------
    if user.role == UserRole.DRIVER:
        driver_query = await db.execute(select(Driver).where(Driver.driver_id == uid))
        driver = driver_query.scalar_one_or_none()

        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver operational profile is missing."
            )
            
        user_data.update({
            "license_number": driver.license_number,
            "vehicle_number": driver.vehicle_number,
            "vehicle_type": driver.vehicle_type,
            "status": driver.status,
            "commission_rate": driver.commission_rate
        })
        
        return user_data

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Unknown user role detected."
    )


async def process_user_login(uid: str, db: AsyncSession, fcm_token: str | None = None) -> dict:
    """
    Handles the write operations for a user login.
    Updates timestamps for admins, saves FCM tokens for staff, and returns the formatted profile.
    """
    # 1. Check if user is a SuperAdmin to update their specific timestamp
    admin_query = await db.execute(select(SuperAdmin).where(SuperAdmin.admin_id == uid))
    admin = admin_query.scalar_one_or_none()
    
    if admin:
        admin.last_access_at = datetime.now(timezone.utc)
        try:
            await db.commit()
        except Exception as e:
            print(f"⚠️ Warning: Could not update last_access_at for admin {uid}: {e}")
            await db.rollback()
            
    # 2. Update fcm_token for standard Users (Managers and Drivers)
    else:
        user_query = await db.execute(select(User).where(User.user_id == uid))
        user = user_query.scalar_one_or_none()
        
        # Only update if the user exists and the frontend actually sent a token
        if user and fcm_token is not None:
            user.fcm_token = fcm_token
            try:
                await db.commit()
            except Exception as e:
                print(f"⚠️ Warning: Could not update fcm_token for user {uid}: {e}")
                await db.rollback()

    # 3. Fetch and return the fully formatted profile using the safe read-only function
    return await get_current_db_user(uid=uid, db=db)


async def process_user_logout(uid: str, db: AsyncSession) -> None:
    """
    Handles the write operations for a user logout.
    Clears the FCM token to stop push notifications and revokes Firebase sessions.
    """
    # 1. Clear the FCM token for standard Users (Managers and Drivers)
    user_query = await db.execute(select(User).where(User.user_id == uid))
    user = user_query.scalar_one_or_none()
    
    if user:
        user.fcm_token = None
        try:
            await db.commit()
        except Exception as e:
            print(f"⚠️ Warning: Could not clear fcm_token for user {uid}: {e}")
            await db.rollback()

    # 2. Revoke Firebase refresh tokens globally (Security Best Practice)
    try:
        firebase_auth.revoke_refresh_tokens(uid)
    except Exception as e:
        print(f"⚠️ Warning: Could not revoke Firebase tokens for {uid}: {e}")