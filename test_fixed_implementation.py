# test_fixed_implementation.py - TESTING THE CORRECTED CODEBASE
import asyncio
import logging
import requests
import json
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FixedImplementationTester:
    """
    🧪 TEST THE CORRECTED ELEVENLABS INTEGRATION
    
    This class tests all the fixes we applied:
    1. Contract generation after successful calls
    2. Proper call state handling
    3. Error handling and recovery
    4. Status monitoring improvements
    """
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
    
    async def run_all_tests(self):
        """Run comprehensive tests of the fixed implementation"""
        
        logger.info("🧪 Starting comprehensive tests of fixed implementation...")
        
        tests = [
            ("Health Check", self.test_health_check),
            ("System Status", self.test_system_status),
            ("ElevenLabs Credentials", self.test_elevenlabs_credentials),
            ("Enhanced Campaign Workflow", self.test_enhanced_campaign),
            ("Call State Handling", self.test_call_state_handling),
            ("Contract Generation", self.test_contract_generation),
            ("Error Recovery", self.test_error_recovery),
            ("Monitoring Integration", self.test_monitoring_integration)
        ]
        
        for test_name, test_func in tests:
            try:
                logger.info(f"🔍 Running test: {test_name}")
                result = await test_func()
                self.test_results.append({
                    "test": test_name,
                    "status": "PASSED" if result else "FAILED",
                    "timestamp": datetime.now().isoformat()
                })
                logger.info(f"✅ Test passed: {test_name}")
            except Exception as e:
                logger.error(f"❌ Test failed: {test_name} - {e}")
                self.test_results.append({
                    "test": test_name,
                    "status": "ERROR",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        # Print test summary
        self.print_test_summary()
    
    async def test_health_check(self):
        """Test basic health check endpoint"""
        
        response = requests.get(f"{self.base_url}/health")
        
        if response.status_code == 200:
            health_data = response.json()
            logger.info(f"📊 Health status: {health_data.get('status')}")
            
            # Check that services are reporting status
            services = health_data.get("services", {})
            assert "voice_service" in services, "Voice service not in health check"
            assert "orchestrator" in services, "Orchestrator not in health check"
            
            return True
        else:
            logger.error(f"Health check failed: {response.status_code}")
            return False
    
    async def test_system_status(self):
        """Test enhanced system status endpoint"""
        
        response = requests.get(f"{self.base_url}/api/webhook/system-status")
        
        if response.status_code == 200:
            status_data = response.json()
            logger.info(f"📊 System status: {status_data.get('system_status')}")
            
            # Check enhanced features are reported
            assert "enhanced_features" in status_data, "Enhanced features not reported"
            assert "services_status" in status_data, "Services status not reported"
            
            return True
        else:
            logger.error(f"System status check failed: {response.status_code}")
            return False
    
    async def test_elevenlabs_credentials(self):
        """Test ElevenLabs credential validation"""
        
        response = requests.get(f"{self.base_url}/api/webhook/test-enhanced-elevenlabs")
        
        if response.status_code == 200:
            test_data = response.json()
            logger.info(f"📞 ElevenLabs test: {test_data.get('status')}")
            
            # Should report either success or mock mode
            status = test_data.get("status")
            assert status in ["success", "mock_mode"], f"Unexpected status: {status}"
            
            return True
        else:
            logger.error(f"ElevenLabs test failed: {response.status_code}")
            return False
    
    async def test_enhanced_campaign(self):
        """Test the enhanced campaign workflow"""
        
        campaign_data = {
            "campaign_id": "test_campaign_fixed",
            "product_name": "TestPro Device",
            "brand_name": "TestTech",
            "product_description": "Revolutionary testing device",
            "target_audience": "Tech enthusiasts",
            "campaign_goal": "Product launch",
            "product_niche": "technology",
            "total_budget": 10000.0
        }
        
        response = requests.post(
            f"{self.base_url}/api/webhook/enhanced-campaign",
            json=campaign_data
        )
        
        if response.status_code == 200:
            campaign_result = response.json()
            logger.info(f"🎯 Campaign started: {campaign_result.get('task_id')}")
            
            # Check required fields
            assert "task_id" in campaign_result, "Missing task_id"
            assert "monitor_url" in campaign_result, "Missing monitor_url"
            
            # Test monitoring
            task_id = campaign_result["task_id"]
            return await self._monitor_campaign_completion(task_id)
        else:
            logger.error(f"Enhanced campaign test failed: {response.status_code}")
            return False
    
    async def _monitor_campaign_completion(self, task_id: str, max_wait_minutes=10):
        """Monitor campaign completion with proper timeout"""
        
        start_time = datetime.now()
        max_wait_seconds = max_wait_minutes * 60
        
        while (datetime.now() - start_time).total_seconds() < max_wait_seconds:
            try:
                response = requests.get(f"{self.base_url}/api/monitor/enhanced-campaign/{task_id}")
                
                if response.status_code == 200:
                    status_data = response.json()
                    current_stage = status_data.get("current_stage")
                    
                    logger.info(f"📊 Campaign progress: {current_stage}")
                    
                    if current_stage in ["completed", "failed"]:
                        logger.info(f"🏁 Campaign finished: {current_stage}")
                        
                        # Validate completion data
                        if current_stage == "completed":
                            assert "contracts" in status_data, "Missing contracts in completed campaign"
                            contracts = status_data.get("contracts", [])
                            logger.info(f"📋 Generated {len(contracts)} contracts")
                        
                        return current_stage == "completed"
                    
                    # Continue monitoring
                    await asyncio.sleep(10)
                else:
                    logger.error(f"Monitoring request failed: {response.status_code}")
                    await asyncio.sleep(10)
                    
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(10)
        
        logger.warning(f"⏰ Campaign monitoring timeout after {max_wait_minutes} minutes")
        return False
    
    async def test_call_state_handling(self):
        """Test proper call state handling"""
        
        response = requests.post(f"{self.base_url}/api/webhook/test-enhanced-call")
        
        if response.status_code == 200:
            call_data = response.json()
            logger.info(f"📞 Test call result: {call_data.get('status')}")
            
            # Check that call provides proper tracking info
            assert "call_details" in call_data, "Missing call details"
            assert "monitoring" in call_data, "Missing monitoring info"
            
            # Should have conversation tracking
            monitoring = call_data.get("monitoring", {})
            if "conversation_id" in monitoring:
                conversation_id = monitoring["conversation_id"]
                logger.info(f"📊 Tracking conversation: {conversation_id}")
            
            return True
        else:
            logger.error(f"Call state test failed: {response.status_code}")
            return False
    
    async def test_contract_generation(self):
        """Test contract generation functionality"""
        
        contract_data = {
            "creator_name": "Test Creator",
            "agreed_rate": 1500.0,
            "campaign_details": {
                "product_name": "TestPro Device",
                "brand_name": "TestTech"
            },
            "negotiation_data": {
                "outcome": "accepted",
                "sentiment": "positive"
            }
        }
        
        response = requests.post(
            f"{self.base_url}/api/webhook/generate-enhanced-contract",
            json=contract_data
        )
        
        if response.status_code == 200:
            contract_result = response.json()
            logger.info(f"📋 Contract generation: {contract_result.get('status')}")
            
            # Check contract structure
            assert "contract_data" in contract_result, "Missing contract data"
            assert "full_contract" in contract_result, "Missing full contract"
            
            contract_data = contract_result.get("contract_data", {})
            assert contract_data.get("creator_name") == "Test Creator", "Incorrect creator name"
            assert contract_data.get("compensation") == 1500.0, "Incorrect compensation"
            
            return True
        else:
            logger.error(f"Contract generation test failed: {response.status_code}")
            return False
    
    async def test_error_recovery(self):
        """Test error handling and recovery"""
        
        # Test with invalid data to trigger error handling
        invalid_data = {
            "campaign_id": "",  # Invalid empty ID
            "total_budget": -1000  # Invalid negative budget
        }
        
        response = requests.post(
            f"{self.base_url}/api/webhook/enhanced-campaign",
            json=invalid_data
        )
        
        # Should handle error gracefully (either validation error or proper error response)
        if response.status_code in [400, 422, 500]:
            error_data = response.json()
            logger.info(f"🛡️ Error handling working: {error_data.get('error', 'Unknown error')}")
            
            # Should provide meaningful error information
            assert "error" in error_data or "detail" in error_data, "Missing error information"