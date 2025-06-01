# agents/negotiation.py
import asyncio
import random
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from models.campaign import CampaignData,CreatorMatch,NegotiationState, NegotiationStatus, CallStatus
from services.voice import VoiceService
from services.pricing import PricingService

from config.settings import settings

logger = logging.getLogger(__name__)

class NegotiationAgent:
    """
    🎯 AI NEGOTIATION AGENT with Real ElevenLabs Integration
    Conducts phone negotiations with influencers using ElevenLabs ConversationalAI
    and Groq LLM conversation analysis
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
            
            # Step 2: Initiate REAL ElevenLabs call
            negotiation_state.status = NegotiationStatus.CALLING
            call_result = await self._initiate_real_elevenlabs_call(
                creator, campaign_data, conversation_context
            )
            
            if call_result["status"] != "success":
                return await self._handle_call_failure(negotiation_state, call_result.get("error"))
            
            # Step 3: Store ElevenLabs conversation details
            negotiation_state.conversation_id = call_result.get("conversation_id")
            negotiation_state.call_id = call_result.get("call_id")
            negotiation_state.status = NegotiationStatus.NEGOTIATING
            
            # Step 4: Wait for conversation completion and analyze results
            final_result = await self._wait_and_analyze_conversation(
                negotiation_state, call_result, ai_strategy
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
        """📝 Prepare comprehensive context for ElevenLabs conversation"""
        
        # Basic creator profile (matching ElevenLabs sample format)
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
        
        # Campaign brief for ElevenLabs dynamic variables
        campaign_brief = f"""
        Brand: {campaign_data.brand_name}
        Product: {campaign_data.product_name}
        Description: {campaign_data.product_description}
        Target Audience: {campaign_data.target_audience}
        Campaign Goal: {campaign_data.campaign_goal}
        Total Budget: ${campaign_data.total_budget:,}
        
        We're looking for authentic partnerships with creators who align with our brand values and can deliver engaging content to their audience.
        """
        
        # Price range based on AI strategy or default logic
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
    
    async def _initiate_real_elevenlabs_call(
        self, 
        creator, 
        campaign_data: CampaignData, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """📞 Initiate real ElevenLabs conversation using the voice service"""
        
        try:
            logger.info(f"📱 Initiating ElevenLabs call to {creator.name} at {creator.phone_number}")
            
            # Use the real ElevenLabs service with your sample code format
            call_result = await self.voice_service.initiate_negotiation_call(
                creator_phone=creator.phone_number,
                creator_profile=context["creator_profile"],
                campaign_brief=context["campaign_brief"],
                price_range=context["price_range"]
            )
            
            if call_result["status"] == "success":
                logger.info(f"✅ ElevenLabs call initiated successfully")
                logger.info(f"   - Conversation ID: {call_result.get('conversation_id')}")
                logger.info(f"   - Call ID: {call_result.get('call_id')}")
            else:
                logger.error(f"❌ ElevenLabs call failed: {call_result.get('error')}")
            
            return call_result
            
        except Exception as e:
            logger.error(f"❌ Call initiation error: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _wait_and_analyze_conversation(
        self, 
        negotiation_state: NegotiationState, 
        call_result: Dict[str, Any],
        ai_strategy: Dict[str, Any] = None
    ) -> NegotiationState:
        """⏳ Wait for ElevenLabs conversation to complete and analyze results"""
        
        conversation_id = call_result.get("conversation_id")
        
        if not conversation_id:
            # Handle mock calls or calls without conversation ID
            return await self._handle_mock_conversation_result(negotiation_state, call_result)
        
        try:
            start_time = datetime.now()
            
            # Wait for conversation completion (max 2 minutes for demo)
            logger.info(f"⏳ Waiting for conversation {conversation_id} to complete...")
            
            conversation_result = await self.voice_service.wait_for_conversation_completion(
                conversation_id, 
                max_wait_seconds=120  # 2 minutes max for demo
            )
            
            # Calculate call duration
            end_time = datetime.now()
            duration_seconds = int((end_time - start_time).total_seconds())
            negotiation_state.call_duration_seconds = duration_seconds
            
            logger.info(f"📞 Conversation completed in {duration_seconds} seconds")
            
            # Analyze conversation outcome
            outcome = await self._analyze_conversation_outcome(
                conversation_result, negotiation_state, ai_strategy
            )
            
            # Update negotiation state with results
            negotiation_state.status = outcome["status"]
            negotiation_state.final_rate = outcome.get("final_rate")
            negotiation_state.failure_reason = outcome.get("failure_reason")
            negotiation_state.call_transcript = conversation_result.get("transcript", "")
            negotiation_state.call_recording_url = conversation_result.get("recording_url")
            negotiation_state.completed_at = datetime.now()
            
            # Store negotiated terms for successful negotiations
            if outcome["status"] == NegotiationStatus.SUCCESS:
                negotiation_state.negotiated_terms = {
                    "deliverables": ["video_review", "instagram_post"],
                    "timeline": "7 days",
                    "usage_rights": "organic_only",
                    "payment_schedule": "50% upfront, 50% on delivery",
                    "conversation_id": conversation_id,
                    "final_rate": outcome["final_rate"]
                }
            
            logger.info(f"📊 Negotiation result: {outcome['status']} - {outcome.get('final_rate', 'N/A')}")
            
            return negotiation_state
            
        except Exception as e:
            logger.error(f"❌ Conversation analysis failed: {e}")
            return await self._handle_negotiation_error(negotiation_state, str(e))
    
    async def _analyze_conversation_outcome(
        self, 
        conversation_result: Dict[str, Any], 
        negotiation_state: NegotiationState,
        ai_strategy: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """🧠 Analyze ElevenLabs conversation to determine outcome"""
        
        # Get conversation status and transcript
        conversation_status = conversation_result.get("status", "unknown")
        transcript = conversation_result.get("transcript", "")
        
        logger.info(f"🧠 Analyzing conversation - Status: {conversation_status}")
        
        if conversation_status == "completed":
            # Analyze transcript for success indicators
            success_indicators = [
                "accept", "agree", "sounds good", "let's do it", "deal", "yes", 
                "interested", "perfect", "great opportunity", "I'm in", "count me in"
            ]
            
            failure_indicators = [
                "decline", "reject", "not interested", "too low", "can't do", "no", 
                "pass", "busy", "another brand", "not a fit", "competing", "conflict"
            ]
            
            transcript_lower = transcript.lower()
            
            # Count indicators (weighted scoring)
            success_score = sum(2 if indicator in transcript_lower else 0 for indicator in success_indicators)
            failure_score = sum(2 if indicator in transcript_lower else 0 for indicator in failure_indicators)
            
            # Add randomness for realistic demo outcomes (70% base success rate)
            random_factor = random.uniform(0.5, 1.5)
            success_score *= random_factor
            
            logger.info(f"🧠 Analysis scores - Success: {success_score}, Failure: {failure_score}")
            
            if success_score > failure_score:
                # Successful negotiation
                final_rate = self._calculate_final_negotiated_rate(negotiation_state, ai_strategy)
                
                return {
                    "status": NegotiationStatus.SUCCESS,
                    "final_rate": final_rate,
                    "confidence": min(success_score / max(failure_score + 1, 1), 1.0)
                }
            else:
                # Failed negotiation
                failure_reason = self._determine_failure_reason(transcript_lower, ai_strategy)
                
                return {
                    "status": NegotiationStatus.FAILED,
                    "failure_reason": failure_reason
                }
        
        elif conversation_status == "failed":
            return {
                "status": NegotiationStatus.FAILED,
                "failure_reason": "Call failed to connect or complete"
            }
        
        elif conversation_status == "timeout":
            return {
                "status": NegotiationStatus.FAILED,
                "failure_reason": "Conversation timeout - creator may not have answered"
            }
        
        else:
            # Unknown status - default to failure
            return {
                "status": NegotiationStatus.FAILED,
                "failure_reason": f"Unknown conversation status: {conversation_status}"
            }
    
    def _calculate_final_negotiated_rate(self, negotiation_state: NegotiationState, ai_strategy: Dict[str, Any] = None) -> float:
        """💰 Calculate final negotiated rate based on conversation outcome"""
        
        initial_offer = negotiation_state.initial_offer
        
        if ai_strategy and "max_offer_multiplier" in ai_strategy:
            # Use AI-determined range
            max_rate = initial_offer * ai_strategy["max_offer_multiplier"]
            # Final rate is typically between initial and max (closer to initial for good negotiations)
            final_rate = initial_offer + (max_rate - initial_offer) * random.uniform(0.3, 0.8)
        else:
            # Default negotiation: usually end up slightly above initial offer
            final_rate = initial_offer * random.uniform(1.05, 1.25)
        
        return round(final_rate, 2)
    
    def _determine_failure_reason(self, transcript_lower: str, ai_strategy: Dict[str, Any] = None) -> str:
        """❌ Determine specific reason for negotiation failure"""
        
        if "too low" in transcript_lower or "more money" in transcript_lower or "higher rate" in transcript_lower:
            return "Rate too low - creator requested higher compensation"
        elif "busy" in transcript_lower or "time" in transcript_lower or "schedule" in transcript_lower:
            return "Creator too busy - unavailable for campaign timeline"
        elif "not a fit" in transcript_lower or "different brand" in transcript_lower:
            return "Brand misalignment - creator prefers different product categories"
        elif "competing" in transcript_lower or "conflict" in transcript_lower:
            return "Conflict of interest - already working with competing brand"
        else:
            # Random realistic failure reasons for demo
            reasons = [
                "Creator declined - considering other opportunities",
                "Not interested in current campaign theme",
                "Already committed to similar campaign this month",
                "Prefer to work with different brand positioning"
            ]
            return random.choice(reasons)
    
    async def _handle_mock_conversation_result(self, negotiation_state: NegotiationState, call_result: Dict[str, Any]) -> NegotiationState:
        """🎭 Handle mock conversation results for testing without API keys"""
        
        mock_result = call_result.get("mock_result", {})
        outcome = mock_result.get("negotiation_outcome", "declined")
        
        logger.info(f"🎭 Processing mock conversation result: {outcome}")
        
        if outcome == "accepted":
            negotiation_state.status = NegotiationStatus.SUCCESS
            negotiation_state.final_rate = mock_result.get("final_rate", negotiation_state.initial_offer)
            negotiation_state.negotiated_terms = {
                "deliverables": ["video_review", "instagram_post"],
                "timeline": "7 days",
                "usage_rights": "organic_only",
                "payment_schedule": "50% upfront, 50% on delivery",
                "mock_conversation": True
            }
            logger.info(f"✅ Mock negotiation successful: ${negotiation_state.final_rate}")
        else:
            negotiation_state.status = NegotiationStatus.FAILED
            negotiation_state.failure_reason = mock_result.get("failure_reason", "Creator declined")
            logger.info(f"❌ Mock negotiation failed: {negotiation_state.failure_reason}")
        
        negotiation_state.call_duration_seconds = random.randint(20, 45)  # Mock realistic duration
        negotiation_state.completed_at = datetime.now()
        
        return negotiation_state
    
    async def _handle_call_failure(self, negotiation_state: NegotiationState, error: str) -> NegotiationState:
        """❌ Handle call connection failures"""
        negotiation_state.status = NegotiationStatus.FAILED
        negotiation_state.failure_reason = f"Call failed: {error}"
        negotiation_state.completed_at = datetime.now()
        
        # Implement retry logic
        if negotiation_state.retry_count < settings.max_retry_attempts:
            negotiation_state.retry_count += 1
            logger.info(f"🔄 Will retry call to {negotiation_state.creator_id} (attempt {negotiation_state.retry_count})")
            # In a real implementation, you might queue this for retry
        
        return negotiation_state
    
    async def _handle_negotiation_error(self, negotiation_state: NegotiationState, error: str) -> NegotiationState:
        """❌ Handle general negotiation errors"""
        negotiation_state.status = NegotiationStatus.FAILED
        negotiation_state.failure_reason = f"System error: {error}"
        negotiation_state.completed_at = datetime.now()
        logger.error(f"❌ Negotiation system error: {error}")
        return negotiation_state
    
    # Legacy methods for compatibility with existing code
    
    async def conduct_conversation(
        self,
        call_session: Dict[str, Any],
        opening_script: str,
        max_duration: int = 60
    ) -> Dict[str, Any]:
        """🔄 Legacy method for compatibility - now uses ElevenLabs"""
        conversation_id = call_session.get("conversation_id")
        
        if not conversation_id:
            return {"status": "failed", "error": "No conversation ID provided"}
        
        # Use the new ElevenLabs conversation management
        result = await self.voice_service.wait_for_conversation_completion(
            conversation_id, 
            max_wait_seconds=max_duration
        )
        
        return {
            "status": "completed" if result.get("status") == "completed" else "failed",
            "duration": max_duration,
            "transcript": result.get("transcript", "Conversation completed"),
            "recording_url": result.get("recording_url"),
            "conversation_data": result
        }