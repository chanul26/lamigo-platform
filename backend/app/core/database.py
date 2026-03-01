from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings

# 1. Initialize the Asynchronous Database Engine
# This object maintains a 'pool' of connections to your PostgreSQL database.
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # Prints every SQL query to logs; incredibly helpful for debugging.
)

# 2. Configure the Session Factory (SessionLocal)
# Think of this as the 'manager' that creates new database sessions.
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False, # Keeps objects usable after a commit (vital for async).
    autoflush=False
)

# 3. Database Dependency Generator
# Used in FastAPI route functions to provide a fresh DB session per request.
# The 'async with' block guarantees the session closes automatically when done.
async def get_db():
    async with SessionLocal() as session:
        yield session