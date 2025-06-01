# services/voice.py - REAL ELEVENLABS INTEGRATION
import asyncio
import logging
import requests
from typing import Dict, Any, Optional
from datetime import datetime

from config.settings import settings
logger = logging.getLogger(__name__)

class VoiceService:
    """
    🎯 REAL ELEVENLABS CONVERSATIONAL AI INTEGRATION
    Using your exact sample code format for outbound calls
    """
    
    def __init__(self):
        # ✅ Load credentials from settings
        self.api_key = settings.elevenlabs_api_key
        self.agent_id = settings.elevenlabs_agent_id
        self.phone_number_id = settings.elevenlabs_phone_number_id
        self.base_url = "https://api.elevenlabs.io"
        
        # Check credentials and decide whether to use mock
        self.use_mock = not all([self.api_key, self.agent_id, self.phone_number_id])
        
        # Debug credential status
        self._debug_credentials()
    
    def _debug_credentials(self):
        """🔍 Debug credential status"""
        logger.info("🔍 ElevenLabs Credential Status:")
        logger.info(f"   API Key: {'✅ Set' if self.api_key else '❌ Missing'}")
        logger.info(f"   Agent ID: {'✅ Set' if self.agent_id else '❌ Missing'}")
        logger.info(f"   Phone Number ID: {'✅ Set' if self.phone_number_id else '❌ Missing'}")
        
        if self.use_mock:
            logger.warning("⚠️  ElevenLabs credentials incomplete - using mock calls")
            logger.info("📋 To enable real calls, add to your .env file:")
            logger.info("   ELEVENLABS_API_KEY=sk_your_key_here")
            logger.info("   ELEVENLABS_AGENT_ID=your_agent_id_here") 
            logger.info("   ELEVENLABS_PHONE_NUMBER_ID=your_phone_id_here")
        else:
            logger.info("✅ ElevenLabs service initialized with real API")
    
    async def initiate_negotiation_call(
        self,
        creator_phone: str,
        creator_profile: Dict[str, Any],
        campaign_brief: str,
        price_range: str
    ) -> Dict[str, Any]:
        """
        🔥 REAL ELEVENLABS OUTBOUND CALL - Using your exact sample code format
        """
        
        if self.use_mock:
            return await self._mock_call(creator_phone, creator_profile)
        
        try:
            # Format creator profile exactly like your sample
            influencer_profile = self._format_influencer_profile(creator_profile)
            
            logger.info(f"📱 Initiating REAL ElevenLabs call to {creator_phone}")
            logger.info(f"🎯 Agent ID: {self.agent_id}")
            logger.info(f"📞 Phone Number ID: {self.phone_number_id}")
            
            # 🎯 YOUR EXACT ELEVENLABS SAMPLE CODE (with dynamic data)
            response = requests.post(
                f"{self.base_url}/v1/convai/twilio/outbound-call",
                headers={
                    "Xi-Api-Key": self.api_key
                },
                json={
                    "agent_id": self.agent_id,
                    "agent_phone_number_id": self.phone_number_id,
                    "to_number": creator_phone,
                    "conversation_initiation_client_data": {
                        "dynamic_variables": {
                            "InfluencerProfile": influencer_profile,
                            "campaignBrief": campaign_brief,
                            "PriceRange": price_range,
                            "influencerName": creator_profile.get("name", "Creator")
                        }
                    }
                }
            )
            
            logger.info(f"📡 ElevenLabs API Response: {response.status_code}")
            
            # Handle response
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ ElevenLabs call initiated successfully!")
                logger.info(f"   Conversation ID: {result.get('conversation_id')}")
                logger.info(f"   Call ID: {result.get('call_id')}")
                
                return {
                    "status": "success",
                    "conversation_id": result.get("conversation_id"),
                    "call_id": result.get("call_id"),
                    "phone_number": creator_phone,
                    "raw_response": result
                }
            else:
                logger.error(f"❌ ElevenLabs call failed: {response.status_code}")
                logger.error(f"   Response: {response.text}")
                return {
                    "status": "failed",
                    "error": f"API Error {response.status_code}: {response.text}",
                    "phone_number": creator_phone
                }
                
        except Exception as e:
            logger.error(f"❌ ElevenLabs call exception: {e}")
            return {
                "status": "failed", 
                "error": str(e),
                "phone_number": creator_phone
            }
    
    async def get_conversation_status(self, conversation_id: str) -> Dict[str, Any]:
        """
        📞 Get conversation status using ElevenLabs API
        """
        if self.use_mock:
            return {"status": "completed", "transcript": "Mock conversation completed"}
        
        try:
            response = requests.get(
                f"{self.base_url}/v1/convai/conversations/{conversation_id}",
                headers={"Xi-Api-Key": self.api_key}
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"📞 Conversation status: {result.get('status', 'unknown')}")
                return result
            else:
                logger.error(f"❌ Status check failed: {response.status_code}")
                return {"status": "error", "message": response.text}
                
        except Exception as e:
            logger.error(f"❌ Status check exception: {e}")
            return {"status": "error", "message": str(e)}
    
    async def wait_for_conversation_completion(
        self, 
        conversation_id: str, 
        max_wait_seconds: int = 120,
        poll_interval: int = 5
    ) -> Dict[str, Any]:
        """
        ⏳ Wait for conversation to complete with polling
        """
        start_time = asyncio.get_event_loop().time()
        
        while (asyncio.get_event_loop().time() - start_time) < max_wait_seconds:
            status_result = await self.get_conversation_status(conversation_id)
            
            conversation_status = status_result.get("status", "unknown")
            
            # Check if conversation is complete
            if conversation_status in ["completed", "ended", "failed"]:
                logger.info(f"📞 Conversation completed with status: {conversation_status}")
                return status_result
            
            # Wait before next poll
            await asyncio.sleep(poll_interval)
            logger.debug(f"📞 Conversation status: {conversation_status} - continuing to wait...")
        
        # Timeout
        logger.warning(f"⏰ Conversation timeout after {max_wait_seconds} seconds")
        return {"status": "timeout", "message": "Conversation did not complete within timeout"}
    
    def _format_influencer_profile(self, creator_profile: Dict[str, Any]) -> str:
        """
        📝 Format creator profile exactly like your sample:
        "name:Abhiram, channel: olivia_rodriguez519, niche: Fitness, about: Certified personal trainer..."
        """
        
        # Extract data with defaults
        name = creator_profile.get("name", "Unknown")
        channel = creator_profile.get("id", creator_profile.get("channel", "unknown_channel"))
        niche = creator_profile.get("niche", "General")
        about = creator_profile.get("about", f"Content creator specializing in {niche}")
        followers = creator_profile.get("followers", 0)
        audience_type = creator_profile.get("audience_type", f"{niche.title()} Enthusiasts")
        engagement = creator_profile.get("engagement_rate", 0)
        avg_views = creator_profile.get("average_views", 0)
        location = creator_profile.get("location", "Unknown")
        languages = creator_profile.get("languages", ["English"])
        collaboration_rate = creator_profile.get("typical_rate", 0)
        
        # Format exactly like your sample
        formatted_profile = (
            f"name:{name}, "
            f"channel: {channel}, "
            f"niche: {niche}, "
            f"about: {about}, "
            f"followers: {followers//1000}K, "
            f"audienceType: {audience_type}, "
            f"engagement:{engagement}%, "
            f"avgViews: {avg_views//1000}K, "
            f"location: {location}, "
            f"languages:{', '.join(languages) if isinstance(languages, list) else languages}, "
            f"collaboration_rate: {collaboration_rate}"
        )
        
        return formatted_profile
    
    async def test_credentials(self) -> Dict[str, Any]:
        """
        🧪 Test ElevenLabs credentials and setup
        """
        if self.use_mock:
            return {
                "status": "mock_mode",
                "message": "ElevenLabs credentials not configured - using mock mode",
                "missing": [
                    field for field, value in [
                        ("api_key", self.api_key),
                        ("agent_id", self.agent_id), 
                        ("phone_number_id", self.phone_number_id)
                    ] if not value
                ]
            }
        
        try:
            # Test API key by getting account info
            response = requests.get(
                f"{self.base_url}/v1/user",
                headers={"Xi-Api-Key": self.api_key}
            )
            
            if response.status_code == 200:
                user_info = response.json()
                return {
                    "status": "success",
                    "message": "ElevenLabs credentials verified",
                    "user": user_info.get("email", "Unknown"),
                    "agent_id": self.agent_id,
                    "phone_number_id": self.phone_number_id
                }
            else:
                return {
                    "status": "failed",
                    "message": f"API key validation failed: {response.status_code}",
                    "error": response.text
                }
                
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Credential test failed: {str(e)}"
            }
    
    async def _mock_call(self, phone: str, creator_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        🎭 Mock call for testing without API credentials
        """
        import random
        
        logger.info(f"🎭 Mock call to {phone} for {creator_profile.get('name', 'Unknown')}")
        
        # Simulate call duration
        await asyncio.sleep(2)
        
        # Random success/failure for realistic demo
        success = random.choice([True, True, False])  # 66% success rate
        
        mock_conversation_id = f"mock_conv_{creator_profile.get('id', 'unknown')}"
        
        if success:
            # Mock successful negotiation
            final_rate = creator_profile.get("typical_rate", 3000) * random.uniform(0.9, 1.1)
            
            return {
                "status": "success", 
                "conversation_id": mock_conversation_id,
                "call_id": f"mock_call_{phone[-4:]}",
                "phone_number": phone,
                "mock_result": {
                    "negotiation_outcome": "accepted",
                    "final_rate": round(final_rate, 2),
                    "conversation_summary": f"Creator {creator_profile.get('name')} accepted the collaboration"
                }
            }
        else:
            # Mock failed negotiation
            failure_reasons = [
                "Rate too low - requested higher compensation",
                "Timeline too tight - creator unavailable", 
                "Brand misalignment - prefers different product categories",
                "Already committed to competing brand"
            ]
            
            return {
                "status": "failed",
                "conversation_id": mock_conversation_id,
                "call_id": f"mock_call_{phone[-4:]}",
                "phone_number": phone,
                "mock_result": {
                    "negotiation_outcome": "declined",
                    "failure_reason": random.choice(failure_reasons)
                }
            }
    
    async def conduct_conversation(
        self,
        call_session: Dict[str, Any],
        opening_script: str,
        max_duration: int = 60
    ) -> Dict[str, Any]:
        """
        🎯 Legacy method for compatibility with existing code
        Now uses ElevenLabs conversation management
        """
        conversation_id = call_session.get("conversation_id")
        
        if not conversation_id:
            return {"status": "failed", "error": "No conversation ID provided"}
        
        if call_session.get("status") == "success":
            # Wait for real conversation to complete
            result = await self.wait_for_conversation_completion(
                conversation_id, 
                max_wait_seconds=max_duration
            )
            
            return {
                "status": "completed",
                "duration": max_duration,
                "transcript": result.get("transcript", "Conversation completed"),
                "recording_url": result.get("recording_url"),
                "conversation_data": result
            }
        else:
            # Mock conversation for failed calls
            await asyncio.sleep(min(max_duration, 10))
            return {
                "status": "failed",
                "duration": 10,
                "transcript": "Call failed to connect",
                "error": call_session.get("error", "Unknown error")
            }