# core/models.py - UNIFIED MODELS WITH CONSISTENT ATTRIBUTES
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class NegotiationStatus(str, Enum):
    """Negotiation status enumeration"""
    NOT_STARTED = "not_started"
    CALLING = "calling"
    NEGOTIATING = "negotiating"
    SUCCESS = "success"
    FAILED = "failed"

class CallStatus(str, Enum):
    """Call status enumeration"""
    NOT_STARTED = "not_started"
    CONNECTING = "connecting"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

class NegotiationResult(BaseModel):
    """
    🤝 Unified Negotiation Result Model
    
    Contains results from voice negotiations with creators.
    Fixed to have consistent attribute naming across the system.
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
    
    # FINANCIAL TERMS - UNIFIED ATTRIBUTES
    # Using both attribute names for compatibility
    agreed_rate: Optional[float] = None
    final_rate: Optional[float] = None  # Added for compatibility
    original_rate: Optional[float] = None
    
    # Negotiation deliverables
    negotiated_deliverables: List[str] = Field(default_factory=list)
    agreed_timeline_days: Optional[int] = None
    
    # Analysis results
    sentiment_score: float = 0.0  # -1 to 1 scale
    key_concerns: List[str] = Field(default_factory=list)
    decision_factors: List[str] = Field(default_factory=list)
    
    # Metadata
    negotiated_at: datetime = Field(default_factory=datetime.now)
    last_contact_date: datetime = Field(default_factory=datetime.now)
    notes: Optional[str] = None
    follow_up_required: bool = False
    
    # Additional terms
    negotiated_terms: Dict[str, Any] = Field(default_factory=dict)
    
    def __init__(self, **data):
        """Initialize with rate synchronization"""
        super().__init__(**data)
        # Ensure both rate attributes are synchronized
        self._sync_rate_attributes()
    
    def _sync_rate_attributes(self):
        """Synchronize agreed_rate and final_rate for compatibility"""
        if self.agreed_rate is not None and self.final_rate is None:
            self.final_rate = self.agreed_rate
        elif self.final_rate is not None and self.agreed_rate is None:
            self.agreed_rate = self.final_rate
    
    @property
    def rate(self) -> Optional[float]:
        """Get the agreed rate (unified access method)"""
        return self.agreed_rate or self.final_rate
    
    def get_discount_percentage(self) -> float:
        """Calculate discount percentage from original rate"""
        if not self.original_rate or not self.rate:
            return 0.0
        return ((self.original_rate - self.rate) / self.original_rate) * 100
    
    def set_rate(self, rate: float):
        """Set rate with automatic synchronization"""
        self.agreed_rate = rate
        self.final_rate = rate
    
    def is_successful(self) -> bool:
        """Check if negotiation was successful"""
        return self.status == NegotiationStatus.SUCCESS
    
    def get_summary(self) -> Dict[str, Any]:
        """Get negotiation summary for reporting"""
        return {
            "creator_id": self.creator_id,
            "creator_name": self.creator_name,
            "status": self.status.value,
            "final_rate": self.rate,
            "call_duration_minutes": self.call_duration_seconds // 60,
            "sentiment": "positive" if self.sentiment_score > 0 else "negative" if self.sentiment_score < 0 else "neutral",
            "negotiated_at": self.negotiated_at.isoformat() if self.negotiated_at else None
        }

class Contract(BaseModel):
    """
    📝 Contract Model
    
    Represents legal agreements with creators
    """
    id: str
    creator_id: str
    campaign_id: str
    
    # Financial terms
    rate: float
    payment_schedule: str = "upon_completion"
    currency: str = "USD"
    
    # Deliverables and timeline
    deliverables: List[str]
    deadline: datetime
    
    # Contract metadata
    status: str = "draft"
    created_at: datetime = Field(default_factory=datetime.now)
    signed_at: Optional[datetime] = None
    
    # References
    negotiation_id: Optional[str] = None
    
    def is_signed(self) -> bool:
        """Check if contract is signed"""
        return self.signed_at is not None
    
    def mark_signed(self):
        """Mark contract as signed"""
        self.signed_at = datetime.now()
        self.status = "signed"

class CampaignData(BaseModel):
    """
    🎯 Campaign Data Model
    
    Contains campaign information and requirements
    Compatible with existing API expectations
    """
    id: str
    name: str
    description: str
    
    # API-compatible fields (legacy support)
    product_name: Optional[str] = None
    brand_name: Optional[str] = None
    product_description: Optional[str] = None
    target_audience: Optional[str] = None
    campaign_goal: Optional[str] = None
    product_niche: Optional[str] = None
    campaign_code: Optional[str] = None
    
    # Budget and targeting
    total_budget: float
    max_creators: int = 10
    timeline_days: int = 30
    target_demographics: Dict[str, Any] = Field(default_factory=dict)
    
    # Campaign details
    requirements: List[str] = Field(default_factory=list)
    content_requirements: List[str] = Field(default_factory=list)
    preferred_engagement_rate: float = 3.0
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    
    def __init__(self, **data):
        """Initialize with backward compatibility"""
        super().__init__(**data)
        
        # Auto-populate name and description from legacy fields if not provided
        if not self.name and self.product_name and self.brand_name:
            self.name = f"{self.brand_name} - {self.product_name}"
        
        if not self.description and self.product_description:
            self.description = self.product_description
            
        # Auto-populate legacy fields from name/description if not provided
        if not self.product_name and self.name:
            # Try to extract product name from combined name
            parts = self.name.split(" - ")
            if len(parts) >= 2:
                self.brand_name = parts[0]
                self.product_name = parts[1]
            else:
                self.product_name = self.name
                
        if not self.product_description and self.description:
            self.product_description = self.description
    
    def generate_campaign_code(self) -> str:
        """Generate campaign code if not provided (API compatibility)"""
        if not self.campaign_code:
            self.campaign_code = f"CAMP-{self.id[:8].upper()}"
        return self.campaign_code
    
    def get_budget_per_creator(self) -> float:
        """Calculate average budget per creator (API compatibility)"""
        return self.total_budget / max(self.max_creators, 1)

class Creator(BaseModel):
    """
    🎭 Creator Profile Model
    
    Contains creator information and metrics for matching and outreach
    """
    id: str
    name: str
    handle: Optional[str] = None  # Made optional to handle existing data
    platform: str = "instagram"  # instagram, tiktok, youtube, etc.
    
    # Audience metrics
    followers: int
    engagement_rate: float
    average_views: int = 0
    
    # Creator details
    niche: str
    location: str = "Unknown"
    phone: str = "+1234567890"
    languages: List[str] = Field(default_factory=lambda: ["English"])
    specialties: List[str] = Field(default_factory=list)
    
    # Pricing and availability
    rate_per_post: float = 1000.0
    typical_rate: float = 1000.0  # Alias for compatibility
    availability: str = "good"  # excellent, good, limited, busy
    
    # Performance metrics
    brand_safety_score: float = 8.0
    last_campaign_date: Optional[str] = None
    preferred_collaboration_style: str = "Professional"
    
    # Matching metadata
    match_score: float = 0.0
    rate_compatible: bool = True
    
    # Additional attributes for compatibility
    audience_demographics: Dict[str, Any] = Field(default_factory=dict)
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)
    recent_campaigns: List[Dict[str, Any]] = Field(default_factory=list)
    rate_history: Dict[str, float] = Field(default_factory=dict)
    
    def __init__(self, **data):
        """Initialize with backward compatibility"""
        super().__init__(**data)
        
        # Auto-generate handle if missing
        if not self.handle:
            self.handle = f"@{self.name.lower().replace(' ', '_')}"
        
        # Sync typical_rate and rate_per_post
        if not self.typical_rate and self.rate_per_post:
            self.typical_rate = self.rate_per_post
        elif not self.rate_per_post and self.typical_rate:
            self.rate_per_post = self.typical_rate
    
    @property
    def tier(self) -> str:
        """Determine creator tier based on followers"""
        if self.followers < 100_000:
            return "micro_influencer"
        elif self.followers < 1_000_000:
            return "macro_influencer"
        else:
            return "mega_influencer"
    
    @property
    def estimated_cpm(self) -> float:
        """Estimate cost per thousand views"""
        if self.average_views > 0:
            return (self.rate_per_post / self.average_views) * 1000
        return 0.0
    
    def calculate_match_score(self, campaign_niche: str, max_budget: float) -> float:
        """Calculate match score for campaign"""
        score = 0.0
        
        # Niche matching (40% of score)
        if self.niche.lower() == campaign_niche.lower():
            score += 40.0
        elif campaign_niche.lower() in [s.lower() for s in self.specialties]:
            score += 25.0
        
        # Budget compatibility (30% of score)
        if self.rate_per_post <= max_budget:
            score += 30.0
        elif self.rate_per_post <= max_budget * 1.2:
            score += 20.0
        
        # Engagement rate (20% of score)
        if self.engagement_rate >= 5.0:
            score += 20.0
        elif self.engagement_rate >= 3.0:
            score += 15.0
        elif self.engagement_rate >= 1.0:
            score += 10.0
        
        # Follower count bonus (10% of score)
        if 10000 <= self.followers <= 500000:
            score += 10.0
        elif self.followers > 100000:
            score += 5.0
        
        self.match_score = min(score, 100.0)
        return self.match_score

class CreatorMatch(BaseModel):
    """
    🎯 Creator Matching Result
    
    Result from discovery agent with scoring and compatibility
    """
    creator: Creator
    similarity_score: float
    estimated_rate: float
    match_reasons: List[str] = Field(default_factory=list)
    availability_score: float = 0.8
    rate_compatible: bool = True
    
    def __str__(self):
        return f"{self.creator.name} ({self.similarity_score:.2f} match, ${self.estimated_rate:,.0f})"
    
class OrchestrationState(BaseModel):
    """
    🧠 Campaign Orchestration State
    
    Tracks the complete state of campaign execution
    """
    campaign_id: str
    campaign_data: CampaignData
    
    # Discovery results
    discovered_creators: List[Any] = Field(default_factory=list)
    
    # Negotiation results using unified model
    negotiations: List[NegotiationResult] = Field(default_factory=list)
    
    # Summary metrics
    successful_negotiations: int = 0
    failed_negotiations: int = 0
    total_cost: float = 0.0
    
    # Status tracking
    current_stage: str = "initializing"
    current_influencer: Optional[str] = None
    estimated_completion_minutes: int = 5
    
    # Contract storage
    contracts: List[Contract] = Field(default_factory=list)
    
    # Timestamps
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    def add_negotiation_result(self, result: NegotiationResult):
        """Add a completed negotiation result with proper counting"""
        self.negotiations.append(result)
        
        if result.is_successful():
            self.successful_negotiations += 1
            if result.rate:
                self.total_cost += result.rate
        else:
            self.failed_negotiations += 1
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get current progress summary for monitoring"""
        total_negotiations = len(self.negotiations)
        
        return {
            "campaign_id": self.campaign_id,
            "current_stage": self.current_stage,
            "total_negotiations": total_negotiations,
            "successful_negotiations": self.successful_negotiations,
            "success_rate": (self.successful_negotiations / max(total_negotiations, 1)) * 100,
            "total_cost": self.total_cost,
            "contracts_generated": len(self.contracts),
            "estimated_completion": self.estimated_completion_minutes
        }

# ================================
# API REQUEST/RESPONSE MODELS
# ================================

class CampaignCreateRequest(BaseModel):
    """
    📝 Campaign Creation Request Model
    
    Used by the API to receive campaign creation requests
    """
    product_name: str
    brand_name: str
    product_description: str
    target_audience: str
    campaign_goal: str
    product_niche: str
    total_budget: float
    max_creators: int = 10
    timeline_days: int = 30

    def to_campaign_data(self, campaign_id: str) -> CampaignData:
        """Convert request to CampaignData object"""
        return CampaignData(
            id=campaign_id,
            name=f"{self.brand_name} - {self.product_name}",
            description=self.product_description,
            
            # API-compatible legacy fields
            product_name=self.product_name,
            brand_name=self.brand_name,
            product_description=self.product_description,
            target_audience=self.target_audience,
            campaign_goal=self.campaign_goal,
            product_niche=self.product_niche,
            
            # Budget and settings
            total_budget=self.total_budget,
            max_creators=self.max_creators,
            timeline_days=self.timeline_days,
            
            # Derived fields
            target_demographics={
                "audience": self.target_audience,
                "niche": self.product_niche,
                "goal": self.campaign_goal
            },
            requirements=[
                f"Product: {self.product_name}",
                f"Target: {self.target_audience}",
                f"Goal: {self.campaign_goal}"
            ]
        )

class CampaignStatusResponse(BaseModel):
    """
    📊 Campaign Status Response Model
    
    Used by the API to return campaign status information
    """
    task_id: str
    campaign_id: str
    current_stage: str
    is_complete: bool
    progress: Dict[str, Any]
    started_at: str
    completed_at: Optional[str] = None
    error_message: Optional[str] = None

    @classmethod
    def from_orchestration_state(cls, task_id: str, state: OrchestrationState):
        """Create response from orchestration state"""
        # Calculate progress metrics
        total_negotiations = len(state.negotiations)
        progress = {
            "creators_discovered": len(state.discovered_creators),
            "negotiations_completed": total_negotiations,
            "successful_negotiations": state.successful_negotiations,
            "contracts_generated": len(state.contracts),
            "total_cost": state.total_cost,
            "budget_utilization_percentage": (state.total_cost / state.campaign_data.total_budget * 100) if state.campaign_data.total_budget > 0 else 0,
            "success_rate_percentage": (state.successful_negotiations / max(total_negotiations, 1)) * 100,
            "duration_minutes": (datetime.now() - state.started_at).total_seconds() / 60 if not state.completed_at else (state.completed_at - state.started_at).total_seconds() / 60
        }
        
        return cls(
            task_id=task_id,
            campaign_id=state.campaign_id,
            current_stage=state.current_stage,
            is_complete=state.completed_at is not None,
            progress=progress,
            started_at=state.started_at.isoformat(),
            completed_at=state.completed_at.isoformat() if state.completed_at else None,
            error_message=getattr(state, 'error_message', None)
        )