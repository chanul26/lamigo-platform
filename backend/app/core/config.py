import os
import json
from dotenv import load_dotenv, find_dotenv

# --- Environment Variable Loader ---
env_path = find_dotenv()
load_dotenv(env_path)

class Settings:
    """
    Centralized configuration management for the LamiGo API.
    Strictly enforces that required environment variables are present.
    """
    # System Metadata
    PROJECT_NAME: str = "LamiGo API"
    PROJECT_DESCRIPTION: str = "Last-Mile Delivery Optimization Platform"
    VERSION: str = "1.0.0"

    # Variables (No fallback defaults allowed)
    DATABASE_URL: str | None = os.getenv("DATABASE_URL")
    SECRET_KEY: str | None = os.getenv("SECRET_KEY")
    FIREBASE_CREDENTIALS_PATH: str | None = os.getenv("FIREBASE_CREDENTIALS_PATH")
    
    # We fetch the raw string first, then parse it into a list in __init__
    _CORS_ORIGINS_RAW: str | None = os.getenv("BACKEND_CORS_ORIGINS")
    BACKEND_CORS_ORIGINS: list[str] = []

    def __init__(self):
        # --- Strict Validation ---
        # If the .env file didn't load properly, these will be None.
        # We explicitly crash the application here so we know immediately.
        if not self.DATABASE_URL:
            raise ValueError("❌ CRITICAL ERROR: DATABASE_URL is missing! Check your .env file.")
        
        if not self.SECRET_KEY:
            raise ValueError("❌ CRITICAL ERROR: SECRET_KEY is missing! Check your .env file.")
            
        if not self.FIREBASE_CREDENTIALS_PATH:
            raise ValueError("❌ CRITICAL ERROR: FIREBASE_CREDENTIALS_PATH is missing! Check your .env file.")

        # --- CORS Validation and Parsing ---
        if not self._CORS_ORIGINS_RAW:
            raise ValueError("❌ CRITICAL ERROR: BACKEND_CORS_ORIGINS is missing! Check your .env file.")
        
        try:
            self.BACKEND_CORS_ORIGINS = json.loads(self._CORS_ORIGINS_RAW)
        except json.JSONDecodeError:
            raise ValueError("❌ CRITICAL ERROR: BACKEND_CORS_ORIGINS is not valid JSON! It should look like '[\"http://localhost:3000\"]'.")

# Global settings instance
# This will trigger the __init__ validation the moment the server boots
settings = Settings()