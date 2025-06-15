# core/models.py - COMPLETE FIXED MODELS
from typing import List, Optional, Any, Dict
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from pydantic import BaseModel, Field


# Enums for status tracking
class NegotiationStatus(str, Enum):
    """Negotiation status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"


class CampaignStage(str, Enum):
    """Campaign orchestration stages"""
    STARTING = "starting"
    DISCOVERY = "discovery"
    NEGOTIATIONS = "negotiations"
    CONTRACTS = "contracts"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Core data models
@dataclass
class Creator:
    """Creator/Influencer model with all required fields"""
    id: str
    name: str
    handle: str
    platform: str
    followers: int
    engagement_rate: float
    average_views: int
    niche: str
    location: str
    phone: str
    languages: List[str]
    specialties: List[str]
    rate_per_post: float
    content_types: List[str]
    availability: str
    bio: Optional[str] = None
    verified: bool = False
    last_active: Optional[datetime] = None
    
    # Calculated fields
    match_score: float = 0.0
    rate_compatible: bool = True
    
    def __post_init__(self):
        """Post-initialization calculations"""
        if self.last_active is None:
            self.last_active = datetime.now()
    
    def __str__(self) -> str:
        return f"{self.name} ({self.platform}, {self.followers:,} followers)"
    
    @property
    def rate(self) -> float:
        """Compatibility property for legacy code"""
        return self.rate_per_post
    
    @property
    def email(self) -> str:
        """Generate email from handle for compatibility"""
        return f"{self.handle.replace('@', '')}@{self.platform}.com"
    
    @property
    def tier(self) -> str:
        """Determine influencer tier based on followers"""
        if self.followers < 1000:
            return "nano_influencer"
        elif self.followers < 10000:
            return "micro_influencer"
        elif self.followers < 100000:
            return "mid_tier_influencer"
        elif self.followers < 1000000:
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
    
    class Config:
        arbitrary_types_allowed = True
    
    def __str__(self):
        return f"{self.creator.name} ({self.similarity_score:.1%} match)"


@dataclass
class CampaignData:
    """Campaign configuration and requirements"""
    campaign_id: str
    company_name: str
    product_name: str
    product_description: str
    target_audience: str
    campaign_goals: str
    budget_per_creator: float
    max_creators: int
    timeline: str
    content_requirements: str
    brand_guidelines: str
    created_at: datetime = field(default_factory=datetime.now)
    
    # Additional fields for compatibility
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    product_niche: Optional[str] = None
    total_budget: Optional[float] = None
    
    def __post_init__(self):
        """Post-initialization setup"""
        if self.id is None:
            self.id = self.campaign_id
        if self.name is None:
            self.name = f"{self.company_name} - {self.product_name}"
        if self.description is None:
            self.description = self.product_description
        if self.product_niche is None:
            # Extract niche from target audience or set default
            self.product_niche = "tech"  # Default fallback
        if self.total_budget is None:
            self.total_budget = self.budget_per_creator * self.max_creators
    
    def __str__(self) -> str:
        return f"Campaign: {self.company_name} - {self.product_name}"


@dataclass
class NegotiationResult:
    """Negotiation result with proper status handling"""
    creator_id: str
    status: str  # Using string instead of enum to avoid .value errors
    conversation_id: Optional[str] = None
    final_rate: Optional[float] = None
    timeline: Optional[str] = None
    deliverables: Optional[str] = None
    error_message: Optional[str] = None
    negotiation_date: datetime = None
    
    # Additional fields for database compatibility
    creator_name: Optional[str] = None
    negotiated_rate: Optional[float] = None
    agreed_timeline: Optional[str] = None
    content_deliverables: Optional[str] = None
    
    def __post_init__(self):
        if self.negotiation_date is None:
            self.negotiation_date = datetime.now()
        
        # Set compatibility fields
        if self.creator_name is None:
            self.creator_name = self.creator_id
        if self.negotiated_rate is None:
            self.negotiated_rate = self.final_rate
        if self.agreed_timeline is None:
            self.agreed_timeline = self.timeline
        if self.content_deliverables is None:
            self.content_deliverables = self.deliverables
    
    def is_successful(self) -> bool:
        """Check if negotiation was successful"""
        return self.status == "success"
    
    @property
    def rate(self) -> Optional[float]:
        """Compatibility property for rate access"""
        return self.final_rate


@dataclass
class Contract:
    """Generated contract document"""
    contract_id: str
    creator_id: str
    campaign_id: str
    terms: Dict[str, Any]
    contract_text: str
    generated_at: datetime
    status: str = "draft"
    
    # Additional fields for compatibility
    creator_name: Optional[str] = None
    company_name: Optional[str] = None
    compensation: Optional[float] = None
    deliverables: Optional[str] = None
    
    def __post_init__(self):
        """Extract fields from terms for compatibility"""
        if isinstance(self.terms, dict):
            self.creator_name = self.terms.get("creator_name", self.creator_id)
            self.company_name = self.terms.get("company_name", "Unknown Company")
            self.compensation = self.terms.get("compensation", 0.0)
            self.deliverables = self.terms.get("deliverables", "TBD")
    
    def __str__(self) -> str:
        return f"Contract {self.contract_id}: {self.creator_name}"


@dataclass
class OrchestrationState:
    """
    FIXED: Complete orchestration state with all required fields
    """
    stage: str
    campaign_id: str
    company_name: str
    product_name: str
    start_time: datetime
    
    # Required fields that were missing
    error_message: Optional[str] = None
    end_time: Optional[datetime] = None
    is_complete: bool = False
    
    # Discovery results
    discovered_creators: List[Creator] = field(default_factory=list)
    creators_found: int = 0
    
    # Negotiation results  
    negotiation_results: List[NegotiationResult] = field(default_factory=list)
    successful_negotiations: int = 0
    failed_negotiations: int = 0
    
    # Contract results
    contracts_generated: List[Contract] = field(default_factory=list)
    contracts_count: int = 0
    
    # Additional compatibility fields
    campaign_data: Optional[CampaignData] = None
    started_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Set compatibility fields"""
        if self.started_at is None:
            self.started_at = self.start_time
    
    def get_progress_percentage(self) -> float:
        """Calculate overall progress percentage"""
        stage_progress = {
            "starting": 0.0,
            "discovery": 25.0,
            "negotiations": 50.0,
            "contracts": 75.0,
            "completed": 100.0,
            "failed": 0.0,
            "cancelled": 0.0
        }
        return stage_progress.get(self.stage, 0.0)


# Additional utility models for API responses
class CampaignResponse(BaseModel):
    """Campaign creation response"""
    success: bool
    campaign_id: str
    task_id: str
    message: str
    campaign_code: Optional[str] = None


class CampaignStatusResponse(BaseModel):
    """Campaign status response"""
    task_id: str
    campaign_id: str
    stage: str
    is_complete: bool
    progress_percentage: float
    creators_found: int
    successful_negotiations: int
    contracts_generated: int
    error_message: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None


# Legacy compatibility aliases
CreatorData = Creator  # For backward compatibility
CampaignConfig = CampaignData  # For backward compatibility