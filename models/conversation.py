# models/conversation.py
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class CampaignBrief(BaseModel):
    creator_name: str
    budget: int
    deliverables: List[str]
    timeline: str
    campaign_type: str
    additional_requirements: Optional[str] = None

class DealParams(BaseModel):
    price: int
    deliverables: List[str]
    timeline: str
    usage_rights: Optional[str] = None
    status: str = "negotiating"

class ConversationState(BaseModel):
    conversation_id: str
    messages: List[Dict[str, str]]
    deal_params: DealParams
    creator_profile: Dict[str, Any]
    negotiation_strategy: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

class NegotiationRequest(BaseModel):
    conversation_id: str
    message: str
    speaker: str  # "agency" or "creator"

class MessageRole(str, Enum):
    AGENCY = "agency"
    CREATOR = "creator"
    AI_AGENT = "ai_agent"
    SYSTEM = "system"

class ConversationStatus(str, Enum):
    INITIALIZING = "initializing"
    NEGOTIATING = "negotiating"
    AGREED = "agreed"
    REJECTED = "rejected"
    ON_HOLD = "on_hold"
    EXPIRED = "expired"