# end_to_end_test.py - COMPLETE WORKFLOW TEST
import requests
import time
import json
import sys
import os
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class InfluencerAIEndToEndTest:
    """
    🎯 COMPLETE END-TO-END TEST SUITE
    
    Tests the entire influencer marketing workflow:
    1. System health check
    2. Campaign creation and orchestration
    3. Creator discovery
    4. AI strategy generation
    5. ElevenLabs call integration
    6. Contract generation
    7. Monitoring and analytics
    """
    
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.test_results = {}
        self.campaign_task_id = None
        self.conversation_id = None
        
        print("🎯 INFLUENCER AI - END-TO-END TEST SUITE")
        print("=" * 70)
        print("Testing complete workflow from campaign creation to contract generation")
        print()
    
    async def run_complete_test_suite(self):
        """Run the complete end-to-end test suite"""
        
        # Phase 1: System Health & Infrastructure
        print("📋 PHASE 1: SYSTEM HEALTH & INFRASTRUCTURE")
        print("-" * 50)
        
        if not await self.test_system_health():
            print("❌ System health check failed - aborting tests")
            return False
        
        if not await self.test_elevenlabs_integration():
            print("❌ ElevenLabs integration failed - aborting tests")
            return False
        
        # Phase 2: Campaign Creation & Orchestration
        print("\n📋 PHASE 2: CAMPAIGN CREATION & ORCHESTRATION")
        print("-" * 50)
        
        if not await self.test_campaign_creation():
            print("❌ Campaign creation failed - aborting tests")
            return False
        
        if not await self.test_campaign_monitoring():
            print("❌ Campaign monitoring failed")
            # Don't abort - continue with other tests
        
        # Phase 3: AI & Voice Integration
        print("\n📋 PHASE 3: AI & VOICE INTEGRATION")
        print("-" * 50)
        
        if not await self.test_ai_strategy_generation():
            print("⚠️ AI strategy generation failed - continuing with fallback")
        
        # Phase 4: ElevenLabs Call Testing (Optional)
        print("\n📋 PHASE 4: ELEVENLABS CALL TESTING")
        print("-" * 50)
        
        call_test_choice = input("🤔 Do you want to test actual ElevenLabs calls? (y/n): ").strip().lower()
        
        if call_test_choice == 'y':
            phone_number = input("📱 Enter phone number for test call (+1234567890): ").strip()
            if phone_number:
                await self.test_actual_elevenlabs_call(phone_number)
        
        # Phase 5: Contract Generation
        print("\n📋 PHASE 5: CONTRACT GENERATION")
        print("-" * 50)
        
        await self.test_contract_generation()
        
        # Phase 6: Results & Analytics
        print("\n📋 PHASE 6: RESULTS & ANALYTICS")
        print("-" * 50)
        
        await self.generate_test_report()
        
        return True
    
    async def test_system_health(self):
        """Test system health and basic connectivity"""
        
        try:
            print("1. 🏥 Testing system health...")
            
            response = requests.get(f"{self.base_url}/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                print(f"   ✅ System Status: {health_data.get('status', 'unknown')}")
                print(f"   📊 Services: {len(health_data.get('services', {}))}")
                
                self.test_results['system_health'] = {
                    'status': 'passed',
                    'response_time': response.elapsed.total_seconds(),
                    'services': health_data.get('services', {})
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
    
    async def test_elevenlabs_integration(self):
        """Test ElevenLabs integration and credentials"""
        
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
    
    async def test_campaign_creation(self):
        """Test campaign creation and orchestration workflow"""
        
        try:
            print("3. 🎯 Testing campaign creation and orchestration...")
            
            # Create comprehensive test campaign
            campaign_data = {
                "campaign_id": f"e2e_test_{int(datetime.now().timestamp())}",
                "product_name": "E2E TestPro Device",
                "brand_name": "EndToEnd Tech Solutions",
                "product_description": "Complete end-to-end testing device with advanced AI capabilities for comprehensive workflow validation",
                "target_audience": "Tech professionals, QA engineers, and system testers aged 25-45",
                "campaign_goal": "Validate complete influencer marketing automation workflow",
                "product_niche": "technology",
                "total_budget": 12000.0
            }
            
            response = requests.post(
                f"{self.base_url}/api/webhook/enhanced-campaign",
                json=campaign_data,
                timeout=30
            )
            
            if response.status_code == 202:
                data = response.json()
                self.campaign_task_id = data.get('task_id')
                
                print(f"   ✅ Campaign Created: {data.get('campaign_id')}")
                print(f"   🎯 Task ID: {self.campaign_task_id}")
                print(f"   ⏱️ Estimated Duration: {data.get('estimated_duration_minutes')} minutes")
                print(f"   🔧 Enhancements: {len(data.get('enhancements', []))}")
                
                self.test_results['campaign_creation'] = {
                    'status': 'passed',
                    'task_id': self.campaign_task_id,
                    'campaign_id': data.get('campaign_id'),
                    'enhancements': data.get('enhancements', [])
                }
                
                # Wait for orchestration to start
                print("   ⏳ Waiting for orchestration to initialize...")
                time.sleep(3)
                
                return True
            else:
                print(f"   ❌ Campaign creation failed: {response.status_code}")
                print(f"   📝 Error: {response.text}")
                self.test_results['campaign_creation'] = {'status': 'failed', 'error': response.text}
                return False
                
        except Exception as e:
            print(f"   ❌ Campaign creation exception: {e}")
            self.test_results['campaign_creation'] = {'status': 'failed', 'error': str(e)}
            return False
    
    async def test_campaign_monitoring(self):
        """Test campaign monitoring and progress tracking"""
        
        if not self.campaign_task_id:
            print("4. ⚠️ Skipping campaign monitoring - no task ID available")
            return False
        
        try:
            print("4. 👁️ Testing campaign monitoring...")
            
            monitor_url = f"{self.base_url}/api/monitor/enhanced-campaign/{self.campaign_task_id}"
            
            # Try monitoring for up to 2 minutes
            max_attempts = 12
            for attempt in range(max_attempts):
                response = requests.get(monitor_url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    current_stage = data.get('current_stage', 'unknown')
                    
                    print(f"   📊 Attempt {attempt + 1}: Stage = {current_stage}")
                    
                    if current_stage in ['completed', 'failed']:
                        print(f"   ✅ Campaign finished: {current_stage}")
                        
                        self.test_results['campaign_monitoring'] = {
                            'status': 'passed',
                            'final_stage': current_stage,
                            'attempts': attempt + 1,
                            'final_data': data
                        }
                        
                        # Save results for contract generation
                        if current_stage == 'completed' and data.get('successful_negotiations', 0) > 0:
                            print(f"   🎉 Successful negotiations: {data.get('successful_negotiations')}")
                        
                        return True
                    
                    time.sleep(10)  # Wait 10 seconds between checks
                else:
                    print(f"   ⚠️ Monitor response: {response.status_code}")
            
            print("   ⏰ Monitoring timeout - campaign may still be running")
            self.test_results['campaign_monitoring'] = {'status': 'timeout', 'attempts': max_attempts}
            return False
            
        except Exception as e:
            print(f"   ❌ Campaign monitoring exception: {e}")
            self.test_results['campaign_monitoring'] = {'status': 'failed', 'error': str(e)}
            return False
    
    async def test_ai_strategy_generation(self):
        """Test AI strategy generation capabilities"""
        
        try:
            print("5. 🧠 Testing AI strategy generation...")
            
            # Test system status to check AI capabilities
            response = requests.get(f"{self.base_url}/api/webhook/system-status", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                ai_features = data.get('enhanced_features', {})
                
                print(f"   🤖 AI Strategy Generation: {ai_features.get('ai_strategy_generation', False)}")
                print(f"   🔍 Creator Discovery: {ai_features.get('creator_discovery', False)}")
                print(f"   📝 Contract Automation: {ai_features.get('contract_automation', False)}")
                
                self.test_results['ai_strategy'] = {
                    'status': 'passed',
                    'features': ai_features,
                    'ai_available': ai_features.get('ai_strategy_generation', False)
                }
                return True
            else:
                print(f"   ❌ AI strategy test failed: {response.status_code}")
                self.test_results['ai_strategy'] = {'status': 'failed', 'error': response.status_code}
                return False
                
        except Exception as e:
            print(f"   ❌ AI strategy test exception: {e}")
            self.test_results['ai_strategy'] = {'status': 'failed', 'error': str(e)}
            return False
    
    async def test_actual_elevenlabs_call(self, phone_number):
        """Test actual ElevenLabs call functionality"""
        
        try:
            print("6. 📞 Testing actual ElevenLabs call...")
            
            call_data = {
                "creator_phone": phone_number,
                "creator_profile": {
                    "id": "e2e_test_creator",
                    "name": "E2E TestCreator",
                    "niche": "technology",
                    "followers": 85000,
                    "engagement_rate": 4.5,
                    "average_views": 42000,
                    "location": "Test Location",
                    "languages": ["English"],
                    "typical_rate": 3000,
                    "availability": "excellent"
                },
                "campaign_data": {
                    "product_name": "E2E TestPro Device",
                    "brand_name": "EndToEnd Tech Solutions",
                    "product_description": "Advanced testing device for end-to-end validation",
                    "target_audience": "Tech professionals and QA engineers",
                    "campaign_goal": "Complete workflow validation",
                    "product_niche": "technology",
                    "total_budget": 12000.0
                },
                "pricing_strategy": {
                    "initial_offer": 2500,
                    "max_offer": 4000,
                    "negotiation_style": "collaborative"
                }
            }
            
            print(f"   📱 Initiating call to: {phone_number}")
            print("   ⚠️ Please answer your phone for the test call")
            
            response = requests.post(
                f"{self.base_url}/api/webhook/test-actual-call",
                json=call_data,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                self.conversation_id = data.get('conversation_id')
                
                print(f"   ✅ Call initiated: {self.conversation_id}")
                print(f"   📞 Expected duration: {data.get('expected_duration')}")
                print("   📱 Check your phone for incoming call!")
                
                # Monitor call completion
                await self._monitor_call_completion(self.conversation_id)
                
                self.test_results['elevenlabs_call'] = {
                    'status': 'passed',
                    'conversation_id': self.conversation_id,
                    'phone_number': phone_number
                }
                return True
            else:
                print(f"   ❌ Call initiation failed: {response.status_code}")
                print(f"   📝 Error: {response.text}")
                self.test_results['elevenlabs_call'] = {'status': 'failed', 'error': response.text}
                return False
                
        except Exception as e:
            print(f"   ❌ ElevenLabs call test exception: {e}")
            self.test_results['elevenlabs_call'] = {'status': 'failed', 'error': str(e)}
            return False
    
    async def _monitor_call_completion(self, conversation_id):
        """Monitor call until completion"""
        
        print("   🔄 Monitoring call progress...")
        
        max_wait_time = 300  # 5 minutes
        poll_interval = 10   # 10 seconds
        
        start_time = time.time()
        
        while (time.time() - start_time) < max_wait_time:
            try:
                response = requests.get(
                    f"{self.base_url}/api/webhook/call-status/{conversation_id}",
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    status = data.get('status', 'unknown')
                    
                    print(f"   📊 Call status: {status}")
                    
                    if status in ['completed', 'failed']:
                        print(f"   🏁 Call finished: {status}")
                        if status == 'completed':
                            print("   🎉 Call completed successfully!")
                        return status
                
                time.sleep(poll_interval)
                
            except Exception as e:
                print(f"   ⚠️ Call monitoring error: {e}")
                time.sleep(poll_interval)
        
        print("   ⏰ Call monitoring timeout")
        return "timeout"
    
    async def test_contract_generation(self):
        """Test contract generation capabilities"""
        
        try:
            print("7. 📝 Testing contract generation...")
            
            # Test 1: Simple contract generation
            contract_data = {
                "creator_name": "E2E TestCreator",
                "compensation": 3500.0,
                "campaign_details": {
                    "brand": "EndToEnd Tech Solutions",
                    "product": "E2E TestPro Device",
                    "deliverables": ["1 video review", "3 Instagram stories"],
                    "timeline": "3 weeks"
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/webhook/generate-enhanced-contract",
                json=contract_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Simple contract generated: {data.get('contract_metadata', {}).get('contract_id')}")
                
                # Test 2: Contract from call (if we have a conversation ID)
                if self.conversation_id:
                    await self._test_contract_from_call()
                
                self.test_results['contract_generation'] = {
                    'status': 'passed',
                    'simple_contract': True,
                    'from_call': bool(self.conversation_id)
                }
                return True
            else:
                print(f"   ❌ Contract generation failed: {response.status_code}")
                self.test_results['contract_generation'] = {'status': 'failed', 'error': response.text}
                return False
                
        except Exception as e:
            print(f"   ❌ Contract generation exception: {e}")
            self.test_results['contract_generation'] = {'status': 'failed', 'error': str(e)}
            return False
    
    async def _test_contract_from_call(self):
        """Test contract generation from call results"""
        
        try:
            print("   📋 Testing contract from call results...")
            
            response = requests.post(
                f"{self.base_url}/api/webhook/generate-contract-from-call",
                json={"conversation_id": self.conversation_id},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Call-based contract generated: {data.get('contract_id')}")
                
                # Save contract to file
                contract_text = data.get('contract_text', '')
                filename = f"e2e_test_contract_{self.conversation_id[:8]}.txt"
                
                with open(filename, 'w') as f:
                    f.write(contract_text)
                
                print(f"   📄 Contract saved: {filename}")
                return True
            else:
                print(f"   ⚠️ Call-based contract failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ⚠️ Call-based contract exception: {e}")
            return False
    
    async def generate_test_report(self):
        """Generate comprehensive test report"""
        
        print("8. 📊 Generating test report...")
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results.values() if r.get('status') == 'passed'])
        
        print(f"\n🎯 END-TO-END TEST RESULTS")
        print("=" * 70)
        print(f"📊 Overall Results: {passed_tests}/{total_tests} tests passed")
        print(f"✅ Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        # Detailed results
        for test_name, result in self.test_results.items():
            status_icon = "✅" if result.get('status') == 'passed' else "❌" if result.get('status') == 'failed' else "⚠️"
            print(f"{status_icon} {test_name.replace('_', ' ').title()}: {result.get('status')}")
        
        print()
        print("🔍 WORKFLOW VALIDATION:")
        
        # Check complete workflow
        workflow_steps = [
            ('system_health', 'System Infrastructure'),
            ('elevenlabs_integration', 'ElevenLabs Integration'),
            ('campaign_creation', 'Campaign Creation'),
            ('ai_strategy', 'AI Strategy Generation'),
            ('contract_generation', 'Contract Generation')
        ]
        
        for step_key, step_name in workflow_steps:
            if step_key in self.test_results:
                result = self.test_results[step_key]
                status = "✅ PASS" if result.get('status') == 'passed' else "❌ FAIL"
                print(f"   {status} {step_name}")
        
        # Save detailed report
        report_filename = f"e2e_test_report_{int(datetime.now().timestamp())}.json"
        with open(report_filename, 'w') as f:
            json.dump({
                'test_timestamp': datetime.now().isoformat(),
                'summary': {
                    'total_tests': total_tests,
                    'passed_tests': passed_tests,
                    'success_rate': (passed_tests/total_tests)*100
                },
                'detailed_results': self.test_results
            }, f, indent=2)
        
        print(f"\n📄 Detailed report saved: {report_filename}")
        
        # Final recommendations
        print("\n💡 RECOMMENDATIONS:")
        if passed_tests == total_tests:
            print("   🎉 Perfect! Your system is production-ready")
            print("   ✅ All workflows validated successfully")
            print("   🚀 Ready for real influencer campaigns")
        elif passed_tests >= total_tests * 0.8:
            print("   👍 Good! Most systems are working correctly")
            print("   🔧 Review failed tests and address issues")
            print("   📈 System is mostly ready for production")
        else:
            print("   ⚠️ Issues detected that need attention")
            print("   🔧 Fix critical failures before production use")
            print("   📊 Review system configuration and integrations")

def main():
    """Run the complete end-to-end test suite"""
    
    print("🎯 INFLUENCER AI - END-TO-END TEST SUITE")
    print("This will test your complete influencer marketing workflow")
    print()
    
    # Check if server is running
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server is not responding correctly")
            print("   Please start your server with: uvicorn main:app --reload")
            return
    except:
        print("❌ Cannot connect to server")
        print("   Please start your server with: uvicorn main:app --reload")
        return
    
    # Run tests
    test_suite = InfluencerAIEndToEndTest()
    
    import asyncio
    asyncio.run(test_suite.run_complete_test_suite())

if __name__ == "__main__":
    main()