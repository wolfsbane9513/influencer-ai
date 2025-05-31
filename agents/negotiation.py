# agents/negotiation.py
import asyncio
import random
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from models.campaign import CampaignData
from models.creator import CreatorMatch
from models.negotiation import NegotiationState, NegotiationStatus, CallStatus
from services.voice import VoiceService
from services.pricing import PricingService

# Import settings with fallback
try:
    from config.settings import settings
except ImportError:
    from config.simple_settings import settings

logger = logging.getLogger(__name__)

class NegotiationAgent:
    """
    AI agent that conducts phone negotiations with influencers
    using ElevenLabs voice synthesis and Groq LLM conversation
    """
    
    def __init__(self):
        self.voice_service = VoiceService()
        self.pricing_service = PricingService()
        self.negotiation_scripts = self._load_negotiation_scripts()
    
    def _load_negotiation_scripts(self) -> Dict[str, Any]:
        """Load negotiation scripts and tactics"""
        # Mock negotiation scripts - in production would load from file
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
            },
            "closing_scripts": {
                "soft_close": "Based on everything we've discussed - ${final_price} for {deliverables} with delivery by {timeline} - does this sound like something you'd be interested in moving forward with?",
                "urgency_close": "We're finalizing our creator lineup by {date}. If you're interested, I can get the contract over to you today. Should I send that your way?",
                "summary_close": "Perfect! Let me confirm: ${price} for {detailed_deliverables}, delivered by {timeline}, with {usage_rights}. I'll email you the contract within 2 hours. Thank you for the great conversation!"
            }
        }
    
    async def negotiate(
        self, 
        influencer_match: CreatorMatch, 
        campaign_data: CampaignData
    ) -> NegotiationState:
        """
        Conduct AI-powered negotiation with an influencer
        """
        creator = influencer_match.creator
        negotiation_state = NegotiationState(
            creator_id=creator.id,
            campaign_id=campaign_data.id,
            initial_offer=influencer_match.estimated_rate
        )
        
        logger.info(f"📞 Starting negotiation with {creator.name}")
        
        try:
            # Step 1: Initiate call
            negotiation_state.status = NegotiationStatus.CALLING
            call_session = await self._initiate_call(creator, negotiation_state)
            
            if not call_session:
                return await self._handle_call_failure(negotiation_state, "Failed to connect")
            
            # Step 2: Conduct negotiation conversation
            negotiation_state.status = NegotiationStatus.NEGOTIATING
            conversation_result = await self._conduct_negotiation_conversation(
                call_session, creator, campaign_data, negotiation_state
            )
            
            # Step 3: Evaluate outcome
            final_result = await self._evaluate_negotiation_outcome(
                conversation_result, creator, campaign_data, negotiation_state
            )
            
            return final_result
            
        except Exception as e:
            logger.error(f"❌ Negotiation failed with {creator.name}: {e}")
            return await self._handle_negotiation_error(negotiation_state, str(e))
    
    async def _initiate_call(
        self, 
        creator, 
        negotiation_state: NegotiationState
    ) -> Optional[Dict[str, Any]]:
        """Initiate phone call using ElevenLabs"""
        try:
            logger.info(f"📱 Calling {creator.name} at {creator.phone_number}")
            
            if settings.mock_calls:
                # Mock call for demo/testing
                await asyncio.sleep(2)  # Simulate dialing time
                logger.info("🎭 Mock call connected")
                return {"call_id": f"mock_call_{creator.id}", "status": "connected"}
            else:
                # Real ElevenLabs call
                call_session = await self.voice_service.initiate_call(
                    phone_number=creator.phone_number,
                    voice_id=settings.elevenlabs_voice_id
                )
                
                if call_session.get("status") == "connected":
                    negotiation_state.call_status = CallStatus.COMPLETED
                    logger.info(f"✅ Call connected to {creator.name}")
                    return call_session
                else:
                    logger.warning(f"⚠️  Call connection failed: {call_session}")
                    return None
        
        except Exception as e:
            logger.error(f"❌ Call initiation failed: {e}")
            return None
    
    async def _conduct_negotiation_conversation(
        self,
        call_session: Dict[str, Any],
        creator,
        campaign_data: CampaignData,
        negotiation_state: NegotiationState
    ) -> Dict[str, Any]:
        """Conduct the actual negotiation conversation"""
        try:
            start_time = datetime.now()
            
            # Generate opening script
            opening_script = self._generate_opening_script(creator, campaign_data, negotiation_state)
            
            # Start conversation
            conversation_log = []
            conversation_log.append(f"AI: {opening_script}")
            
            if settings.mock_calls:
                # Mock conversation for demo
                conversation_result = await self._mock_conversation(
                    creator, campaign_data, negotiation_state
                )
            else:
                # Real ElevenLabs + Groq conversation
                conversation_result = await self.voice_service.conduct_conversation(
                    call_session,
                    opening_script,
                    max_duration=settings.max_negotiation_duration
                )
            
            # Calculate call duration
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            negotiation_state.call_duration_seconds = int(duration)
            
            # Store conversation details
            negotiation_state.call_transcript = conversation_result.get("transcript", "")
            negotiation_state.call_recording_url = conversation_result.get("recording_url", "")
            
            logger.info(f"📞 Conversation completed in {duration:.1f}s")
            
            return conversation_result
            
        except Exception as e:
            logger.error(f"❌ Conversation failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _mock_conversation(
        self,
        creator,
        campaign_data: CampaignData,
        negotiation_state: NegotiationState
    ) -> Dict[str, Any]:
        """Generate mock conversation for demo purposes"""
        
        # Simulate conversation duration
        conversation_time = random.uniform(15, 45)  # 15-45 seconds for demo
        await asyncio.sleep(conversation_time)
        
        # Generate realistic mock conversation based on creator characteristics
        mock_responses = self._generate_mock_responses(creator, campaign_data, negotiation_state)
        
        # Determine success probability based on factors
        success_factors = self._calculate_success_factors(creator, campaign_data, negotiation_state)
        success_probability = success_factors["overall_probability"]
        
        # Random outcome with weighted probability
        is_successful = random.random() < success_probability
        
        if is_successful:
            # Successful negotiation
            final_rate = self._negotiate_final_rate(creator, campaign_data, negotiation_state)
            transcript = self._generate_success_transcript(creator, final_rate, mock_responses)
            
            return {
                "status": "success",
                "outcome": "accepted",
                "final_rate": final_rate,
                "transcript": transcript,
                "recording_url": f"mock_recording_{creator.id}.mp3",
                "success_factors": success_factors
            }
        else:
            # Failed negotiation
            failure_reason = self._determine_failure_reason(success_factors)
            transcript = self._generate_failure_transcript(creator, failure_reason, mock_responses)
            
            return {
                "status": "failed",
                "outcome": "rejected",
                "failure_reason": failure_reason,
                "transcript": transcript,
                "recording_url": None,
                "success_factors": success_factors
            }
    
    def _generate_opening_script(
        self, 
        creator, 
        campaign_data: CampaignData, 
        negotiation_state: NegotiationState
    ) -> str:
        """Generate personalized opening script"""
        
        # Choose script type based on creator tier and campaign
        if creator.followers > 500000:
            script_type = "high_value"
        elif campaign_data.total_budget > 20000:
            script_type = "time_sensitive"  
        else:
            script_type = "standard"
        
        script_template = self.negotiation_scripts["opening_scripts"][script_type]
        
        # Format script with campaign and creator data
        formatted_script = script_template.format(
            creator_name=creator.name,
            brand_name=campaign_data.brand_name,
            campaign_type=campaign_data.campaign_goal,
            platform=creator.platform,
            follower_count=f"{creator.followers//1000}K" if creator.followers >= 1000 else str(creator.followers),
            engagement_rate=creator.engagement_rate,
            initial_offer=int(negotiation_state.initial_offer or creator.typical_rate),
            deliverables="video review and social posts"
        )
        
        return formatted_script
    
    def _calculate_success_factors(
        self, 
        creator, 
        campaign_data: CampaignData, 
        negotiation_state: NegotiationState
    ) -> Dict[str, float]:
        """Calculate factors that influence negotiation success"""
        
        # Base success rate
        base_rate = settings.base_success_rate
        
        # Rate factor - how reasonable is our offer
        offered_rate = negotiation_state.initial_offer or creator.typical_rate
        rate_ratio = offered_rate / creator.typical_rate
        if rate_ratio >= 1.1:  # 10% above typical
            rate_factor = 0.9
        elif rate_ratio >= 1.0:  # At typical rate
            rate_factor = 0.8
        elif rate_ratio >= 0.9:  # 10% below typical
            rate_factor = 0.6
        else:  # Significantly below
            rate_factor = 0.3
        
        # Availability factor
        availability_factors = {
            "excellent": 0.9,
            "good": 0.8,
            "limited": 0.5,
            "busy": 0.2
        }
        availability_factor = availability_factors.get(creator.availability.value, 0.5)
        
        # Niche match factor
        if creator.niche.lower() == campaign_data.product_niche.lower():
            niche_factor = 0.9
        elif creator.niche.lower() in campaign_data.product_description.lower():
            niche_factor = 0.7
        else:
            niche_factor = 0.4
        
        # Brand safety and collaboration rating
        brand_safety = creator.performance_metrics.get("brand_safety_score", 8.0) / 10.0
        collaboration_rating = creator.performance_metrics.get("collaboration_rating", 4.0) / 5.0
        
        # Calculate overall probability
        overall_probability = (
            base_rate * 0.3 +
            rate_factor * 0.25 +
            availability_factor * 0.2 +
            niche_factor * 0.15 +
            brand_safety * 0.05 +
            collaboration_rating * 0.05
        )
        
        # Add some randomness (±15%)
        randomness = random.uniform(0.85, 1.15)
        overall_probability = min(overall_probability * randomness, 0.95)
        
        return {
            "base_rate": base_rate,
            "rate_factor": rate_factor,
            "availability_factor": availability_factor,
            "niche_factor": niche_factor,
            "brand_safety": brand_safety,
            "collaboration_rating": collaboration_rating,
            "overall_probability": overall_probability
        }
    
    def _negotiate_final_rate(
        self, 
        creator, 
        campaign_data: CampaignData, 
        negotiation_state: NegotiationState
    ) -> float:
        """Calculate the final negotiated rate"""
        initial_offer = negotiation_state.initial_offer or creator.typical_rate
        creator_typical = creator.typical_rate
        
        # Negotiation usually results in something between initial offer and typical rate
        if initial_offer >= creator_typical:
            # We offered above their rate - they accept at slight discount
            final_rate = creator_typical * random.uniform(0.95, 1.05)
        else:
            # We offered below - negotiate to middle ground
            midpoint = (initial_offer + creator_typical) / 2
            final_rate = midpoint * random.uniform(0.9, 1.1)
        
        return round(final_rate, 2)
    
    def _determine_failure_reason(self, success_factors: Dict[str, float]) -> str:
        """Determine the most likely reason for negotiation failure"""
        
        if success_factors["rate_factor"] < 0.5:
            return "Rate too low - creator requested higher compensation"
        elif success_factors["availability_factor"] < 0.4:
            return "Creator too busy - unavailable for campaign timeline"
        elif success_factors["niche_factor"] < 0.5:
            return "Misaligned brand fit - creator prefers different product categories"
        else:
            return "Creator declined - considering other opportunities"
    
    def _generate_mock_responses(self, creator, campaign_data, negotiation_state):
        """Generate realistic mock creator responses"""
        return {
            "opening_response": f"Hi Alex! Thanks for reaching out. I'm interested in learning more about the {campaign_data.product_name} campaign.",
            "rate_response": f"The rate sounds interesting. My typical rate for this type of content is around ${creator.typical_rate}.",
            "timeline_response": "The timeline works for me. I can deliver high-quality content within that timeframe.",
            "closing_response": "This sounds like a great opportunity. I'd love to move forward with this collaboration."
        }
    
    def _generate_success_transcript(self, creator, final_rate, mock_responses):
        """Generate transcript for successful negotiation"""
        return f"""
Call Transcript - {creator.name}

AI: [Opening script with campaign details]
{creator.name}: {mock_responses["opening_response"]}

AI: Great! We're looking at a rate of ${final_rate} for this campaign...
{creator.name}: {mock_responses["rate_response"]}

AI: Perfect! Let me confirm the deliverables and timeline...
{creator.name}: {mock_responses["timeline_response"]}

AI: Excellent! I'll send over the contract today.
{creator.name}: {mock_responses["closing_response"]}

[Call ended - SUCCESS - Final rate: ${final_rate}]
""".strip()
    
    def _generate_failure_transcript(self, creator, failure_reason, mock_responses):
        """Generate transcript for failed negotiation"""
        return f"""
Call Transcript - {creator.name}

AI: [Opening script with campaign details]
{creator.name}: Thanks for reaching out, but I have some concerns...

AI: I understand. Let me see if we can address those...
{creator.name}: [Explains concerns about rate/timeline/brand fit]

AI: I appreciate your feedback. Let me check with my team...
{creator.name}: I don't think this is the right fit for me right now.

[Call ended - DECLINED - Reason: {failure_reason}]
""".strip()
    
    async def _evaluate_negotiation_outcome(
        self,
        conversation_result: Dict[str, Any],
        creator,
        campaign_data: CampaignData,
        negotiation_state: NegotiationState
    ) -> NegotiationState:
        """Evaluate and finalize negotiation outcome"""
        
        if conversation_result.get("status") == "success":
            # Successful negotiation
            negotiation_state.status = NegotiationStatus.SUCCESS
            negotiation_state.final_rate = conversation_result.get("final_rate")
            negotiation_state.negotiated_terms = {
                "deliverables": ["video_review", "instagram_post"],
                "timeline": "7 days",
                "usage_rights": "organic_only",
                "payment_schedule": "50% upfront, 50% on delivery"
            }
            negotiation_state.completed_at = datetime.now()
            
            logger.info(f"✅ Negotiation successful: ${negotiation_state.final_rate}")
            
        else:
            # Failed negotiation
            negotiation_state.status = NegotiationStatus.FAILED
            negotiation_state.failure_reason = conversation_result.get("failure_reason", "Unknown reason")
            negotiation_state.completed_at = datetime.now()
            
            logger.info(f"❌ Negotiation failed: {negotiation_state.failure_reason}")
        
        return negotiation_state
    
    async def _handle_call_failure(self, negotiation_state: NegotiationState, reason: str) -> NegotiationState:
        """Handle call connection failure"""
        negotiation_state.call_status = CallStatus.NO_ANSWER
        negotiation_state.status = NegotiationStatus.FAILED
        negotiation_state.failure_reason = f"Call failed: {reason}"
        negotiation_state.completed_at = datetime.now()
        
        # Implement retry logic
        if negotiation_state.retry_count < settings.max_retry_attempts:
            negotiation_state.retry_count += 1
            logger.info(f"🔄 Retrying call to {negotiation_state.creator_id} (attempt {negotiation_state.retry_count})")
            # Would retry here in real implementation
        
        return negotiation_state
    
    async def _handle_negotiation_error(self, negotiation_state: NegotiationState, error: str) -> NegotiationState:
        """Handle general negotiation errors"""
        negotiation_state.status = NegotiationStatus.FAILED
        negotiation_state.failure_reason = f"System error: {error}"
        negotiation_state.completed_at = datetime.now()
        return negotiation_state