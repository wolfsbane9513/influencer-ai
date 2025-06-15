# end_to_end_test.py - FIXED E2E TEST
import requests
import time
import json
import sys
import os
from datetime import datetime

class InfluencerAIEndToEndTest:
    """
    🎯 FIXED END-TO-END TEST SUITE
    
    Tests the unified InfluencerAI workflow with proper endpoint expectations
    """
    
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.test_results = {}
        self.campaign_task_id = None
        
        print("🎯 INFLUENCER AI - END-TO-END TEST SUITE")
        print("This will test your complete influencer marketing workflow")
        print("🎯 INFLUENCER AI - END-TO-END TEST SUITE")
        print("=" * 70)
        print("Testing complete workflow from campaign creation to contract generation")
        print()
    
    def run_all_tests(self):
        """Run the complete test suite"""
        
        # Phase 1: System Health & Infrastructure
        print("📋 PHASE 1: SYSTEM HEALTH & INFRASTRUCTURE")
        print("-" * 50)
        
        if not self.test_system_health():
            print("❌ System health check failed - aborting tests")
            return False
        
        if not self.test_elevenlabs_integration():
            print("❌ ElevenLabs integration failed - aborting tests")
            return False
        
        # Phase 2: Campaign Creation & Orchestration
        print("\n📋 PHASE 2: CAMPAIGN CREATION & ORCHESTRATION")
        print("-" * 50)
        
        if not self.test_campaign_creation():
            print("❌ Campaign creation failed - aborting tests")
            return False
        
        if not self.test_campaign_monitoring():
            print("⚠️ Campaign monitoring issues detected")
        
        # Phase 3: Final Results
        print("\n📋 PHASE 3: FINAL RESULTS")
        print("-" * 50)
        
        self.print_test_summary()
        return True
    
    def test_system_health(self):
        """Test system health endpoint"""
        try:
            print("1. 🏥 Testing system health...")
            
            response = requests.get(f"{self.base_url}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ System Status: {data.get('status', 'unknown')}")
                print(f"   📊 Services: {data.get('services_count', 'unknown')}")
                
                self.test_results['system_health'] = {
                    'status': 'passed',
                    'services_count': data.get('services_count', 0)
                }
                return True
            else:
                print(f"   ❌ Health check failed: {response.status_code}")
                self.test_results['system_health'] = {'status': 'failed', 'error': response.status_code}
                return False
                
        except Exception as e:
            print(f"   ❌ Health check exception: {e}")
            self.test_results['system_health'] = {'status': 'failed', 'error': str(e)}
            return False
    
    def test_elevenlabs_integration(self):
        """Test ElevenLabs integration"""
        try:
            print("2. 📞 Testing ElevenLabs integration...")
            
            response = requests.get(f"{self.base_url}/api/webhook/test-enhanced-elevenlabs", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ ElevenLabs Status: {data.get('status', 'unknown')}")
                print(f"   🔌 API Connected: {data.get('api_connected', False)}")
                
                self.test_results['elevenlabs_integration'] = {
                    'status': 'passed',
                    'api_connected': data.get('api_connected', False),
                    'features': data.get('features', [])
                }
                return True
            else:
                print(f"   ❌ ElevenLabs test failed: {response.status_code}")
                self.test_results['elevenlabs_integration'] = {'status': 'failed', 'error': response.status_code}
                return False
                
        except Exception as e:
            print(f"   ❌ ElevenLabs test exception: {e}")
            self.test_results['elevenlabs_integration'] = {'status': 'failed', 'error': str(e)}
            return False
    
    def test_campaign_creation(self):
        """Test campaign creation and orchestration workflow"""
        try:
            print("3. 🎯 Testing campaign creation and orchestration...")
            
            # Create test campaign using new unified API
            campaign_data = {
                "product_name": "E2E TestPro Device",
                "brand_name": "TestTech Solutions",
                "product_description": "Revolutionary testing device for end-to-end validation",
                "target_audience": "Tech enthusiasts and developers",
                "campaign_goal": "Generate awareness and drive pre-orders",
                "product_niche": "tech",
                "total_budget": 12000.0,
                "max_creators": 10,
                "timeline_days": 30
            }
            
            response = requests.post(
                f"{self.base_url}/api/campaigns",
                json=campaign_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.campaign_task_id = data.get("task_id")
                
                print(f"   ✅ Campaign created successfully")
                print(f"   📋 Task ID: {self.campaign_task_id}")
                print(f"   💰 Budget: ${data.get('budget_per_creator', 'N/A')} per creator")
                print(f"   🎯 Campaign Code: {data.get('campaign_code', 'N/A')}")
                
                self.test_results['campaign_creation'] = {
                    'status': 'passed',
                    'task_id': self.campaign_task_id,
                    'campaign_id': data.get("campaign_id"),
                    'campaign_code': data.get("campaign_code")
                }
                return True
            else:
                print(f"   ❌ Campaign creation failed: {response.status_code}")
                print(f"   📝 Error: {response.text}")
                self.test_results['campaign_creation'] = {
                    'status': 'failed', 
                    'error': response.status_code,
                    'response': response.text
                }
                return False
                
        except Exception as e:
            print(f"   ❌ Campaign creation exception: {e}")
            self.test_results['campaign_creation'] = {'status': 'failed', 'error': str(e)}
            return False
    
    def test_campaign_monitoring(self):
        """Test campaign monitoring and progress tracking"""
        if not self.campaign_task_id:
            print("4. ⚠️ Skipping monitoring test - no campaign task ID")
            return False
        
        try:
            print("4. 📊 Testing campaign monitoring...")
            
            # Wait a moment for campaign to start
            time.sleep(3)
            
            # Check campaign status using new API
            response = requests.get(
                f"{self.base_url}/api/campaigns/{self.campaign_task_id}",
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"   ✅ Campaign Status: {data.get('current_stage', 'unknown')}")
                print(f"   🏁 Complete: {data.get('is_complete', False)}")
                
                # Check progress metrics
                progress = data.get('progress', {})
                print(f"   👥 Creators Discovered: {progress.get('creators_discovered', 0)}")
                print(f"   🤝 Negotiations: {progress.get('negotiations_completed', 0)}")
                print(f"   📝 Contracts: {progress.get('contracts_generated', 0)}")
                
                self.test_results['campaign_monitoring'] = {
                    'status': 'passed',
                    'current_stage': data.get('current_stage'),
                    'progress': progress
                }
                
                # Wait for campaign to complete (up to 30 seconds)
                return self._wait_for_campaign_completion()
            else:
                print(f"   ❌ Monitoring failed: {response.status_code}")
                self.test_results['campaign_monitoring'] = {'status': 'failed', 'error': response.status_code}
                return False
                
        except Exception as e:
            print(f"   ❌ Monitoring exception: {e}")
            self.test_results['campaign_monitoring'] = {'status': 'failed', 'error': str(e)}
            return False
    
    def _wait_for_campaign_completion(self):
        """Wait for campaign to complete and show final results"""
        print("   ⏳ Waiting for campaign completion...")
        
        for attempt in range(10):  # Wait up to 30 seconds
            try:
                response = requests.get(
                    f"{self.base_url}/api/campaigns/{self.campaign_task_id}",
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('is_complete'):
                        print("   🎉 Campaign completed!")
                        
                        # Get detailed results
                        progress = data.get('progress', {})
                        print(f"   ✅ Final Results:")
                        print(f"      👥 Creators: {progress.get('creators_discovered', 0)}")
                        print(f"      🤝 Successful Negotiations: {progress.get('successful_negotiations', 0)}")
                        print(f"      📝 Contracts Generated: {progress.get('contracts_generated', 0)}")
                        print(f"      💰 Total Cost: ${progress.get('total_cost', 0)}")
                        print(f"      📊 Success Rate: {progress.get('success_rate_percentage', 0):.1f}%")
                        
                        self.test_results['final_results'] = progress
                        return True
                    else:
                        current_stage = data.get('current_stage', 'unknown')
                        print(f"   ⏳ Stage: {current_stage}")
                        time.sleep(3)
                else:
                    print(f"   ⚠️ Status check failed: {response.status_code}")
                    time.sleep(3)
                    
            except Exception as e:
                print(f"   ⚠️ Status check error: {e}")
                time.sleep(3)
        
        print("   ⏰ Campaign still running (timeout reached)")
        return False
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("📊 TEST SUMMARY")
        print("-" * 30)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result.get('status') == 'passed')
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL TESTS PASSED - System is working correctly!")
        else:
            print(f"\n⚠️ {total_tests - passed_tests} tests failed - Check logs for details")
        
        # Show detailed results
        print("\n📋 Detailed Results:")
        for test_name, result in self.test_results.items():
            status_emoji = "✅" if result.get('status') == 'passed' else "❌"
            print(f"   {status_emoji} {test_name}: {result.get('status', 'unknown')}")
        
        # Show final campaign metrics if available
        final_results = self.test_results.get('final_results')
        if final_results:
            print(f"\n🎯 Campaign Performance:")
            print(f"   👥 Creators Discovered: {final_results.get('creators_discovered', 0)}")
            print(f"   🤝 Successful Negotiations: {final_results.get('successful_negotiations', 0)}")
            print(f"   📝 Contracts Generated: {final_results.get('contracts_generated', 0)}")
            print(f"   💰 Total Campaign Cost: ${final_results.get('total_cost', 0)}")
            print(f"   📊 Success Rate: {final_results.get('success_rate_percentage', 0):.1f}%")

if __name__ == "__main__":
    test = InfluencerAIEndToEndTest()
    success = test.run_all_tests()
    
    if success:
        print(f"\n🚀 END-TO-END TEST COMPLETED!")
        print("💡 Your InfluencerAI platform is working correctly")
    else:
        print(f"\n❌ TESTS FAILED")
        print("🔧 Check the error details above and fix any issues")
    
    sys.exit(0 if success else 1)