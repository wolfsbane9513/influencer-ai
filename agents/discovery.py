# agents/discovery.py - COMPLETELY FIXED DISCOVERY AGENT
import json
import logging
from typing import List, Dict, Any
from pathlib import Path

from core.models import CampaignData, Creator, CreatorMatch

logger = logging.getLogger(__name__)


class DiscoveryAgent:
    """
    🔍 Fixed Discovery Agent
    
    Clean, maintainable implementation that discovers creators for campaigns.
    Compatible with orchestrator expectations and proper method names.
    """
    
    def __init__(self):
        """Initialize discovery agent"""
        self.creators_data = self._load_creators_data()
        logger.info("🔍 Discovery Agent initialized")
    
    def _load_creators_data(self) -> List[Creator]:
        """Load creators from JSON file or return mock data"""
        try:
            creators_file = Path("data/creators.json")
            if not creators_file.exists():
                logger.warning("📁 creators.json not found, using mock data")
                return self._get_mock_creators()
            
            with open(creators_file, 'r') as f:
                data = json.load(f)
            
            creators = []
            for creator_data in data.get("creators", []):
                try:
                    creator = Creator(**creator_data)
                    creators.append(creator)
                except Exception as e:
                    logger.error(f"❌ Failed to parse creator {creator_data.get('name', 'unknown')}: {e}")
            
            logger.info(f"📊 Loaded {len(creators)} creators from file")
            return creators
            
        except Exception as e:
            logger.error(f"❌ Failed to load creators data: {e}")
            return self._get_mock_creators()
    
    def _get_mock_creators(self) -> List[Creator]:
        """Get mock creators for testing"""
        mock_creator_data = [
            {
                "id": "creator_tech_001",
                "name": "TechReviewer_Sarah",
                "handle": "@techsarah",
                "platform": "instagram",
                "followers": 125000,
                "engagement_rate": 4.8,
                "average_views": 18000,
                "niche": "tech",
                "location": "San Francisco",
                "phone": "+918806859890",  # Your verified number
                "languages": ["English"],
                "specialties": ["tech", "gadgets", "reviews"],
                "rate_per_post": 1000.0,
                "content_types": ["posts", "stories", "reels"],
                "availability": "excellent"
            },
            {
                "id": "creator_food_002",
                "name": "FoodBlogger_Lisa",
                "handle": "@foodielisa",
                "platform": "instagram",
                "followers": 85000,
                "engagement_rate": 6.2,
                "average_views": 12000,
                "niche": "food",
                "location": "New York",
                "phone": "+18005551238",
                "languages": ["English"],
                "specialties": ["food", "lifestyle", "cooking"],
                "rate_per_post": 1000.0,
                "content_types": ["posts", "stories"],
                "availability": "good"
            },
            {
                "id": "creator_gaming_003",
                "name": "GamingStreamer_Alex",
                "handle": "@alexgames",
                "platform": "youtube",
                "followers": 200000,
                "engagement_rate": 5.5,
                "average_views": 35000,
                "niche": "gaming",
                "location": "Los Angeles",
                "phone": "+18005551237",
                "languages": ["English"],
                "specialties": ["gaming", "tech", "streaming"],
                "rate_per_post": 1000.0,
                "content_types": ["videos", "live streams"],
                "availability": "fair"
            },
            {
                "id": "creator_fitness_004",
                "name": "FitnessGuru_Mike",
                "handle": "@mikefitness",
                "platform": "tiktok",
                "followers": 150000,
                "engagement_rate": 7.1,
                "average_views": 22000,
                "niche": "fitness",
                "location": "Miami",
                "phone": "+18005551235",
                "languages": ["English", "Spanish"],
                "specialties": ["fitness", "wellness", "nutrition"],
                "rate_per_post": 1000.0,
                "content_types": ["short videos", "tutorials"],
                "availability": "excellent"
            },
            {
                "id": "creator_beauty_005",
                "name": "BeautyInfluencer_Priya",
                "handle": "@priyabeauty",
                "platform": "instagram",
                "followers": 95000,
                "engagement_rate": 5.8,
                "average_views": 14000,
                "niche": "beauty",
                "location": "Toronto",
                "phone": "+18005551236",
                "languages": ["English"],
                "specialties": ["beauty", "skincare", "makeup"],
                "rate_per_post": 1000.0,
                "content_types": ["posts", "stories", "tutorials"],
                "availability": "good"
            }
        ]
        
        creators = []
        for data in mock_creator_data:
            try:
                creator = Creator(**data)
                creators.append(creator)
            except Exception as e:
                logger.error(f"❌ Failed to create mock creator: {e}")
        
        logger.info(f"🎭 Created {len(creators)} mock creators")
        return creators
    
    async def find_creators(
        self,
        target_audience: str,
        budget_per_creator: float,
        max_creators: int = 10
    ) -> List[Creator]:
        """
        Main method expected by orchestrator - find creators matching criteria
        
        Args:
            target_audience: Target audience description (used to infer niche)
            budget_per_creator: Budget available per creator
            max_creators: Maximum number of creators to return
            
        Returns:
            List of matching Creator objects
        """
        
        logger.info(f"🔍 Searching for creators...")
        logger.info(f"📊 Budget: ${budget_per_creator}, Max creators: {max_creators}")
        
        try:
            # Extract niche from target audience (simple keyword matching)
            niche = self._extract_niche_from_audience(target_audience)
            
            # Filter and score creators
            matching_creators = []
            
            for creator in self.creators_data:
                # Calculate match score
                match_score = self._calculate_match_score(creator, niche, budget_per_creator)
                
                if match_score > 50.0:  # Only include good matches
                    creator.match_score = match_score
                    creator.rate_compatible = creator.rate_per_post <= budget_per_creator * 1.2
                    matching_creators.append(creator)
            
            # Sort by match score (highest first)
            matching_creators.sort(key=lambda c: c.match_score, reverse=True)
            
            # Return top matches
            result = matching_creators[:max_creators]
            
            logger.info(f"✅ Found {len(result)} matching creators")
            for creator in result:
                logger.info(f"   👤 {creator.name} - Score: {creator.match_score}, Rate: ${creator.rate_per_post}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Discovery failed: {e}")
            # Return mock creators for demo
            return self.creators_data[:min(max_creators, len(self.creators_data))]
    
    def _extract_niche_from_audience(self, target_audience: str) -> str:
        """Extract niche from target audience description"""
        audience_lower = target_audience.lower()
        
        # Simple keyword matching for niche detection
        if any(word in audience_lower for word in ["tech", "technology", "gadget", "device"]):
            return "tech"
        elif any(word in audience_lower for word in ["food", "cooking", "recipe", "culinary"]):
            return "food"
        elif any(word in audience_lower for word in ["game", "gaming", "gamer", "esports"]):
            return "gaming"
        elif any(word in audience_lower for word in ["fitness", "workout", "gym", "health"]):
            return "fitness"
        elif any(word in audience_lower for word in ["beauty", "makeup", "skincare", "cosmetic"]):
            return "beauty"
        else:
            # Default to tech for unknown niches
            return "tech"
    
    def _calculate_match_score(
        self,
        creator: Creator,
        target_niche: str,
        budget_per_creator: float
    ) -> float:
        """Calculate how well a creator matches the campaign criteria"""
        score = 0.0
        
        # Niche matching (40% of score)
        if creator.niche.lower() == target_niche.lower():
            score += 40.0
        elif target_niche.lower() in [s.lower() for s in creator.specialties]:
            score += 25.0
        else:
            # Partial match for related niches
            related_matches = {
                "tech": ["gaming"],
                "gaming": ["tech"],
                "fitness": ["lifestyle"],
                "beauty": ["lifestyle"]
            }
            if target_niche in related_matches and creator.niche in related_matches[target_niche]:
                score += 15.0
        
        # Budget compatibility (30% of score)
        if creator.rate_per_post <= budget_per_creator:
            score += 30.0
        elif creator.rate_per_post <= budget_per_creator * 1.2:
            score += 20.0
        elif creator.rate_per_post <= budget_per_creator * 1.5:
            score += 10.0
        
        # Engagement rate (20% of score)
        if creator.engagement_rate >= 6.0:
            score += 20.0
        elif creator.engagement_rate >= 4.0:
            score += 15.0
        elif creator.engagement_rate >= 2.0:
            score += 10.0
        elif creator.engagement_rate >= 1.0:
            score += 5.0
        
        # Follower count and availability (10% of score)
        if creator.availability == "excellent":
            score += 5.0
        elif creator.availability == "good":
            score += 3.0
        elif creator.availability == "fair":
            score += 1.0
        
        # Optimal follower range bonus
        if 50000 <= creator.followers <= 500000:  # Sweet spot for engagement
            score += 5.0
        elif creator.followers > 100000:
            score += 3.0
        elif creator.followers > 10000:
            score += 2.0
        
        return min(score, 100.0)
    
    # Additional methods for compatibility
    
    async def discover_creators(
        self,
        campaign_data: CampaignData,
        max_creators: int = 10
    ) -> List[Creator]:
        """
        Alternative interface using CampaignData object
        
        Args:
            campaign_data: Complete campaign information
            max_creators: Maximum number of creators to return
            
        Returns:
            List of matching Creator objects
        """
        
        return await self.find_creators(
            target_audience=campaign_data.target_audience,
            budget_per_creator=campaign_data.budget_per_creator,
            max_creators=max_creators
        )
    
    async def find_matches(
        self,
        campaign_data: CampaignData,
        max_results: int = 5
    ) -> List[CreatorMatch]:
        """
        Alternative interface that returns CreatorMatch objects
        
        Args:
            campaign_data: Campaign information for matching
            max_results: Maximum number of matches to return
            
        Returns:
            List of CreatorMatch objects with detailed scoring
        """
        
        creators = await self.discover_creators(campaign_data, max_results)
        
        matches = []
        for creator in creators:
            match = CreatorMatch(
                creator=creator,
                similarity_score=creator.match_score / 100.0,
                estimated_rate=creator.rate_per_post,
                match_reasons=[
                    f"Niche: {creator.niche}",
                    f"Engagement: {creator.engagement_rate}%",
                    f"Followers: {creator.followers:,}"
                ],
                availability_score=0.9 if creator.availability == "excellent" else (
                    0.7 if creator.availability == "good" else 0.5
                ),
                rate_compatible=creator.rate_compatible
            )
            matches.append(match)
        
        return matches
    
    async def discover_influencers(self, product_niche: str, total_budget: float) -> List[Dict[str, Any]]:
        """
        Legacy interface for backward compatibility
        
        Args:
            product_niche: Product niche for matching
            total_budget: Total campaign budget
            
        Returns:
            List of creator dictionaries
        """
        
        max_creators = 5
        budget_per_creator = total_budget / max_creators
        
        creators = await self.find_creators(
            target_audience=f"People interested in {product_niche}",
            budget_per_creator=budget_per_creator,
            max_creators=max_creators
        )
        
        # Convert to dictionary format for legacy compatibility
        return [
            {
                "id": creator.id,
                "name": creator.name,
                "platform": creator.platform,
                "followers": creator.followers,
                "engagement_rate": creator.engagement_rate,
                "niche": creator.niche,
                "estimated_rate": creator.rate_per_post,
                "match_score": creator.match_score,
                "availability": creator.availability
            }
            for creator in creators
        ]