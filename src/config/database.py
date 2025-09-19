import os
from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL from Railway environment or fallback to local
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/api_auth")

# Convert Railway DATABASE_URL to async if needed
# Using psycopg (v3) for async compatibility
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    # Use psycopg driver for async compatibility
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://")
else:
    ASYNC_DATABASE_URL = DATABASE_URL

# Create async engine for database operations
engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,  # Disable SQLAlchemy query logging
    pool_pre_ping=True,
    pool_recycle=300,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for all database models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    """
    Create all database tables
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)