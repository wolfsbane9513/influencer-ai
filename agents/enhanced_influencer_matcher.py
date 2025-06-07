# agents/enhanced_influencer_matcher.py
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from pydantic import BaseModel

from models.campaign import CampaignData, Creator, CreatorMatch, CreatorTier
from agents.discovery import InfluencerDiscoveryAgent
from services.pricing import PricingService

logger = logging.getLogger(__name__)

class InfluencerSelectionStrategy(str, Enum):
    BUDGET_OPTIMIZED = "budget_optimized"
    REACH_MAXIMIZED = "reach_maximized"
    ENGAGEMENT_FOCUSED = "engagement_focused"
    DIVERSIFIED = "diversified"
    PREMIUM_QUALITY = "premium_quality"

class InfluencerStatus(str, Enum):
    AVAILABLE = "available"
    SELECTED = "selected"
    CONTACTED = "contacted"
    NEGOTIATING = "negotiating"
    CONFIRMED = "confirmed"
    DECLINED = "declined"
    RESERVE = "reserve"
    BACKUP = "backup"

class BudgetAllocation(BaseModel):
    """Budget allocation strategy"""
    total_budget: float
    primary_allocation: float  # 70-80% for primary selections
    reserve_allocation: float  # 15-20% for reserve influencers
    buffer_allocation: float   # 5-10% for negotiations buffer
    
    def get_per_influencer_budget(self, num_influencers: int) -> float:
        """Calculate budget per influencer"""
        return self.primary_allocation / num_influencers if num_influencers > 0 else 0

class InfluencerPool(BaseModel):
    """Manages influencer selection pools"""
    primary_selections: List[CreatorMatch] = []
    reserve_selections: List[CreatorMatch] = []
    backup_selections: List[CreatorMatch] = []
    contacted_influencers: List[str] = []
    confirmed_influencers: List[str] = []
    declined_influencers: List[str] = []
    
    def get_total_selected(self) -> int:
        return len(self.primary_selections)
    
    def get_available_reserves(self) -> List[CreatorMatch]:
        return [match for match in self.reserve_selections 
                if match.creator.id not in self.contacted_influencers]

class EnhancedInfluencerMatcher:
    """
    🎯 ENHANCED INFLUENCER MATCHER
    
    Features:
    1. Budget-based intelligent selection
    2. Sequential calling strategy
    3. Reserve influencer management
    4. Multi-tier selection optimization
    """
    
    def __init__(self):
        self.discovery_agent = InfluencerDiscoveryAgent()
        self.pricing_service = PricingService()
        
        # Configuration
        self.max_primary_selections = 5
        self.max_reserve_selections = 8
        self.max_backup_selections = 10
        
        # Budget allocation defaults
        self.default_primary_ratio = 0.75  # 75% for primary
        self.default_reserve_ratio = 0.20  # 20% for reserves
        self.default_buffer_ratio = 0.05   # 5% buffer
    
    async def enhanced_influencer_matching(
        self,
        campaign_data: CampaignData,
        strategy: InfluencerSelectionStrategy = InfluencerSelectionStrategy.BUDGET_OPTIMIZED,
        max_influencers: Optional[int] = None
    ) -> Tuple[InfluencerPool, BudgetAllocation]:
        """
        🚀 Enhanced influencer matching with budget optimization
        """
        
        logger.info(f"🎯 Starting enhanced matching for {campaign_data.product_name}")
        logger.info(f"💰 Budget: ${campaign_data.total_budget:,} | Strategy: {strategy.value}")
        
        # Step 1: Discover all potential influencers
        all_matches = await self._discover_all_potential_influencers(campaign_data)
        
        # Step 2: Calculate optimal budget allocation
        budget_allocation = self._calculate_budget_allocation(
            campaign_data.total_budget, strategy
        )
        
        # Step 3: Determine optimal number of influencers
        optimal_count = self._calculate_optimal_influencer_count(
            campaign_data.total_budget, all_matches, strategy, max_influencers
        )
        
        # Step 4: Select primary influencers based on strategy
        influencer_pool = await self._select_influencer_pools(
            all_matches, optimal_count, budget_allocation, strategy
        )
        
        # Step 5: Validate selections against budget
        await self._validate_budget_constraints(influencer_pool, budget_allocation)
        
        logger.info(f"✅ Enhanced matching complete:")
        logger.info(f"   Primary: {len(influencer_pool.primary_selections)} influencers")
        logger.info(f"   Reserve: {len(influencer_pool.reserve_selections)} influencers")
        logger.info(f"   Budget per primary: ${budget_allocation.get_per_influencer_budget(len(influencer_pool.primary_selections)):,.2f}")
        
        return influencer_pool, budget_allocation
    
    async def _discover_all_potential_influencers(self, campaign_data: CampaignData) -> List[CreatorMatch]:
        """🔍 Discover all potential influencers with expanded search"""
        
        # Get extended results for better selection
        max_discovery = self.max_primary_selections + self.max_reserve_selections + self.max_backup_selections
        
        all_matches = await self.discovery_agent.find_matches(
            campaign_data, 
            max_results=max_discovery
        )
        
        # Enhance matches with budget compatibility scoring
        enhanced_matches = []
        for match in all_matches:
            enhanced_match = await self._enhance_match_with_budget_data(match, campaign_data)
            enhanced_matches.append(enhanced_match)
        
        # Sort by combined score (similarity + budget + engagement)
        enhanced_matches.sort(key=lambda x: x.overall_score, reverse=True)
        
        logger.info(f"🔍 Discovered {len(enhanced_matches)} potential influencers")
        return enhanced_matches
    
    async def _enhance_match_with_budget_data(self, match: CreatorMatch, campaign_data: CampaignData) -> CreatorMatch:
        """💰 Enhance match with detailed budget analysis"""
        
        # Calculate more accurate estimated rate
        enhanced_rate = self.pricing_service.calculate_estimated_rate(match.creator, campaign_data)
        match.estimated_rate = enhanced_rate
        
        # Add budget efficiency scoring
        budget_per_influencer = campaign_data.total_budget / 3  # Assume 3 influencers default
        budget_efficiency = min(1.0, budget_per_influencer / enhanced_rate)
        
        # Enhanced overall score calculation
        base_score = match.similarity_score
        engagement_bonus = min(0.2, match.creator.engagement_rate / 10.0)  # Max 0.2 bonus
        budget_bonus = budget_efficiency * 0.15  # Max 0.15 bonus
        
        # Tier-based adjustments
        tier_adjustments = {
            CreatorTier.MICRO: 0.05,    # Micro influencers bonus
            CreatorTier.MACRO: 0.0,     # Neutral
            CreatorTier.MEGA: -0.05     # Slight penalty for cost
        }
        
        tier_adjustment = tier_adjustments.get(match.creator.tier, 0.0)
        
        enhanced_score = base_score + engagement_bonus + budget_bonus + tier_adjustment
        match.similarity_score = min(1.0, enhanced_score)  # Cap at 1.0
        
        return match
    
    def _calculate_budget_allocation(
        self, 
        total_budget: float, 
        strategy: InfluencerSelectionStrategy
    ) -> BudgetAllocation:
        """💰 Calculate optimal budget allocation based on strategy"""
        
        # Adjust ratios based on strategy
        if strategy == InfluencerSelectionStrategy.PREMIUM_QUALITY:
            primary_ratio = 0.80  # More for fewer, higher-quality influencers
            reserve_ratio = 0.15
            buffer_ratio = 0.05
        elif strategy == InfluencerSelectionStrategy.REACH_MAXIMIZED:
            primary_ratio = 0.70  # Spread budget across more influencers
            reserve_ratio = 0.25
            buffer_ratio = 0.05
        elif strategy == InfluencerSelectionStrategy.DIVERSIFIED:
            primary_ratio = 0.75  # Balanced approach
            reserve_ratio = 0.20
            buffer_ratio = 0.05
        else:  # BUDGET_OPTIMIZED and others
            primary_ratio = self.default_primary_ratio
            reserve_ratio = self.default_reserve_ratio
            buffer_ratio = self.default_buffer_ratio
        
        return BudgetAllocation(
            total_budget=total_budget,
            primary_allocation=total_budget * primary_ratio,
            reserve_allocation=total_budget * reserve_ratio,
            buffer_allocation=total_budget * buffer_ratio
        )
    
    def _calculate_optimal_influencer_count(
        self,
        total_budget: float,
        all_matches: List[CreatorMatch],
        strategy: InfluencerSelectionStrategy,
        max_influencers: Optional[int] = None
    ) -> int:
        """🔢 Calculate optimal number of influencers for budget"""
        
        if not all_matches:
            return 0
        
        # Get average rates by tier
        avg_rates = self._calculate_average_rates_by_tier(all_matches)
        
        # Strategy-based calculations
        if strategy == InfluencerSelectionStrategy.PREMIUM_QUALITY:
            # Fewer, higher-quality influencers
            target_rate = avg_rates.get(CreatorTier.MACRO, 5000)
            optimal_count = max(1, min(3, int(total_budget * 0.8 / target_rate)))
            
        elif strategy == InfluencerSelectionStrategy.REACH_MAXIMIZED:
            # More influencers for maximum reach
            target_rate = avg_rates.get(CreatorTier.MICRO, 3000)
            optimal_count = max(2, min(6, int(total_budget * 0.7 / target_rate)))
            
        elif strategy == InfluencerSelectionStrategy.ENGAGEMENT_FOCUSED:
            # Focus on high-engagement creators
            high_engagement_matches = [m for m in all_matches if m.creator.engagement_rate > 5.0]
            if high_engagement_matches:
                avg_high_engagement_rate = sum(m.estimated_rate for m in high_engagement_matches[:5]) / min(5, len(high_engagement_matches))
                optimal_count = max(1, min(4, int(total_budget * 0.75 / avg_high_engagement_rate)))
            else:
                optimal_count = 3
                
        elif strategy == InfluencerSelectionStrategy.DIVERSIFIED:
            # Mix of different tiers
            optimal_count = max(2, min(4, int(total_budget / 4000)))  # Assume $4k average
            
        else:  # BUDGET_OPTIMIZED
            # Optimize for best ROI
            if total_budget < 5000:
                optimal_count = 1
            elif total_budget < 15000:
                optimal_count = min(3, len([m for m in all_matches if m.estimated_rate < total_budget / 3]))
            else:
                optimal_count = min(4, len([m for m in all_matches if m.estimated_rate < total_budget / 4]))
        
        # Apply max_influencers constraint
        if max_influencers:
            optimal_count = min(optimal_count, max_influencers)
        
        # Ensure we have enough matches
        optimal_count = min(optimal_count, len(all_matches))
        
        logger.info(f"🔢 Optimal influencer count: {optimal_count} (strategy: {strategy.value})")
        return optimal_count
    
    def _calculate_average_rates_by_tier(self, matches: List[CreatorMatch]) -> Dict[CreatorTier, float]:
        """Calculate average rates by creator tier"""
        
        tier_rates = {}
        tier_counts = {}
        
        for match in matches:
            tier = match.creator.tier
            if tier not in tier_rates:
                tier_rates[tier] = 0
                tier_counts[tier] = 0
            
            tier_rates[tier] += match.estimated_rate
            tier_counts[tier] += 1
        
        # Calculate averages
        avg_rates = {}
        for tier in tier_rates:
            avg_rates[tier] = tier_rates[tier] / tier_counts[tier]
        
        return avg_rates
    
    async def _select_influencer_pools(
        self,
        all_matches: List[CreatorMatch],
        optimal_count: int,
        budget_allocation: BudgetAllocation,
        strategy: InfluencerSelectionStrategy
    ) -> InfluencerPool:
        """🎯 Select primary, reserve, and backup influencer pools"""
        
        pool = InfluencerPool()
        
        # Step 1: Select primary influencers
        pool.primary_selections = await self._select_primary_influencers(
            all_matches, optimal_count, budget_allocation, strategy
        )
        
        # Step 2: Select reserve influencers from remaining matches
        remaining_matches = [m for m in all_matches if m not in pool.primary_selections]
        pool.reserve_selections = await self._select_reserve_influencers(
            remaining_matches, budget_allocation, strategy
        )
        
        # Step 3: Select backup influencers
        remaining_after_reserve = [m for m in remaining_matches if m not in pool.reserve_selections]
        pool.backup_selections = remaining_after_reserve[:self.max_backup_selections]
        
        return pool
    
    async def _select_primary_influencers(
        self,
        all_matches: List[CreatorMatch],
        count: int,
        budget_allocation: BudgetAllocation,
        strategy: InfluencerSelectionStrategy
    ) -> List[CreatorMatch]:
        """🥇 Select primary influencers for initial contact"""
        
        budget_per_influencer = budget_allocation.get_per_influencer_budget(count)
        
        # Filter by budget constraints
        affordable_matches = [
            match for match in all_matches
            if match.estimated_rate <= budget_per_influencer * 1.2  # 20% buffer
        ]
        
        if len(affordable_matches) < count:
            logger.warning(f"⚠️ Only {len(affordable_matches)} affordable influencers found (need {count})")
        
        # Strategy-specific selection
        if strategy == InfluencerSelectionStrategy.PREMIUM_QUALITY:
            # Select highest-quality creators within budget
            primary_selections = sorted(
                affordable_matches, 
                key=lambda x: (x.creator.tier.value == "macro_influencer", x.similarity_score),
                reverse=True
            )[:count]
            
        elif strategy == InfluencerSelectionStrategy.ENGAGEMENT_FOCUSED:
            # Prioritize engagement rate
            primary_selections = sorted(
                affordable_matches,
                key=lambda x: (x.creator.engagement_rate, x.similarity_score),
                reverse=True
            )[:count]
            
        elif strategy == InfluencerSelectionStrategy.DIVERSIFIED:
            # Mix of different tiers and niches
            primary_selections = await self._select_diversified_influencers(affordable_matches, count)
            
        else:  # BUDGET_OPTIMIZED, REACH_MAXIMIZED
            # Best overall score within budget
            primary_selections = affordable_matches[:count]
        
        logger.info(f"🥇 Selected {len(primary_selections)} primary influencers")
        for i, match in enumerate(primary_selections):
            logger.info(f"   {i+1}. {match.creator.name} - ${match.estimated_rate:,} ({match.creator.tier.value})")
        
        return primary_selections
    
    async def _select_diversified_influencers(self, matches: List[CreatorMatch], count: int) -> List[CreatorMatch]:
        """Select a diversified mix of influencers"""
        
        # Group by tier
        tier_groups = {}
        for match in matches:
            tier = match.creator.tier
            if tier not in tier_groups:
                tier_groups[tier] = []
            tier_groups[tier].append(match)
        
        # Select from each tier proportionally
        selections = []
        remaining_count = count
        
        # Prioritize micro and macro influencers
        for tier in [CreatorTier.MICRO, CreatorTier.MACRO, CreatorTier.MEGA]:
            if tier in tier_groups and remaining_count > 0:
                tier_matches = tier_groups[tier]
                tier_count = min(remaining_count, max(1, remaining_count // len(tier_groups)))
                
                tier_selections = tier_matches[:tier_count]
                selections.extend(tier_selections)
                remaining_count -= len(tier_selections)
        
        # Fill remaining slots with best overall matches
        if remaining_count > 0:
            used_ids = {match.creator.id for match in selections}
            remaining_matches = [m for m in matches if m.creator.id not in used_ids]
            selections.extend(remaining_matches[:remaining_count])
        
        return selections[:count]
    
    async def _select_reserve_influencers(
        self,
        remaining_matches: List[CreatorMatch],
        budget_allocation: BudgetAllocation,
        strategy: InfluencerSelectionStrategy
    ) -> List[CreatorMatch]:
        """🛡️ Select reserve influencers for backup"""
        
        # Reserve budget should handle slightly higher rates
        reserve_budget_per_influencer = budget_allocation.reserve_allocation / max(1, len(remaining_matches[:self.max_reserve_selections]))
        
        # Filter affordable reserves
        affordable_reserves = [
            match for match in remaining_matches
            if match.estimated_rate <= reserve_budget_per_influencer * 1.3  # 30% buffer for reserves
        ]
        
        # Select top reserves by overall score
        reserve_selections = affordable_reserves[:self.max_reserve_selections]
        
        logger.info(f"🛡️ Selected {len(reserve_selections)} reserve influencers")
        
        return reserve_selections
    
    async def _validate_budget_constraints(self, pool: InfluencerPool, budget_allocation: BudgetAllocation):
        """✅ Validate that selections fit within budget"""
        
        primary_cost = sum(match.estimated_rate for match in pool.primary_selections)
        reserve_cost = sum(match.estimated_rate for match in pool.reserve_selections[:3])  # Assume max 3 reserves used
        
        total_estimated_cost = primary_cost + reserve_cost
        
        if total_estimated_cost > budget_allocation.total_budget:
            logger.warning(f"⚠️ Estimated cost (${total_estimated_cost:,}) exceeds budget (${budget_allocation.total_budget:,})")
        else:
            logger.info(f"✅ Budget validation passed: ${total_estimated_cost:,} / ${budget_allocation.total_budget:,}")
    
    async def get_next_influencer_to_contact(self, pool: InfluencerPool) -> Optional[CreatorMatch]:
        """📞 Get next influencer to contact based on sequential strategy"""
        
        # First, try primary selections not yet contacted
        for match in pool.primary_selections:
            if match.creator.id not in pool.contacted_influencers:
                pool.contacted_influencers.append(match.creator.id)
                return match
        
        # Then try reserves if primary selections are exhausted
        available_reserves = pool.get_available_reserves()
        if available_reserves:
            match = available_reserves[0]
            pool.contacted_influencers.append(match.creator.id)
            return match
        
        # Finally try backups
        for match in pool.backup_selections:
            if match.creator.id not in pool.contacted_influencers:
                pool.contacted_influencers.append(match.creator.id)
                return match
        
        return None
    
    def mark_influencer_response(
        self, 
        pool: InfluencerPool, 
        creator_id: str, 
        status: InfluencerStatus
    ):
        """📝 Mark influencer response status"""
        
        if status == InfluencerStatus.CONFIRMED:
            if creator_id not in pool.confirmed_influencers:
                pool.confirmed_influencers.append(creator_id)
        elif status == InfluencerStatus.DECLINED:
            if creator_id not in pool.declined_influencers:
                pool.declined_influencers.append(creator_id)
        
        logger.info(f"📝 Marked {creator_id} as {status.value}")
    
    def get_pool_status(self, pool: InfluencerPool) -> Dict[str, Any]:
        """📊 Get current status of influencer pools"""
        
        return {
            "primary_influencers": {
                "total": len(pool.primary_selections),
                "contacted": len([c for c in pool.contacted_influencers if c in [m.creator.id for m in pool.primary_selections]]),
                "confirmed": len([c for c in pool.confirmed_influencers if c in [m.creator.id for m in pool.primary_selections]]),
                "declined": len([c for c in pool.declined_influencers if c in [m.creator.id for m in pool.primary_selections]])
            },
            "reserve_influencers": {
                "total": len(pool.reserve_selections),
                "available": len(pool.get_available_reserves()),
                "contacted": len([c for c in pool.contacted_influencers if c in [m.creator.id for m in pool.reserve_selections]])
            },
            "backup_influencers": {
                "total": len(pool.backup_selections),
                "available": len([m for m in pool.backup_selections if m.creator.id not in pool.contacted_influencers])
            },
            "overall_progress": {
                "total_contacted": len(pool.contacted_influencers),
                "total_confirmed": len(pool.confirmed_influencers),
                "total_declined": len(pool.declined_influencers),
                "success_rate": len(pool.confirmed_influencers) / max(1, len(pool.contacted_influencers)) * 100
            }
        }