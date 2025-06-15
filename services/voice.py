# services/voice.py - CORRECTED UNIFIED VOICE SERVICE
import asyncio
import logging
import httpx
import json
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

from core.models import Creator, CampaignData
from core.config import settings

logger = logging.getLogger(__name__)


class CallStatus(str, Enum):
    """Standard call status enumeration"""
    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class VoiceService:
    """
    🎙️ Clean Voice Service Implementation
    
    Fixed ElevenLabs integration with proper endpoint and OOP design:
    - Correct API endpoint usage
    - Clean class structure without unnecessary helpers
    - Maintainable modular approach
    - No legacy code retention
    """
    
    def __init__(self):
        """Initialize voice service with proper configuration"""
        self.api_key = settings.elevenlabs_api_key
        self.agent_id = settings.elevenlabs_agent_id
        self.phone_number_id = settings.elevenlabs_phone_number_id
        self.use_mock = settings.use_mock_services
        
        # ElevenLabs API configuration
        self.base_url = "https://api.elevenlabs.io"
        self.timeout = 30.0
        
        # HTTP client configuration
        self._configure_client()
        
        logger.info(f"🎙️ Voice Service initialized (mock: {self.use_mock})")
    
    def _configure_client(self) -> None:
        """Configure HTTP client with proper headers"""
        headers = {
            "Xi-Api-Key": self.api_key or "mock-key",
            "Content-Type": "application/json"
        }
        
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            headers=headers
        )
    
    async def initiate_call(
        self,
        creator: Creator,
        campaign_data: CampaignData,
        dynamic_variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Initiate voice call to creator
        
        Args:
            creator: Creator to contact
            campaign_data: Campaign information
            dynamic_variables: Additional context for AI agent
            
        Returns:
            Call result with conversation_id and status
        """
        
        if self.use_mock:
            return self._create_mock_response(creator, campaign_data)
        
        try:
            # Prepare call payload
            payload = self._build_call_payload(creator, campaign_data, dynamic_variables)
            
            # Make API call to correct ElevenLabs endpoint
            response = await self._make_api_call(payload)
            
            # Process and validate response
            return self._process_response(response, creator)
            
        except Exception as e:
            logger.error(f"❌ Call initiation failed for {creator.name}: {e}")
            return {
                "status": CallStatus.FAILED,
                "error": str(e),
                "creator_id": creator.id
            }
    
    def _build_call_payload(
        self,
        creator: Creator,
        campaign_data: CampaignData,
        dynamic_variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Build API payload for ElevenLabs call"""
        
        # Base payload structure
        payload = {
            "agent_id": self.agent_id,
            "from": self.phone_number_id,
            "to": creator.phone_number,
            "max_duration": 300  # 5 minutes max
        }
        
        # Prepare dynamic variables for AI agent
        variables = self._prepare_dynamic_variables(creator, campaign_data, dynamic_variables)
        if variables:
            payload["dynamic_variables"] = variables
        
        return payload
    
    def _prepare_dynamic_variables(
        self,
        creator: Creator,
        campaign_data: CampaignData,
        additional_variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Prepare context variables for AI agent"""
        
        variables = {
            "influencerName": creator.name,
            "influencerNiche": creator.niche,
            "influencerFollowers": creator.follower_count,
            "brandName": campaign_data.brand_name,
            "productName": campaign_data.product_name,
            "productDescription": campaign_data.product_description,
            "targetAudience": campaign_data.target_audience,
            "campaignGoal": campaign_data.campaign_goal,
            "suggestedRate": creator.rate_per_post,
            "timeline": "4-6 weeks",
            "deliverables": "video review, social posts"
        }
        
        # Add any additional variables
        if additional_variables:
            variables.update(additional_variables)
        
        return variables
    
    async def _make_api_call(self, payload: Dict[str, Any]) -> httpx.Response:
        """Make HTTP request to ElevenLabs API"""
        
        # Use the CORRECT ElevenLabs endpoint
        url = f"{self.base_url}/v1/convai/twilio/outbound-call"
        
        logger.info(f"📞 Making real ElevenLabs call to {payload.get('to')}")
        logger.info(f"🔧 Using agent_id: {self.agent_id}")
        
        response = await self.client.post(url, json=payload)
        return response
    
    def _process_response(
        self,
        response: httpx.Response,
        creator: Creator
    ) -> Dict[str, Any]:
        """Process ElevenLabs API response"""
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                # Validate response has required fields
                if "conversation_id" not in data:
                    logger.error("❌ Missing conversation_id in API response")
                    return {
                        "status": CallStatus.FAILED,
                        "error": "Missing conversation_id in response",
                        "creator_id": creator.id
                    }
                
                logger.info(f"✅ Call initiated successfully: {data['conversation_id']}")
                
                return {
                    "status": CallStatus.INITIATED,
                    "conversation_id": data["conversation_id"],
                    "call_id": data.get("call_id"),
                    "creator_id": creator.id,
                    "phone_number": creator.phone_number,
                    "started_at": datetime.now().isoformat()
                }
                
            except json.JSONDecodeError as e:
                logger.error(f"❌ Invalid JSON response: {e}")
                return {
                    "status": CallStatus.FAILED,
                    "error": f"Invalid JSON response: {e}",
                    "creator_id": creator.id
                }
        else:
            logger.error(f"❌ API error {response.status_code}: {response.text}")
            return {
                "status": CallStatus.FAILED,
                "error": f"API Error {response.status_code}: {response.text}",
                "creator_id": creator.id,
                "status_code": response.status_code
            }
    
    def _create_mock_response(
        self,
        creator: Creator,
        campaign_data: CampaignData
    ) -> Dict[str, Any]:
        """Create mock response for development/testing"""
        
        conversation_id = f"mock-{creator.id}-{int(datetime.now().timestamp())}"
        
        logger.info(f"🎭 Mock call initiated for {creator.name}")
        
        return {
            "status": CallStatus.INITIATED,
            "conversation_id": conversation_id,
            "creator_id": creator.id,
            "phone_number": creator.phone_number or "+1-555-MOCK",
            "started_at": datetime.now().isoformat(),
            "mock": True
        }
    
    async def check_call_status(self, conversation_id: str) -> Dict[str, Any]:
        """
        Check status of ongoing call
        
        Args:
            conversation_id: ElevenLabs conversation ID
            
        Returns:
            Current call status and any available results
        """
        
        if self.use_mock:
            return self._create_mock_status(conversation_id)
        
        try:
            url = f"{self.base_url}/v1/convai/conversations/{conversation_id}"
            response = await self.client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                return self._extract_call_results(data)
            else:
                logger.error(f"❌ Status check failed: {response.status_code}")
                return {
                    "status": CallStatus.FAILED,
                    "error": f"Status check failed: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"❌ Status check error: {e}")
            return {
                "status": CallStatus.FAILED,
                "error": str(e)
            }
    
    def _extract_call_results(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract meaningful results from ElevenLabs conversation data"""
        
        # Get basic call information
        status = data.get("status", "unknown")
        analysis = data.get("analysis", {})
        
        # Extract negotiation results if available
        data_collection = analysis.get("data_collection_results", {})
        
        result = {
            "status": self._map_elevenlabs_status(status),
            "conversation_id": data.get("id"),
            "raw_status": status
        }
        
        # Add negotiation results if call completed successfully
        if status == "done" and data_collection:
            result.update({
                "final_rate": data_collection.get("final_rate_mentioned", {}).get("value"),
                "timeline": data_collection.get("timeline_mentioned", {}).get("value"),
                "deliverables": data_collection.get("deliverables_discussed", {}).get("value"),
                "call_successful": analysis.get("call_successful") == "success"
            })
        
        return result
    
    def _map_elevenlabs_status(self, status: str) -> CallStatus:
        """Map ElevenLabs status to our standard status enum"""
        mapping = {
            "initiated": CallStatus.INITIATED,
            "in-progress": CallStatus.IN_PROGRESS,
            "processing": CallStatus.IN_PROGRESS,
            "done": CallStatus.COMPLETED,
            "completed": CallStatus.COMPLETED,
            "failed": CallStatus.FAILED,
            "error": CallStatus.FAILED,
            "timeout": CallStatus.TIMEOUT
        }
        return mapping.get(status, CallStatus.FAILED)
    
    def _create_mock_status(self, conversation_id: str) -> Dict[str, Any]:
        """Create mock status response for development"""
        
        # Simulate completed call with successful negotiation
        return {
            "status": CallStatus.COMPLETED,
            "conversation_id": conversation_id,
            "final_rate": 800.0,
            "timeline": "4 weeks",
            "deliverables": "video_review,instagram_story",
            "call_successful": True,
            "mock": True
        }
    
    async def close(self) -> None:
        """Clean up HTTP client"""
        if hasattr(self, 'client'):
            await self.client.aclose()