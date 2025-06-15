# core/models.py - UNIFIED DATA MODELS
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

class NegotiationStatus(str, Enum):
    """Negotiation status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"

class CallStatus(str, Enum):
    """Call status enumeration"""
    NOT_STARTED = "not_started"
    INITIATED = "initiated"
    RINGING = "ringing"
    ANSWERED = "answered"
    COMPLETED = "completed"
    FAILED = "failed"
    NO_ANSWER = "no_answer"

class ContractStatus(str, Enum):
    """Contract status enumeration"""
    DRAFT = "draft"
    SENT = "sent"
    SIGNED = "signed"
    REJECTED = "rejected"
    EXPIRED = "expired"

class CampaignData(BaseModel):
    """
    Unified campaign data model
    
    Contains all information needed to run a complete campaign workflow
    """
    id: str
    product_name: str
    brand_name: str
    product_description: str
    target_audience: str
    campaign_goal: str
    product_niche: str
    total_budget: float
    campaign_code: Optional[str] = None
    
    # Optional campaign parameters
    max_creators: int = 10
    preferred_engagement_rate: float = 3.0
    content_requirements: List[str] = Field(default_factory=list)
    timeline_days: int = 30
    
    @validator('total_budget')
    def validate_budget(cls, v):
        if v <= 0:
            raise ValueError('Budget must be positive')
        return v
    
    @validator('product_niche')
    def validate_niche(cls, v):
        valid_niches = ['fitness', 'beauty', 'tech', 'fashion', 'food', 'travel', 'lifestyle']
        if v.lower() not in valid_niches:
            raise ValueError(f'Niche must be one of: {", ".join(valid_niches)}')
        return v.lower()
    
    def generate_campaign_code(self) -> str:
        """Generate campaign code if not provided"""
        if not self.campaign_code:
            self.campaign_code = f"CAMP-{self.id[:8].upper()}"
        return self.campaign_code
    
    def get_budget_per_creator(self) -> float:
        """Calculate average budget per creator"""
        return self.total_budget / self.max_creators

class Creator(BaseModel):
    """
    Creator profile model
    
    Contains creator information and metrics for matching and outreach
    """
    id: str
    name: str
    handle: str
    platform: str = "instagram"  # instagram, tiktok, youtube, etc.
    followers: int
    engagement_rate: float
    niche: str
    rate_per_post: float
    
    # Contact information
    contact_email: str
    phone_number: Optional[str] = None
    
    # Profile metrics
    average_likes: int = 0
    average_comments: int = 0
    recent_post_count: int = 0
    
    # Matching score (calculated during discovery)
    match_score: float = 0.0
    
    @validator('engagement_rate')
    def validate_engagement_rate(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Engagement rate must be between 0 and 100')
        return v
    
    @validator('rate_per_post')
    def validate_rate(cls, v):
        if v < 0:
            raise ValueError('Rate must be non-negative')
        return v
    
    def calculate_match_score(self, campaign: 'CampaignData') -> float:
        """
        Calculate how well this creator matches the campaign
        
        Returns:
            Float between 0-100 representing match quality
        """
        score = 0.0
        
        # Niche match (40% weight)
        if self.niche.lower() == campaign.product_niche.lower():
            score += 40.0
        
        # Engagement rate (30% weight)
        if self.engagement_rate >= campaign.preferred_engagement_rate:
            score += 30.0
        else:
            score += (self.engagement_rate / campaign.preferred_engagement_rate) * 30.0
        
        # Budget fit (20% weight)
        budget_per_creator = campaign.get_budget_per_creator()
        if self.rate_per_post <= budget_per_creator:
            score += 20.0
        elif self.rate_per_post <= budget_per_creator * 1.2:  # 20% over budget tolerance
            score += 10.0
        
        # Follower count (10% weight) - sweet spot between 10k-100k
        if 10000 <= self.followers <= 100000:
            score += 10.0
        elif self.followers > 100000:
            score += 5.0
        
        self.match_score = min(score, 100.0)
        return self.match_score

class NegotiationResult(BaseModel):
    """
    Negotiation outcome model
    
    Contains results from voice negotiations with creators
    """
    creator_id: str
    creator_name: str
    status: NegotiationStatus
    
    # Call details
    call_status: CallStatus = CallStatus.NOT_STARTED
    call_duration_seconds: int = 0
    call_recording_url: Optional[str] = None
    call_transcript: Optional[str] = None
    conversation_id: Optional[str] = None
    
    # Negotiation results
    agreed_rate: Optional[float] = None
    original_rate: Optional[float] = None
    negotiated_deliverables: List[str] = Field(default_factory=list)
    agreed_timeline_days: Optional[int] = None
    
    # Analysis results
    sentiment_score: float = 0.0  # -1 to 1
    key_concerns: List[str] = Field(default_factory=list)
    decision_factors: List[str] = Field(default_factory=list)
    
    # Metadata
    negotiated_at: datetime = Field(default_factory=datetime.now)
    notes: Optional[str] = None
    follow_up_required: bool = False
    
    def get_discount_percentage(self) -> float:
        """Calculate discount percentage from original rate"""
        if not self.original_rate or not self.agreed_rate:
            return 0.0
        return ((self.original_rate - self.agreed_rate) / self.original_rate) * 100

class Contract(BaseModel):
    """
    Contract model
    
    Represents legal agreements with creators
    """
    id: str
    creator_id: str
    campaign_id: str
    
    # Financial terms
    rate: float
    payment_schedule: str = "upon_completion"  # upon_completion, 50_50_split, net_30
    
    # Deliverables
    deliverables: List[str]
    content_requirements: List[str] = Field(default_factory=list)
    revision_rounds: int = 2
    
    # Timeline
    deadline: datetime
    milestones: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Legal terms
    usage_rights: str = "6_months_exclusive"
    cancellation_terms: str = "48_hours_notice"
    intellectual_property: str = "shared_rights"
    
    # Status tracking
    status: ContractStatus = ContractStatus.DRAFT
    contract_url: Optional[str] = None
    signed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)
    
    def is_expired(self) -> bool:
        """Check if contract deadline has passed"""
        return datetime.now() > self.deadline
    
    def days_until_deadline(self) -> int:
        """Calculate days remaining until deadline"""
        delta = self.deadline - datetime.now()
        return max(0, delta.days)

class OrchestrationState(BaseModel):
    """
    Campaign orchestration state
    
    Tracks the complete workflow state and progress
    """
    campaign_id: str
    campaign_data: CampaignData
    
    # Workflow tracking
    current_stage: str = "initialized"
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    # Phase results
    discovered_creators: List[Creator] = Field(default_factory=list)
    negotiations: List[NegotiationResult] = Field(default_factory=list)
    contracts: List[Contract] = Field(default_factory=list)
    
    # Metrics
    successful_negotiations: int = 0
    total_cost: float = 0.0
    
    # Error handling
    error_message: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)
    
    # Progress tracking
    phase_timings: Dict[str, float] = Field(default_factory=dict)
    
    def add_timing(self, phase: str, duration_seconds: float):
        """Add timing information for a phase"""
        self.phase_timings[phase] = duration_seconds
    
    def get_total_duration(self) -> float:
        """Get total campaign duration in seconds"""
        if not self.completed_at:
            return (datetime.now() - self.started_at).total_seconds()
        return (self.completed_at - self.started_at).total_seconds()
    
    def get_success_rate(self) -> float:
        """Calculate negotiation success rate"""
        total_negotiations = len(self.negotiations)
        if total_negotiations == 0:
            return 0.0
        return (self.successful_negotiations / total_negotiations) * 100
    
    def get_budget_utilization(self) -> float:
        """Calculate budget utilization percentage"""
        if self.campaign_data.total_budget == 0:
            return 0.0
        return (self.total_cost / self.campaign_data.total_budget) * 100
    
    def is_complete(self) -> bool:
        """Check if campaign is complete"""
        return self.completed_at is not None
    
    def has_errors(self) -> bool:
        """Check if campaign has errors"""
        return self.error_message is not None

# Request/Response models for API
class CampaignCreateRequest(BaseModel):
    """Request model for creating campaigns"""
    product_name: str
    brand_name: str
    product_description: str
    target_audience: str
    campaign_goal: str
    product_niche: str
    total_budget: float
    max_creators: int = 10
    timeline_days: int = 30

class CampaignStatusResponse(BaseModel):
    """Response model for campaign status"""
    task_id: str
    campaign_id: str
    current_stage: str
    is_complete: bool
    progress: Dict[str, Any]
    started_at: str
    completed_at: Optional[str] = None
    error_message: Optional[str] = None