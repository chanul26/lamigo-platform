import os
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

    def __init__(self):
        # --- Strict Validation ---
        # If the .env file didn't load properly, these will be None.
        # We explicitly crash the application here so we know immediately.
        if not self.DATABASE_URL:
            raise ValueError("❌ CRITICAL ERROR: DATABASE_URL is missing! Check your .env file path.")
        
        if not self.SECRET_KEY:
            raise ValueError("❌ CRITICAL ERROR: SECRET_KEY is missing! Check your .env file path.")

# Global settings instance
# This will trigger the __init__ validation the moment the server boots
settings = Settings()