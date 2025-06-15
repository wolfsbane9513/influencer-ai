# services/voice.py - UNIFIED VOICE SERVICE
import asyncio
import logging
import json
import httpx
from typing import Dict, Any, Optional
from datetime import datetime

from core.models import Creator, CampaignData, CallStatus
from core.config import settings

logger = logging.getLogger(__name__)

class VoiceService:
    """
    🎙️ Unified Voice Service
    
    Single implementation for ElevenLabs integration with:
    - Dynamic variable support
    - Conversation monitoring
    - Error handling and retries
    - Mock mode for development
    """
    
    def __init__(self):
        self.api_key = settings.elevenlabs_api_key
        self.agent_id = settings.elevenlabs_agent_id
        self.phone_number_id = settings.elevenlabs_phone_number_id
        self.use_mock = settings.use_mock_services
        self.base_url = "https://api.elevenlabs.io/v1"
        
        # HTTP client for API calls
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "xi-api-key": self.api_key or "mock-key",
                "Content-Type": "application/json"
            }
        )
        
        logger.info(f"🎙️ Voice Service initialized (mock: {self.use_mock})")
    
    async def initiate_call(
        self,
        creator: Creator,
        campaign_data: CampaignData,
        dynamic_variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Initiate voice call with creator
        
        Args:
            creator: Creator to call
            campaign_data: Campaign information
            dynamic_variables: Additional variables to pass to AI agent
            
        Returns:
            Dict containing call information and conversation ID
        """
        
        if self.use_mock:
            return await self._mock_call(creator, campaign_data)
        
        try:
            # Prepare dynamic variables for the call
            call_variables = self._prepare_call_variables(creator, campaign_data, dynamic_variables)
            
            # Prepare call data
            call_data = {
                "agent_id": self.agent_id,
                "phone_number_id": self.phone_number_id,
                "to": creator.phone_number,
                "dynamic_variables": call_variables
            }
            
            logger.info(f"📞 Initiating call to {creator.name} ({creator.phone_number})")
            
            # Make API call to ElevenLabs
            response = await self._make_api_call("/conversations", call_data, method="POST")
            
            conversation_id = response.get("conversation_id")
            logger.info(f"📞 Call initiated for {creator.name}: {conversation_id}")
            
            return {
                "conversation_id": conversation_id,
                "status": "initiated",
                "creator_id": creator.id,
                "started_at": datetime.now().isoformat(),
                "phone_number": creator.phone_number
            }
            
        except Exception as e:
            logger.error(f"❌ Call initiation failed for {creator.name}: {e}")
            raise
    
    async def get_call_status(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get call status and results
        
        Args:
            conversation_id: ID of the conversation to check
            
        Returns:
            Dict containing call status, transcript, and analysis
        """
        
        if self.use_mock:
            return await self._mock_call_status(conversation_id)
        
        try:
            response = await self._make_api_call(f"/conversations/{conversation_id}")
            
            # Extract call status
            call_status = response.get("status", "unknown")
            
            # Get transcript if call is completed
            transcript = ""
            if call_status == "completed":
                transcript = response.get("transcript", "")
            
            # Get analysis if available
            analysis = response.get("analysis", {})
            
            return {
                "conversation_id": conversation_id,
                "status": call_status,
                "duration_seconds": response.get("duration_seconds", 0),
                "transcript": transcript,
                "recording_url": response.get("recording_url"),
                "analysis": analysis,
                "updated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get call status for {conversation_id}: {e}")
            raise
    
    async def wait_for_call_completion(
        self, 
        conversation_id: str, 
        timeout_seconds: int = 300,
        poll_interval: int = 10
    ) -> Dict[str, Any]:
        """
        Wait for call to complete with polling
        
        Args:
            conversation_id: ID of the conversation
            timeout_seconds: Maximum time to wait
            poll_interval: How often to check status
            
        Returns:
            Final call status and results
        """
        
        start_time = datetime.now()
        
        while True:
            try:
                status = await self.get_call_status(conversation_id)
                
                call_status = status.get("status")
                
                # Check if call is complete
                if call_status in ["completed", "failed", "no_answer"]:
                    logger.info(f"📞 Call {conversation_id} finished with status: {call_status}")
                    return status
                
                # Check timeout
                elapsed = (datetime.now() - start_time).total_seconds()
                if elapsed > timeout_seconds:
                    logger.warning(f"⏰ Call {conversation_id} timed out after {elapsed:.1f}s")
                    return {
                        "conversation_id": conversation_id,
                        "status": "timeout",
                        "error": f"Call timed out after {timeout_seconds} seconds"
                    }
                
                # Wait before next poll
                await asyncio.sleep(poll_interval)
                
            except Exception as e:
                logger.error(f"❌ Error polling call status: {e}")
                # Continue polling unless it's a critical error
                await asyncio.sleep(poll_interval)
    
    def _prepare_call_variables(
        self, 
        creator: Creator, 
        campaign_data: CampaignData,
        additional_variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Prepare dynamic variables for the AI agent
        
        Args:
            creator: Creator information
            campaign_data: Campaign details
            additional_variables: Extra variables to include
            
        Returns:
            Dict of variables to pass to the AI agent
        """
        
        variables = {
            # Creator information
            "creator_name": creator.name,
            "creator_handle": creator.handle,
            "creator_followers": creator.followers,
            "creator_engagement_rate": creator.engagement_rate,
            "creator_current_rate": creator.rate_per_post,
            
            # Campaign information
            "brand_name": campaign_data.brand_name,
            "product_name": campaign_data.product_name,
            "product_description": campaign_data.product_description,
            "target_audience": campaign_data.target_audience,
            "campaign_goal": campaign_data.campaign_goal,
            "product_niche": campaign_data.product_niche,
            "total_budget": campaign_data.total_budget,
            "max_budget_per_creator": campaign_data.get_budget_per_creator(),
            
            # Negotiation parameters
            "preferred_timeline_days": campaign_data.timeline_days,
            "content_requirements": ", ".join(campaign_data.content_requirements),
            
            # System variables
            "call_initiated_at": datetime.now().isoformat(),
            "campaign_code": campaign_data.campaign_code or campaign_data.generate_campaign_code()
        }
        
        # Add any additional variables
        if additional_variables:
            variables.update(additional_variables)
        
        return variables
    
    async def _make_api_call(
        self, 
        endpoint: str, 
        data: Optional[Dict] = None,
        method: str = "GET"
    ) -> Dict[str, Any]:
        """
        Make HTTP request to ElevenLabs API
        
        Args:
            endpoint: API endpoint (with leading slash)
            data: Request data for POST requests
            method: HTTP method
            
        Returns:
            API response as dictionary
        """
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "POST":
                response = await self.client.post(url, json=data)
            else:
                response = await self.client.get(url)
            
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ API request failed: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"❌ API request error: {e}")
            raise
    
    async def _mock_call(self, creator: Creator, campaign_data: CampaignData) -> Dict[str, Any]:
        """
        Mock call implementation for testing
        
        Simulates a real call with realistic data for development
        """
        conversation_id = f"mock-{creator.id}-{campaign_data.id}-{int(datetime.now().timestamp())}"
        
        logger.info(f"🎭 Mock call initiated for {creator.name}")
        
        return {
            "conversation_id": conversation_id,
            "status": "initiated",
            "creator_id": creator.id,
            "started_at": datetime.now().isoformat(),
            "phone_number": creator.phone_number or "+1-555-MOCK",
            "mock": True
        }
    
    async def _mock_call_status(self, conversation_id: str) -> Dict[str, Any]:
        """
        Mock call status for testing
        
        Simulates realistic call outcomes with various scenarios
        """
        
        # Simulate different outcomes based on conversation ID
        if "fail" in conversation_id:
            outcome = "failed"
            agreed_rate = None
            sentiment = -0.5
        elif "timeout" in conversation_id:
            outcome = "no_answer"
            agreed_rate = None
            sentiment = 0.0
        else:
            outcome = "success"
            # Simulate negotiated rate (usually 10-20% lower than original)
            import random
            discount = random.uniform(0.1, 0.25)
            base_rate = 500.0  # Mock base rate
            agreed_rate = base_rate * (1 - discount)
            sentiment = random.uniform(0.3, 0.9)
        
        return {
            "conversation_id": conversation_id,
            "status": "completed",
            "duration_seconds": 180 + int(conversation_id.split('-')[-1]) % 300,  # 3-8 minutes
            "transcript": self._generate_mock_transcript(outcome),
            "recording_url": f"https://mock-recordings.com/{conversation_id}.mp3",
            "analysis": {
                "outcome": outcome,
                "agreed_rate": agreed_rate,
                "sentiment": sentiment,
                "key_points": [
                    "Interested in the campaign concept",
                    "Requested more details about timeline",
                    "Negotiated on pricing and deliverables"
                ],
                "concerns": [
                    "Timeline might be tight",
                    "Need approval for content style"
                ] if outcome == "success" else ["Not interested in this type of campaign"],
                "decision_factors": [
                    "Brand alignment",
                    "Fair compensation",
                    "Creative freedom"
                ]
            },
            "updated_at": datetime.now().isoformat(),
            "mock": True
        }
    
    def _generate_mock_transcript(self, outcome: str) -> str:
        """Generate realistic mock transcript based on outcome"""
        
        if outcome == "success":
            return """
AI Agent: Hi! This is Alex calling on behalf of HydroTech about a potential collaboration for their new smart water bottle campaign.

Creator: Oh hi! Yes, I got your email about this. I'm definitely interested in learning more.

AI Agent: Great! So we're looking for fitness influencers to showcase our IoT-enabled water bottle that tracks hydration. Your content style would be perfect for our health-conscious millennial audience.

Creator: That sounds really cool! What kind of content are you thinking and what's the timeline?

AI Agent: We'd love 2-3 Instagram posts and 1-2 stories over the next 30 days. We were thinking around $400 per post initially.

Creator: I appreciate the offer, but my usual rate is $500 per post. Could we meet somewhere in the middle? Maybe $450 per post?

AI Agent: Let me see what I can do... I think we could work with $450 per post. That would be $1,350 total for 3 posts. Does that work for you?

Creator: Perfect! That sounds fair. I'm excited to work with HydroTech. When can we get started?

AI Agent: Excellent! I'll send over the contract details today and we can kick off next week. Thank you so much!

Creator: Thank you! Looking forward to it.
            """.strip()
        
        elif outcome == "failed":
            return """
AI Agent: Hi! This is Alex calling on behalf of HydroTech about a potential collaboration.

Creator: Hi there. Actually, I'm not really interested in fitness or tech products right now. I'm focusing more on fashion content.

AI Agent: I understand. We think your audience might still be interested in our health-focused product.

Creator: I appreciate the offer, but it's really not a good fit for my brand right now. Thanks for thinking of me though.

AI Agent: No problem at all. Thank you for your time and have a great day!
            """.strip()
        
        else:  # no_answer or timeout
            return "Call went to voicemail - no transcript available."
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()