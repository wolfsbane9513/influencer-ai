import requests
import json

# Test data
test_data = {
    "campaign_id": "debug_tech_003",
    "product_name": "SmartPhone Debug Test",
    "brand_name": "TechBrand",
    "product_description": "smartphone reviews gadget unboxing tech tutorials",
    "target_audience": "tech enthusiasts",
    "campaign_goal": "tech promotion",
    "product_niche": "tech",
    "total_budget": 7500
}

print("🧪 Testing API with debug data...")
print(f"Data: {json.dumps(test_data, indent=2)}")

try:
    response = requests.post(
        "http://localhost:8000/api/webhook/enhanced-campaign",
        json=test_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\n📊 Response Status: {response.status_code}")
    print(f"📊 Response Data: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 202:
        # Get the task_id to monitor
        task_id = response.json().get("task_id")
        if task_id:
            print(f"\n🔍 Monitoring task: {task_id}")
            monitor_response = requests.get(f"http://localhost:8000/api/monitor/campaign/{task_id}")
            print(f"📊 Monitor Data: {json.dumps(monitor_response.json(), indent=2)}")
    
except Exception as e:
    print(f"❌ Error: {e}") 