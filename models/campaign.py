# models/campaign.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# ================================
# CAMPAIGN MODELS
# ================================

class CampaignStatus(str, Enum):
    ACTIVE = "active"
    DRAFT = "draft"
    COMPLETED = "completed"
    PAUSED = "paused"

class CampaignWebhook(BaseModel):
    """Incoming webhook data from campaign creation"""
    campaign_id: str
    product_name: str
    brand_name: str
    product_description: str
    target_audience: str
    campaign_goal: str
    product_niche: str
    total_budget: float

class CampaignData(BaseModel):
    """Internal campaign representation"""
    id: str
    product_name: str
    brand_name: str
    product_description: str
    target_audience: str
    key_use_cases: Optional[str] = None
    campaign_goal: str
    product_niche: str
    total_budget: float
    status: CampaignStatus = CampaignStatus.ACTIVE
    influencer_count: int = 0
    campaign_code: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

# ================================
# CREATOR MODELS
# ================================

class CreatorTier(str, Enum):
    MICRO = "micro_influencer"      # < 100K followers
    MACRO = "macro_influencer"      # 100K - 1M followers  
    MEGA = "mega_influencer"        # > 1M followers

class Platform(str, Enum):
    YOUTUBE = "YouTube"
    INSTAGRAM = "Instagram"
    TIKTOK = "TikTok"
    TWITCH = "Twitch"

class Availability(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    LIMITED = "limited"
    BUSY = "busy"

class Creator(BaseModel):
    """Creator model based on creators.json structure"""
    id: str
    name: str
    platform: Platform
    followers: int
    niche: str
    typical_rate: float
    engagement_rate: float
    average_views: int
    last_campaign_date: str
    availability: Availability
    location: str
    phone_number: str
    languages: List[str]
    specialties: List[str]
    
    # Audience demographics
    audience_demographics: Dict[str, Any]
    
    # Performance metrics
    performance_metrics: Dict[str, float]
    
    # Recent campaigns and rate history
    recent_campaigns: List[Dict[str, Any]]
    rate_history: Dict[str, float]
    
    preferred_collaboration_style: str
    
    @property
    def tier(self) -> CreatorTier:
        """Determine creator tier based on follower count"""
        if self.followers < 100000:
            return CreatorTier.MICRO
        elif self.followers < 1000000:
            return CreatorTier.MACRO
        else:
            return CreatorTier.MEGA
    
    @property
    def cost_per_view(self) -> float:
        """Calculate cost per view"""
        return self.typical_rate / self.average_views if self.average_views > 0 else 0

class CreatorMatch(BaseModel):
    """Represents a matched creator with similarity score"""
    creator: Creator
    similarity_score: float
    rate_compatible: bool
    match_reasons: List[str]
    estimated_rate: float
    
    @property
    def overall_score(self) -> float:
        """Combined score for ranking matches"""
        base_score = self.similarity_score
        rate_bonus = 0.1 if self.rate_compatible else -0.1
        availability_bonus = 0.05 if self.creator.availability.value == "excellent" else 0
        
        return min(base_score + rate_bonus + availability_bonus, 1.0)

# ================================
# NEGOTIATION MODELS
# ================================

class NegotiationStatus(str, Enum):
    PENDING = "pending"
    CALLING = "calling"
    NEGOTIATING = "negotiating"
    SUCCESS = "success"
    FAILED = "failed"

class CallStatus(str, Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    NO_ANSWER = "no_answer"
    CANCELLED = "cancelled"

class EmailStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    REPLIED = "replied"
    BOUNCED = "bounced"

class NegotiationState(BaseModel):
    """Tracks the state of a single negotiation"""
    creator_id: str
    campaign_id: str
    status: NegotiationStatus = NegotiationStatus.PENDING
    call_status: CallStatus = CallStatus.PENDING
    email_status: EmailStatus = EmailStatus.PENDING
    
    # ElevenLabs integration fields
    conversation_id: Optional[str] = None
    call_id: Optional[str] = None
    
    # Pricing
    initial_offer: Optional[float] = None
    final_rate: Optional[float] = None
    negotiated_terms: Dict[str, Any] = Field(default_factory=dict)
    
    # Call details
    call_duration_seconds: int = 0
    call_recording_url: Optional[str] = None
    call_transcript: Optional[str] = None
    
    # Retry logic
    retry_count: int = 0
    failure_reason: Optional[str] = None
    
    # Timestamps
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    last_contact_date: datetime = Field(default_factory=datetime.now)
    
    @property
    def is_complete(self) -> bool:
        """Check if negotiation is finished"""
        return self.status in [NegotiationStatus.SUCCESS, NegotiationStatus.FAILED]
    
    @property
    def success_rate_factor(self) -> float:
        """Calculate success probability based on current state"""
        if self.retry_count > 1:
            return 0.3  # Lower success on retries
        elif self.initial_offer and self.initial_offer > 0:
            # Higher success if we made a reasonable offer
            return 0.8
        else:
            return 0.7  # Default probability

# ================================
# ORCHESTRATION STATE MODEL
# ================================

class CampaignOrchestrationState(BaseModel):
    """Overall campaign orchestration state"""
    campaign_id: str
    campaign_data: CampaignData
    
    # Discovery results
    discovered_influencers: List[CreatorMatch] = Field(default_factory=list)
    
    # Negotiation states
    negotiations: List[NegotiationState] = Field(default_factory=list)
    
    # Summary
    successful_negotiations: int = 0
    failed_negotiations: int = 0
    total_cost: float = 0.0
    
    # Status tracking
    current_stage: str = "initializing"
    current_influencer: Optional[str] = None
    estimated_completion_minutes: int = 5
    
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    negotiated_terms: Dict[str, Any] = Field(default_factory=dict)
    
    def add_negotiation_result(self, result: NegotiationState):
        """Add a completed negotiation result"""
        self.negotiations.append(result)
        
        if result.status == NegotiationStatus.SUCCESS:
            self.successful_negotiations += 1
            if result.final_rate:
                self.total_cost += result.final_rate
        else:
            self.failed_negotiations += 1
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get current progress summary for monitoring"""
        total_negotiations = len(self.negotiations)
        
        return {
            "campaign_id": self.campaign_id,
            "current_stage": self.current_stage,
            "current_influencer": self.current_influencer,
            "discovered_count": len(self.discovered_influencers),
            "total_negotiations": total_negotiations,
            "successful": self.successful_negotiations,
            "failed": self.failed_negotiations,
            "success_rate": self.successful_negotiations / max(total_negotiations, 1),
            "total_cost": self.total_cost,
            "average_cost": self.total_cost / max(self.successful_negotiations, 1),
            "is_complete": self.completed_at is not None,
            "duration_minutes": (datetime.now() - self.started_at).total_seconds() / 60
        }
    
    def get_campaign_summary(self) -> Dict[str, Any]:
        """Get final campaign summary for results"""
        duration = (self.completed_at or datetime.now()) - self.started_at
        
        return {
            "campaign_name": f"{self.campaign_data.brand_name} - {self.campaign_data.product_name}",
            "total_budget": self.campaign_data.total_budget,
            "spent_amount": self.total_cost,
            "budget_utilization": (self.total_cost / self.campaign_data.total_budget) * 100 if self.campaign_data.total_budget > 0 else 0,
            "creators_contacted": len(self.negotiations),
            "successful_partnerships": self.successful_negotiations,
            "success_rate": f"{(self.successful_negotiations / max(len(self.negotiations), 1)) * 100:.1f}%",
            "average_rate": self.total_cost / max(self.successful_negotiations, 1) if self.successful_negotiations > 0 else 0,
            "duration": f"{duration.total_seconds() / 60:.1f} minutes",
            "roi_projection": "TBD - depends on campaign performance"
        }
    
    def get_detailed_summary(self) -> Dict[str, Any]:
        """Get comprehensive campaign summary with all details"""
        base_summary = self.get_campaign_summary()
        
        # Add detailed negotiation breakdown
        negotiation_details = []
        for negotiation in self.negotiations:
            details = {
                "creator_id": negotiation.creator_id,
                "status": negotiation.status.value,
                "final_rate": negotiation.final_rate,
                "call_duration_seconds": negotiation.call_duration_seconds,
                "failure_reason": negotiation.failure_reason,
                "conversation_id": negotiation.conversation_id,
                "retry_count": negotiation.retry_count,
                "started_at": negotiation.started_at.isoformat(),
                "completed_at": negotiation.completed_at.isoformat() if negotiation.completed_at else None
            }
            negotiation_details.append(details)
        
        # Add discovered creators info
        creator_matches = []
        for match in self.discovered_influencers:
            creator_info = {
                "name": match.creator.name,
                "platform": match.creator.platform.value,
                "followers": match.creator.followers,
                "niche": match.creator.niche,
                "similarity_score": match.similarity_score,
                "estimated_rate": match.estimated_rate,
                "rate_compatible": match.rate_compatible,
                "match_reasons": match.match_reasons,
                "overall_score": match.overall_score
            }
            creator_matches.append(creator_info)
        
        # Performance metrics
        performance_metrics = {
            "discovery_efficiency": len(self.discovered_influencers) / max(len(self.negotiations), 1),
            "cost_efficiency": self.total_cost / max(self.successful_negotiations, 1) if self.successful_negotiations > 0 else 0,
            "time_efficiency": f"{(datetime.now() - self.started_at).total_seconds() / 60:.1f} minutes per successful negotiation" if self.successful_negotiations > 0 else "N/A",
            "budget_efficiency": f"{(self.total_cost / self.campaign_data.total_budget) * 100:.1f}%" if self.campaign_data.total_budget > 0 else "N/A"
        }
        
        return {
            **base_summary,
            "discovered_creators": creator_matches,
            "negotiation_details": negotiation_details,
            "performance_metrics": performance_metrics,
            "campaign_config": {
                "campaign_id": self.campaign_id,
                "niche": self.campaign_data.product_niche,
                "target_audience": self.campaign_data.target_audience,
                "campaign_goal": self.campaign_data.campaign_goal
            },
            "timing": {
                "started_at": self.started_at.isoformat(),
                "completed_at": self.completed_at.isoformat() if self.completed_at else None,
                "current_stage": self.current_stage,
                "estimated_completion_minutes": self.estimated_completion_minutes
            }
        }

# ================================
# LEGACY COMPATIBILITY
# ================================

# For backward compatibility, export the models that might be imported elsewhere
__all__ = [
    # Campaign models
    "CampaignStatus",
    "CampaignWebhook", 
    "CampaignData",
    "CampaignOrchestrationState",
    
    # Creator models
    "Creator",
    "CreatorTier",
    "Platform", 
    "Availability",
    "CreatorMatch",
    
    # Negotiation models
    "NegotiationState",
    "NegotiationStatus",
    "CallStatus",
    "EmailStatus"
]
