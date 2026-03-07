from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.security import get_current_user
from app.core.database import get_db
from app.models.sql_models import SuperAdmin, User, Driver
from app.schemas.user_schemas import SuperAdminProfile, UserProfile, DriverProfile
from app.models.enums import UserRole

router = APIRouter()

@router.get("/me")
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user),  # Firebase decoded token
    db: AsyncSession = Depends(get_db)                     # PostgreSQL session
):
    # Extract email and phone from the decoded Firebase token
    email = current_user.get("email")
    phone = current_user.get("phone_number")  # Firebase always uses "phone_number"
    uid = current_user.get("uid")             # Firebase UID = primary key in DB

    # --- Super Admin Flow ---
    # If token has an email, this is an email/password login → Super Admin
    if email:
        admin = await db.execute(
            select(SuperAdmin).filter(SuperAdmin.admin_id == uid)
            )
        admin = admin.scalar_one_or_none()

        if not admin:
            raise HTTPException(status_code=404, detail="Super admin not found")

        return SuperAdminProfile.model_validate(admin)

    # --- Staff Flow ---
    # If token has a phone number, this is an OTP login → Manager or Driver
    elif phone:
        user =await db.execute(
            select(User).filter(User.user_id == uid)
            )
        user = user.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Block inactive/fired accounts
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Account is inactive")

        # Driver → fetch extra data from drivers table and return combined profile
        if user.role == UserRole.DRIVER:
            result = await db.execute(
                select(Driver).where(Driver.driver_id == uid)
            )
            driver = result.scalar_one_or_none()

            if not driver:
                raise HTTPException(status_code=404, detail="Driver profile not found")

            return DriverProfile(
                user_id=user.user_id,
                phone_number=user.phone_number,
                role=user.role,
                full_name=user.full_name,
                preferred_name=user.preferred_name,
                is_active=user.is_active,
                created_at=user.created_at,
                license_number=driver.license_number,
                vehicle_number=driver.vehicle_number,
                vehicle_type=driver.vehicle_type,
                status=driver.status
            )

        # Station Manager → return just the user profile
        return UserProfile.model_validate(user)

    else:
        raise HTTPException(status_code=400, detail="Could not identify user from token")