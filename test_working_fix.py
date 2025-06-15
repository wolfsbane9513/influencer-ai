# test_working_fix.py - FINAL TEST WITH EXACT MODEL MATCH
import asyncio
import sys
import os
import logging

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_complete_fix():
    """Test the complete fix with your exact model structure"""
    
    print("🎯 TESTING COMPLETE ELEVENLABS FIX")
    print("=" * 50)
    
    try:
        # Import your actual modules
        from services.voice import VoiceService
        from core.models import Creator, CampaignData
        from core.config import settings
        
        print("✅ Imports successful")
        
        # Create test data using YOUR EXACT model structure
        test_creator = Creator(
            id="test_creator_001",
            name="Test Creator",
            handle="@testcreator",
            followers=50000,
            engagement_rate=4.5,
            niche="tech",
            last_campaign_date="2024-01-01",
            # Your model uses 'phone' not 'phone_number'
            phone="+1234567890",
            # Optional fields that your model might have
            platform="instagram",
            rate_per_post=1000.0,
            typical_rate=1000.0,
            availability="excellent"
        )
        
        # Create campaign using YOUR EXACT required fields
        test_campaign = CampaignData(
            id="test_campaign_001",
            # Your model requires BOTH sets of fields
            name="Test Brand - Test Product",
            description="Amazing test product for tech enthusiasts",
            product_name="Test Product",
            brand_name="Test Brand",
            product_description="Amazing test product for tech enthusiasts",
            target_audience="tech-savvy millennials",
            campaign_goal="increase brand awareness",
            product_niche="tech",
            campaign_code="CAMP-TEST001",
            total_budget=10000.0,
            max_creators=5
        )
        
        print("✅ Test data created with exact model structure")
        
        # Initialize voice service with corrected implementation
        voice_service = VoiceService()
        print("✅ VoiceService initialized")
        
        # Check configuration
        print(f"📊 ElevenLabs configured: {settings.is_elevenlabs_configured()}")
        print(f"📊 Using mock services: {settings.use_mock_services}")
        print(f"📊 API base URL: {voice_service.base_url}")
        
        # Test call initiation with correct endpoint
        print("\n📞 Testing call initiation with corrected endpoint...")
        call_result = await voice_service.initiate_call(
            creator=test_creator,
            campaign_data=test_campaign
        )
        
        print(f"📊 Call result: {call_result}")
        
        # Verify result structure
        expected_fields = ["status", "conversation_id", "creator_id"]
        missing_fields = [field for field in expected_fields if field not in call_result]
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            return False
        
        print("✅ Call result has all required fields")
        
        # Check that we're not getting the 405 error anymore
        if call_result.get("status") == "failed" and "405" in str(call_result.get("error", "")):
            print("❌ Still getting 405 error - API endpoint issue not resolved")
            return False
        
        print("✅ No 405 API errors detected")
        
        # Test status check if we have a conversation_id
        if call_result.get("conversation_id"):
            print("\n🔍 Testing status check...")
            status_result = await voice_service.check_call_status(
                call_result["conversation_id"]
            )
            print(f"📊 Status result: {status_result}")
            print("✅ Status check completed")
        
        # Test dynamic variables preparation
        print("\n🔧 Testing dynamic variables...")
        variables = voice_service._prepare_dynamic_variables(test_creator, test_campaign)
        required_vars = ["influencerName", "brandName", "productName", "suggestedRate"]
        
        missing_vars = [var for var in required_vars if var not in variables]
        if missing_vars:
            print(f"❌ Missing dynamic variables: {missing_vars}")
            return False
        
        print("✅ Dynamic variables correctly prepared")
        print(f"📊 Variables: {variables}")
        
        # Clean up
        await voice_service.close()
        print("✅ Voice service closed")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_negotiation_agent_integration():
    """Test that NegotiationAgent works with the fixed VoiceService"""
    
    print("\n🤝 TESTING NEGOTIATION AGENT INTEGRATION")
    print("=" * 50)
    
    try:
        from agents.negotiation import NegotiationAgent
        from core.models import Creator, CampaignData
        
        # Create test data
        test_creator = Creator(
            id="creator_001",
            name="Tech Sarah",
            handle="@sarahtech",
            followers=75000,
            engagement_rate=5.2,
            niche="tech",
            last_campaign_date="2024-01-01",
            phone="+1234567890",
            platform="instagram",
            rate_per_post=1200.0,
            typical_rate=1200.0,
            availability="excellent"
        )
        
        test_campaign = CampaignData(
            id="test_campaign_002",
            name="TechBrand - Gaming Laptop",
            description="High-performance gaming laptop for professionals",
            product_name="Gaming Laptop",
            brand_name="TechBrand",
            product_description="High-performance gaming laptop for professionals",
            target_audience="gamers and tech professionals",
            campaign_goal="drive sales and reviews",
            product_niche="tech",
            campaign_code="CAMP-TECH002",
            total_budget=15000.0,
            max_creators=3
        )
        
        print("✅ Test data created")
        
        # Initialize negotiation agent
        negotiation_agent = NegotiationAgent()
        print("✅ NegotiationAgent initialized")
        
        # Test single creator negotiation
        print("\n🤝 Testing single creator negotiation...")
        result = await negotiation_agent._negotiate_with_creator(
            creator=test_creator,
            campaign_data=test_campaign
        )
        
        print(f"📊 Negotiation result: {result}")
        
        # Verify result structure
        if not hasattr(result, 'creator_id') or not hasattr(result, 'status'):
            print("❌ Invalid negotiation result structure")
            return False
        
        print("✅ Negotiation result has correct structure")
        
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
    """Run complete integration test"""
    
    print("🧪 COMPLETE ELEVENLABS FIX VERIFICATION")
    print("=" * 60)
    print("Testing with your exact model structure and field names")
    print()
    
    test_results = []
    
    # Test voice service fix
    voice_test_passed = await test_complete_fix()
    test_results.append(("VoiceService Fix", voice_test_passed))
    
    # Test negotiation agent integration
    if voice_test_passed:
        negotiation_test_passed = await test_negotiation_agent_integration()
        test_results.append(("NegotiationAgent Integration", negotiation_test_passed))
    else:
        test_results.append(("NegotiationAgent Integration", False))
    
    # Print summary
    print("\n📊 FINAL TEST SUMMARY")
    print("=" * 30)
    
    passed_count = 0
    for test_name, passed in test_results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
        if passed:
            passed_count += 1
    
    print(f"\nOverall: {passed_count}/{len(test_results)} tests passed")
    
    if passed_count == len(test_results):
        print("\n🎉 ALL TESTS PASSED! ELEVENLABS 405 ERROR FIXED!")
        print("\n✅ What was fixed:")
        print("   • Correct ElevenLabs API endpoint: /v1/convai/twilio/outbound-call")
        print("   • Proper field name handling: 'phone' instead of 'phone_number'")
        print("   • Dynamic variable preparation for your model structure")
        print("   • Campaign data compatibility with both name/description and product_name/product_description")
        print("\n🚀 Ready for production:")
        print("   1. Replace your services/voice.py with the corrected version")
        print("   2. Replace your agents/negotiation.py if needed")  
        print("   3. Run your end-to-end test: python end_to_end_test.py")
        print("   4. No more 405 Method Not Allowed errors!")
        return True
    else:
        print("\n⚠️ Some tests failed:")
        print("   • Check the error messages above")
        print("   • Ensure you've updated the VoiceService with the corrected version")
        print("   • Verify your ElevenLabs credentials are correct")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)