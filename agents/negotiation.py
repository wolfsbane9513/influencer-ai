# agents/negotiation.py - FIXED LEGACY VERSION
import asyncio
import random
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from core.models import CampaignData, CreatorMatch, NegotiationState, NegotiationStatus, CallStatus
from services.voice import VoiceService
from services.pricing import PricingService

from core.config import settings

logger = logging.getLogger(__name__)

class NegotiationAgent:
    """
    🎯 LEGACY NEGOTIATION AGENT
    Legacy version for backward compatibility
    """
    
    def __init__(self):
        self.voice_service = VoiceService()
        self.pricing_service = PricingService()
        self.negotiation_scripts = self._load_negotiation_scripts()
    
    def _load_negotiation_scripts(self) -> Dict[str, Any]:
        """Load negotiation scripts and tactics"""
        return {
            "opening_scripts": {
                "standard": "Hi {creator_name}, this is Alex calling from {brand_name}. I hope I'm catching you at a good time! We have an exciting {campaign_type} campaign that would be perfect for your {platform} audience of {follower_count} followers. Your {engagement_rate}% engagement rate is exactly what we're looking for. Do you have 3-4 minutes to discuss a collaboration worth around ${initial_offer}?",
                "high_value": "Hi {creator_name}, this is Alex from {brand_name}. I'm reaching out because we specifically identified you as our top choice for an exclusive {campaign_type} campaign. Your content quality and {engagement_rate}% engagement with {follower_count} followers makes you perfect for this premium collaboration. Are you available to discuss a partnership in the ${initial_offer} range?",
                "time_sensitive": "Hi {creator_name}, this is Alex from {brand_name}. I'm calling because we have an urgent but exciting opportunity that I think would be perfect for you. We need to move quickly on this {campaign_type} campaign, but we're prepared to offer premium rates - around ${initial_offer} for {deliverables}. Do you have a few minutes to discuss?"
            },
            "objection_responses": {
                "price_too_low": [
                    "I understand your concern. Looking at your engagement rate of {engagement_rate}% and average views of {avg_views}, I can see the value. Given those strong metrics, I could go up to ${max_budget}. How does that sound?",
                    "You're absolutely right about your value. Your cost-per-view of ${cost_per_view} is actually excellent compared to industry standards. Let me see what I can do - I could offer ${higher_amount} plus a performance bonus if we hit engagement targets."
                ],
                "timeline_too_tight": [
                    "I completely understand - quality content takes time. What if we extended this to {alternative_timeline}? Would that work better for your content creation process?",
                    "That's totally fair. We could either extend to {extended_weeks} weeks or reduce the scope to just {primary_deliverable} to meet the original timeline. Which would you prefer?"
                ]
            }
        }
    
    async def negotiate(
        self, 
        influencer_match: CreatorMatch, 
        campaign_data: CampaignData,
        ai_strategy: Dict[str, Any] = None
    ) -> NegotiationState:
        """
        🎯 MAIN NEGOTIATION METHOD - Conducts complete negotiation workflow
        """
        creator = influencer_match.creator
        
        # Initialize negotiation state
        negotiation_state = NegotiationState(
            creator_id=creator.id,
            campaign_id=campaign_data.id,
            initial_offer=self._calculate_initial_offer(influencer_match, ai_strategy)
        )
        
        logger.info(f"📞 Starting negotiation with {creator.name} - Initial offer: ${negotiation_state.initial_offer}")
        
        try:
            # Step 1: Prepare conversation context with AI strategy
            conversation_context = self._prepare_conversation_context(
                creator, campaign_data, negotiation_state, ai_strategy
            )
            
            # Step 2: Initiate call (ElevenLabs or mock)
            negotiation_state.status = NegotiationStatus.CALLING
            call_result = await self._initiate_call(
                creator, campaign_data, conversation_context
            )
            
            if call_result["status"] != "success":
                return await self._handle_call_failure(negotiation_state, call_result.get("error"))
            
            # Step 3: Store call details
            negotiation_state.conversation_id = call_result.get("conversation_id")
            negotiation_state.call_id = call_result.get("call_id")
            negotiation_state.status = NegotiationStatus.NEGOTIATING
            
            # Step 4: Conduct conversation
            conversation_result = await self._conduct_conversation(
                call_result, negotiation_state, ai_strategy
            )
            
            # Step 5: Analyze outcome
            final_result = await self._analyze_conversation_outcome(
                negotiation_state, conversation_result, ai_strategy
            )
            
            return final_result
            
        except Exception as e:
            logger.error(f"❌ Negotiation failed with {creator.name}: {e}")
            return await self._handle_negotiation_error(negotiation_state, str(e))
    
    def _calculate_initial_offer(self, influencer_match: CreatorMatch, ai_strategy: Dict[str, Any] = None) -> float:
        """💰 Calculate initial offer using AI strategy or default logic"""
        
        base_rate = influencer_match.estimated_rate
        
        if ai_strategy:
            # Use AI-determined multiplier
            multiplier = ai_strategy.get("opening_offer_multiplier", 1.0)
            initial_offer = base_rate * multiplier
            logger.info(f"🧠 AI Strategy: Using {multiplier}x multiplier for initial offer")
        else:
            # Default: start slightly below estimated rate to leave negotiation room
            initial_offer = base_rate * 0.95
        
        return round(initial_offer, 2)
    
    def _prepare_conversation_context(
        self, 
        creator, 
        campaign_data: CampaignData, 
        negotiation_state: NegotiationState,
        ai_strategy: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """📝 Prepare conversation context"""
        
        # Basic creator profile
        creator_profile = {
            "id": creator.id,
            "name": creator.name,
            "niche": creator.niche,
            "followers": creator.followers,
            "engagement_rate": creator.engagement_rate,
            "average_views": creator.average_views,
            "location": creator.location,
            "languages": creator.languages,
            "typical_rate": creator.typical_rate,
            "availability": creator.availability.value,
            "about": f"Content creator specializing in {creator.niche} with {creator.followers//1000}K followers"
        }
        
        # Campaign brief
        campaign_brief = f"""
        Brand: {campaign_data.brand_name}
        Product: {campaign_data.product_name}
        Description: {campaign_data.product_description}
        Target Audience: {campaign_data.target_audience}
        Campaign Goal: {campaign_data.campaign_goal}
        Total Budget: ${campaign_data.total_budget:,}
        """
        
        # Price range
        if ai_strategy:
            max_multiplier = ai_strategy.get("max_offer_multiplier", 1.2)
            max_offer = creator.typical_rate * max_multiplier
        else:
            max_offer = negotiation_state.initial_offer * 1.3
        
        price_range = f"{negotiation_state.initial_offer:.0f}-{max_offer:.0f}"
        
        return {
            "creator_profile": creator_profile,
            "campaign_brief": campaign_brief,
            "price_range": price_range,
            "ai_strategy": ai_strategy or {}
        }
    
    async def _initiate_call(
        self, 
        creator, 
        campaign_data: CampaignData, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """📞 Initiate call using voice service"""
        
        try:
            logger.info(f"📱 Initiating call to {creator.name} at {creator.phone_number}")
            
            call_result = await self.voice_service.initiate_negotiation_call(
                creator_phone=creator.phone_number,
                creator_profile=context["creator_profile"],
                campaign_brief=context["campaign_brief"],
                price_range=context["price_range"]
            )
            
            if call_result["status"] == "success":
                logger.info(f"✅ Call initiated successfully")
                logger.info(f"   - Conversation ID: {call_result.get('conversation_id')}")
                logger.info(f"   - Call ID: {call_result.get('call_id')}")
            else:
                logger.error(f"❌ Call failed: {call_result.get('error')}")
            
            return call_result
            
        except Exception as e:
            logger.error(f"❌ Call initiation error: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _conduct_conversation(
        self,
        call_result: Dict[str, Any],
        negotiation_state: NegotiationState,
        ai_strategy: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """🎯 Conduct the actual conversation"""
        
        conversation_id = call_result.get("conversation_id")
        
        if not conversation_id:
            # Handle mock calls or calls without conversation ID
            return await self._handle_mock_conversation(call_result)
        
        try:
            start_time = datetime.now()
            
            # Wait for conversation completion
            logger.info(f"⏳ Waiting for conversation {conversation_id} to complete...")
            
            conversation_result = await self.voice_service.conduct_conversation(
                call_result,
                opening_script="",
                max_duration=60
            )
            
            # Calculate call duration
            end_time = datetime.now()
            duration_seconds = int((end_time - start_time).total_seconds())
            negotiation_state.call_duration_seconds = duration_seconds
            
            logger.info(f"📞 Conversation completed in {duration_seconds} seconds")
            
            return conversation_result
            
        except Exception as e:
            logger.error(f"❌ Conversation error: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _analyze_conversation_outcome(
        self, 
        negotiation_state: NegotiationState, 
        conversation_result: Dict[str, Any],
        ai_strategy: Dict[str, Any] = None
    ) -> NegotiationState:
        """🧠 Analyze conversation to determine outcome"""
        
        conversation_status = conversation_result.get("status", "unknown")
        
        logger.info(f"🧠 Analyzing conversation - Status: {conversation_status}")
        
        if conversation_status == "completed":
            # Determine success based on conversation
            success = self._determine_success(conversation_result, ai_strategy)
            
            if success:
                # Successful negotiation
                final_rate = self._calculate_final_negotiated_rate(negotiation_state, ai_strategy)
                
                negotiation_state.status = NegotiationStatus.SUCCESS
                negotiation_state.final_rate = final_rate
                negotiation_state.negotiated_terms = {
                    "deliverables": ["video_review", "instagram_post"],
                    "timeline": "7 days",
                    "usage_rights": "organic_only",
                    "payment_schedule": "50% upfront, 50% on delivery",
                    "conversation_id": negotiation_state.conversation_id,
                    "final_rate": final_rate
                }
                
                logger.info(f"✅ Negotiation successful: ${final_rate:,.2f}")
            else:
                # Failed negotiation
                failure_reason = self._determine_failure_reason(conversation_result, ai_strategy)
                
                negotiation_state.status = NegotiationStatus.FAILED
                negotiation_state.failure_reason = failure_reason
                
                logger.info(f"❌ Negotiation failed: {failure_reason}")
        
        elif conversation_status == "failed":
            negotiation_state.status = NegotiationStatus.FAILED
            negotiation_state.failure_reason = "Call failed to connect or complete"
        
        else:
            # Unknown status - default to failure
            negotiation_state.status = NegotiationStatus.FAILED
            negotiation_state.failure_reason = f"Unknown conversation status: {conversation_status}"
        
        # Store conversation data
        negotiation_state.call_transcript = conversation_result.get("transcript", "")
        negotiation_state.call_recording_url = conversation_result.get("recording_url")
        negotiation_state.completed_at = datetime.now()
        
        return negotiation_state
    
    def _determine_success(self, conversation_result: Dict[str, Any], ai_strategy: Dict[str, Any] = None) -> bool:
        """Determine if negotiation was successful"""
        
        # Check for mock result first
        mock_result = conversation_result.get("mock_result", {})
        if mock_result:
            return mock_result.get("negotiation_outcome") == "accepted"
        
        # For real conversations, use simple success logic
        # In a real implementation, this would analyze the transcript
        return random.choice([True, True, False])  # 66% success rate
    
    def _calculate_final_negotiated_rate(self, negotiation_state: NegotiationState, ai_strategy: Dict[str, Any] = None) -> float:
        """💰 Calculate final negotiated rate"""
        
        initial_offer = negotiation_state.initial_offer
        
        if ai_strategy and "max_offer_multiplier" in ai_strategy:
            # Use AI-determined range
            max_rate = initial_offer * ai_strategy["max_offer_multiplier"]
            # Final rate is typically between initial and max
            final_rate = initial_offer + (max_rate - initial_offer) * random.uniform(0.3, 0.8)
        else:
            # Default negotiation: usually end up slightly above initial offer
            final_rate = initial_offer * random.uniform(1.05, 1.25)
        
        return round(final_rate, 2)
    
    def _determine_failure_reason(self, conversation_result: Dict[str, Any], ai_strategy: Dict[str, Any] = None) -> str:
        """❌ Determine specific reason for negotiation failure"""
        
        # Check for mock result first
        mock_result = conversation_result.get("mock_result", {})
        if mock_result:
            return mock_result.get("failure_reason", "Creator declined")
        
        # Random realistic failure reasons for demo
        reasons = [
            "Rate too low - creator requested higher compensation",
            "Creator too busy - unavailable for campaign timeline",
            "Brand misalignment - creator prefers different product categories",
            "Conflict of interest - already working with competing brand",
            "Creator declined - considering other opportunities"
        ]
        return random.choice(reasons)
    
    async def _handle_mock_conversation(self, call_result: Dict[str, Any]) -> Dict[str, Any]:
        """🎭 Handle mock conversation results"""
        
        mock_result = call_result.get("mock_result", {})
        
        # Simulate conversation duration
        await asyncio.sleep(random.randint(30, 60))
        
        return {
            "status": "completed",
            "duration": random.randint(30, 60),
            "transcript": "Mock conversation completed",
            "mock_result": mock_result
        }
    
    async def _handle_call_failure(self, negotiation_state: NegotiationState, error: str) -> NegotiationState:
        """❌ Handle call connection failures"""
        negotiation_state.status = NegotiationStatus.FAILED
        negotiation_state.failure_reason = f"Call failed: {error}"
        negotiation_state.completed_at = datetime.now()
        
        # Implement retry logic
        if negotiation_state.retry_count < settings.max_retry_attempts:
            negotiation_state.retry_count += 1
            logger.info(f"🔄 Will retry call to {negotiation_state.creator_id} (attempt {negotiation_state.retry_count})")
        
        return negotiation_state
    
    async def _handle_negotiation_error(self, negotiation_state: NegotiationState, error: str) -> NegotiationState:
        """❌ Handle general negotiation errors"""
        negotiation_state.status = NegotiationStatus.FAILED
        negotiation_state.failure_reason = f"System error: {error}"
        negotiation_state.completed_at = datetime.now()
        logger.error(f"❌ Negotiation system error: {error}")
        return negotiation_state
    
    # Legacy methods for compatibility
    async def conduct_conversation(
        self,
        call_session: Dict[str, Any],
        opening_script: str,
        max_duration: int = 60
    ) -> Dict[str, Any]:
        """🔄 Legacy method for compatibility"""
        conversation_id = call_session.get("conversation_id")
        
        if not conversation_id:
            return {"status": "failed", "error": "No conversation ID provided"}
        
        # Use the voice service conversation management
        result = await self.voice_service.conduct_conversation(
            call_session, opening_script, max_duration
        )
        
        return {
            "status": "completed" if result.get("status") == "completed" else "failed",
            "duration": max_duration,
            "transcript": result.get("transcript", "Conversation completed"),
            "recording_url": result.get("recording_url"),
            "conversation_data": result
        }