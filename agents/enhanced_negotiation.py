# agents/enhanced_negotiation.py
import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

from models.campaign import (
    CampaignData, CreatorMatch, NegotiationState, 
    NegotiationStatus, CallStatus
)
from services.elevenlabs_voice_service import VoiceServiceFactory
from services.pricing import PricingService
from config.settings import settings

logger = logging.getLogger(__name__)

class EnhancedNegotiationAgent:
    """
    🎯 ENHANCED NEGOTIATION AGENT
    Uses ElevenLabs dynamic variables and structured analysis for better outcomes
    """
    
    def __init__(self):
        self.voice_service = VoiceServiceFactory.create_voice_service(
            api_key=settings.elevenlabs_api_key,
            agent_id=settings.elevenlabs_agent_id,
            phone_number_id=settings.elevenlabs_phone_number_id,
            use_mock=settings.mock_calls,
        )
        self.pricing_service = PricingService()
    
    async def negotiate(
        self, 
        influencer_match: CreatorMatch, 
        campaign_data: CampaignData,
        ai_strategy: Dict[str, Any] = None
    ) -> NegotiationState:
        """
        🎯 Enhanced negotiation with structured data extraction
        """
        creator = influencer_match.creator
        
        # Initialize negotiation state
        negotiation_state = NegotiationState(
            creator_id=creator.id,
            campaign_id=campaign_data.id,
            initial_offer=self._calculate_strategic_offer(influencer_match, ai_strategy)
        )
        
        logger.info(f"📞 Starting enhanced negotiation with {creator.name}")
        logger.info(f"💰 Strategic offer: ${negotiation_state.initial_offer:,.2f}")
        
        try:
            # PHASE 1: Prepare enhanced conversation context
            conversation_context = self._prepare_enhanced_context(
                creator, campaign_data, negotiation_state, ai_strategy
            )
            
            # PHASE 2: Initiate ElevenLabs call with dynamic variables
            negotiation_state.status = NegotiationStatus.CALLING
            call_result = await self.voice_service.initiate_negotiation_call(
                creator_phone=creator.phone_number,
                creator_profile=conversation_context["creator_profile"],
                campaign_data=conversation_context["campaign_data"],
                pricing_strategy=conversation_context["pricing_strategy"]
            )
            
            if call_result["status"] != "success":
                return await self._handle_call_failure(negotiation_state, call_result.get("error"))
            
            # PHASE 3: Store conversation tracking data
            negotiation_state.conversation_id = call_result.get("conversation_id")
            negotiation_state.call_id = call_result.get("call_id")
            negotiation_state.status = NegotiationStatus.NEGOTIATING
            negotiation_state.call_status = CallStatus.COMPLETED
            
            logger.info(f"📱 Call initiated - Conversation ID: {negotiation_state.conversation_id}")
            
            # PHASE 4: Wait for completion and extract structured analysis
            conversation_result = await self.voice_service.wait_for_conversation_completion_with_analysis(
                negotiation_state.conversation_id,
                max_wait_seconds=300  # 3 minutes max
            )
            
            # PHASE 5: Process structured analysis data
            final_result = await self._process_conversation_analysis(
                negotiation_state, conversation_result, ai_strategy
            )
            
            return final_result
            
        except Exception as e:
            logger.error(f"❌ Enhanced negotiation failed with {creator.name}: {e}")
            return await self._handle_negotiation_error(negotiation_state, str(e))
    
    def _calculate_strategic_offer(
        self, 
        influencer_match: CreatorMatch, 
        ai_strategy: Dict[str, Any] = None
    ) -> float:
        """💰 Calculate strategic opening offer"""
        
        base_rate = influencer_match.estimated_rate
        
        if ai_strategy:
            # Use AI-determined strategy
            approach = ai_strategy.get("negotiation_approach", "collaborative")
            multiplier = ai_strategy.get("opening_offer_multiplier", 0.95)
            
            if approach == "aggressive":
                multiplier *= 0.9  # Start lower for aggressive approach
            elif approach == "premium":
                multiplier *= 1.05  # Start higher for premium approach
            
            strategic_offer = base_rate * multiplier
            
            logger.info(f"🧠 AI Strategy: {approach} approach with {multiplier:.2f}x multiplier")
        else:
            # Default strategy: start slightly below market rate
            strategic_offer = base_rate * 0.95
        
        return round(strategic_offer, 2)
    
    def _prepare_enhanced_context(
        self,
        creator,
        campaign_data: CampaignData,
        negotiation_state: NegotiationState,
        ai_strategy: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """📝 Prepare enhanced context for ElevenLabs conversation"""
        
        # Enhanced creator profile
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
            "platform": creator.platform.value,
            "tier": creator.tier.value,
            "specialties": creator.specialties,
            "about": f"Content creator specializing in {creator.niche} with {creator.followers//1000}K followers",
            "audience_type": f"{creator.niche.title()} Enthusiasts"
        }
        
        # Enhanced campaign data
        enhanced_campaign_data = {
            "brand_name": campaign_data.brand_name,
            "product_name": campaign_data.product_name,
            "product_description": campaign_data.product_description,
            "target_audience": campaign_data.target_audience,
            "campaign_goal": campaign_data.campaign_goal,
            "product_niche": campaign_data.product_niche,
            "total_budget": campaign_data.total_budget
        }
        
        # Enhanced pricing strategy
        max_offer = self._calculate_max_offer(negotiation_state.initial_offer, ai_strategy)
        pricing_strategy = {
            "initial_offer": negotiation_state.initial_offer,
            "max_offer": max_offer,
            "negotiation_room": max_offer - negotiation_state.initial_offer,
            "approach": ai_strategy.get("negotiation_approach", "collaborative") if ai_strategy else "collaborative"
        }
        
        return {
            "creator_profile": creator_profile,
            "campaign_data": enhanced_campaign_data,
            "pricing_strategy": pricing_strategy,
            "ai_strategy": ai_strategy or {}
        }
    
    def _calculate_max_offer(self, initial_offer: float, ai_strategy: Dict[str, Any] = None) -> float:
        """Calculate maximum offer we're willing to pay"""
        
        if ai_strategy and "max_offer_multiplier" in ai_strategy:
            max_multiplier = ai_strategy["max_offer_multiplier"]
        else:
            max_multiplier = 1.25  # Default 25% above initial
        
        return round(initial_offer * max_multiplier, 2)
    
    async def _process_conversation_analysis(
        self,
        negotiation_state: NegotiationState,
        conversation_result: Dict[str, Any],
        ai_strategy: Dict[str, Any] = None
    ) -> NegotiationState:
        """
        🧠 Process ElevenLabs conversation analysis into structured negotiation data
        """
        
        # Calculate call duration
        start_time = negotiation_state.started_at
        end_time = datetime.now()
        duration_seconds = int((end_time - start_time).total_seconds())
        negotiation_state.call_duration_seconds = duration_seconds
        
        # Extract analysis data
        analysis_data = conversation_result.get("analysis_data") or {}
        
        # Store basic conversation data
        negotiation_state.call_transcript = conversation_result.get("transcript", "")
        negotiation_state.call_recording_url = conversation_result.get("recording_url")
        negotiation_state.completed_at = datetime.now()
        
        # Process negotiation outcome
        outcome = analysis_data.get("negotiation_outcome", "unclear")
        
        if outcome == "accepted":
            # SUCCESS: Extract negotiated terms
            negotiation_state.status = NegotiationStatus.SUCCESS
            negotiation_state.final_rate = self._extract_final_rate(analysis_data, negotiation_state)
            negotiation_state.negotiated_terms = self._extract_negotiated_terms(
                analysis_data, negotiation_state, ai_strategy
            )
            
            logger.info(f"✅ Negotiation successful: ${negotiation_state.final_rate:,.2f}")
            logger.info(f"📋 Terms: {negotiation_state.negotiated_terms}")
            
        elif outcome == "needs_followup":
            # FOLLOW-UP REQUIRED: Store for future processing
            negotiation_state.status = NegotiationStatus.PENDING
            negotiation_state.failure_reason = "Follow-up required - creator needs more time to decide"
            
            # Store follow-up information
            negotiation_state.negotiated_terms = {
                "follow_up_required": True,
                "follow_up_reason": analysis_data.get("conversation_summary", "Creator needs time to consider"),
                "objections_to_address": analysis_data.get("objections_raised", []),
                "enthusiasm_level": analysis_data.get("creator_enthusiasm_level", 5)
            }
            
            logger.info(f"🔄 Follow-up required: {negotiation_state.failure_reason}")
            
        else:
            # FAILURE: Extract failure details
            negotiation_state.status = NegotiationStatus.FAILED
            negotiation_state.failure_reason = self._determine_enhanced_failure_reason(analysis_data)
            
            logger.info(f"❌ Negotiation failed: {negotiation_state.failure_reason}")
        
        # Store analysis metadata
        negotiation_state.negotiated_terms.update({
            "analysis_data": analysis_data,
            "conversation_id": negotiation_state.conversation_id,
            "call_duration_seconds": duration_seconds,
            "analysis_confidence": self._calculate_analysis_confidence(analysis_data)
        })
        
        return negotiation_state
    
    def _extract_final_rate(
        self, 
        analysis_data: Dict[str, Any], 
        negotiation_state: NegotiationState
    ) -> float:
        """💰 Extract final negotiated rate from analysis"""
        
        # First try to get from ElevenLabs analysis
        final_rate = analysis_data.get("final_rate_mentioned")
        
        if final_rate and isinstance(final_rate, (int, float)) and final_rate > 0:
            return float(final_rate)
        
        # Fallback: Estimate based on conversation outcome and strategy
        initial_offer = negotiation_state.initial_offer
        enthusiasm_level = analysis_data.get("creator_enthusiasm_level", 5)
        
        if enthusiasm_level >= 8:
            # High enthusiasm - likely accepted near initial offer
            return initial_offer * 1.05
        elif enthusiasm_level >= 6:
            # Moderate enthusiasm - likely negotiated upward
            return initial_offer * 1.15
        else:
            # Lower enthusiasm - probably negotiated higher
            return initial_offer * 1.25
    
    def _extract_negotiated_terms(
        self, 
        analysis_data: Dict[str, Any],
        negotiation_state: NegotiationState,
        ai_strategy: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """📋 Extract detailed negotiated terms from analysis"""
        
        # Extract deliverables
        deliverables_discussed = analysis_data.get("deliverables_discussed", [])
        if not deliverables_discussed:
            # Default deliverables based on creator tier and platform
            deliverables_discussed = self._get_default_deliverables(negotiation_state)
        
        # Extract timeline
        timeline = analysis_data.get("timeline_mentioned", "7 days")
        if not timeline or timeline == "not_discussed":
            timeline = "7 days"  # Default
        
        # Extract usage rights
        usage_rights = analysis_data.get("usage_rights_discussed", "organic_only")
        if usage_rights == "not_discussed":
            usage_rights = "organic_only"  # Default safe option
        
        # Payment schedule based on rate and negotiation
        payment_schedule = self._determine_payment_schedule(
            negotiation_state.final_rate, 
            analysis_data
        )
        
        # Compile negotiated terms
        terms = {
            "deliverables": deliverables_discussed,
            "timeline": timeline,
            "usage_rights": usage_rights,
            "payment_schedule": payment_schedule,
            "final_rate": negotiation_state.final_rate,
            "negotiation_notes": analysis_data.get("conversation_summary", ""),
            "creator_enthusiasm": analysis_data.get("creator_enthusiasm_level", 5),
            "key_quotes": analysis_data.get("key_quotes", []),
            "objections_addressed": analysis_data.get("objections_raised", []),
            
            # Additional terms for contract generation
            "content_approval_process": "Brand reviews draft within 24 hours, final approval within 48 hours",
            "revision_policy": "Up to 2 minor revisions included",
            "posting_coordination": "Coordinate posting schedule with brand team",
            "performance_tracking": "Brand will provide performance metrics post-campaign",
            
            # Legal and compliance
            "brand_guidelines_required": True,
            "disclosure_requirements": "Must include #ad or #sponsored as per FTC guidelines",
            "cancellation_policy": "48 hours notice required, 50% payment for cancellation"
        }
        
        return terms
    
    def _get_default_deliverables(self, negotiation_state: NegotiationState) -> List[str]:
        """Get default deliverables based on creator and campaign context"""
        
        # This could be enhanced to look up creator platform and tier
        return ["video_review", "instagram_post", "instagram_story"]
    
    def _determine_payment_schedule(
        self, 
        final_rate: float, 
        analysis_data: Dict[str, Any]
    ) -> str:
        """📅 Determine payment schedule based on rate and negotiation"""
        
        if final_rate > 5000:
            # High-value collaborations: Milestone-based payments
            return "25% on contract signing, 50% on content delivery, 25% after posting"
        elif final_rate > 2000:
            # Medium-value: Split payment
            return "50% upfront on contract signing, 50% on content delivery and approval"
        else:
            # Smaller collaborations: Simpler payment
            return "Full payment on content delivery and approval"
    
    def _determine_enhanced_failure_reason(self, analysis_data: Dict[str, Any]) -> str:
        """❌ Determine detailed failure reason from analysis"""
        
        objections = analysis_data.get("objections_raised", [])
        conversation_summary = analysis_data.get("conversation_summary", "")
        
        if "price_too_low" in objections:
            return "Rate too low - creator requested higher compensation than our maximum budget"
        elif "timeline_tight" in objections:
            return "Timeline too tight - creator unavailable for campaign schedule"
        elif "brand_misalignment" in objections:
            return "Brand misalignment - creator prefers different product categories"
        elif "already_committed" in objections:
            return "Conflict of interest - creator already working with competing brand"
        elif analysis_data.get("creator_enthusiasm_level", 5) < 3:
            return "Low interest - creator not enthusiastic about collaboration"
        else:
            # Use conversation summary or default
            return conversation_summary or "Creator declined - exploring other opportunities"
    
    def _calculate_analysis_confidence(self, analysis_data: Dict[str, Any]) -> float:
        """📊 Calculate confidence in analysis results"""
        
        confidence_factors = []
        
        # Check if key fields are populated
        if analysis_data.get("negotiation_outcome") != "unclear":
            confidence_factors.append(0.3)
        
        if analysis_data.get("final_rate_mentioned"):
            confidence_factors.append(0.2)
        
        if analysis_data.get("conversation_summary"):
            confidence_factors.append(0.2)
        
        if analysis_data.get("creator_enthusiasm_level", 0) > 0:
            confidence_factors.append(0.15)
        
        if analysis_data.get("key_quotes"):
            confidence_factors.append(0.15)
        
        return sum(confidence_factors)
    
    async def _handle_call_failure(self, negotiation_state: NegotiationState, error: str) -> NegotiationState:
        """❌ Handle call connection failures"""
        negotiation_state.status = NegotiationStatus.FAILED
        negotiation_state.call_status = CallStatus.CANCELLED
        negotiation_state.failure_reason = f"Call failed to connect: {error}"
        negotiation_state.completed_at = datetime.now()
        
        logger.warning(f"📞 Call failed for {negotiation_state.creator_id}: {error}")
        
        return negotiation_state
    
    async def _handle_negotiation_error(self, negotiation_state: NegotiationState, error: str) -> NegotiationState:
        """❌ Handle general negotiation system errors"""
        negotiation_state.status = NegotiationStatus.FAILED
        negotiation_state.failure_reason = f"System error during negotiation: {error}"
        negotiation_state.completed_at = datetime.now()
        
        logger.error(f"❌ Negotiation system error for {negotiation_state.creator_id}: {error}")
        
        return negotiation_state

class NegotiationResultValidator:
    """
    🔍 Validates negotiation results before passing to contract generation
    """
    
    @staticmethod
    def validate_negotiation_result(negotiation_state: NegotiationState) -> Dict[str, Any]:
        """Validate negotiation state for contract generation"""
        
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "missing_fields": []
        }
        
        # Check if negotiation was successful
        if negotiation_state.status != NegotiationStatus.SUCCESS:
            validation_result["is_valid"] = False
            validation_result["errors"].append(f"Negotiation status is {negotiation_state.status.value}, not successful")
            return validation_result
        
        # Check for required fields
        required_fields = {
            "final_rate": negotiation_state.final_rate,
            "negotiated_terms": negotiation_state.negotiated_terms,
            "conversation_id": negotiation_state.conversation_id
        }
        
        for field_name, field_value in required_fields.items():
            if not field_value:
                validation_result["missing_fields"].append(field_name)
                validation_result["warnings"].append(f"Missing {field_name}")
        
        # Validate final rate
        if negotiation_state.final_rate and negotiation_state.final_rate <= 0:
            validation_result["errors"].append("Final rate must be greater than 0")
            validation_result["is_valid"] = False
        
        # Validate negotiated terms structure
        if negotiation_state.negotiated_terms:
            required_terms = ["deliverables", "timeline", "usage_rights", "payment_schedule"]
            for term in required_terms:
                if term not in negotiation_state.negotiated_terms:
                    validation_result["missing_fields"].append(f"negotiated_terms.{term}")
                    validation_result["warnings"].append(f"Missing negotiated term: {term}")
        
        # Set validity based on errors
        if validation_result["errors"]:
            validation_result["is_valid"] = False
        
        return validation_result