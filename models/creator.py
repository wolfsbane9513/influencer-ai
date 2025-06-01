# models/creator.py
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from enum import Enum

class Platform(str, Enum):
    YOUTUBE = "YouTube"
    INSTAGRAM = "Instagram" 
    TIKTOK = "TikTok"
    TWITCH = "Twitch"

class CreatorTier(str, Enum):
    MICRO = "micro_influencer"      # < 100K followers
    MACRO = "macro_influencer"      # 100K - 1M followers  
    MEGA = "mega_influencer"        # > 1M followers

class Availability(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good" 
    LIMITED = "limited"
    BUSY = "busy"

class Creator(BaseModel):
    """Creator model matching your creators.json structure"""
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
    audience_demographics: Dict[str, Any]
    performance_metrics: Dict[str, float]
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
        """Calculate cost per view for ROI analysis"""
        return self.typical_rate / self.average_views if self.average_views > 0 else 0
    
    @property
    def brand_safety_score(self) -> float:
        """Get brand safety score from performance metrics"""
        return self.performance_metrics.get("brand_safety_score", 8.0)
    
    @property
    def collaboration_rating(self) -> float:
        """Get collaboration rating from performance metrics"""
        return self.performance_metrics.get("collaboration_rating", 4.0)

class CreatorMatch(BaseModel):
    """Represents a matched creator with scoring details"""
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