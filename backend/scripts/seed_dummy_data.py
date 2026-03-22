import asyncio
import sys
import os
from decimal import Decimal
from datetime import datetime, timezone
import selectors

# Adjust the path so the script can see the 'app' folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import engine
from app.models.sql_models import Organization, Branch, User, Driver
from app.models.enums import UserRole, VehicleType, DriverStatus

async def seed_data():
    print("\n" + "="*60)
    print("🚀 SEEDING: APEX DISPATCH SOLUTIONS")
    print("="*60)

    async with AsyncSession(engine) as session:
        try:
            # 1. Create Organization
            org = Organization(
                name="Apex Dispatch Solutions",
                contact_email="admin@apex-dispatch.com",
                website="https://apex-dispatch.com",
                is_active=True
            )
            session.add(org)
            await session.flush() 
            print(f"🏢 Organization Created: {org.name}")

            # 2. Create Two Regional Branches
            branch_south = Branch(
                org_id=org.org_id,
                name="Southern Coastal Hub",
                address="Matara Road, Galle",
                gps_lat=Decimal("6.0367"),
                gps_lng=Decimal("80.2170"),
                default_commission_rate=Decimal("15.00")
            )
            branch_western = Branch(
                org_id=org.org_id,
                name="Western Metro Station",
                address="Baseline Road, Colombo",
                gps_lat=Decimal("6.9271"),
                gps_lng=Decimal("79.8612"),
                default_commission_rate=Decimal("12.50")
            )
            session.add_all([branch_south, branch_western])
            await session.flush()
            print(f"📍 Branches Created: {branch_south.name}, {branch_western.name}")

            # 3. Create Two Station Managers
            # Manager 1: Southern Hub
            mgr_south = User(
                user_id="Kacju0gUqTN2ceNjZuaeM93HMXn2", 
                branch_id=branch_south.branch_id,
                phone_number="+94713230532",
                role=UserRole.STATION_MANAGER,
                full_name="Arjun Rathnayake",
                preferred_name="Arjun",
                nic_number="198823456789",
                is_active=True
            )
            # Manager 2: Western Hub
            mgr_western = User(
                user_id="D2yYxq6ajMXCreAZdmbKDX4GDvn2",
                branch_id=branch_western.branch_id,
                phone_number="+94774384919",
                role=UserRole.STATION_MANAGER,
                full_name="Dilshan Perera",
                preferred_name="Dilshan",
                nic_number="199045678901",
                is_active=True
            )
            session.add_all([mgr_south, mgr_western])
            await session.flush()
            print(f"👤 Station Managers assigned to respective hubs.")

            # 4. Create Three Drivers (Users + Operational Profiles)
            
            # Driver 1 (South - Motorcycle)
            d1_user = User(
                user_id="uC2V93X7znQOfrHxtAOt8WkIVFl2",
                branch_id=branch_south.branch_id,
                phone_number="+94703595518",
                role=UserRole.DRIVER,
                full_name="Kasun Mendis",
                preferred_name="Kasun",
                nic_number="199511223344",
                is_active=True
            )
            # Driver 2 (Western - Three Wheel)
            d2_user = User(
                user_id="TgNvRy2AfXQfsFnkqBjJQ9bbHbZ2",
                branch_id=branch_western.branch_id,
                phone_number="+94774779060",
                role=UserRole.DRIVER,
                full_name="Roshan Silva",
                preferred_name="Roshan",
                nic_number="199733445566",
                is_active=True
            )
            # Driver 3 (Western - Lorry)
            d3_user = User(
                user_id="rLFD1Go28QSh29Ubs1zkZGIICbY2",
                branch_id=branch_western.branch_id,
                phone_number="+94761997415",
                role=UserRole.DRIVER,
                full_name="Niroshan Bandara",
                preferred_name="Niro",
                nic_number="199955667788",
                is_active=True
            )
            
            session.add_all([d1_user, d2_user, d3_user])
            await session.flush()

            # 5. Create Driver Operational Profiles (Linking to User IDs)
            profiles = [
                Driver(
                    driver_id=d1_user.user_id,
                    license_number="L-SOUTH-001",
                    vehicle_number="WP GA-1111",
                    vehicle_type=VehicleType.MOTORCYCLE,
                    status=DriverStatus.OFF_DUTY,
                    created_by=mgr_south.user_id
                ),
                Driver(
                    driver_id=d2_user.user_id,
                    license_number="L-WEST-002",
                    vehicle_number="WP QZ-2222",
                    vehicle_type=VehicleType.THREE_WHEEL,
                    status=DriverStatus.OFF_DUTY,
                    created_by=mgr_western.user_id
                ),
                Driver(
                    driver_id=d3_user.user_id,
                    license_number="L-WEST-003",
                    vehicle_number="WP LY-3333",
                    vehicle_type=VehicleType.LORRY,
                    status=DriverStatus.OFF_DUTY,
                    created_by=mgr_western.user_id
                )
            ]
            session.add_all(profiles)
            
            await session.commit()
            print("✅ Seeding successful! Apex Dispatch is operational.")

        except Exception as e:
            await session.rollback()
            print(f"❌ FATAL ERROR DURING SEEDING: {e}")
            raise e

    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(seed_data(), loop_factory=lambda: asyncio.SelectorEventLoop(selectors.SelectSelector()))