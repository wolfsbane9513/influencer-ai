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
    """Unified campaign data model"""
    id: str
    product_name: str
    brand_name: str
    product_description: str
    target_audience: str
    campaign_goal: str
    product_niche: str
    total_budget: float
    campaign_code: Optional[str] = None
    max_creators: int = 10
    preferred_engagement_rate: float = 3.0
    content_requirements: List[str] = Field(default_factory=list)
    timeline_days: int = 30
    
    @validator('total_budget')
    def validate_budget(cls, v):
        if v < 0:
            raise ValueError('Budget must be non-negative')
        return v
    
    @validator('product_niche')
    def validate_niche(cls, v):
        niche_mapping = {
            'fitness': 'fitness',
            'beauty': 'beauty', 
            'tech': 'tech',
            'technology': 'tech',
            'fashion': 'fashion',
            'food': 'food',
            'travel': 'travel',
            'lifestyle': 'lifestyle'
        }
        
        normalized_niche = v.lower()
        if normalized_niche in niche_mapping:
            return niche_mapping[normalized_niche]
        
        valid_niches = list(set(niche_mapping.values()))
        raise ValueError(f'Niche must be one of: {", ".join(valid_niches)} (or technology)')
    
    def generate_campaign_code(self) -> str:
        """Generate campaign code if not provided"""
        if not self.campaign_code:
            self.campaign_code = f"CAMP-{self.id[:8].upper()}"
        return self.campaign_code
    
    def get_budget_per_creator(self) -> float:
        """Calculate average budget per creator"""
        return self.total_budget / self.max_creators

class Creator(BaseModel):
    """Creator profile model"""
    id: str
    name: str
    handle: str
    platform: str = "instagram"
    followers: int
    engagement_rate: float
    niche: str
    rate_per_post: float
    contact_email: str
    phone_number: Optional[str] = None
    average_likes: int = 0
    average_comments: int = 0
    recent_post_count: int = 0
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

class CreatorMatch(BaseModel):
    """Creator matching result"""
    creator: Creator
    match_score: float
    reasons: List[str] = Field(default_factory=list)
    
    class Config:
        arbitrary_types_allowed = True

class NegotiationResult(BaseModel):
    """Negotiation outcome model"""
    creator_id: str
    creator_name: str
    status: NegotiationStatus
    agreed_rate: Optional[float] = None
    original_rate: Optional[float] = None
    negotiated_terms: List[str] = Field(default_factory=list)
    negotiated_deliverables: List[str] = Field(default_factory=list)
    call_duration_seconds: int = 0
    call_recording_url: Optional[str] = None
    call_transcript: Optional[str] = None
    negotiated_at: datetime = Field(default_factory=datetime.now)
    email_status: str = "not_sent"
    last_contact_date: datetime = Field(default_factory=datetime.now)

class NegotiationState(BaseModel):
    """Negotiation state tracking model"""
    creator_id: str
    creator_name: str
    campaign_id: str
    status: NegotiationStatus = NegotiationStatus.PENDING
    call_status: CallStatus = CallStatus.NOT_STARTED
    conversation_id: Optional[str] = None
    call_started_at: Optional[datetime] = None
    call_ended_at: Optional[datetime] = None
    call_duration_seconds: int = 0
    agreed_rate: Optional[float] = None
    original_rate: Optional[float] = None
    terms_agreed: List[str] = Field(default_factory=list)
    last_contact_date: datetime = Field(default_factory=datetime.now)
    notes: Optional[str] = None
    follow_up_required: bool = False
    
    def get_call_duration_minutes(self) -> float:
        """Get call duration in minutes"""
        return self.call_duration_seconds / 60.0

class Contract(BaseModel):
    """Contract model"""
    id: str
    creator_id: str
    campaign_id: str
    rate: float
    payment_schedule: str = "upon_completion"
    deliverables: List[str]
    content_requirements: List[str] = Field(default_factory=list)
    revision_rounds: int = 2
    deadline: datetime
    milestones: List[Dict[str, Any]] = Field(default_factory=list)
    usage_rights: str = "6_months_exclusive"
    cancellation_terms: str = "48_hours_notice"
    intellectual_property: str = "shared_rights"
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
    """Campaign orchestration state"""
    campaign_id: str
    campaign_data: CampaignData
    current_stage: str = "initialized"
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    discovered_creators: List[Creator] = Field(default_factory=list)
    negotiations: List[NegotiationResult] = Field(default_factory=list)
    contracts: List[Contract] = Field(default_factory=list)
    successful_negotiations: int = 0
    total_cost: float = 0.0
    error_message: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)
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

# API models
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

# Legacy compatibility aliases
CampaignWebhook = CampaignData
CampaignOrchestrationState = OrchestrationState
