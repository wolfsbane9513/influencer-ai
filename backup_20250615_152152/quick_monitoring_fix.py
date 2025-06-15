# quick_monitoring_fix.py - Fix the monitoring endpoint issue
import requests

def test_monitoring_endpoints():
    """Test different monitoring endpoint variations"""
    
    print("🔍 TESTING MONITORING ENDPOINTS")
    print("=" * 50)
    
    # Use the task_id from your test
    task_id = "7c13e808-fb02-41e7-857b-b15c1f5b5b7b"
    base_url = "http://127.0.0.1:8000"
    
    # Test different endpoint variations
    endpoints = [
        f"/api/monitor/campaign/{task_id}",
        f"/api/monitor/enhanced-campaign/{task_id}",
        f"/api/webhook/enhanced-campaign/{task_id}",
        f"/campaign/{task_id}",
        f"/monitor/campaign/{task_id}"
    ]
    
    print(f"Testing with task_id: {task_id}")
    print()
    
    for endpoint in endpoints:
        try:
            print(f"Testing: {endpoint}")
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS: {response.status_code}")
                print(f"   📊 Stage: {data.get('current_stage', 'unknown')}")
                print(f"   🎯 Campaign: {data.get('campaign_id', 'unknown')}")
                break
            else:
                print(f"   ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test listing all campaigns
    print("\n🔍 Testing campaign listing...")
    
    list_endpoints = [
        "/api/monitor/campaigns",
        "/api/monitor/enhanced-campaigns"
    ]
    
    for endpoint in list_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {endpoint}: Found {len(data.get('campaigns', data.get('summary', {}).get('total_campaigns', 0)))} campaigns")
            else:
                print(f"❌ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")

if __name__ == "__main__":
    test_monitoring_endpoints()