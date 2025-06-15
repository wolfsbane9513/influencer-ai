# services/voice.py - FIXED WITH CAMPAIGN-SPECIFIC CONTEXT
import asyncio
import logging
import httpx
import json
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

from core.models import Creator, CampaignData
from core.config import settings

logger = logging.getLogger(__name__)


class CallStatus(str, Enum):
    """Standard call status enumeration"""
    NOT_STARTED = "not_started"
    CONNECTING = "connecting"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class VoiceService:
    """
    🎙️ Fixed Voice Service with Campaign-Specific Context
    
    Key Fix: The AI agent now knows exactly what campaign it's representing
    and behaves as a brand representative, not a generic assistant.
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
        
        # Configure HTTP client
        self._configure_client()
        
        logger.info(f"🎙️ Voice Service initialized (mock: {self.use_mock})")
    
    def _configure_client(self) -> None:
        """Configure HTTP client with proper headers"""
        headers = {
            "Xi-Api-Key": self.api_key or "mock-key",
            "Content-Type": "application/json",
            "Accept": "application/json"
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
        Initiate campaign-specific voice call with proper context
        
        FIXED: Now passes complete campaign context so AI knows:
        - What brand it represents (TestTech Solutions)
        - What product to pitch (E2E TestPro Device)
        - What terms to negotiate
        - Who the influencer is and why they're a good fit
        """
        
        logger.info(f"📞 Initiating call to {creator.name} at {creator.phone}")
        
        if self.use_mock:
            return await self._mock_call_initiation(creator, campaign_data)
        
        try:
            # FIXED: Build campaign-specific context instead of generic variables
            campaign_context = self._build_campaign_context(creator, campaign_data, dynamic_variables)
            
            # Prepare API payload with campaign context
            payload = {
                "agent_id": self.agent_id,
                "agent_phone_number_id": self.phone_number_id,
                "to_number": creator.phone,
                "dynamic_variables": campaign_context
            }
            
            logger.info(f"🔧 Making ElevenLabs API call with payload keys: {list(payload.keys())}")
            
            # Make API call
            response = await self.client.post(
                f"{self.base_url}/v1/convai/twilio/outbound-call",
                json=payload
            )
            
            # Parse response
            response_data = await self._parse_api_response(response)
            
            logger.info(f"🔍 ElevenLabs API response: {response_data}")
            
            # Return standardized result
            return self._format_call_result(response_data, creator)
            
        except Exception as e:
            logger.error(f"❌ Call initiation failed for {creator.name}: {e}")
            return {
                "success": False,
                "message": f"Call initiation error: {str(e)}",
                "conversation_id": None,
                "status": "failed"
            }
    
    def _build_campaign_context(
        self,
        creator: Creator,
        campaign_data: CampaignData,
        additional_vars: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        FIXED: Build campaign context to match your ElevenLabs configuration exactly
        
        This matches the variable names I can see in your ElevenLabs setup.
        """
        
        # Calculate personalized offer details
        personalized_rate = min(campaign_data.budget_per_creator, creator.rate_per_post * 1.2)
        rate_range_min = max(campaign_data.budget_per_creator * 0.8, creator.rate_per_post * 0.9)
        rate_range_max = campaign_data.budget_per_creator
        
        # Match your ElevenLabs variable structure exactly
        campaign_context = {
            # Core identification variables (matching your ElevenLabs config)
            "influencerName": creator.name,
            "campaignBriefbrand_name": campaign_data.company_name,
            
            # Influencer Profile object (as shown in your config)
            "InfluencerProfile": {
                "name": creator.name,
                "channel": f"{creator.handle}",
                "niche": creator.niche,
                "followers": creator.followers,
                "engagement": creator.engagement_rate,
                "audienceType": f"{creator.niche} enthusiasts",
                "location": getattr(creator, 'location', 'Global'),
                "performanceMetrics": f"{creator.engagement_rate}% engagement rate with {creator.followers:,} followers"
            },
            
            # Campaign Brief object (matching your structure)
            "campaignBrief": {
                "brand_name": campaign_data.company_name,
                "product_name": campaign_data.product_name,
                "product_description": campaign_data.product_description,
                "product_niche": getattr(campaign_data, 'product_niche', 'tech'),
                "uniqueValue": f"exclusive early access to {campaign_data.product_name}"
            },
            
            # Negotiation Strategy object
            "negotiationStrategy": {
                "approach": "collaborative",
                "matchReasons": f"Your {creator.niche} content and {creator.engagement_rate}% engagement aligns perfectly with our target audience",
                "objectionHandling": "flexible_on_timeline_firm_on_quality",
                "brandAlignment": f"Strong alignment between {creator.niche} content and {campaign_data.product_name}"
            },
            
            # Deliverable Requirements
            "deliverableRequirements": {
                "primary": f"Product review video featuring {campaign_data.product_name}",
                "secondary": campaign_data.content_requirements
            },
            
            # Timeline Expectations
            "timelineExpectations": {
                "preferred": campaign_data.timeline,
                "launchDate": "within 4 weeks",
                "deadline": "6 weeks maximum"
            },
            
            # Usage Rights
            "usageRights": {
                "type": "organic_plus_website_features", 
                "duration": "12 months from posting date"
            },
            
            # Budget Strategy
            "budgetStrategy": {
                "initialOffer": str(int(personalized_rate)),
                "maxOffer": str(int(rate_range_max)),
                "rushPremium": "+20% for expedited delivery"
            },
            
            # Competitor Context
            "competitorContext": {
                "marketRates": f"${int(rate_range_min)}-${int(rate_range_max)} range for similar campaigns",
                "platform": f"Leading {creator.platform} creators in {creator.niche}"
            },
            
            # Additional flat variables for direct access
            "InfluencerProfileniche": creator.niche,
            "InfluencerProfilefollowers": str(creator.followers),
            "InfluencerProfileengagement": str(creator.engagement_rate),
            "InfluencerProfileaudienceType": f"{creator.niche} enthusiasts",
            "InfluencerProfilelocation": getattr(creator, 'location', 'Global'),
            "InfluencerProfileperformanceMetrics": f"{creator.engagement_rate}% engagement with {creator.followers:,} followers",
            
            "campaignBriefproduct_niche": getattr(campaign_data, 'product_niche', 'tech'),
            "campaignBriefuniqueValue": f"exclusive early access to {campaign_data.product_name}",
            
            "negotiationStrategymatchReasons": f"Your {creator.niche} content perfectly aligns with our {campaign_data.product_name} campaign",
            "negotiationStrategyobjectionHandling": "flexible_on_timeline_firm_on_quality",
            "negotiationStrategyapproach": "collaborative",
            "negotiationStrategybrandAlignment": f"Perfect fit between {creator.niche} audience and {campaign_data.product_name}",
            
            "deliverableRequirementsprimary": f"Authentic product review of {campaign_data.product_name}",
            "deliverableRequirementssecondary": campaign_data.content_requirements,
            
            "timelineExpectationspreferred": campaign_data.timeline,
            "timelineExpectationslaunchDate": "coordinated campaign launch",
            "timelineExpectationsdeadline": "6 weeks maximum",
            
            "usageRightstype": "organic_plus_website_features",
            "usageRightsduration": "12 months from posting date",
            
            "budgetStrategyinitialOffer": str(int(personalized_rate)),
            "budgetStrategymaxOffer": str(int(rate_range_max)),
            "budgetStrategyrusshPremium": "+20% for expedited delivery",
            
            "competitorContextmarketRates": f"${int(rate_range_min)}-${int(rate_range_max)} range",
            
            # Final agreement fields (will be updated during conversation)
            "finalAgreedRate": str(int(personalized_rate)),
            "finalDeliverables": campaign_data.content_requirements,
            "finalTimeline": campaign_data.timeline
        }
        
        # Add any additional variables
        if additional_vars:
            campaign_context.update(additional_vars)
        
        logger.info(f"🎯 Built ElevenLabs-compatible context for {creator.name}: {campaign_data.company_name} - {campaign_data.product_name}")
        
        return campaign_context
    
    def _determine_match_reasons(self, creator: Creator, campaign_data: CampaignData) -> str:
        """Determine specific reasons why this creator is a good fit"""
        
        reasons = []
        
        # Niche alignment
        if creator.niche.lower() in campaign_data.target_audience.lower():
            reasons.append(f"your {creator.niche} content aligns perfectly with our target audience")
        
        # Platform fit
        if creator.platform in ["instagram", "youtube", "tiktok"]:
            reasons.append(f"your {creator.platform} presence is ideal for product showcases")
        
        # Engagement quality
        if creator.engagement_rate > 4.0:
            reasons.append(f"your {creator.engagement_rate}% engagement rate shows strong audience connection")
        
        # Follower range
        if 50000 <= creator.followers <= 500000:
            reasons.append("your audience size is perfect for authentic product reviews")
        
        # Specialties match
        matching_specialties = [spec for spec in creator.specialties if spec.lower() in campaign_data.product_description.lower()]
        if matching_specialties:
            reasons.append(f"your expertise in {', '.join(matching_specialties)} matches our product perfectly")
        
        return "; ".join(reasons[:3])  # Top 3 reasons to keep it concise
    
    async def _parse_api_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Parse ElevenLabs API response with proper error handling"""
        
        try:
            if response.status_code == 200:
                response_json = response.json()
                return {
                    "success": True,
                    "message": "Call initiated successfully",
                    "conversation_id": response_json.get("conversation_id"),
                    "call_sid": response_json.get("call_sid"),
                    "raw_response": response_json
                }
            else:
                try:
                    error_data = response.json()
                    error_message = error_data.get("detail", f"HTTP {response.status_code} error")
                except:
                    error_message = f"HTTP {response.status_code} error"
                
                return {
                    "success": False,
                    "message": f"HTTP {response.status_code} error: {error_message}",
                    "conversation_id": None,
                    "call_sid": None
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to parse API response: {e}")
            return {
                "success": False,
                "message": f"Response parsing error: {str(e)}",
                "conversation_id": None,
                "call_sid": None
            }
    
    def _format_call_result(self, api_response: Dict[str, Any], creator: Creator) -> Dict[str, Any]:
        """Format API response into standardized call result"""
        
        if api_response.get("success", False):
            conversation_id = api_response.get("conversation_id")
            
            if conversation_id:
                return {
                    "success": True,
                    "message": f"Campaign call successfully initiated to {creator.name}",
                    "conversation_id": conversation_id,
                    "call_sid": api_response.get("call_sid"),
                    "status": "connecting"
                }
            else:
                # Generate fallback ID if API doesn't provide one
                fallback_id = f"elevenlabs-{int(datetime.now().timestamp())}"
                logger.warning("⚠️ No conversation_id found in response, using generated ID")
                
                return {
                    "success": True,
                    "message": f"Campaign call initiated to {creator.name} (fallback ID)",
                    "conversation_id": fallback_id,
                    "status": "connecting"
                }
        else:
            return {
                "success": False,
                "message": api_response.get("message", "Campaign call initiation failed"),
                "conversation_id": None,
                "status": "failed"
            }
    
    async def _mock_call_initiation(
        self,
        creator: Creator,
        campaign_data: CampaignData
    ) -> Dict[str, Any]:
        """Mock call initiation for testing with campaign context"""
        
        mock_conversation_id = f"mock-campaign-{uuid.uuid4().hex[:8]}"
        
        logger.info(f"🎭 Mock campaign call initiated for {creator.name}: {mock_conversation_id}")
        logger.info(f"🎯 Campaign: {campaign_data.company_name} - {campaign_data.product_name}")
        
        return {
            "success": True,
            "message": f"Mock campaign call initiated to {creator.name} for {campaign_data.product_name}",
            "conversation_id": mock_conversation_id,
            "status": "in_progress"
        }
    
    async def check_call_status(self, conversation_id: str) -> Dict[str, Any]:
        """Check current status of ongoing call"""
        
        if self.use_mock:
            return await self._mock_status_check(conversation_id)
        
        try:
            response = await self.client.get(
                f"{self.base_url}/v1/convai/conversation/{conversation_id}"
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_status_response(data, conversation_id)
            else:
                logger.error(f"❌ Status check failed: {response.status_code}")
                return {
                    "status": "failed",
                    "conversation_id": conversation_id,
                    "error": f"Status check failed: {response.status_code}",
                    "call_successful": False
                }
                
        except Exception as e:
            logger.error(f"❌ Status check error: {e}")
            return {
                "status": "failed",
                "conversation_id": conversation_id,
                "error": str(e),
                "call_successful": False
            }
    
    def _parse_status_response(self, data: Dict[str, Any], conversation_id: str) -> Dict[str, Any]:
        """Parse status response from ElevenLabs API"""
        
        try:
            status = data.get("status", "unknown")
            call_successful = data.get("call_successful", False)
            
            # Extract conversation analysis if available
            analysis = data.get("analysis", {})
            
            return {
                "status": status,
                "conversation_id": conversation_id,
                "call_successful": call_successful,
                "analysis": analysis,
                "final_rate": analysis.get("final_rate"),
                "timeline": analysis.get("timeline"),
                "deliverables": analysis.get("deliverables"),
                "raw_data": data
            }
            
        except Exception as e:
            logger.error(f"❌ Error parsing status response: {e}")
            return {
                "status": "failed",
                "conversation_id": conversation_id,
                "error": f"Status parsing error: {str(e)}",
                "call_successful": False
            }
    
    async def _mock_status_check(self, conversation_id: str) -> Dict[str, Any]:
        """Mock status check with campaign negotiation results"""
        
        return {
            "status": "completed",
            "conversation_id": conversation_id,
            "call_successful": True,
            "final_rate": 1200.0,
            "timeline": "4 weeks",
            "deliverables": "3 Instagram posts, 2 TikTok videos showcasing E2E TestPro Device",
            "negotiation_outcome": "agreed to campaign terms",
            "influencer_interest": "high",
            "analysis": {
                "sentiment": "positive",
                "negotiation_outcome": "successful",
                "agreement_reached": "yes"
            }
        }
    
    async def close(self) -> None:
        """Clean up HTTP client resources"""
        try:
            await self.client.aclose()
            logger.info("✅ Voice Service resources cleaned up")
        except Exception as e:
            logger.error(f"❌ Error cleaning up voice service: {e}")