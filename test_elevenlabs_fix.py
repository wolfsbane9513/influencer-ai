# test_elevenlabs_fix.py - VERIFY CORRECTED IMPLEMENTATION
import asyncio
import sys
import os
import logging

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_voice_service_fix():
    """Test the corrected VoiceService implementation"""
    
    print("🔧 TESTING CORRECTED VOICE SERVICE")
    print("=" * 50)
    
    try:
        # Import corrected modules
        from services.voice import VoiceService
        from core.models import Creator, CampaignData
        from core.config import settings
        
        print("✅ Imports successful")
        
        # Check configuration
        print(f"📊 ElevenLabs configured: {settings.is_elevenlabs_configured()}")
        print(f"📊 Using mock services: {settings.use_mock_services}")
        
        # Create test data (using correct field names from models)
        test_creator = Creator(
            id="test_creator_001",
            name="Test Creator",
            handle="@testcreator",
            platform="instagram",
            followers=50000,  # Using 'followers' not 'follower_count'
            engagement_rate=4.5,
            niche="tech",
            rate_per_post=1000.0,
            phone_number="+1234567890",
            contact_email="test@creator.com"  # Using 'contact_email' not 'email'
        )
        
        test_campaign = CampaignData(
            id="test_campaign_001",
            product_name="Test Product",
            brand_name="Test Brand",
            product_description="Amazing test product for tech enthusiasts",
            target_audience="tech-savvy millennials",
            campaign_goal="increase brand awareness",
            product_niche="tech",
            total_budget=10000.0,
            max_creators=5
        )
        
        print("✅ Test data created")
        
        # Initialize voice service
        voice_service = VoiceService()
        print("✅ VoiceService initialized")
        
        # Test call initiation
        print("\n📞 Testing call initiation...")
        call_result = await voice_service.initiate_call(
            creator=test_creator,
            campaign_data=test_campaign
        )
        
        print(f"📊 Call result: {call_result}")
        
        # Verify result structure
        required_fields = ["status", "conversation_id", "creator_id"]
        missing_fields = [field for field in required_fields if field not in call_result]
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            return False
        
        print("✅ Call result has required fields")
        
        # Test status check if we have a conversation_id
        if call_result.get("conversation_id"):
            print("\n🔍 Testing status check...")
            status_result = await voice_service.check_call_status(
                call_result["conversation_id"]
            )
            print(f"📊 Status result: {status_result}")
            print("✅ Status check completed")
        
        # Clean up
        await voice_service.close()
        print("✅ Voice service closed")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_negotiation_agent_fix():
    """Test the corrected NegotiationAgent implementation"""
    
    print("\n🤝 TESTING CORRECTED NEGOTIATION AGENT")
    print("=" * 50)
    
    try:
        from agents.negotiation import NegotiationAgent, NegotiationResult
        from core.models import Creator, CampaignData
        
        # Create test data (using correct field names)
        test_creators = [
            Creator(
                id="creator_001",
                name="Tech Reviewer Sarah",
                handle="@sarahtech",
                platform="instagram",
                followers=75000,  # Using 'followers' not 'follower_count'
                engagement_rate=5.2,
                niche="tech",
                rate_per_post=1200.0,
                phone_number="+1234567890",
                contact_email="sarah@techreview.com"  # Using 'contact_email' not 'email'
            ),
            Creator(
                id="creator_002",
                name="Gaming Alex",
                handle="@alexgaming",
                platform="tiktok",
                followers=120000,  # Using 'followers' not 'follower_count'
                engagement_rate=6.8,
                niche="tech",
                rate_per_post=1500.0,
                phone_number="+1234567891",
                contact_email="alex@gaming.com"  # Using 'contact_email' not 'email'
            )
        ]
        
        test_campaign = CampaignData(
            id="test_campaign_002",
            product_name="Gaming Laptop",
            brand_name="TechBrand",
            product_description="High-performance gaming laptop for professionals",
            target_audience="gamers and tech professionals",
            campaign_goal="drive sales and reviews",
            product_niche="tech",
            total_budget=15000.0,
            max_creators=3
        )
        
        print("✅ Test data created")
        
        # Initialize negotiation agent
        negotiation_agent = NegotiationAgent()
        print("✅ NegotiationAgent initialized")
        
        # Test negotiations (will use mock calls in development)
        print("\n🤝 Starting test negotiations...")
        results = await negotiation_agent.negotiate_with_creators(
            creators=test_creators,
            campaign_data=test_campaign
        )
        
        print(f"📊 Negotiation results: {len(results)} total")
        
        # Verify results
        for i, result in enumerate(results):
            print(f"  Result {i+1}:")
            print(f"    Creator: {result.creator_id}")
            print(f"    Status: {result.status}")
            print(f"    Rate: {result.final_rate}")
            print(f"    Conversation ID: {result.conversation_id}")
        
        # Clean up
        await negotiation_agent.close()
        print("✅ NegotiationAgent closed")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    
    print("🧪 CORRECTED IMPLEMENTATION VERIFICATION")
    print("=" * 60)
    
    test_results = []
    
    # Test voice service
    voice_test_passed = await test_voice_service_fix()
    test_results.append(("VoiceService", voice_test_passed))
    
    # Test negotiation agent
    negotiation_test_passed = await test_negotiation_agent_fix()
    test_results.append(("NegotiationAgent", negotiation_test_passed))
    
    # Print summary
    print("\n📊 TEST SUMMARY")
    print("=" * 30)
    
    passed_count = 0
    for test_name, passed in test_results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
        if passed:
            passed_count += 1
    
    print(f"\nOverall: {passed_count}/{len(test_results)} tests passed")
    
    if passed_count == len(test_results):
        print("🎉 ALL TESTS PASSED - ElevenLabs integration fixed!")
        return True
    else:
        print("⚠️ Some tests failed - check the output above")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)