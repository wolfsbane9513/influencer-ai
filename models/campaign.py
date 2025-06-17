# models/campaign.py - FIXED VERSION
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
    email: str  # 🚀 NEW: Email field for contract delivery
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
    
    # Additional fields that agents expect
    audience_demographics: Optional[Dict[str, Any]] = Field(default_factory=dict)
    performance_metrics: Optional[Dict[str, Any]] = Field(default_factory=dict)
    recent_campaigns: Optional[List[Dict[str, Any]]] = Field(default_factory=list)  # Fixed: accepts complex objects
    rate_history: Optional[Dict[str, Any]] = Field(default_factory=dict)  # Fixed: more flexible type
    preferred_collaboration_style: str = "Professional and collaborative"
    
    @property
    def tier(self) -> CreatorTier:
        """Determine creator tier based on followers"""
        if self.followers < 100_000:
            return CreatorTier.MICRO
        elif self.followers < 1_000_000:
            return CreatorTier.MACRO
        else:
            return CreatorTier.MEGA
    
    @property
    def estimated_cpm(self) -> float:
        """Estimate cost per thousand views"""
        if self.average_views > 0:
            return (self.typical_rate / self.average_views) * 1000
        return 0.0

class CreatorMatch(BaseModel):
    """Creator matching result from discovery"""
    creator: Creator
    similarity_score: float
    estimated_rate: float
    match_reasons: List[str] = Field(default_factory=list)
    availability_score: float = 0.8
    rate_compatible: bool = True
    
    def __str__(self):
        return f"{self.creator.name} ({self.similarity_score:.2f} match, ${self.estimated_rate:,.0f})"

# ================================
# NEGOTIATION MODELS
# ================================

class NegotiationStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    PAUSED = "paused"

class CallStatus(str, Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NO_ANSWER = "no_answer"

class EmailStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    OPENED = "opened"
    REPLIED = "replied"
    BOUNCED = "bounced"

class NegotiationState(BaseModel):
    """State tracking for individual creator negotiations"""
    creator_id: str
    campaign_id: str
    
    # Status tracking
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
    """Overall campaign orchestration state - CORRECT VERSION with exact required fields"""
    campaign_id: str
    campaign_data: CampaignData
    
    # Discovery results
    discovered_influencers: List[CreatorMatch] = Field(default_factory=list)
    
    # Negotiation states
    negotiations: List[NegotiationState] = Field(default_factory=list)
    
    # Summary metrics
    successful_negotiations: int = 0
    failed_negotiations: int = 0
    total_cost: float = 0.0
    
    # Status tracking
    current_stage: str = "initializing"
    current_influencer: Optional[str] = None
    estimated_completion_minutes: int = 5
    
    # AI strategy field (the one that was missing)
    ai_strategy: Optional[str] = None
    
    # Contract storage
    contracts: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Timestamps (using exact field names)
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
            "duration_minutes": (datetime.now() - self.started_at).total_seconds() / 60,
            "ai_strategy": self.ai_strategy
        }
    
    def get_campaign_summary(self) -> Dict[str, Any]:
        """Get final campaign summary for results"""
        duration = (self.completed_at or datetime.now()) - self.started_at
        
        return {
            "campaign_name": f"{self.campaign_data.brand_name} - {self.campaign_data.product_name}",
            "total_budget": self.campaign_data.total_budget,
            "spent_amount": self.total_cost,
            "budget_utilization": (self.total_cost / self.campaign_data.total_budget) * 100 if self.campaign_data.total_budget > 0 else 0,
            "successful_partnerships": self.successful_negotiations,
            "total_contacted": len(self.negotiations),
            "success_rate": f"{(self.successful_negotiations / max(len(self.negotiations), 1)) * 100:.1f}%",
            "duration": f"{duration.total_seconds() / 60:.1f} minutes",
            "ai_strategy_used": bool(self.ai_strategy),
            "strategy_approach": self.strategy_data.get("negotiation_approach", "default"),
            "contracts_generated": len(self.contracts)
        }

# ================================
# CONTRACT MODELS
# ================================

class ContractStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    SIGNED = "signed"
    EXECUTED = "executed"
    CANCELLED = "cancelled"

class ContractData(BaseModel):
    """Contract data model"""
    contract_id: str
    campaign_id: str
    creator_id: str
    creator_name: str
    
    # Terms
    compensation_amount: float
    deliverables: List[str] = Field(default_factory=list)
    timeline: Dict[str, str] = Field(default_factory=dict)
    usage_rights: Dict[str, Any] = Field(default_factory=dict)
    
    # Status
    status: ContractStatus = ContractStatus.DRAFT
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    signed_at: Optional[datetime] = None
    
    # Additional fields
    contract_text: Optional[str] = None
    legal_review_status: str = "pending"
    amendments: List[Dict[str, Any]] = Field(default_factory=list)

# ================================
# VALIDATION MODELS
# ================================

class ValidationResult(BaseModel):
    """Validation result for campaign data"""
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    
    def add_error(self, message: str):
        """Add an error message"""
        self.errors.append(message)
        self.is_valid = False
    
    def add_warning(self, message: str):
        """Add a warning message"""
        self.warnings.append(message)

# ================================
# UTILITY FUNCTIONS
# ================================

def validate_campaign_data(data: CampaignData) -> ValidationResult:
    """Validate campaign data completeness"""
    result = ValidationResult(is_valid=True)
    
    # Required field checks
    if not data.product_name.strip():
        result.add_error("Product name is required")
    
    if not data.brand_name.strip():
        result.add_error("Brand name is required")
    
    if data.total_budget <= 0:
        result.add_error("Total budget must be greater than 0")
    
    if not data.target_audience.strip():
        result.add_error("Target audience is required")
    
    # Warning checks
    if data.total_budget < 1000:
        result.add_warning("Budget is quite low for influencer marketing")
    
    if not data.product_description.strip():
        result.add_warning("Product description would help with creator matching")
    
    return result

def create_campaign_from_webhook(webhook_data: CampaignWebhook) -> CampaignData:
    """Convert webhook data to internal campaign representation"""
    return CampaignData(
        id=webhook_data.campaign_id,
        product_name=webhook_data.product_name,
        brand_name=webhook_data.brand_name,
        product_description=webhook_data.product_description,
        target_audience=webhook_data.target_audience,
        campaign_goal=webhook_data.campaign_goal,
        product_niche=webhook_data.product_niche,
        total_budget=webhook_data.total_budget
    )