import firebase_admin
from firebase_admin import auth
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Imported the Driver model and all our schemas
from app.models.sql_models import User, Branch, Driver
from app.models.enums import UserRole, DriverStatus
from app.schemas.user_schemas import UserCreate, UserUpdate, DriverCreate, DriverUpdate


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    """
    Onboards a new Station Manager.
    Automatically provisions their Firebase Auth account and links it to PostgreSQL.
    """
    # 1. PRE-FLIGHT CHECKS
    branch_result = await db.execute(select(Branch).where(Branch.branch_id == user_in.branch_id))
    if not branch_result.scalars().first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Branch not found.")

    # Note: user_id check removed because we generate it now
    existing_user = await db.execute(
        select(User).where(
            (User.nic_number == user_in.nic_number) |
            (User.phone_number == user_in.phone_number)
        )
    )
    if existing_user.scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Identity duplicate found (NIC or Phone).")

    # 2. FIREBASE PROVISIONING
    firebase_uid = None
    try:
        try:
            existing_fb_user = auth.get_user_by_phone_number(user_in.phone_number)
            firebase_uid = existing_fb_user.uid
        except auth.UserNotFoundError:
            new_fb_user = auth.create_user(
                phone_number=user_in.phone_number,
                display_name=user_in.full_name
            )
            firebase_uid = new_fb_user.uid
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to communicate with Firebase: {str(e)}"
        )

    # 3. POSTGRESQL EXECUTION
    # Inject the newly generated firebase_uid into the database model
    new_user = User(user_id=firebase_uid, **user_in.model_dump())
    db.add(new_user)
    
    # 4. SAFETY ROLLBACK
    try:
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except Exception as e:
        await db.rollback()
        # Clean up Firebase so we don't have ghost accounts if the DB fails
        if firebase_uid:
            auth.delete_user(firebase_uid)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Database transaction failed. Cleaned up Firebase Auth."
        )


async def create_driver(db: AsyncSession, driver_in: DriverCreate, created_by_id: str) -> User:
    """
    All-In-One Onboarding for Drivers.
    Provisions Firebase, creates the base User identity, AND the operational Driver profile.
    """
    # 1. PRE-FLIGHT CHECKS
    branch_result = await db.execute(select(Branch).where(Branch.branch_id == driver_in.branch_id))
    if not branch_result.scalars().first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Branch not found.")

    existing_user = await db.execute(
        select(User).where(
            (User.nic_number == driver_in.nic_number) |
            (User.phone_number == driver_in.phone_number)
        )
    )
    if existing_user.scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Identity duplicate found (NIC or Phone).")

    existing_license = await db.execute(select(Driver).where(Driver.license_number == driver_in.license_number))
    if existing_license.scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Driving License already registered.")

    # 2. FIREBASE PROVISIONING
    firebase_uid = None
    try:
        try:
            existing_fb_user = auth.get_user_by_phone_number(driver_in.phone_number)
            firebase_uid = existing_fb_user.uid
        except auth.UserNotFoundError:
            new_fb_user = auth.create_user(
                phone_number=driver_in.phone_number,
                display_name=driver_in.full_name
            )
            firebase_uid = new_fb_user.uid
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to communicate with Firebase: {str(e)}"
        )

    # 3. SPLIT DATA & EXECUTE POSTGRESQL
    user_data = driver_in.model_dump(exclude={'license_number', 'vehicle_number', 'vehicle_type', 'commission_rate'})
    driver_data = driver_in.model_dump(include={'license_number', 'vehicle_number', 'vehicle_type', 'commission_rate'})

    # Inject the firebase_uid into BOTH tables
    new_user = User(user_id=firebase_uid, **user_data)
    db.add(new_user)
    
    new_driver = Driver(
        driver_id=firebase_uid, 
        created_by=created_by_id,
        status=DriverStatus.OFF_DUTY,
        **driver_data
    )
    db.add(new_driver)

    # 4. SAFETY ROLLBACK
    try:
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except Exception as e:
        await db.rollback()
        if firebase_uid:
            auth.delete_user(firebase_uid)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Database transaction failed. Cleaned up Firebase Auth."
        )


async def get_user(db: AsyncSession, user_id: str) -> User:
    """Fetches a specific user by their Firebase UID."""
    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


async def get_user_by_nic(db: AsyncSession, nic_number: str) -> User:
    """
    Looks up a user strictly by their National Identity Card number.
    Used for frontend search bars where a Manager needs to find a specific staff member.
    """
    result = await db.execute(select(User).where(User.nic_number == nic_number))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No user found with NIC: {nic_number}")
    return user


async def get_users_by_branch(db: AsyncSession, branch_id: UUID, role: UserRole = None) -> list[User]:
    """Fetches staff for a specific branch with optional role filtering."""
    query = select(User).where(User.branch_id == branch_id)
    if role:
        query = query.where(User.role == role)
        
    result = await db.execute(query)
    return result.scalars().all()


async def update_user(db: AsyncSession, user_id: str, user_in: UserUpdate) -> User:
    """Updates specific fields of a Station Manager profile."""
    user = await get_user(db, user_id)
    
    update_data = user_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
        
    await db.commit()
    await db.refresh(user)
    
    return user


async def update_driver(db: AsyncSession, driver_id: str, driver_in: DriverUpdate) -> User:
    """
    Updates a Driver's profile.
    Smartly routes identity changes to the 'users' table and operational changes to the 'drivers' table.
    """
    user = await get_user(db, driver_id)
    
    driver_result = await db.execute(select(Driver).where(Driver.driver_id == driver_id))
    driver = driver_result.scalars().first()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Driver operational profile not found for this user."
        )

    update_data = driver_in.model_dump(exclude_unset=True)
    driver_specific_fields = {'license_number', 'vehicle_number', 'vehicle_type', 'commission_rate', 'status'}

    for field, value in update_data.items():
        if field in driver_specific_fields:
            setattr(driver, field, value)
        else:
            setattr(user, field, value)
            
    await db.commit()
    await db.refresh(user)
    
    return user