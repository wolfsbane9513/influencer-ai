# agents/discovery.py - CREATOR DISCOVERY AGENT
import logging
from typing import List, Dict, Any, Optional
from core.models import Creator, CampaignData
from core.config import settings

logger = logging.getLogger(__name__)

class DiscoveryAgent:
    """
    🔍 Creator Discovery Agent
    
    Finds and matches creators for campaigns using AI-powered matching
    """
    
    def __init__(self):
        self.initialized = True
        logger.info("🔍 Discovery Agent initialized")
    
    async def find_creators(
        self, 
        product_niche: str,
        target_audience: str, 
        budget: float,
        max_creators: int = 10
    ) -> List[Creator]:
        """
        Find creators matching campaign criteria
        
        Args:
            product_niche: Product niche (fitness, beauty, etc.)
            target_audience: Target audience description
            budget: Total campaign budget
            max_creators: Maximum number of creators to return
            
        Returns:
            List of matching creators
        """
        logger.info(f"🔍 Searching for {product_niche} creators...")
        logger.info(f"📊 Budget: ${budget}, Max creators: {max_creators}")
        
        # Get sample creators for testing
        sample_creators = self._get_sample_creators(product_niche, max_creators)
        
        logger.info(f"✅ Found {len(sample_creators)} matching creators")
        return sample_creators
    
    def _get_sample_creators(self, niche: str, max_creators: int) -> List[Creator]:
        """Get sample creators for testing"""
        
        sample_creators = [
            Creator(
                id="creator_001",
                name="Sample Creator 1",
                handle="@sample_creator_1",
                followers=50000,
                engagement_rate=4.2,
                niche=niche,
                rate_per_post=800.0,
                contact_email="creator1@example.com",
                phone_number="+1-555-0001"
            ),
            Creator(
                id="creator_002", 
                name="Sample Creator 2",
                handle="@sample_creator_2",
                followers=75000,
                engagement_rate=3.8,
                niche=niche,
                rate_per_post=1200.0,
                contact_email="creator2@example.com",
                phone_number="+1-555-0002"
            ),
            Creator(
                id="creator_003",
                name="Sample Creator 3", 
                handle="@sample_creator_3",
                followers=30000,
                engagement_rate=5.1,
                niche=niche,
                rate_per_post=600.0,
                contact_email="creator3@example.com",
                phone_number="+1-555-0003"
            )
        ]
        
        return sample_creators[:max_creators]

# Legacy compatibility aliases
InfluencerDiscoveryAgent = DiscoveryAgent
