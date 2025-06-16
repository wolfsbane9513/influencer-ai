"""Database testing script"""
import asyncio
from services.database import DatabaseService
from models.campaign import CampaignData, CampaignStatus
from models.campaign import Creator as CampaignCreator, Platform, Availability

async def test_database_operations():
    """Test all database operations"""
    print("🧪 Testing database operations...")
    
    db_service = DatabaseService()
    await db_service.initialize()
    
    try:
        # Test campaign creation
        print("\n1. Testing campaign creation...")
        test_campaign = CampaignData(
            id="test-campaign-001",
            product_name="Test Product",
            brand_name="Test Brand",
            product_description="A test product for database testing",
            target_audience="Test audience",
            campaign_goal="Test goal",
            product_niche="technology",
            total_budget=10000.0,
            status=CampaignStatus.ACTIVE
        )
        
        campaign = await db_service.create_campaign(test_campaign)
        print(f"✅ Campaign created: {campaign.id}")
        
        # Test creator creation
        print("\n2. Testing creator creation...")
        test_creator = CampaignCreator(
            id="test_creator_001",
            name="Test Creator",
            platform=Platform.YOUTUBE,
            followers=100000,
            niche="technology",
            typical_rate=2000.0,
            engagement_rate=3.5,
            average_views=25000,
            last_campaign_date="2024-12-01",
            availability=Availability.EXCELLENT,
            location="Test Location",
            phone_number="+1-555-0000",
            languages=["English"],
            specialties=["tech reviews"]
        )
        
        creator = await db_service.create_or_update_creator(test_creator)
        print(f"✅ Creator created: {creator.id}")
        
        # Test analytics
        print("\n3. Testing analytics...")
        analytics = await db_service.get_campaign_analytics(test_campaign.id)
        print(f"✅ Analytics generated: {analytics.get('campaign_name', 'Unknown')}")
        
        print("\n🎉 All database tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise
    finally:
        await db_service.close()

if __name__ == "__main__":
    asyncio.run(test_database_operations())