# services/enhanced_voice.py - CORRECTED VERSION
import asyncio
import logging
import requests
import random
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from config.settings import settings

logger = logging.getLogger(__name__)

class EnhancedVoiceService:
    """
    🎯 CORRECTED ELEVENLABS INTEGRATION
    
    Fixes:
    1. Proper API response validation for contract generation
    2. Improved error handling for call state management
    3. Better timeout and retry logic
    4. Correct conversation status monitoring
    """
    
    def __init__(self):
        self.api_key = settings.elevenlabs_api_key
        self.agent_id = settings.elevenlabs_agent_id
        self.phone_number_id = settings.elevenlabs_phone_number_id
        self.base_url = "https://api.elevenlabs.io"
        
        # Optimized timeouts based on ElevenLabs documentation
        self.request_timeout = 30
        self.status_check_timeout = 15
        self.retry_attempts = 3
        self.retry_delay = 2
        
        self.use_mock = not all([self.api_key, self.agent_id, self.phone_number_id])
        
        if self.use_mock:
            logger.warning("⚠️ ElevenLabs credentials incomplete - using mock calls")
        else:
            logger.info("✅ ElevenLabs service initialized with real API")
    
    async def test_credentials(self) -> Dict[str, Any]:
        """Test ElevenLabs API credentials with proper validation"""
        if self.use_mock:
            return {
                "status": "mock_mode",
                "message": "Using mock mode - no real API calls"
            }
        
        try:
            # Test API connectivity with simple request
            response = requests.get(
                f"{self.base_url}/v1/user",
                headers={"Xi-Api-Key": self.api_key},
                timeout=self.status_check_timeout
            )
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "message": "ElevenLabs API credentials valid",
                    "api_connected": True
                }
            else:
                return {
                    "status": "failed",
                    "message": f"API validation failed: {response.status_code}",
                    "error": response.text[:200]
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Credential test failed: {str(e)}"
            }
    
    async def initiate_negotiation_call(
        self,
        creator_phone: str,
        creator_profile: Dict[str, Any],
        campaign_data: Dict[str, Any],
        pricing_strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        🔥 CORRECTED CALL INITIATION
        
        Key fixes:
        - Proper response validation before returning
        - Better error handling for contract generation
        - Timeout management with retries
        """
        
        if self.use_mock:
            return await self._mock_enhanced_call(creator_phone, creator_profile, campaign_data)
        
        # Retry logic for network issues
        for attempt in range(self.retry_attempts):
            try:
                logger.info(f"📱 Initiating ElevenLabs call (attempt {attempt + 1})")
                
                # Generate dynamic variables
                dynamic_vars = self._generate_dynamic_variables(
                    creator_profile, campaign_data, pricing_strategy
                )
                
                # Make API call with proper error handling
                response = await self._make_outbound_call_request(
                    creator_phone, dynamic_vars
                )
                
                # CRITICAL FIX: Validate response before proceeding
                if response.get("status") == "success":
                    conversation_id = response.get("conversation_id")
                    
                    # Ensure we have conversation_id for contract generation
                    if not conversation_id:
                        raise ValueError("Missing conversation_id in API response")
                    
                    logger.info(f"✅ Call initiated successfully: {conversation_id}")
                    return response
                
                elif attempt < self.retry_attempts - 1:
                    logger.warning(f"⚠️ Call failed, retrying in {self.retry_delay}s...")
                    await asyncio.sleep(self.retry_delay)
                    continue
                else:
                    logger.error(f"❌ All retry attempts failed: {response}")
                    return response
                    
            except Exception as e:
                logger.error(f"❌ Call exception (attempt {attempt + 1}): {e}")
                
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(self.retry_delay)
                    continue
                else:
                    # Return error response for contract generation handling
                    return {
                        "status": "failed",
                        "error": str(e),
                        "phone_number": creator_phone,
                        "retry_attempts": self.retry_attempts
                    }
        
        # Fallback should not reach here
        return {
            "status": "failed",
            "error": "Unknown failure after all retries",
            "phone_number": creator_phone
        }
    
    async def _make_outbound_call_request(
        self,
        phone_number: str,
        dynamic_variables: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make the actual API request with proper validation"""
        
        try:
            # Prepare request payload
            payload = {
                "agent_id": self.agent_id,
                "agent_phone_number_id": self.phone_number_id,
                "to_number": phone_number,
                "conversation_initiation_client_data": {
                    "dynamic_variables": dynamic_variables
                }
            }
            
            # Make request using asyncio for timeout handling
            loop = asyncio.get_event_loop()
            
            def make_request():
                return requests.post(
                    f"{self.base_url}/v1/convai/twilio/outbound-call",
                    headers={"Xi-Api-Key": self.api_key},
                    json=payload,
                    timeout=self.request_timeout
                )
            
            response = await loop.run_in_executor(None, make_request)
            
            # CRITICAL: Proper response validation
            if response.status_code == 200:
                try:
                    result = response.json()
                    
                    # Validate required fields for contract generation
                    if "conversation_id" not in result:
                        logger.error("❌ Missing conversation_id in successful response")
                        return {
                            "status": "failed",
                            "error": "Missing conversation_id in API response",
                            "raw_response": result
                        }
                    
                    return {
                        "status": "success",
                        "conversation_id": result["conversation_id"],
                        "call_id": result.get("call_id"),
                        "phone_number": phone_number,
                        "raw_response": result
                    }
                    
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Invalid JSON response: {e}")
                    return {
                        "status": "failed",
                        "error": f"Invalid JSON response: {e}",
                        "raw_response": response.text
                    }
            else:
                logger.error(f"❌ API error {response.status_code}: {response.text}")
                return {
                    "status": "failed",
                    "error": f"API Error {response.status_code}: {response.text}",
                    "status_code": response.status_code
                }
                
        except requests.exceptions.Timeout:
            return {
                "status": "failed",
                "error": "Request timeout - ElevenLabs API not responding"
            }
        except Exception as e:
            return {
                "status": "failed",
                "error": f"Request failed: {str(e)}"
            }
    
    async def get_conversation_status(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        📡 CORRECTED STATUS MONITORING
        
        Fixes:
        - Proper async handling
        - Better error handling for failed/ended calls
        - Correct status mapping
        """
        
        if self.use_mock or conversation_id.startswith("mock_"):
            return await self._mock_status_check(conversation_id)
        
        try:
            loop = asyncio.get_event_loop()
            
            def make_status_request():
                return requests.get(
                    f"{self.base_url}/v1/convai/conversations/{conversation_id}",
                    headers={"Xi-Api-Key": self.api_key},
                    timeout=self.status_check_timeout
                )
            
            response = await loop.run_in_executor(None, make_status_request)
            
            if response.status_code == 200:
                result = response.json()
                
                # Add monitoring metadata
                result["monitoring_metadata"] = {
                    "fetched_at": datetime.now().isoformat(),
                    "service": "elevenlabs_api"
                }
                
                # Map ElevenLabs status to our expected states
                status = result.get("status", "unknown")
                result["normalized_status"] = self._normalize_conversation_status(status)
                
                return result
            else:
                logger.error(f"❌ Status check failed {response.status_code}: {response.text}")
                return {
                    "status": "error",
                    "normalized_status": "failed",
                    "error": f"API Error {response.status_code}",
                    "conversation_id": conversation_id
                }
                
        except Exception as e:
            logger.error(f"❌ Status check exception: {e}")
            return {
                "status": "error",
                "normalized_status": "failed", 
                "error": str(e),
                "conversation_id": conversation_id
            }
    
    def _normalize_conversation_status(self, elevenlabs_status: str) -> str:
        """Map ElevenLabs status to standard states"""
        status_mapping = {
            "initiated": "in_progress",
            "in-progress": "in_progress", 
            "processing": "in_progress",
            "done": "completed",
            "completed": "completed",
            "failed": "failed",
            "error": "failed",
            "timeout": "failed"
        }
        return status_mapping.get(elevenlabs_status.lower(), "unknown")
    
    async def wait_for_conversation_completion_with_analysis(
        self,
        conversation_id: str,
        max_wait_seconds: int = 300
    ) -> Dict[str, Any]:
        """
        🔄 CORRECTED CONVERSATION WAITING
        
        Fixes:
        - Proper completion detection
        - Better timeout handling
        - Analysis data extraction
        """
        
        if self.use_mock or conversation_id.startswith("mock_"):
            return await self._mock_conversation_completion(conversation_id)
        
        start_time = datetime.now()
        poll_interval = 10  # Poll every 10 seconds
        
        logger.info(f"🔄 Waiting for conversation completion: {conversation_id}")
        
        while (datetime.now() - start_time).total_seconds() < max_wait_seconds:
            try:
                status_data = await self.get_conversation_status(conversation_id)
                
                if not status_data:
                    logger.warning("⚠️ No status data received, continuing to poll...")
                    await asyncio.sleep(poll_interval)
                    continue
                
                normalized_status = status_data.get("normalized_status", "unknown")
                
                if normalized_status == "completed":
                    logger.info("✅ Conversation completed successfully")
                    
                    # Extract analysis data
                    analysis_data = self._extract_analysis_data(status_data)
                    
                    return {
                        "status": "completed",
                        "conversation_data": status_data,
                        "analysis_data": analysis_data,
                        "completion_time": datetime.now().isoformat()
                    }
                
                elif normalized_status == "failed":
                    logger.error("❌ Conversation failed")
                    return {
                        "status": "failed",
                        "conversation_data": status_data,
                        "error": status_data.get("error", "Conversation failed"),
                        "failure_time": datetime.now().isoformat()
                    }
                
                # Still in progress, continue polling
                logger.info(f"📞 Conversation in progress: {normalized_status}")
                await asyncio.sleep(poll_interval)
                
            except Exception as e:
                logger.error(f"❌ Error during conversation monitoring: {e}")
                await asyncio.sleep(poll_interval)
        
        # Timeout reached
        logger.warning(f"⏰ Conversation timeout after {max_wait_seconds}s")
        return {
            "status": "timeout",
            "error": f"Conversation did not complete within {max_wait_seconds} seconds",
            "conversation_id": conversation_id
        }
    
    def _extract_analysis_data(self, conversation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured analysis from conversation data"""
        
        # Default analysis structure
        analysis = {
            "negotiation_outcome": "unknown",
            "agreed_rate": None,
            "conversation_sentiment": "neutral",
            "key_points": [],
            "next_steps": []
        }
        
        # Extract from transcript if available
        transcript = conversation_data.get("transcript", [])
        if transcript:
            analysis["transcript_length"] = len(transcript)
            analysis["key_points"] = self._extract_key_points(transcript)
        
        # Extract from ElevenLabs analysis if present
        if "analysis" in conversation_data:
            elevenlabs_analysis = conversation_data["analysis"]
            
            # Map ElevenLabs analysis to our structure
            analysis.update({
                "negotiation_outcome": elevenlabs_analysis.get("outcome", "unknown"),
                "agreed_rate": elevenlabs_analysis.get("agreed_price"),
                "conversation_sentiment": elevenlabs_analysis.get("sentiment", "neutral")
            })
        
        return analysis
    
    def _extract_key_points(self, transcript: List[Dict[str, Any]]) -> List[str]:
        """Extract key conversation points from transcript"""
        key_points = []
        
        for entry in transcript:
            text = entry.get("text", "").lower()
            
            # Look for pricing mentions
            if any(word in text for word in ["$", "price", "rate", "cost", "budget"]):
                key_points.append(f"Pricing discussed: {entry.get('text', '')[:100]}")
            
            # Look for agreement indicators
            if any(word in text for word in ["agree", "yes", "deal", "accept"]):
                key_points.append(f"Agreement indicated: {entry.get('text', '')[:100]}")
            
            # Look for objections
            if any(word in text for word in ["no", "can't", "unable", "too"]):
                key_points.append(f"Objection raised: {entry.get('text', '')[:100]}")
        
        return key_points[:5]  # Return top 5 key points
    
    def _generate_dynamic_variables(
        self,
        creator_profile: Dict[str, Any],
        campaign_data: Dict[str, Any],
        pricing_strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate dynamic variables for ElevenLabs agent"""
        
        return {
            "influencerName": creator_profile.get("name", "Creator"),
            "influencerNiche": creator_profile.get("niche", "lifestyle"),
            "followerCount": creator_profile.get("followers", 0),
            "engagementRate": creator_profile.get("engagement_rate", 0.0),
            "campaignBrief": campaign_data.get("product_description", ""),
            "brandName": campaign_data.get("brand_name", ""),
            "productName": campaign_data.get("product_name", ""),
            "targetAudience": campaign_data.get("target_audience", ""),
            "initialOffer": pricing_strategy.get("initial_offer", 1000),
            "maxBudget": pricing_strategy.get("max_offer", 2000),
            "negotiationStyle": pricing_strategy.get("style", "collaborative")
        }
    
    # Mock methods for testing
    async def _mock_enhanced_call(
        self,
        creator_phone: str,
        creator_profile: Dict[str, Any],
        campaign_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Mock call for testing"""
        await asyncio.sleep(1)  # Simulate API delay
        
        mock_conversation_id = f"mock_conv_{random.randint(1000, 9999)}"
        
        return {
            "status": "success",
            "conversation_id": mock_conversation_id,
            "call_id": f"mock_call_{random.randint(1000, 9999)}",
            "phone_number": creator_phone,
            "mock": True
        }
    
    async def _mock_status_check(self, conversation_id: str) -> Dict[str, Any]:
        """Mock status check"""
        await asyncio.sleep(0.5)
        
        return {
            "status": "completed",
            "normalized_status": "completed",
            "conversation_id": conversation_id,
            "transcript": [
                {"role": "agent", "text": "Hello! I'd like to discuss a collaboration opportunity."},
                {"role": "user", "text": "Sure, I'm interested. What's the offer?"},
                {"role": "agent", "text": "We can offer $1,500 for a sponsored post."},
                {"role": "user", "text": "That sounds good, I accept!"}
            ],
            "analysis": {
                "outcome": "accepted",
                "agreed_price": 1500,
                "sentiment": "positive"
            },
            "mock": True
        }
    
    async def _mock_conversation_completion(self, conversation_id: str) -> Dict[str, Any]:
        """Mock conversation completion"""
        await asyncio.sleep(2)  # Simulate conversation time
        
        status_data = await self._mock_status_check(conversation_id)
        analysis_data = self._extract_analysis_data(status_data)
        
        return {
            "status": "completed",
            "conversation_data": status_data,
            "analysis_data": analysis_data,
            "completion_time": datetime.now().isoformat(),
            "mock": True
        }