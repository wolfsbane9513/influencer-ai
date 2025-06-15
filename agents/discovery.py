# agents/discovery.py - FIXED DISCOVERY AGENT
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
    Compatible with orchestrator expectations.
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
                "id": "creator_001",
                "name": "Sample Creator 1",
                "handle": "@samplecreator1",
                "platform": "instagram",
                "followers": 75000,
                "engagement_rate": 4.5,
                "average_views": 15000,
                "niche": "tech",
                "location": "San Francisco",
                "phone": "+1234567890",
                "languages": ["English"],
                "specialties": ["tech", "gadgets"],
                "rate_per_post": 1200.0,
                "typical_rate": 1200.0,
                "availability": "excellent",
                "brand_safety_score": 9.0
            },
            {
                "id": "creator_002",
                "name": "Sample Creator 2", 
                "handle": "@samplecreator2",
                "platform": "youtube",
                "followers": 150000,
                "engagement_rate": 5.2,
                "average_views": 25000,
                "niche": "tech",
                "location": "New York",
                "phone": "+1234567891",
                "languages": ["English"],
                "specialties": ["tech", "reviews"],
                "rate_per_post": 1800.0,
                "typical_rate": 1800.0,
                "availability": "good",
                "brand_safety_score": 8.5
            },
            {
                "id": "creator_003",
                "name": "Sample Creator 3",
                "handle": "@samplecreator3", 
                "platform": "tiktok",
                "followers": 45000,
                "engagement_rate": 6.1,
                "average_views": 12000,
                "niche": "tech",
                "location": "Los Angeles",
                "phone": "+1234567892",
                "languages": ["English"],
                "specialties": ["tech", "unboxing"],
                "rate_per_post": 900.0,
                "typical_rate": 900.0,
                "availability": "excellent",
                "brand_safety_score": 8.8
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
    
    async def discover_creators(
        self, 
        campaign_data: CampaignData, 
        max_creators: int = 10
    ) -> List[Creator]:
        """
        Discover creators for campaign (main interface method)
        
        Args:
            campaign_data: Campaign information for matching
            max_creators: Maximum number of creators to return
            
        Returns:
            List of Creator objects
        """
        logger.info(f"🔍 Searching for creators...")
        logger.info(f"📊 Budget: ${campaign_data.total_budget}, Max creators: {max_creators}")
        
        try:
            # Calculate budget per creator
            budget_per_creator = campaign_data.total_budget / max_creators
            
            # Filter and score creators
            matching_creators = []
            
            for creator in self.creators_data:
                # Calculate match score
                match_score = self._calculate_match_score(creator, campaign_data, budget_per_creator)
                
                if match_score > 50.0:  # Only include good matches
                    creator.match_score = match_score
                    creator.rate_compatible = creator.rate_per_post <= budget_per_creator * 1.2
                    matching_creators.append(creator)
            
            # Sort by match score
            matching_creators.sort(key=lambda c: c.match_score, reverse=True)
            
            # Return top matches
            result = matching_creators[:max_creators]
            
            logger.info(f"✅ Found {len(result)} matching creators")
            for creator in result:
                logger.info(f"   👤 {creator.name} - Score: {creator.match_score:.1f}, Rate: ${creator.rate_per_post}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Discovery failed: {e}")
            # Return mock creators for demo
            return self.creators_data[:min(3, len(self.creators_data))]
    
    def _calculate_match_score(
        self, 
        creator: Creator, 
        campaign_data: CampaignData, 
        budget_per_creator: float
    ) -> float:
        """Calculate how well a creator matches the campaign"""
        score = 0.0
        
        # Niche matching (40% of score)
        campaign_niche = getattr(campaign_data, 'product_niche', 'tech')
        if creator.niche.lower() == campaign_niche.lower():
            score += 40.0
        elif campaign_niche.lower() in [s.lower() for s in creator.specialties]:
            score += 25.0
        
        # Budget compatibility (30% of score)
        if creator.rate_per_post <= budget_per_creator:
            score += 30.0
        elif creator.rate_per_post <= budget_per_creator * 1.2:
            score += 20.0
        elif creator.rate_per_post <= budget_per_creator * 1.5:
            score += 10.0
        
        # Engagement rate (20% of score)
        if creator.engagement_rate >= 5.0:
            score += 20.0
        elif creator.engagement_rate >= 3.0:
            score += 15.0
        elif creator.engagement_rate >= 1.0:
            score += 10.0
        
        # Follower count and availability (10% of score)
        if creator.availability in ["excellent", "good"]:
            score += 5.0
        
        if 10000 <= creator.followers <= 500000:  # Sweet spot
            score += 5.0
        elif creator.followers > 100000:
            score += 3.0
        
        return min(score, 100.0)
    
    async def find_matches(
        self, 
        campaign_data: CampaignData, 
        max_results: int = 5
    ) -> List[CreatorMatch]:
        """
        Alternative interface that returns CreatorMatch objects
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
                availability_score=0.8 if creator.availability == "excellent" else 0.6,
                rate_compatible=creator.rate_compatible
            )
            matches.append(match)
        
        return matches
    
    async def discover_influencers(self, product_niche: str, total_budget: float) -> List[Dict[str, Any]]:
        """
        Legacy interface for backward compatibility
        """
        # Create mock campaign data
        mock_campaign = CampaignData(
            id="discovery_temp",
            name=f"Discovery for {product_niche}",
            description=f"Product in {product_niche} niche",
            product_niche=product_niche,
            total_budget=total_budget,
            max_creators=5
        )
        
        creators = await self.discover_creators(mock_campaign, 5)
        
        # Convert to dictionary format
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