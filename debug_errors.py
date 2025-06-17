# debug_errors.py - Debug the specific 500 errors
import requests
import json

def debug_elevenlabs_error():
    """Debug the ElevenLabs 500 error"""
    print("🔍 DEBUGGING ELEVENLABS ERROR")
    print("=" * 40)
    
    try:
        response = requests.get("http://127.0.0.1:8000/api/webhook/test-enhanced-elevenlabs")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            error_data = response.json()
            print(f"Error Response: {json.dumps(error_data, indent=2)}")
        else:
            print(f"Raw Response: {response.text}")
            
    except Exception as e:
        print(f"Request Error: {e}")

def debug_contract_error():
    """Debug the contract generation 500 error"""
    print("\n🔍 DEBUGGING CONTRACT GENERATION ERROR")
    print("=" * 40)
    
    contract_data = {
        "creator_name": "TestCreator Pro",
        "agreed_rate": 2500.0,
        "campaign_details": {
            "product_name": "TestPro Device",
            "brand_name": "TestTech Solutions",
            "campaign_goal": "Product launch validation"
        },
        "negotiation_data": {
            "outcome": "accepted",
            "sentiment": "positive",
            "key_points": ["Agreed to collaboration", "Positive response"]
        }
    }
    
    try:
        response = requests.post(
            "http://127.0.0.1:8000/api/webhook/generate-enhanced-contract",
            json=contract_data
        )
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            error_data = response.json()
            print(f"Error Response: {json.dumps(error_data, indent=2)}")
        else:
            print(f"Raw Response: {response.text}")
            
    except Exception as e:
        print(f"Request Error: {e}")

def check_campaign_progress():
    """Check the campaign that was started successfully"""
    print("\n🔍 CHECKING CAMPAIGN PROGRESS")
    print("=" * 40)
    
    # Use the task ID from your previous test
    task_id = "d7eeb644-9b08-4aee-ae8b-6e558fa1a14d"
    
    try:
        response = requests.get(f"http://127.0.0.1:8000/api/monitor/enhanced-campaign/{task_id}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            progress_data = response.json()
            print(f"Current Stage: {progress_data.get('current_stage')}")
            print(f"Progress: {progress_data.get('progress', {})}")
            
            # Check for any errors in the campaign
            if 'error_details' in progress_data:
                print(f"Campaign Errors: {progress_data['error_details']}")
                
        else:
            print(f"Campaign monitoring failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Campaign check error: {e}")

def test_simple_endpoints():
    """Test some simple endpoints to isolate the issue"""
    print("\n🔍 TESTING SIMPLE ENDPOINTS")
    print("=" * 40)
    
    endpoints = [
        "/",
        "/health", 
        "/api/webhook/system-status"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"http://127.0.0.1:8000{endpoint}")
            print(f"{endpoint}: {response.status_code} - {'✅' if response.status_code == 200 else '❌'}")
        except Exception as e:
            print(f"{endpoint}: Error - {e}")

if __name__ == "__main__":
    test_simple_endpoints()
    debug_elevenlabs_error()
    debug_contract_error()
    check_campaign_progress()
    
    print("\n💡 DEBUGGING SUMMARY:")
    print("1. Check server logs for detailed error messages")
    print("2. Verify all required imports are available")
    print("3. Check if any environment variables are missing")
    print("4. Look for any module import errors in the logs")