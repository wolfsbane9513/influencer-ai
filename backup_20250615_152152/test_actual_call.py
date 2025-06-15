# test_actual_call.py - REAL ELEVENLABS CALL TEST
import requests
import asyncio
import sys
import os
import json
import time
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_actual_elevenlabs_call():
    """
    🧪 TEST ACTUAL ELEVENLABS CALL
    
    This will make a real phone call using ElevenLabs
    Make sure you have proper credentials set up!
    """
    
    print("🧪 TESTING ACTUAL ELEVENLABS CALL")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8000"
    
    # 1. First check if ElevenLabs is properly configured
    print("1. 🔍 Checking ElevenLabs Configuration...")
    try:
        response = requests.get(f"{base_url}/api/webhook/test-enhanced-elevenlabs")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ ElevenLabs Status: {data.get('status', 'unknown')}")
            print(f"   🔌 API Connected: {data.get('api_connected', False)}")
            
            if not data.get('api_connected', False):
                print("   ⚠️  ElevenLabs is in mock mode - no real calls will be made")
                print("   📋 To enable real calls, add these to your .env file:")
                print("      ELEVENLABS_API_KEY=sk_your_key_here")
                print("      ELEVENLABS_AGENT_ID=your_agent_id_here")
                print("      ELEVENLABS_PHONE_NUMBER_ID=your_phone_id_here")
                return False
        else:
            print(f"   ❌ ElevenLabs test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ ElevenLabs test error: {e}")
        return False
    
    # 2. Get phone number for test call
    print("\n2. 📞 Setting Up Test Call...")
    
    # IMPORTANT: Replace with your actual phone number
    # For testing, you can use your own number
    test_phone_number = input("   📱 Enter your phone number (format: +1234567890): ").strip()
    
    if not test_phone_number:
        test_phone_number = "+918806859890"  # Default to your number from previous logs
        print(f"   📱 Using default number: {test_phone_number}")
    
    print(f"   📱 Test call will be made to: {test_phone_number}")
    
    # 3. Confirm before making actual call
    print("\n3. ⚠️  CONFIRMATION REQUIRED")
    print("   🚨 This will make a REAL phone call using ElevenLabs")
    print("   💰 This may incur charges on your ElevenLabs account")
    print(f"   📞 Call will be made to: {test_phone_number}")
    
    confirm = input("   ❓ Do you want to proceed? (type 'yes' to confirm): ").strip().lower()
    
    if confirm != 'yes':
        print("   🛑 Test cancelled by user")
        return False
    
    # 4. Prepare test data
    print("\n4. 🎯 Preparing Test Call Data...")
    
    test_call_data = {
        "creator_phone": test_phone_number,
        "creator_profile": {
            "id": "test_creator_001",
            "name": "TestCreator Pro",
            "niche": "technology",
            "followers": 75000,
            "engagement_rate": 4.2,
            "average_views": 35000,
            "location": "India",
            "languages": ["English", "Hindi"],
            "typical_rate": 2500,
            "availability": "excellent"
        },
        "campaign_data": {
            "product_name": "TechPro Device",
            "brand_name": "InnovaTech Solutions",
            "product_description": "Revolutionary AI-powered smart device for tech enthusiasts with advanced features and seamless integration",
            "target_audience": "Tech professionals and early adopters aged 25-40",
            "campaign_goal": "Drive product awareness and generate pre-orders",
            "product_niche": "technology",
            "total_budget": 15000.0
        },
        "pricing_strategy": {
            "initial_offer": 2000,
            "max_offer": 3000,
            "negotiation_style": "collaborative"
        }
    }
    
    print("   📋 Test call configured with:")
    print(f"      Creator: {test_call_data['creator_profile']['name']}")
    print(f"      Product: {test_call_data['campaign_data']['product_name']}")
    print(f"      Offer Range: ${test_call_data['pricing_strategy']['initial_offer']}-${test_call_data['pricing_strategy']['max_offer']}")
    
    # 5. Initiate the actual call
    print("\n5. 🚀 Initiating Actual ElevenLabs Call...")
    print("   📞 Making API request to start call...")
    
    try:
        response = requests.post(
            f"{base_url}/api/webhook/test-actual-call",
            json=test_call_data,
            timeout=30
        )
        
        if response.status_code == 200:
            call_result = response.json()
            print("   ✅ Call initiated successfully!")
            print(f"   🆔 Conversation ID: {call_result.get('conversation_id', 'N/A')}")
            print(f"   📞 Call ID: {call_result.get('call_id', 'N/A')}")
            
            # Check your phone for the incoming call
            print("\n6. 📱 CHECK YOUR PHONE!")
            print("   🔔 You should receive a call from ElevenLabs within 30 seconds")
            print("   🤖 The AI agent will discuss the collaboration opportunity")
            print("   💬 Try responding naturally to test the conversation")
            
            # Monitor call status
            conversation_id = call_result.get('conversation_id')
            if conversation_id:
                print(f"\n7. 👁️  Monitoring call progress...")
                await_call_completion(base_url, conversation_id)
            
            return True
            
        else:
            print(f"   ❌ Call initiation failed: {response.status_code}")
            print(f"   📝 Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Call test error: {e}")
        return False

def await_call_completion(base_url: str, conversation_id: str):
    """
    👁️  Monitor call completion and get results
    """
    print("   🔄 Waiting for call to complete...")
    print("   ⏰ This may take 2-5 minutes depending on conversation length")
    
    start_time = time.time()
    max_wait_time = 600  # 10 minutes max
    
    while time.time() - start_time < max_wait_time:
        try:
            # Check call status
            response = requests.get(f"{base_url}/api/webhook/call-status/{conversation_id}")
            
            if response.status_code == 200:
                status_data = response.json()
                call_status = status_data.get('status', 'unknown')
                
                print(f"   📊 Call Status: {call_status}")
                
                if call_status in ['completed', 'failed', 'ended']:
                    print("   🏁 Call completed!")
                    
                    # Get final results
                    if call_status == 'completed':
                        print("   📊 Call Results:")
                        print(f"      Duration: {status_data.get('duration', 'N/A')} seconds")
                        print(f"      Outcome: {status_data.get('outcome', 'N/A')}")
                        
                        # Show conversation analysis if available
                        analysis = status_data.get('analysis', {})
                        if analysis:
                            print("   🧠 Conversation Analysis:")
                            print(f"      Negotiation Result: {analysis.get('negotiation_outcome', 'N/A')}")
                            print(f"      Agreed Rate: ${analysis.get('agreed_rate', 'N/A')}")
                            print(f"      Sentiment: {analysis.get('sentiment', 'N/A')}")
                    
                    break
                    
            time.sleep(10)  # Check every 10 seconds
            
        except Exception as e:
            print(f"   ⚠️  Status check error: {e}")
            time.sleep(10)
    
    else:
        print("   ⏰ Call monitoring timed out")

def create_test_call_endpoint():
    """
    🔧 Create the test call endpoint code that needs to be added to webhooks
    """
    
    endpoint_code = '''
@enhanced_webhook_router.post("/test-actual-call")
async def test_actual_call(call_data: Dict[str, Any]):
    """
    🧪 MAKE ACTUAL ELEVENLABS CALL - FOR TESTING
    
    This endpoint makes a real phone call using ElevenLabs
    """
    try:
        logger.info("🧪 Initiating actual ElevenLabs call test...")
        
        # Extract call data
        creator_phone = call_data.get("creator_phone")
        creator_profile = call_data.get("creator_profile", {})
        campaign_data = call_data.get("campaign_data", {})
        pricing_strategy = call_data.get("pricing_strategy", {})
        
        logger.info(f"📞 Making real call to: {creator_phone}")
        
        # Use the enhanced voice service to make actual call
        call_result = await enhanced_voice_service.initiate_negotiation_call(
            creator_phone=creator_phone,
            creator_profile=creator_profile,
            campaign_data=campaign_data,
            pricing_strategy=pricing_strategy
        )
        
        if call_result.get("status") == "success":
            logger.info(f"✅ Real call initiated successfully: {call_result.get('conversation_id')}")
            
            return {
                "status": "success",
                "message": "Actual ElevenLabs call initiated successfully",
                "conversation_id": call_result.get("conversation_id"),
                "call_id": call_result.get("call_id"),
                "phone_number": creator_phone,
                "expected_duration": "2-5 minutes",
                "monitor_instructions": "Check your phone for incoming call from ElevenLabs"
            }
        else:
            logger.error(f"❌ Real call failed: {call_result}")
            return JSONResponse(
                status_code=500,
                content={
                    "status": "failed",
                    "message": "ElevenLabs call initiation failed",
                    "error": call_result.get("error", "Unknown error"),
                    "details": call_result
                }
            )
            
    except Exception as e:
        logger.error(f"❌ Actual call test exception: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Actual call test failed",
                "error": str(e)
            }
        )
'''
    
    print("🔧 ADD THIS ENDPOINT TO YOUR enhanced_webhooks.py:")
    print("=" * 60)
    print(endpoint_code)
    print("=" * 60)

if __name__ == "__main__":
    print("🎯 ElevenLabs Actual Call Test")
    print("This script will help you test real phone calls with ElevenLabs")
    print()
    
    choice = input("Choose an option:\n1. Run actual call test\n2. Show endpoint code to add\n\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        success = test_actual_elevenlabs_call()
        if success:
            print("\n🎉 ACTUAL CALL TEST COMPLETED!")
            print("💡 Check the call quality and conversation flow")
            print("🔍 Review logs for any issues or improvements needed")
        else:
            print("\n❌ CALL TEST FAILED")
            print("🔧 Check your ElevenLabs configuration and try again")
    
    elif choice == "2":
        create_test_call_endpoint()
    
    else:
        print("Invalid choice. Please run again and select 1 or 2.")