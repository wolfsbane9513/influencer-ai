import json
import logging
from pathlib import Path
from typing import Dict, Any

from models.campaign import CampaignData,Creator

logger = logging.getLogger(__name__)

class PricingService:
    """Service for pricing calculations and market data"""
    
    def __init__(self):
        self.market_data = self._load_market_data()
    
    def _load_market_data(self) -> Dict[str, Any]:
        """Load market pricing data"""
        try:
            market_file = Path("data/market_data.json")
            if market_file.exists():
                with open(market_file, 'r') as f:
                    data = json.load(f)
                logger.info("✅ Market data loaded from file")
                return data
            else:
                logger.warning("⚠️  market_data.json not found, using mock data")
                return self._get_mock_market_data()
        except Exception as e:
            logger.error(f"❌ Failed to load market data: {e}")
            return self._get_mock_market_data()
    
    def _get_mock_market_data(self) -> Dict[str, Any]:
        """Get mock market data"""
        return {
            "rate_benchmarks": {
                "fitness": {
                    "micro_influencer": {"min": 1800, "max": 3800, "avg": 2800},
                    "macro_influencer": {"min": 3800, "max": 6500, "avg": 5000},
                    "mega_influencer": {"min": 6500, "max": 12000, "avg": 9000}
                },
                "tech": {
                    "micro_influencer": {"min": 2000, "max": 4000, "avg": 3000},
                    "macro_influencer": {"min": 4000, "max": 8000, "avg": 6000},
                    "mega_influencer": {"min": 8000, "max": 15000, "avg": 12000}
                },
                "beauty": {
                    "micro_influencer": {"min": 1500, "max": 3500, "avg": 2500},
                    "macro_influencer": {"min": 3500, "max": 7000, "avg": 5000},
                    "mega_influencer": {"min": 7000, "max": 12000, "avg": 9500}
                }
            }
        }
    
    def calculate_estimated_rate(self, creator: Creator, campaign_data: CampaignData) -> float:
        """Calculate estimated rate for creator based on market data"""
        try:
            # Get market benchmarks for niche and tier
            niche = creator.niche.lower()
            tier = creator.tier.value
            
            benchmarks = self.market_data.get("rate_benchmarks", {})
            niche_benchmarks = benchmarks.get(niche, benchmarks.get("fitness", {}))
            tier_benchmarks = niche_benchmarks.get(tier, {"avg": creator.typical_rate})
            
            # Start with market average
            base_rate = tier_benchmarks.get("avg", creator.typical_rate)
            
            # Apply adjustments
            rate_multiplier = 1.0
            
            # Engagement rate adjustment
            if creator.engagement_rate > 6.0:
                rate_multiplier *= 1.2  # High engagement premium
            elif creator.engagement_rate < 2.0:
                rate_multiplier *= 0.8  # Low engagement discount
            
            # Availability adjustment
            if creator.availability.value == "busy":
                rate_multiplier *= 1.15  # Scarcity premium
            elif creator.availability.value == "excellent":
                rate_multiplier *= 0.95  # Availability discount
            
            # Budget pressure adjustment
            budget_per_influencer = campaign_data.total_budget / 3
            if base_rate > budget_per_influencer:
                rate_multiplier *= 0.9  # Budget constraint discount
            
            estimated_rate = base_rate * rate_multiplier
            
            # Ensure it's within reasonable bounds
            min_rate = tier_benchmarks.get("min", base_rate * 0.7)
            max_rate = tier_benchmarks.get("max", base_rate * 1.5)
            estimated_rate = max(min_rate, min(max_rate, estimated_rate))
            
            return round(estimated_rate, 2)
            
        except Exception as e:
            logger.error(f"Rate calculation failed: {e}")
            return creator.typical_rate