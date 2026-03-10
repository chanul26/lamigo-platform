from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
import firebase_admin
from firebase_admin import credentials

from app.core.config import settings
from app.core.database import engine

# --- 1. Import your Master Central Hub ---
from app.api.api_v1.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    LamiGo Pre-Flight Startup Checklist
    """
    print("\n" + "="*50)
    print("🚀 INITIATING LAMIGO SERVER BOOT SEQUENCE")
    print("="*50)

    # 1. Environment Variables Check
    print("⏳ 1/3: Environment Variables Loaded Successfully.")
    print("   ✅ Security configurations locked.")

    # 2. Active Database Ping
    print("⏳ 2/3: Checking PostgreSQL physical connection...")
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        print("   ✅ DATABASE CONNECTED SUCCESSFULLY!")
    except Exception as e:
        print(f"   ❌ FATAL: Database connection failed! Error: {e}")
        raise e

    # 3. Firebase Admin SDK Initialization
    print("⏳ 3/3: Verifying Firebase Master Credentials...")
    try:
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
    
    yield
    
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

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. Register the Master Router ---
# We apply the global "/api/v1" prefix here. 
# Combined with router.py, the final URL becomes /api/v1/auth/me
app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Health Check"])
def read_root():
    return {
        "message": f"Welcome to the {settings.PROJECT_NAME}",
        "status": "online"
    }

@app.get("/api/health", tags=["Health Check"])
def health_check():
    return {"status": "ok", "message": "LamiGo API is running"}