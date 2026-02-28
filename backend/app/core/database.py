from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings

# 1. Initialize the Asynchronous Database Engine
# This object maintains a 'pool' of connections to your Mac's PostgreSQL.
# Using 'create_async_engine' ensures the API doesn't freeze during DB queries.
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,    # Prints every SQL query to logs; incredibly helpful for debugging.
    future=True   # Ensures we use SQLAlchemy 2.0+ standard style.
)

# 2. Configure the Session Factory (SessionLocal)
# Think of this as the 'manager' that creates new database sessions.
# - autoflush=False: Prevents SQL from sending data to the DB before you explicitly commit.
# - expire_on_commit=False: Keeps objects usable after a commit (vital for async).
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# 3. Database Dependency Generator
# This is used in FastAPI route functions to provide a fresh DB session per request.
# It ensures that every session is automatically closed when the request finishes.
async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()