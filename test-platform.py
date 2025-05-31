# test_platform.py - Automated End-to-End Testing
import requests
import json
import time
import sys
from typing import Dict, Any

class InfluencerAITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.conversation_id = None
        
    def test_health(self) -> bool:
        """Test health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/health")
            if response.status_code == 200:
                print("✅ Health check passed")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to server. Is it running?")
            return False
    
    def test_creators_endpoint(self) -> bool:
        """Test creators listing"""
        try:
            response = requests.get(f"{self.base_url}/api/creators")
            if response.status_code == 200:
                creators = response.json()
                print(f"✅ Creators endpoint: {len(creators)} creators loaded")
                return True
            else:
                print(f"❌ Creators endpoint failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Creators test error: {e}")
            return False
    
    def test_market_data(self) -> bool:
        """Test market data endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/market-data")
            if response.status_code == 200:
                market_data = response.json()
                print(f"✅ Market data endpoint: {len(market_data)} sections loaded")
                return True
            else:
                print(f"❌ Market data failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Market data test error: {e}")
            return False
    
    def test_campaign_creation(self) -> bool:
        """Test campaign brief creation"""
        try:
            campaign_data = {
                "creator_name": "TechReviewer_Sarah",
                "budget": 3000,
                "deliverables": ["video_review", "instagram_posts"],
                "timeline": "next_friday",
                "campaign_type": "product_launch"
            }
            
            response = requests.post(
                f"{self.base_url}/api/campaign/brief",
                json=campaign_data
            )
            
            if response.status_code == 200:
                result = response.json()
                self.conversation_id = result["conversation_id"]
                print(f"✅ Campaign created: {self.conversation_id}")
                print(f"   Initial offer: ${result['initial_offer']:,}")
                return True
            else:
                print(f"❌ Campaign creation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Campaign creation error: {e}")
            return False
    
    def test_text_negotiation(self) -> bool:
        """Test text-based negotiation"""
        if not self.conversation_id:
            print("❌ No conversation ID available for negotiation test")
            return False
        
        try:
            negotiation_data = {
                "conversation_id": self.conversation_id,
                "message": "My rate for phone accessories is $4500, and Friday is too tight - I need at least 10 days",
                "speaker": "creator"
            }
            
            response = requests.post(
                f"{self.base_url}/api/negotiate",
                json=negotiation_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Text negotiation successful")
                print(f"   AI Response: {result['message'][:100]}...")
                print(f"   Current price: ${result['deal_params']['price']:,}")
                return True
            else:
                print(f"❌ Text negotiation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Text negotiation error: {e}")
            return False
    
    def test_conversation_history(self) -> bool:
        """Test conversation history retrieval"""
        if not self.conversation_id:
            print("❌ No conversation ID available for history test")
            return False
        
        try:
            response = requests.get(f"{self.base_url}/api/conversation/{self.conversation_id}")
            
            if response.status_code == 200:
                result = response.json()
                messages = result.get("messages", [])
                print(f"✅ Conversation history: {len(messages)} messages")
                return True
            else:
                print(f"❌ Conversation history failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Conversation history error: {e}")
            return False
    
    def test_insights(self) -> bool:
        """Test negotiation insights"""
        if not self.conversation_id:
            print("❌ No conversation ID available for insights test")
            return False
        
        try:
            response = requests.get(f"{self.base_url}/api/conversation/{self.conversation_id}/insights")
            
            if response.status_code == 200:
                result = response.json()
                recommendations = result.get("recommendations", [])
                print(f"✅ Negotiation insights: {len(recommendations)} recommendations")
                return True
            else:
                print(f"❌ Insights failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Insights error: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests and return results"""
        print("🧪 Starting InfluencerFlow AI End-to-End Tests")
        print("=" * 50)
        
        tests = {
            "Health Check": self.test_health,
            "Creators Endpoint": self.test_creators_endpoint,
            "Market Data": self.test_market_data,
            "Campaign Creation": self.test_campaign_creation,
            "Text Negotiation": self.test_text_negotiation,
            "Conversation History": self.test_conversation_history,
            "Negotiation Insights": self.test_insights,
        }
        
        results = {}
        
        for test_name, test_func in tests.items():
            print(f"\n🔄 Running: {test_name}")
            results[test_name] = test_func()
            time.sleep(0.5)  # Small delay between tests
        
        print("\n" + "=" * 50)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 50)
        
        passed = 0
        failed = 0
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:20} {status}")
            if result:
                passed += 1
            else:
                failed += 1
        
        print(f"\nTotal: {passed} passed, {failed} failed")
        
        if failed == 0:
            print("🎉 ALL TESTS PASSED! Your platform is ready for the buildathon!")
        else:
            print(f"⚠️  {failed} tests failed. Check the output above for details.")
        
        return results

def main():
    print("InfluencerFlow AI Platform Tester")
    print("Make sure your FastAPI server is running on http://localhost:8000")
    
    input("Press Enter when your server is ready...")
    
    tester = InfluencerAITester()
    results = tester.run_all_tests()
    
    # Check if we can provide the conversation ID for manual testing
    if tester.conversation_id:
        print(f"\n💡 For manual testing, use conversation ID: {tester.conversation_id}")
        print("   You can use this ID for voice testing and frontend testing.")

if __name__ == "__main__":
    main()