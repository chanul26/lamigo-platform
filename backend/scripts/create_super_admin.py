import asyncio
import sys
import os

# Adjust the path so the script can see the 'app' folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import engine
from app.models.sql_models import SuperAdmin
from app.models.enums import UserRole

async def create_admin():
    print("\n" + "="*50)
    print("🛡️  LAMIGO SUPERADMIN INITIALIZATION")
    print("="*50)

    # --- Configuration (Generic Admin) ---
    # 1. GO TO FIREBASE CONSOLE -> AUTHENTICATION
    # 2. CREATE A USER WITH EMAIL: lamigo.sdgp@gmail.com
    # 3. COPY THE 'User UID' AND PASTE IT BELOW
    ADMIN_UID = "MwCKifPTobV7VFb2KwKg7uYbMuX2"
    ADMIN_EMAIL = "lamigo.sdgp@gmail.com"
    ADMIN_NAME = "LamiGo System Admin"

    async with AsyncSession(engine) as session:
        try:
            new_admin = SuperAdmin(
                admin_id=ADMIN_UID,
                email=ADMIN_EMAIL,
                name=ADMIN_NAME,
                role=UserRole.SUPER_ADMIN
            )
            
            session.add(new_admin)
            await session.commit()
            print(f"\n✅ SUCCESS: {ADMIN_NAME} is now a SuperAdmin in PostgreSQL!")
            print(f"🔗 Linked to Firebase UID: {ADMIN_UID}")
            
        except Exception as e:
            await session.rollback()
            print(f"\n❌ ERROR: Could not create admin. (Maybe the UID already exists?)")
            print(f"Details: {e}")

    print("="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(create_admin())