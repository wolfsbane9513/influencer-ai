"""Complete database setup script for InfluencerFlow AI Platform"""
import asyncio
import os
import sys
from datetime import datetime

async def setup_database():
    """Complete database setup process"""
    print("🗄️ Setting up InfluencerFlow AI Database...")
    
    try:
        # Import after path setup
        from config.database import DatabaseConfig
        from services.database import DatabaseService
        
        # Initialize database
        db_service = DatabaseService()
        await db_service.initialize()
        
        print("✅ Database tables created successfully!")
        
        # Test database connection
        await test_database_connection(db_service)
        
        # Optionally seed sample data
        await seed_sample_data(db_service)
        
        await db_service.close()
        print("🎉 Database setup completed!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install sqlalchemy[asyncio] asyncpg psycopg2-binary")
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)

async def test_database_connection(db_service):
    """Test database connection"""
    try:
        async with db_service.get_session() as session:
            await session.execute("SELECT 1")
        print("✅ Database connection test passed!")
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        raise

async def seed_sample_data(db_service):
    """Seed sample data for testing"""
    from models.campaign import CampaignData, CampaignStatus
    from models.campaign import Creator as CampaignCreator, Platform, Availability
    
    try:
        # Sample campaign data
        sample_campaign = CampaignData(
            id="sample-campaign-001",
            product_name="EcoFit Tracker",
            brand_name="GreenTech Solutions",
            product_description="Sustainable fitness tracking device made from recycled materials",
            target_audience="Environmentally conscious fitness enthusiasts aged 25-40",
            campaign_goal="Launch new eco-friendly product line",
            product_niche="fitness",
            total_budget=15000.0,
            status=CampaignStatus.DRAFT
        )
        
        await db_service.create_campaign(sample_campaign)
        
        # Sample creator data
        sample_creator = CampaignCreator(
            id="eco_fitness_guru",
            name="Sarah GreenFit",
            platform=Platform.INSTAGRAM,
            followers=250000,
            niche="fitness",
            typical_rate=5000.0,
            engagement_rate=4.2,
            average_views=50000,
            last_campaign_date="2024-11-15",
            availability=Availability.EXCELLENT,
            location="California, USA",
            phone_number="+1-555-0123",
            languages=["English", "Spanish"],
            specialties=["eco-fitness", "sustainable living", "health coaching"]
        )
        
        await db_service.create_or_update_creator(sample_creator)
        
        print("✅ Sample data seeded successfully!")
        
    except Exception as e:
        print(f"⚠️  Sample data seeding failed: {e}")

if __name__ == "__main__":
    asyncio.run(setup_database())