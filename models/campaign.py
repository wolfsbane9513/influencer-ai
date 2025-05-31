# models/campaign.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

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

# models/creator.py
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

# models/negotiation.py
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

class CreatorMatch(BaseModel):
    """Represents a matched creator with similarity score"""
    creator: Creator
    similarity_score: float
    rate_compatible: bool
    match_reasons: List[str]
    estimated_rate: float

class NegotiationState(BaseModel):
    """Tracks the state of a single negotiation"""
    creator_id: str
    campaign_id: str
    status: NegotiationStatus = NegotiationStatus.PENDING
    call_status: CallStatus = CallStatus.PENDING
    email_status: EmailStatus = EmailStatus.PENDING
    
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
    
    def add_negotiation_result(self, result: NegotiationState):
        """Add a completed negotiation result"""
        self.negotiations.append(result)
        
        if result.status == NegotiationStatus.SUCCESS:
            self.successful_negotiations += 1
            if result.final_rate:
                self.total_cost += result.final_rate
        else:
            self.failed_negotiations += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """Get campaign execution summary"""
        return {
            "campaign_id": self.campaign_id,
            "total_negotiations": len(self.negotiations),
            "successful": self.successful_negotiations,
            "failed": self.failed_negotiations,
            "total_cost": self.total_cost,
            "average_cost": self.total_cost / max(self.successful_negotiations, 1),
            "success_rate": self.successful_negotiations / max(len(self.negotiations), 1),
            "duration_minutes": (datetime.now() - self.started_at).total_seconds() / 60,
            "completed": self.completed_at is not None
        }