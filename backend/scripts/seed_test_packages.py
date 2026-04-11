import asyncio
import sys
import os
import random
import uuid
from decimal import Decimal
from datetime import datetime, timezone
import selectors

# Adjust the path so the script can see the 'app' folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import engine
from app.models.sql_models import Branch, Recipient, Package
from app.models.enums import LocationType, PackageStatus

# 10 Realistic Mock Data Profiles around Colombo
MOCK_PROFILES = [
    {"name": "Nimal Perera", "phone": "+94771112222", "loc": LocationType.HOME, "lat": "6.9270", "lng": "79.8610", "addr": "12/A, Baseline Road, Colombo 08", "is_cod": False, "weight": 1.5},
    {"name": "Fathima Ahmed", "phone": "+94712223333", "loc": LocationType.APARTMENT, "lat": "6.9147", "lng": "79.8514", "addr": "Apt 4B, Marine Drive, Kollupitiya", "is_cod": True, "weight": 5.2},
    {"name": "Ruwan Silva", "phone": "+94703334444", "loc": LocationType.OFFICE, "lat": "6.9344", "lng": "79.8428", "addr": "Level 12, WTC, Colombo 01", "is_cod": False, "weight": 0.5},
    {"name": "Kumari Fernando", "phone": "+94764445555", "loc": LocationType.HOME, "lat": "6.8906", "lng": "79.8584", "addr": "45, Galle Road, Bambalapitiya", "is_cod": True, "weight": 2.0},
    {"name": "Dinesh Bandara", "phone": "+94785556666", "loc": LocationType.RETAIL_STORE, "lat": "6.9052", "lng": "79.8540", "addr": "Tech Shop, Duplication Road", "is_cod": False, "weight": 12.0},
    {"name": "Chamari Alwis", "phone": "+94726667777", "loc": LocationType.HOME, "lat": "6.8741", "lng": "79.8605", "addr": "78, W.A. Silva Mawatha, Wellawatte", "is_cod": True, "weight": 1.2},
    {"name": "Ajantha Mendis", "phone": "+94777778888", "loc": LocationType.APARTMENT, "lat": "6.9215", "lng": "79.8562", "addr": "Unit 2, Park Heights, Colombo 03", "is_cod": False, "weight": 8.5},
    {"name": "Sanjeewa Raj", "phone": "+94718889999", "loc": LocationType.HOME, "lat": "6.9412", "lng": "79.8654", "addr": "100, Kotahena Street, Colombo 13", "is_cod": True, "weight": 3.4},
    {"name": "Nadeeka Peries", "phone": "+94709990000", "loc": LocationType.OFFICE, "lat": "6.9189", "lng": "79.8621", "addr": "HNB Towers, Colombo 02", "is_cod": False, "weight": 0.8},
    {"name": "Lasith Jayakody", "phone": "+94760001111", "loc": LocationType.WAREHOUSE, "lat": "6.9456", "lng": "79.8712", "addr": "Warehouse 4, Grandpass", "is_cod": True, "weight": 25.0},
]

async def seed_packages():
    print("\n" + "="*60)
    print("📦 SEEDING: RECIPIENTS & PACKAGES")
    print("="*60)

    async with AsyncSession(engine) as session:
        try:
            # 1. Fetch an existing Branch (We need this to assign the packages)
            result = await session.execute(select(Branch).limit(1))
            branch = result.scalar_one_or_none()
            
            if not branch:
                print("❌ ERROR: No Branch found in the database. Please run your initial seed script first.")
                return
                
            print(f"🏢 Linking packages to Branch: {branch.name} ({branch.branch_id})")

            recipients_created = 0
            packages_created = 0

            # 2. Loop through our mock data to create Recipients and Packages
            for i, profile in enumerate(MOCK_PROFILES):
                # A. Create Recipient
                recipient = Recipient(
                    name=profile["name"],
                    phone_number=profile["phone"],
                    address=profile["addr"],
                    location_type=profile["loc"],
                    is_location_verified=random.choice([True, False]), # Randomize verification for ML variance
                    gps_lat=Decimal(profile["lat"]),
                    gps_lng=Decimal(profile["lng"])
                )
                session.add(recipient)
                await session.flush() # Flush to get the generated recipient_id
                recipients_created += 1

                # B. Create Package linked to Recipient
                cod_amount = Decimal(random.randint(1500, 15000)) if profile["is_cod"] else Decimal("0.00")
                
                pkg = Package(
                    tracking_id=f"LMG-TEST-{1000 + i}",
                    recipient_id=recipient.recipient_id,
                    branch_id=branch.branch_id,
                    status=PackageStatus.TO_BE_DELIVERED,
                    
                    sender_name="Daraz Sri Lanka", # Mock Sender
                    sender_phone="+94112345678",
                    weight=Decimal(str(profile["weight"])),
                    is_cod=profile["is_cod"],
                    cod_amount=cod_amount,
                    delivery_charge=Decimal("350.00"),
                    
                    # Snapshot Data (As defined in your SQLAlchemy model)
                    recipient_name=recipient.name,
                    address=recipient.address,
                    gps_lat=recipient.gps_lat,
                    gps_lng=recipient.gps_lng
                )
                session.add(pkg)
                packages_created += 1

            # 3. Commit all to PostgreSQL
            await session.commit()
            print(f"✅ Success! Created {recipients_created} Recipients and {packages_created} Packages.")

        except Exception as e:
            await session.rollback()
            print(f"❌ FATAL ERROR DURING SEEDING: {e}")
            raise e

    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(seed_packages(), loop_factory=lambda: asyncio.SelectorEventLoop(selectors.SelectSelector()))