# quick_call_status_test.py - Test call status directly
import requests
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_call_status_directly():
    """
    🔍 Test call status directly using ElevenLabs API
    """
    
    print("🔍 TESTING CALL STATUS DIRECTLY")
    print("=" * 50)
    
    # The conversation ID from your logs
    conversation_id = "conv_01jxsbshjpfx5r1t119nexre7j"
    
    print(f"📞 Checking status for: {conversation_id}")
    
    # Load settings
    from core.config import settings
    
    if not settings.elevenlabs_api_key:
        print("❌ No ElevenLabs API key found")
        return
    
    try:
        # Make direct API call to ElevenLabs
        print("🌐 Making direct API call to ElevenLabs...")
        
        response = requests.get(
            f"https://api.elevenlabs.io/v1/convai/conversations/{conversation_id}",
            headers={"Xi-Api-Key": settings.elevenlabs_api_key},
            timeout=15
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Call status retrieved successfully!")
            print(f"   Status: {result.get('status', 'unknown')}")
            print(f"   Duration: {result.get('duration', 'N/A')} seconds")
            print(f"   Started: {result.get('started_at', 'N/A')}")
            print(f"   Ended: {result.get('ended_at', 'N/A')}")
            
            # Print full response for debugging
            print("\n📋 Full Response:")
            import json
            print(json.dumps(result, indent=2))
            
        elif response.status_code == 404:
            print("❌ Conversation not found")
            print("   This might mean:")
            print("   • The conversation hasn't started yet")
            print("   • The conversation ID is invalid")
            print("   • The call failed to initiate")
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error checking call status: {e}")

def test_via_your_api():
    """
    🔧 Test via your local API endpoints
    """
    
    print("\n🔧 TESTING VIA LOCAL API")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8000"
    conversation_id = "conv_01jxsbshjpfx5r1t119nexre7j"
    
    # Test both endpoints
    endpoints = [
        f"/api/webhook/call-status/{conversation_id}",
        f"/api/webhook/simple-call-status/{conversation_id}"
    ]
    
    for endpoint in endpoints:
        print(f"📡 Testing: {endpoint}")
        
        try:
            response = requests.get(f"{base_url}{endpoint}")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success: {data.get('status', 'unknown')}")
            else:
                print(f"   ❌ Failed: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def check_if_call_actually_happened():
    """
    🤔 Check if the call actually happened
    """
    
    print("\n🤔 DID THE CALL ACTUALLY HAPPEN?")
    print("=" * 50)
    
    print("Please answer these questions:")
    print("1. Did you receive a phone call from ElevenLabs? (y/n)")
    received_call = input("   Answer: ").strip().lower()
    
    if received_call == 'y':
        print("2. Did you answer the call? (y/n)")
        answered = input("   Answer: ").strip().lower()
        
        if answered == 'y':
            print("3. Did the AI agent speak to you about the collaboration? (y/n)")
            agent_spoke = input("   Answer: ").strip().lower()
            
            if agent_spoke == 'y':
                print("4. How long did the conversation last? (in seconds)")
                duration = input("   Duration: ").strip()
                
                print("5. How did the conversation end?")
                print("   a) I hung up")
                print("   b) The AI ended the call")
                print("   c) Call dropped/technical issue")
                ending = input("   Answer (a/b/c): ").strip().lower()
                
                print("\n📊 CALL SUMMARY:")
                print(f"   ✅ Call received and answered")
                print(f"   ✅ AI agent interaction: Yes")
                print(f"   ⏱️ Duration: {duration} seconds")
                print(f"   🔚 Ending: {ending}")
                
                if ending in ['a', 'b']:
                    print("   🎯 Call appears to have completed normally")
                    print("   💡 The ElevenLabs API might take time to process the results")
                    print("   ⏰ Try checking status again in 2-3 minutes")
                else:
                    print("   ⚠️ Call may have ended due to technical issues")
            else:
                print("   ⚠️ AI agent didn't speak - possible configuration issue")
        else:
            print("   📞 Call received but not answered")
    else:
        print("   ❌ No call received")
        print("   🔍 Possible issues:")
        print("   • Phone number format incorrect")
        print("   • ElevenLabs phone service configuration")
        print("   • API call failed silently")

if __name__ == "__main__":
    print("🎯 CALL STATUS INVESTIGATION")
    print("Let's figure out what happened with your ElevenLabs call")
    print()
    
    # First check if call actually happened
    check_if_call_actually_happened()
    
    # Then test the API responses
    test_call_status_directly()
    test_via_your_api()
    
    print("\n💡 RECOMMENDATIONS:")
    print("1. Add the call status endpoints to your enhanced_webhooks.py")
    print("2. If the call completed, results may take 2-3 minutes to appear")
    print("3. Check your ElevenLabs dashboard for call logs")
    print("4. Consider testing with a shorter conversation next time")