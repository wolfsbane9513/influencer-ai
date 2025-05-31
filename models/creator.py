# models/creator.py
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class CreatorProfile(BaseModel):
    id: str
    name: str
    platform: str
    followers: int
    niche: str
    typical_rate: int
    engagement_rate: float
    average_views: int
    last_campaign_date: str
    availability: str
    performance_metrics: Dict[str, Any]

class AudienceDemographics(BaseModel):
    age_18_24: int
    age_25_34: int
    age_35_44: int
    age_45_plus: int
    male: int
    female: int
    top_countries: List[str]

class PerformanceMetrics(BaseModel):
    avg_completion_rate: int
    brand_safety_score: float
    audience_quality: float
    delivery_punctuality: int
    content_quality_score: float
    collaboration_rating: float

class CampaignHistory(BaseModel):
    brand: str
    date: str
    deliverables: List[str]
    price: int
    performance: Dict[str, Any]

class DetailedCreatorProfile(CreatorProfile):
    location: str
    languages: List[str]
    specialties: List[str]
    audience_demographics: AudienceDemographics
    recent_campaigns: List[CampaignHistory]
    rate_history: Dict[str, int]
    preferred_collaboration_style: str