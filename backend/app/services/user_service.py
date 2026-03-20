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
    Establishes their core identity and links them to their physical hub.
    """
    branch_result = await db.execute(select(Branch).where(Branch.branch_id == user_in.branch_id))
    if not branch_result.scalars().first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Branch not found.")

    existing_user = await db.execute(
        select(User).where(
            (User.nic_number == user_in.nic_number) |
            (User.phone_number == user_in.phone_number) |
            (User.user_id == user_in.user_id)
        )
    )
    if existing_user.scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Identity duplicate found (NIC/Phone/UID).")

    new_user = User(**user_in.model_dump())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user


async def create_driver(db: AsyncSession, driver_in: DriverCreate, created_by_id: str) -> User:
    """
    All-In-One Onboarding for Drivers.
    Splits the payload to create the base User identity AND the operational Driver profile.
    """
    branch_result = await db.execute(select(Branch).where(Branch.branch_id == driver_in.branch_id))
    if not branch_result.scalars().first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Branch not found.")

    existing_user = await db.execute(
        select(User).where(
            (User.nic_number == driver_in.nic_number) |
            (User.phone_number == driver_in.phone_number) |
            (User.user_id == driver_in.user_id)
        )
    )
    if existing_user.scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Identity duplicate found.")

    existing_license = await db.execute(select(Driver).where(Driver.license_number == driver_in.license_number))
    if existing_license.scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Driving License already registered.")

    user_data = driver_in.model_dump(exclude={'license_number', 'vehicle_number', 'vehicle_type', 'commission_rate'})
    driver_data = driver_in.model_dump(include={'license_number', 'vehicle_number', 'vehicle_type', 'commission_rate'})

    new_user = User(**user_data)
    db.add(new_user)
    
    new_driver = Driver(
        driver_id=new_user.user_id,
        created_by=created_by_id,
        status=DriverStatus.OFF_DUTY,
        **driver_data
    )
    db.add(new_driver)

    await db.commit()
    await db.refresh(new_user)
    
    return new_user


async def get_user(db: AsyncSession, user_id: str) -> User:
    """Fetches a specific user by their Firebase UID."""
    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
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
    # 1. Fetch the base user (will throw 404 if not found)
    user = await get_user(db, driver_id)
    
    # 2. Fetch the linked driver profile
    driver_result = await db.execute(select(Driver).where(Driver.driver_id == driver_id))
    driver = driver_result.scalars().first()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Driver operational profile not found for this user."
        )

    # 3. Get only the fields the frontend actually sent
    update_data = driver_in.model_dump(exclude_unset=True)
    
    # Define which fields belong to the drivers table
    driver_specific_fields = {'license_number', 'vehicle_number', 'vehicle_type', 'commission_rate', 'status'}

    # 4. Route the updates to the correct SQLAlchemy model
    for field, value in update_data.items():
        if field in driver_specific_fields:
            setattr(driver, field, value)
        else:
            setattr(user, field, value)
            
    # 5. Commit both updates simultaneously
    await db.commit()
    await db.refresh(user)
    
    return user