"""Database migration script"""
import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from config.database import DatabaseConfig

async def create_tables():
    """Create all database tables"""
    db_config = DatabaseConfig()
    try:
        await db_config.create_tables()
        print("✅ All database tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
    finally:
        await db_config.close()

if __name__ == "__main__":
    asyncio.run(create_tables())
