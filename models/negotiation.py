# models/negotiation.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

# Import from existing campaign model
from .campaign import CampaignData
from .creator import CreatorMatch

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
    """Tracks individual creator negotiation state"""
    creator_id: str
    campaign_id: str
    status: NegotiationStatus = NegotiationStatus.PENDING
    call_status: CallStatus = CallStatus.PENDING
    email_status: EmailStatus = EmailStatus.PENDING
    
    # ElevenLabs integration fields
    conversation_id: Optional[str] = None
    call_id: Optional[str] = None
    
    # Pricing negotiation
    initial_offer: Optional[float] = None
    final_rate: Optional[float] = None
    negotiated_terms: Dict[str, Any] = Field(default_factory=dict)
    
    # Call details
    call_duration_seconds: int = 0
    call_recording_url: Optional[str] = None
    call_transcript: Optional[str] = None
    
    # Retry and error handling
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

class CampaignOrchestrationState(BaseModel):
    """Overall campaign orchestration state for monitoring"""
    campaign_id: str
    campaign_data: CampaignData
    
    # Discovery results
    discovered_influencers: List[CreatorMatch] = Field(default_factory=list)
    
    # Negotiation tracking
    negotiations: List[NegotiationState] = Field(default_factory=list)
    
    # Summary metrics
    successful_negotiations: int = 0
    failed_negotiations: int = 0
    total_cost: float = 0.0
    
    # Status and progress tracking
    current_stage: str = "initializing"
    current_influencer: Optional[str] = None
    estimated_completion_minutes: int = 5
    
    # Timestamps
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    def add_negotiation_result(self, result: NegotiationState):
        """Add completed negotiation and update metrics"""
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
            "budget_utilization": (self.total_cost / self.campaign_data.total_budget) * 100,
            "creators_contacted": len(self.negotiations),
            "successful_partnerships": self.successful_negotiations,
            "success_rate": f"{(self.successful_negotiations / max(len(self.negotiations), 1)) * 100:.1f}%",
            "average_rate": self.total_cost / max(self.successful_negotiations, 1),
            "duration": f"{duration.total_seconds() / 60:.1f} minutes",
            "roi_projection": "TBD - depends on campaign performance"
        }