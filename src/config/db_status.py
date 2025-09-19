"""
Database status and fallback handlers
"""
import os
from typing import Optional
from fastapi import HTTPException, status

def check_database_available() -> bool:
    """Check if database is configured and available"""
    database_url = os.getenv("DATABASE_URL")
    return bool(database_url and not database_url.startswith("postgresql://user:password@localhost"))

def require_database():
    """Decorator to require database for certain endpoints"""
    if not check_database_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not configured. This endpoint requires database access."
        )

async def get_db_or_none():
    """Get database session or None if not available"""
    if not check_database_available():
        yield None
        return
    
    # Import here to avoid circular imports
    from src.config.database import get_db
    async for db in get_db():
        yield db