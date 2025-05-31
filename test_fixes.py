#!/usr/bin/env python3
"""
InfluencerFlow AI - Test Script for Fixed Integration
Run this script to validate that all fixes are working properly.
"""

import requests
import json
import time
import sys
from typing import Dict, Any

class FixedSystemTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.conversation_id = None
        self.test_results = []
        
    def log_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def test_health_check(self) -> bool:
        """Test basic health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                details = f"Status: {data['status']}, Active conversations: {data['system']['active_conversations']}"
                self.log_result("Health Check", True, details)
                return True
            else:
                self.log_result("Health Check", False, f"HTTP {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            self.log_result("Health Check", False, "Cannot connect to server")
            return False
        except Exception as e:
            self.log_result("Health Check", False, str(e))
            return False
    
    def test_conversation_creation(self) -> bool:
        """Test conversation creation - FIXED VERSION"""
        try:
            payload = {
                "creator_id": "sarah_tech",
                "campaign_brief": {
                    "brand_name": "TechBrand Agency",
                    "product_name": "iPhone MagSafe Case",
                    "campaign_type": "Product Review",
                    "deliverables": ["video_review", "instagram_post"],
                    "budget_max": 4000,
                    "timeline": "2 weeks"
                },
                "brand_name": "TechBrand Agency",
                "contact_person": "Test Script"
            }
            
            response = requests.post(
                f"{self.base_url}/api/elevenlabs/simulate-call",
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.conversation_id = data["conversation_id"]
                    details = f"ID: {self.conversation_id[:8]}..., Creator: {data['creator_name']}"
                    self.log_result("Conversation Creation", True, details)
                    return True
                else:
                    self.log_result("Conversation Creation", False, "Response success=False")
                    return False
            else:
                self.log_result("Conversation Creation", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Conversation Creation", False, str(e))
            return False
    
    def test_conversation_status(self) -> bool:
        """Test conversation status retrieval - FIXED VERSION"""
        if not self.conversation_id:
            self.log_result("Conversation Status", False, "No conversation ID available")
            return False
        
        try:
            response = requests.get(
                f"{self.base_url}/api/conversation-status/{self.conversation_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                details = f"Status: {data['status']}, Messages: {len(data.get('transcript', []))}"
                self.log_result("Conversation Status", True, details)
                return True
            else:
                self.log_result("Conversation Status", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Conversation Status", False, str(e))
            return False
    
    def test_creator_response(self) -> bool:
        """Test adding creator response - FIXED VERSION"""
        if not self.conversation_id:
            self.log_result("Creator Response", False, "No conversation ID available")
            return False
        
        try:
            payload = {
                "conversation_id": self.conversation_id,
                "creator_response": "I usually charge $5000, and I need at least 3 weeks for quality content."
            }
            
            response = requests.post(
                f"{self.base_url}/api/creator-response",
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    details = f"AI Response generated, Tools used: {', '.join(data.get('tools_used', []))}"
                    self.log_result("Creator Response", True, details)
                    return True
                else:
                    self.log_result("Creator Response", False, "Response success=False")
                    return False
            else:
                self.log_result("Creator Response", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Creator Response", False, str(e))
            return False
    
    def test_update_deal_tool(self) -> bool:
        """Test update deal parameters tool - FIXED VERSION"""
        if not self.conversation_id:
            self.log_result("Update Deal Tool", False, "No conversation ID available")
            return False
        
        try:
            payload = {
                "conversation_id": self.conversation_id,
                "price": 4500,
                "timeline": "3 weeks",
                "rationale": "Test script - updating deal based on creator feedback"
            }
            
            response = requests.post(
                f"{self.base_url}/api/tools/update-deal",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    deal = data.get("updated_deal", {})
                    details = f"Price: ${deal.get('price', 'N/A')}, Timeline: {deal.get('timeline', 'N/A')}"
                    self.log_result("Update Deal Tool", True, details)
                    return True
                else:
                    self.log_result("Update Deal Tool", False, f"Tool error: {data.get('error', 'Unknown')}")
                    return False
            else:
                self.log_result("Update Deal Tool", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Update Deal Tool", False, str(e))
            return False
    
    def test_creator_insights_tool(self) -> bool:
        """Test creator insights tool - FIXED VERSION"""
        try:
            response = requests.get(
                f"{self.base_url}/api/tools/creator-insights?creator_id=sarah_tech&niche=tech",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    creator_data = data.get("creator_data", {})
                    details = f"Engagement: {creator_data.get('engagement_rate', 'N/A')}%, Followers: {creator_data.get('followers', 'N/A'):,}"
                    self.log_result("Creator Insights Tool", True, details)
                    return True
                else:
                    self.log_result("Creator Insights Tool", False, f"Tool error: {data.get('error', 'Unknown')}")
                    return False
            else:
                self.log_result("Creator Insights Tool", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Creator Insights Tool", False, str(e))
            return False
    
    def test_complete_end_to_end(self) -> bool:
        """Test the complete end-to-end workflow - NEW FEATURE"""
        try:
            response = requests.post(
                f"{self.base_url}/api/test/simulate-full-conversation",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    summary = data.get("summary", {})
                    details = f"Final price: ${summary.get('final_agreed_price', 'N/A')}, Tools used: {summary.get('tools_used_count', 0)}, Messages: {summary.get('total_messages', 0)}"
                    self.log_result("Complete End-to-End", True, details)
                    return True
                else:
                    self.log_result("Complete End-to-End", False, f"Workflow error: {data.get('detail', 'Unknown')}")
                    return False
            else:
                self.log_result("Complete End-to-End", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Complete End-to-End", False, str(e))
            return False
    
    def test_conversation_cleanup(self) -> bool:
        """Test conversation cleanup and reset"""
        try:
            response = requests.post(f"{self.base_url}/api/debug/reset-conversations", timeout=10)
            
            if response.status_code == 200:
                self.log_result("Conversation Cleanup", True, "All conversations reset")
                return True
            else:
                self.log_result("Conversation Cleanup", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Conversation Cleanup", False, str(e))
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run comprehensive test suite"""
        print("🧪 INFLUENCERFLOW AI - FIXED INTEGRATION TEST SUITE")
        print("=" * 60)
        print("Testing all fixes and improvements...")
        print()
        
        # Test sequence
        tests = [
            ("Basic System Health", self.test_health_check),
            ("Conversation Creation (Fixed)", self.test_conversation_creation),
            ("Conversation Status (Fixed)", self.test_conversation_status),
            ("Creator Response (Fixed)", self.test_creator_response),
            ("Update Deal Tool (Fixed)", self.test_update_deal_tool),
            ("Creator Insights Tool (Fixed)", self.test_creator_insights_tool),
            ("Complete End-to-End (New)", self.test_complete_end_to_end),
            ("Conversation Cleanup", self.test_conversation_cleanup),
        ]
        
        for test_name, test_func in tests:
            print(f"\n🔄 Running: {test_name}")
            try:
                test_func()
                time.sleep(0.5)  # Small delay between tests
            except Exception as e:
                self.log_result(test_name, False, f"Test execution error: {str(e)}")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        failed = len(self.test_results) - passed
        
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{result['test']:30} {status}")
            if not result["success"] and result["details"]:
                print(f"{'':32} └─ {result['details']}")
        
        print(f"\nResults: {passed} passed, {failed} failed out of {len(self.test_results)} tests")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! The fixed integration is working perfectly!")
            print("✅ Conversation management fixed")
            print("✅ Tool integration working")
            print("✅ End-to-end workflow operational")
            print("✅ ElevenLabs integration ready")
        else:
            print(f"\n⚠️ {failed} tests failed. Check the errors above.")
            print("🔧 Review the failed components and ensure the server is running properly.")
        
        return {
            "total_tests": len(self.test_results),
            "passed": passed,
            "failed": failed,
            "success_rate": round((passed / len(self.test_results)) * 100, 1),
            "all_passed": failed == 0,
            "conversation_id": self.conversation_id,
            "test_results": self.test_results
        }

def main():
    """Main test execution"""
    print("InfluencerFlow AI - Fixed Integration Tester")
    print("Make sure your FastAPI server is running on http://localhost:8000")
    print()
    
    # Optional: wait for user confirmation
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        print("Running in automatic mode...")
    else:
        input("Press Enter when your server is ready...")
    
    tester = FixedSystemTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if results["all_passed"] else 1)

if __name__ == "__main__":
    main()