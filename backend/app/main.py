from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import text
import firebase_admin
from firebase_admin import credentials

# If the .env is missing, the app violently crashes on this exact line 
# thanks to your strict Settings class in config.py!
from app.core.config import settings
from app.core.database import engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    LamiGo Pre-Flight Startup Checklist
    This runs before the server accepts any web traffic.
    """
    print("\n" + "="*50)
    print("🚀 INITIATING LAMIGO SERVER BOOT SEQUENCE")
    print("="*50)

    # 1. Environment Variables Check
    # If the code reached this line, config.py successfully found the .env file!
    print("⏳ 1/3: Environment Variables Loaded Successfully.")
    print("   ✅ Security configurations locked.")

    # 2. Active Database Ping
    print("⏳ 2/3: Checking PostgreSQL physical connection...")
    try:
        # Force a physical connection to PostgreSQL via the Async Engine
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        print("   ✅ DATABASE CONNECTED SUCCESSFULLY!")
    except Exception as e:
        print(f"   ❌ FATAL: Database connection failed! Error: {e}")
        # Crash the app immediately if the DB is down
        raise e

    # 3. Firebase Admin SDK Initialization
    print("⏳ 3/3: Verifying Firebase Master Credentials...")
    try:
        # Prevent crashing during FastAPI hot-reloads
        if not firebase_admin._apps:
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred)
        print("   ✅ FIREBASE ADMIN SDK INITIALIZED SUCCESSFULLY!")
    except Exception as e:
        print(f"   ❌ FATAL: Firebase initialization failed! Check your JSON key path. Error: {e}")
        raise e
        
    print("="*50)
    print("🟢 LAMIGO API IS LIVE AND ACCEPTING TRAFFIC")
    print("="*50 + "\n")
    
    yield # --- Server is running and listening for requests here ---
    
    # --- Shutdown Sequence ---
    print("\n🛑 Shutting down LamiGo API... closing database connections.")
    await engine.dispose()

# Initialize the FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    lifespan=lifespan
)

@app.get("/", tags=["Health Check"])
def read_root():
    return {
        "message": f"Welcome to the {settings.PROJECT_NAME}",
        "status": "online"
    }