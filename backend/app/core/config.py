import os
from dotenv import load_dotenv

# Load environment variables from the root .env file into the OS context
load_dotenv()

class Settings:
    """
    Centralized configuration management for the LamiGo API.
    All environment variables and global constants are defined and accessed through this class.
    """
    # System Metadata
    PROJECT_NAME: str = "LamiGo API"
    PROJECT_DESCRIPTION: str = "Last-Mile Delivery Optimization Platform"
    VERSION: str = "1.0.0"

    # Database Configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres+psycopg:postgres@localhost:5432/lamigo_db"
    )

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default-insecure-key")

# Global settings instance to be imported across the application
settings = Settings()