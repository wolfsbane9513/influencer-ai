# config/database.py
"""Database configuration and connection management"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()

class DatabaseConfig:
    """Database configuration class"""
    
    def __init__(self):
        self.database_url = self._get_database_url()
        self.async_database_url = self._get_async_database_url()
        
        # Create engines
        self.engine = create_engine(self.database_url, echo=False)
        self.async_engine = create_async_engine(self.async_database_url, echo=False)
        
        # Create session makers
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.AsyncSessionLocal = async_sessionmaker(self.async_engine, expire_on_commit=False)
    
    def _get_database_url(self) -> str:
        """Get database URL from environment"""
        return os.getenv(
            "DATABASE_URL", 
            "postgresql://user:password@localhost:5432/influencerflow"
        )
    
    def _get_async_database_url(self) -> str:
        """Get async database URL"""
        url = self._get_database_url()
        return url.replace("postgresql://", "postgresql+asyncpg://")
    
    async def create_tables(self):
        """Create all database tables"""
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables created")
    
    async def close(self):
        """Close database connections"""
        await self.async_engine.dispose()
        self.engine.dispose()