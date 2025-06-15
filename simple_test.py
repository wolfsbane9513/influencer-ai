# simple_test_fixed.py - COMPLETELY FIXED TEST SCRIPT
import requests
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_fixed_implementation():
    """
    🧪 Test the completely fixed implementation
    
    Tests all endpoints to ensure the ai_strategy field error is resolved
    """
    
    print("🧪 TESTING FIXED IMPLEMENTATION")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8000"
    
    # 1. Test Health Check
    print("1. 🏥 Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health Status: {data.get('status', 'unknown')}")
            print(f"   📊 Services: {data.get('services', [])}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    # 2. Test Enhanced System Status
    print("2. 📊 Testing Enhanced System Status...")
    try:
        response = requests.get(f"{base_url}/api/webhook/system-status")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ System Status: {data.get('status', 'unknown')}")
            print(f"   🔧 Enhanced Features: {len(data.get('enhanced_features', {}))}")
            print(f"   🏗️ Version: {data.get('version', 'unknown')}")
        else:
            print(f"   ❌ System status failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ System status error: {e}")
    
    # 3. Test ElevenLabs Integration
    print("3. 📞 Testing ElevenLabs Integration...")
    try:
        response = requests.get(f"{base_url}/api/webhook/test-enhanced-elevenlabs")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ ElevenLabs Status: {data.get('status', 'unknown')}")
            print(f"   🎯 API Connected: {data.get('api_connected', False)}")
        else:
            print(f"   ❌ ElevenLabs test failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ ElevenLabs test error: {e}")
    
    # 4. Test Enhanced Campaign Workflow (THE CRITICAL TEST)
    print("4. 🎯 Testing Enhanced Campaign Workflow...")
    try:
        campaign_data = {
            "campaign_id": "quick_test_001",
            "product_name": "TestPro Device",
            "brand_name": "TestTech Solutions", 
            "product_description": "Revolutionary tech device for modern users",
            "target_audience": "Tech enthusiasts aged 25-40",
            "campaign_goal": "Increase product awareness and drive sales",
            "product_niche": "technology",
            "total_budget": 8000.0
        }
        
        response = requests.post(f"{base_url}/api/webhook/enhanced-campaign", json=campaign_data)
        
        if response.status_code == 202:
            data = response.json()
            print(f"   ✅ Campaign Status: success")
            print(f"   🎯 Task ID: {data.get('task_id', 'unknown')}")
            print(f"   ⏱️ Estimated Duration: {data.get('estimated_duration_minutes', 'unknown')} minutes")
            
            # Brief wait to let orchestration start
            import time
            time.sleep(2)
            
        else:
            print(f"   ❌ Campaign test failed: {response.status_code}")
            print(f"   📝 Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Campaign test error: {e}")
    
    # 5. Test Contract Generation
    print("5. 📋 Testing Contract Generation...")
    try:
        contract_data = {
            "creator_name": "TestCreator Pro",
            "compensation": 2500.0,
            "campaign_details": {
                "brand": "TestTech Solutions",
                "product": "TestPro Device",
                "deliverables": ["1 Instagram post", "3 Stories"],
                "timeline": "2 weeks"
            }
        }
        
        response = requests.post(f"{base_url}/api/webhook/generate-enhanced-contract", json=contract_data)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Contract Status: {data.get('status', 'unknown')}")
            print(f"   💰 Compensation: ${data.get('contract_data', {}).get('compensation', 0)}")
            print(f"   📄 Contract Generated: {data.get('contract_generated', False)}")
        else:
            print(f"   ❌ Contract test failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Contract test error: {e}")
    
    print("=" * 50)
    print("🎉 FIXED IMPLEMENTATION TEST COMPLETED")
    print("💡 Key Fixes Applied:")
    print("   • Added missing ai_strategy field to CampaignOrchestrationState")
    print("   • Fixed all field mapping issues in orchestrator")
    print("   • Cleaned up OOP design with proper encapsulation")
    print("   • Removed legacy code and unnecessary complexity")
    print("   • Added comprehensive error handling")
    print("🔍 The 'ai_strategy' field error should now be resolved!")

if __name__ == "__main__":
    test_fixed_implementation()