# agents/enhanced_negotiation_manager.py
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
from pydantic import BaseModel

from models.campaign import CampaignData, CreatorMatch, NegotiationState, NegotiationStatus
from services.enhanced_voice import EnhancedVoiceService
from services.email_service import EmailService

logger = logging.getLogger(__name__)

class NegotiationPhase(str, Enum):
    INITIAL_CALL = "initial_call"
    POST_CALL_ANALYSIS = "post_call_analysis"
    HUMAN_REVIEW = "human_review"
    FOLLOW_UP_REQUIRED = "follow_up_required"
    SPONSOR_APPROVAL = "sponsor_approval"
    FINAL_CONFIRMATION = "final_confirmation"
    COMPLETED = "completed"
    FAILED = "failed"

class HumanDecision(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    REQUEST_CHANGES = "request_changes"
    SCHEDULE_FOLLOW_UP = "schedule_follow_up"
    ESCALATE = "escalate"

class SponsorDecision(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"
    PENDING = "pending"

class CallAnalysis(BaseModel):
    """Comprehensive call analysis structure"""
    conversation_id: str
    transcript: str
    duration_seconds: int
    recording_url: Optional[str]
    
    # Basic outcomes
    negotiation_outcome: str  # accepted, declined, needs_followup
    final_rate_mentioned: Optional[float]
    creator_enthusiasm_level: int  # 1-10
    
    # Detailed analysis
    deliverables_discussed: List[str]
    timeline_mentioned: str
    usage_rights_discussed: str
    payment_schedule_mentioned: str
    
    # Objections and concerns
    objections_raised: List[str]
    concerns_mentioned: List[str]
    follow_up_questions: List[str]
    
    # Contact preferences
    preferred_contact_method: str
    best_time_to_contact: str
    follow_up_deadline: Optional[datetime]
    
    # Quality metrics
    call_quality_score: float  # 0-1
    analysis_confidence: float  # 0-1
    requires_human_review: bool
    
    # Additional insights
    key_quotes: List[str]
    sentiment_analysis: str  # positive, neutral, negative
    decision_factors: List[str]

class HumanReviewRequest(BaseModel):
    """Human review request structure"""
    negotiation_id: str
    creator_name: str
    call_analysis: CallAnalysis
    ai_recommendation: str
    review_deadline: datetime
    priority_level: str  # high, medium, low
    
    # Context for human reviewer
    campaign_context: Dict[str, Any]
    budget_constraints: Dict[str, Any]
    alternative_options: List[str]

class SponsorApprovalRequest(BaseModel):
    """Sponsor approval request structure"""
    campaign_id: str
    negotiation_summary: Dict[str, Any]
    recommended_influencers: List[Dict[str, Any]]
    total_cost: float
    expected_roi: Dict[str, Any]
    approval_deadline: datetime
    
    # Approval workflow
    approval_url: str
    rejection_url: str
    revision_url: str

class EnhancedNegotiationManager:
    """
    🎯 ENHANCED NEGOTIATION MANAGER
    
    Complete workflow:
    1. ElevenLabs call execution
    2. Comprehensive post-call analysis
    3. Human-in-the-loop review
    4. Follow-up management
    5. Sponsor approval workflow
    6. Final confirmation
    """
    
    def __init__(self):
        self.voice_service = EnhancedVoiceService()
        self.email_service = EmailService()
        
        # Active negotiations tracking
        self.active_negotiations: Dict[str, Dict[str, Any]] = {}
        self.human_review_queue: List[HumanReviewRequest] = []
        self.sponsor_approval_queue: List[SponsorApprovalRequest] = []
        
        # Configuration
        self.auto_approve_threshold = 0.85  # Auto-approve if confidence > 85%
        self.human_review_timeout_hours = 24
        self.sponsor_approval_timeout_hours = 48
        self.follow_up_max_attempts = 3
    
    async def execute_enhanced_negotiation(
        self,
        creator_match: CreatorMatch,
        campaign_data: CampaignData,
        negotiation_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        🚀 Execute complete enhanced negotiation workflow
        """
        
        negotiation_id = f"neg_{creator_match.creator.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"🚀 Starting enhanced negotiation: {negotiation_id}")
        logger.info(f"🎯 Creator: {creator_match.creator.name}")
        logger.info(f"💰 Estimated Rate: ${creator_match.estimated_rate:,}")
        
        # Initialize negotiation tracking
        negotiation_tracker = {
            "negotiation_id": negotiation_id,
            "creator_match": creator_match,
            "campaign_data": campaign_data,
            "context": negotiation_context,
            "phase": NegotiationPhase.INITIAL_CALL,
            "started_at": datetime.now(),
            "call_analysis": None,
            "human_review": None,
            "sponsor_approval": None,
            "follow_up_history": [],
            "final_outcome": None
        }
        
        self.active_negotiations[negotiation_id] = negotiation_tracker
        
        try:
            # Phase 1: Execute initial call
            await self._execute_initial_call(negotiation_tracker)
            
            # Phase 2: Comprehensive post-call analysis
            await self._execute_post_call_analysis(negotiation_tracker)
            
            # Phase 3: Human review (if needed)
            await self._execute_human_review_workflow(negotiation_tracker)
            
            # Phase 4: Handle follow-ups (if needed)
            await self._execute_follow_up_workflow(negotiation_tracker)
            
            # Phase 5: Sponsor approval workflow
            await self._execute_sponsor_approval_workflow(negotiation_tracker)
            
            # Phase 6: Final confirmation
            await self._execute_final_confirmation(negotiation_tracker)
            
            return {
                "negotiation_id": negotiation_id,
                "status": "completed",
                "final_outcome": negotiation_tracker["final_outcome"],
                "total_duration": (datetime.now() - negotiation_tracker["started_at"]).total_seconds() / 3600,
                "phases_completed": self._get_completed_phases(negotiation_tracker)
            }
            
        except Exception as e:
            logger.error(f"❌ Enhanced negotiation failed: {e}")
            negotiation_tracker["phase"] = NegotiationPhase.FAILED
            negotiation_tracker["error"] = str(e)
            
            return {
                "negotiation_id": negotiation_id,
                "status": "failed",
                "error": str(e),
                "phase": negotiation_tracker["phase"]
            }
    
    async def _execute_initial_call(self, tracker: Dict[str, Any]):
        """📞 Execute initial ElevenLabs call"""
        
        logger.info(f"📞 Phase 1: Executing initial call")
        
        creator = tracker["creator_match"].creator
        campaign_data = tracker["campaign_data"]
        
        # Prepare enhanced call context
        creator_profile = {
            "id": creator.id,
            "name": creator.name,
            "niche": creator.niche,
            "followers": creator.followers,
            "engagement_rate": creator.engagement_rate,
            "platform": creator.platform.value,
            "typical_rate": creator.typical_rate
        }
        
        campaign_context = {
            "brand_name": campaign_data.brand_name,
            "product_name": campaign_data.product_name,
            "product_description": campaign_data.product_description,
            "target_audience": campaign_data.target_audience,
            "campaign_goal": campaign_data.campaign_goal
        }
        
        pricing_strategy = {
            "initial_offer": tracker["creator_match"].estimated_rate * 0.95,
            "max_offer": tracker["creator_match"].estimated_rate * 1.25
        }
        
        # Execute call
        call_result = await self.voice_service.initiate_negotiation_call(
            creator_phone=creator.phone_number,
            creator_profile=creator_profile,
            campaign_data=campaign_context,
            pricing_strategy=pricing_strategy
        )
        
        if call_result["status"] == "success":
            tracker["conversation_id"] = call_result["conversation_id"]
            tracker["call_id"] = call_result.get("call_id")
            
            # Wait for call completion with analysis
            conversation_result = await self.voice_service.wait_for_conversation_completion_with_analysis(
                tracker["conversation_id"],
                max_wait_seconds=300
            )
            
            tracker["conversation_result"] = conversation_result
            tracker["phase"] = NegotiationPhase.POST_CALL_ANALYSIS
            
            logger.info(f"✅ Call completed: {conversation_result.get('status')}")
        else:
            raise Exception(f"Call failed: {call_result.get('error')}")
    
    async def _execute_post_call_analysis(self, tracker: Dict[str, Any]):
        """🧠 Execute comprehensive post-call analysis"""
        
        logger.info(f"🧠 Phase 2: Executing post-call analysis")
        
        conversation_result = tracker["conversation_result"]
        
        # Extract comprehensive analysis
        call_analysis = self._extract_comprehensive_analysis(conversation_result, tracker)
        
        # Store analysis
        tracker["call_analysis"] = call_analysis
        
        # Determine next phase based on analysis
        if call_analysis.requires_human_review or call_analysis.analysis_confidence < self.auto_approve_threshold:
            tracker["phase"] = NegotiationPhase.HUMAN_REVIEW
            logger.info(f"🔄 Requires human review (confidence: {call_analysis.analysis_confidence:.2f})")
        elif call_analysis.negotiation_outcome == "needs_followup":
            tracker["phase"] = NegotiationPhase.FOLLOW_UP_REQUIRED
            logger.info(f"🔄 Follow-up required")
        elif call_analysis.negotiation_outcome == "accepted":
            tracker["phase"] = NegotiationPhase.SPONSOR_APPROVAL
            logger.info(f"✅ Auto-approved, moving to sponsor approval")
        else:
            tracker["phase"] = NegotiationPhase.FAILED
            logger.info(f"❌ Call outcome: {call_analysis.negotiation_outcome}")
    
    def _extract_comprehensive_analysis(self, conversation_result: Dict[str, Any], tracker: Dict[str, Any]) -> CallAnalysis:
        """Extract comprehensive analysis from conversation"""
        
        # Use enhanced voice service analysis
        analysis_data = self.voice_service.extract_conversation_analysis(conversation_result)
        
        # Create comprehensive analysis
        call_analysis = CallAnalysis(
            conversation_id=tracker["conversation_id"],
            transcript=conversation_result.get("transcript", ""),
            duration_seconds=conversation_result.get("duration", 0),
            recording_url=conversation_result.get("recording_url"),
            
            # Basic outcomes from ElevenLabs analysis
            negotiation_outcome=analysis_data.get("negotiation_outcome", "unclear"),
            final_rate_mentioned=analysis_data.get("final_rate_mentioned"),
            creator_enthusiasm_level=analysis_data.get("creator_enthusiasm_level", 5),
            
            # Detailed terms
            deliverables_discussed=analysis_data.get("deliverables_discussed", []),
            timeline_mentioned=analysis_data.get("timeline_mentioned", "7 days"),
            usage_rights_discussed=analysis_data.get("usage_rights_discussed", "organic_only"),
            payment_schedule_mentioned=analysis_data.get("payment_schedule_mentioned", "50% upfront"),
            
            # Objections and concerns
            objections_raised=analysis_data.get("objections_raised", []),
            concerns_mentioned=self._extract_concerns(conversation_result.get("transcript", "")),
            follow_up_questions=self._extract_follow_up_questions(conversation_result.get("transcript", "")),
            
            # Contact preferences
            preferred_contact_method=self._extract_contact_preference(conversation_result.get("transcript", "")),
            best_time_to_contact=self._extract_best_contact_time(conversation_result.get("transcript", "")),
            follow_up_deadline=self._calculate_follow_up_deadline(analysis_data),
            
            # Quality metrics
            call_quality_score=self._calculate_call_quality(conversation_result),
            analysis_confidence=analysis_data.get("analysis_confidence", 0.5),
            requires_human_review=self._should_require_human_review(analysis_data, conversation_result),
            
            # Additional insights
            key_quotes=analysis_data.get("key_quotes", []),
            sentiment_analysis=self._analyze_sentiment(conversation_result.get("transcript", "")),
            decision_factors=self._extract_decision_factors(conversation_result.get("transcript", ""))
        )
        
        return call_analysis
    
    async def _execute_human_review_workflow(self, tracker: Dict[str, Any]):
        """👤 Execute human-in-the-loop review workflow"""
        
        if tracker["phase"] != NegotiationPhase.HUMAN_REVIEW:
            return
        
        logger.info(f"👤 Phase 3: Executing human review workflow")
        
        # Create human review request
        review_request = HumanReviewRequest(
            negotiation_id=tracker["negotiation_id"],
            creator_name=tracker["creator_match"].creator.name,
            call_analysis=tracker["call_analysis"],
            ai_recommendation=self._generate_ai_recommendation(tracker),
            review_deadline=datetime.now() + timedelta(hours=self.human_review_timeout_hours),
            priority_level=self._calculate_review_priority(tracker),
            campaign_context=self._prepare_campaign_context(tracker),
            budget_constraints=self._prepare_budget_context(tracker),
            alternative_options=self._prepare_alternative_options(tracker)
        )
        
        # Add to review queue
        self.human_review_queue.append(review_request)
        
        # Send review request notification
        await self._send_human_review_notification(review_request)
        
        # Wait for human decision (with timeout)
        human_decision = await self._wait_for_human_decision(review_request)
        
        tracker["human_review"] = {
            "decision": human_decision,
            "reviewed_at": datetime.now(),
            "reviewer_notes": "Human review completed"  # Would come from actual review
        }
        
        # Route based on human decision
        if human_decision == HumanDecision.APPROVE:
            tracker["phase"] = NegotiationPhase.SPONSOR_APPROVAL
        elif human_decision == HumanDecision.SCHEDULE_FOLLOW_UP:
            tracker["phase"] = NegotiationPhase.FOLLOW_UP_REQUIRED
        else:
            tracker["phase"] = NegotiationPhase.FAILED
        
        logger.info(f"👤 Human review completed: {human_decision.value}")
    
    async def _execute_follow_up_workflow(self, tracker: Dict[str, Any]):
        """🔄 Execute follow-up workflow"""
        
        if tracker["phase"] != NegotiationPhase.FOLLOW_UP_REQUIRED:
            return
        
        logger.info(f"🔄 Phase 4: Executing follow-up workflow")
        
        call_analysis = tracker["call_analysis"]
        
        # Schedule follow-up based on creator's preferences
        follow_up_delay = self._calculate_follow_up_delay(call_analysis)
        follow_up_method = call_analysis.preferred_contact_method
        
        # Wait for appropriate delay
        logger.info(f"⏰ Waiting {follow_up_delay} before follow-up via {follow_up_method}")
        
        # For demo, we'll simulate the follow-up
        await asyncio.sleep(5)  # In real implementation, this would be scheduled
        
        # Execute follow-up (email, call, or message)
        if follow_up_method == "email":
            follow_up_result = await self._send_follow_up_email(tracker)
        elif follow_up_method == "call":
            follow_up_result = await self._execute_follow_up_call(tracker)
        else:
            follow_up_result = await self._send_follow_up_message(tracker)
        
        tracker["follow_up_history"].append({
            "attempt": len(tracker["follow_up_history"]) + 1,
            "method": follow_up_method,
            "result": follow_up_result,
            "timestamp": datetime.now()
        })
        
        # Determine next phase based on follow-up result
        if follow_up_result.get("outcome") == "accepted":
            tracker["phase"] = NegotiationPhase.SPONSOR_APPROVAL
        elif len(tracker["follow_up_history"]) < self.follow_up_max_attempts:
            # Schedule another follow-up
            logger.info(f"🔄 Scheduling additional follow-up attempt")
        else:
            tracker["phase"] = NegotiationPhase.FAILED
            logger.info(f"❌ Max follow-up attempts reached")
    
    async def _execute_sponsor_approval_workflow(self, tracker: Dict[str, Any]):
        """📊 Execute sponsor approval workflow"""
        
        if tracker["phase"] != NegotiationPhase.SPONSOR_APPROVAL:
            return
        
        logger.info(f"📊 Phase 5: Executing sponsor approval workflow")
        
        # Create sponsor approval request
        approval_request = SponsorApprovalRequest(
            campaign_id=tracker["campaign_data"].id,
            negotiation_summary=self._create_negotiation_summary(tracker),
            recommended_influencers=[self._format_influencer_summary(tracker)],
            total_cost=tracker["call_analysis"].final_rate_mentioned or tracker["creator_match"].estimated_rate,
            expected_roi=self._calculate_expected_roi(tracker),
            approval_deadline=datetime.now() + timedelta(hours=self.sponsor_approval_timeout_hours),
            approval_url=f"/api/approval/{tracker['negotiation_id']}/approve",
            rejection_url=f"/api/approval/{tracker['negotiation_id']}/reject",
            revision_url=f"/api/approval/{tracker['negotiation_id']}/revise"
        )
        
        # Add to approval queue
        self.sponsor_approval_queue.append(approval_request)
        
        # Send approval request email
        await self._send_sponsor_approval_email(approval_request)
        
        # Wait for sponsor decision (with timeout and periodic reminders)
        sponsor_decision = await self._wait_for_sponsor_decision(approval_request)
        
        tracker["sponsor_approval"] = {
            "decision": sponsor_decision,
            "approved_at": datetime.now(),
            "approval_notes": "Sponsor approval completed"
        }
        
        # Route based on sponsor decision
        if sponsor_decision == SponsorDecision.APPROVED:
            tracker["phase"] = NegotiationPhase.FINAL_CONFIRMATION
        elif sponsor_decision == SponsorDecision.NEEDS_REVISION:
            tracker["phase"] = NegotiationPhase.FOLLOW_UP_REQUIRED
        else:
            tracker["phase"] = NegotiationPhase.FAILED
        
        logger.info(f"📊 Sponsor decision: {sponsor_decision.value}")
    
    async def _execute_final_confirmation(self, tracker: Dict[str, Any]):
        """✅ Execute final confirmation"""
        
        if tracker["phase"] != NegotiationPhase.FINAL_CONFIRMATION:
            return
        
        logger.info(f"✅ Phase 6: Executing final confirmation")
        
        # Send final confirmation to creator
        confirmation_result = await self._send_final_confirmation(tracker)
        
        tracker["final_outcome"] = {
            "status": "confirmed",
            "final_rate": tracker["call_analysis"].final_rate_mentioned,
            "deliverables": tracker["call_analysis"].deliverables_discussed,
            "timeline": tracker["call_analysis"].timeline_mentioned,
            "confirmed_at": datetime.now()
        }
        
        tracker["phase"] = NegotiationPhase.COMPLETED
        
        logger.info(f"✅ Negotiation successfully completed")
    
    # Helper methods for analysis and workflow management
    
    def _extract_concerns(self, transcript: str) -> List[str]:
        """Extract concerns from transcript"""
        concerns = []
        concern_keywords = ["worried", "concerned", "hesitant", "unsure", "problem", "issue"]
        
        for keyword in concern_keywords:
            if keyword in transcript.lower():
                # Extract surrounding context
                sentences = transcript.split('.')
                for sentence in sentences:
                    if keyword in sentence.lower():
                        concerns.append(sentence.strip())
        
        return concerns[:3]  # Limit to top 3 concerns
    
    def _extract_follow_up_questions(self, transcript: str) -> List[str]:
        """Extract follow-up questions from transcript"""
        questions = []
        question_patterns = ["?", "can you", "could you", "would you", "what about", "how about"]
        
        sentences = transcript.split('.')
        for sentence in sentences:
            if any(pattern in sentence.lower() for pattern in question_patterns):
                questions.append(sentence.strip())
        
        return questions[:3]
    
    def _extract_contact_preference(self, transcript: str) -> str:
        """Extract preferred contact method"""
        if "email" in transcript.lower():
            return "email"
        elif "text" in transcript.lower() or "message" in transcript.lower():
            return "message"
        elif "call" in transcript.lower():
            return "call"
        else:
            return "email"  # Default
    
    def _extract_best_contact_time(self, transcript: str) -> str:
        """Extract best time to contact"""
        time_patterns = ["morning", "afternoon", "evening", "weekday", "weekend"]
        
        for pattern in time_patterns:
            if pattern in transcript.lower():
                return pattern
        
        return "business_hours"  # Default
    
    def _calculate_follow_up_deadline(self, analysis_data: Dict[str, Any]) -> Optional[datetime]:
        """Calculate when follow-up should occur"""
        
        timeline = analysis_data.get("timeline_mentioned", "7 days")
        
        if "day" in timeline.lower():
            try:
                days = int(timeline.split()[0])
                return datetime.now() + timedelta(days=min(days, 3))
            except:
                pass
        
        return datetime.now() + timedelta(days=2)  # Default 2 days
    
    def _should_require_human_review(self, analysis_data: Dict[str, Any], conversation_result: Dict[str, Any]) -> bool:
        """Determine if human review is required"""
        
        # Require human review if:
        # 1. Low confidence
        if analysis_data.get("analysis_confidence", 0) < 0.7:
            return True
        
        # 2. Complex objections
        if len(analysis_data.get("objections_raised", [])) > 2:
            return True
        
        # 3. High-value negotiation
        if analysis_data.get("final_rate_mentioned", 0) > 5000:
            return True
        
        # 4. Unclear outcome
        if analysis_data.get("negotiation_outcome") == "unclear":
            return True
        
        return False
    
    def _generate_ai_recommendation(self, tracker: Dict[str, Any]) -> str:
        """Generate AI recommendation for human reviewer"""
        
        call_analysis = tracker["call_analysis"]
        
        if call_analysis.negotiation_outcome == "accepted":
            return f"RECOMMEND APPROVAL: Creator accepted at ${call_analysis.final_rate_mentioned:,}. High enthusiasm ({call_analysis.creator_enthusiasm_level}/10)."
        elif call_analysis.negotiation_outcome == "needs_followup":
            return f"RECOMMEND FOLLOW-UP: Creator interested but needs time. Schedule follow-up in {call_analysis.follow_up_deadline}."
        else:
            return f"RECOMMEND REJECTION: Creator declined. Objections: {', '.join(call_analysis.objections_raised)}"
    
    # API methods for external interaction
    
    def get_negotiation_status(self, negotiation_id: str) -> Optional[Dict[str, Any]]:
        """Get current negotiation status"""
        return self.active_negotiations.get(negotiation_id)
    
    def get_human_review_queue(self) -> List[HumanReviewRequest]:
        """Get pending human reviews"""
        return self.human_review_queue
    
    def submit_human_decision(self, negotiation_id: str, decision: HumanDecision, notes: str = ""):
        """Submit human review decision"""
        # Implementation would update the negotiation tracker
        logger.info(f"👤 Human decision for {negotiation_id}: {decision.value}")
    
    def submit_sponsor_decision(self, negotiation_id: str, decision: SponsorDecision, notes: str = ""):
        """Submit sponsor approval decision"""
        # Implementation would update the negotiation tracker
        logger.info(f"📊 Sponsor decision for {negotiation_id}: {decision.value}")
    
    async def _send_human_review_notification(self, request: HumanReviewRequest):
        """Send notification to human reviewer"""
        # Implementation would send email/notification
        logger.info(f"📧 Sent human review notification for {request.negotiation_id}")
    
    async def _send_sponsor_approval_email(self, request: SponsorApprovalRequest):
        """Send approval request email to sponsor"""
        # Implementation would send email with approval links
        logger.info(f"📧 Sent sponsor approval email for {request.campaign_id}")
    
    async def _wait_for_human_decision(self, request: HumanReviewRequest) -> HumanDecision:
        """Wait for human decision with timeout"""
        # Mock implementation - in real system would wait for actual decision
        await asyncio.sleep(2)
        return HumanDecision.APPROVE  # Mock decision
    
    async def _wait_for_sponsor_decision(self, request: SponsorApprovalRequest) -> SponsorDecision:
        """Wait for sponsor decision with timeout and reminders"""
        # Mock implementation - in real system would wait for actual decision
        await asyncio.sleep(2)
        return SponsorDecision.APPROVED  # Mock decision