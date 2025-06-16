"""Advanced database queries and analytics for InfluencerFlow platform"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from sqlalchemy.orm import selectinload
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from models.database_models import Campaign, Creator, Negotiation, Contract, Payment, OutreachLog

class DatabaseQueries:
    """Advanced database queries and analytics"""
    
    @staticmethod
    async def get_campaign_analytics(session: AsyncSession, campaign_id: str) -> Dict[str, Any]:
        """Get comprehensive campaign analytics"""
        
        # Get campaign with all relations
        campaign = await session.execute(
            select(Campaign)
            .options(
                selectinload(Campaign.negotiations),
                selectinload(Campaign.contracts),
                selectinload(Campaign.outreach_logs)
            )
            .where(Campaign.id == campaign_id)
        )
        campaign = campaign.scalar_one_or_none()
        
        if not campaign:
            return {}
        
        # Calculate metrics
        total_contacted = len(campaign.negotiations)
        successful_negotiations = [n for n in campaign.negotiations if n.status.value == "success"]
        failed_negotiations = [n for n in campaign.negotiations if n.status.value == "failed"]
        signed_contracts = [c for c in campaign.contracts if c.status.value == "signed"]
        
        success_rate = (len(successful_negotiations) / total_contacted) * 100 if total_contacted > 0 else 0
        average_rate = sum(n.final_rate or 0 for n in successful_negotiations) / len(successful_negotiations) if successful_negotiations else 0
        
        return {
            "campaign_id": campaign_id,
            "campaign_name": f"{campaign.brand_name} - {campaign.product_name}",
            "status": campaign.status.value,
            "total_budget": campaign.total_budget,
            "total_cost": campaign.total_cost,
            "budget_utilization": (campaign.total_cost / campaign.total_budget) * 100 if campaign.total_budget > 0 else 0,
            "creators_contacted": total_contacted,
            "successful_negotiations": len(successful_negotiations),
            "failed_negotiations": len(failed_negotiations),
            "success_rate": success_rate,
            "average_final_rate": average_rate,
            "contracts_generated": len(campaign.contracts),
            "contracts_signed": len(signed_contracts),
            "created_at": campaign.created_at,
            "completed_at": campaign.completed_at
        }
    
    @staticmethod
    async def get_campaign_roi_analysis(session: AsyncSession, campaign_id: str) -> Dict[str, Any]:
        """Calculate ROI and performance metrics for a campaign"""
        
        campaign = await session.execute(
            select(Campaign)
            .options(selectinload(Campaign.negotiations))
            .where(Campaign.id == campaign_id)
        )
        campaign = campaign.scalar_one_or_none()
        
        if not campaign:
            return {}
        
        # Calculate estimated reach and engagement
        total_reach = 0
        total_engagement = 0
        
        for negotiation in campaign.negotiations:
            if negotiation.status.value == "success":
                # Get creator details
                creator = await session.execute(
                    select(Creator).where(Creator.id == negotiation.creator_id)
                )
                creator = creator.scalar_one_or_none()
                
                if creator:
                    total_reach += creator.followers
                    total_engagement += creator.followers * (creator.engagement_rate / 100)
        
        # Calculate cost metrics
        cost_per_reach = campaign.total_cost / total_reach if total_reach > 0 else 0
        cost_per_engagement = campaign.total_cost / total_engagement if total_engagement > 0 else 0
        
        return {
            "campaign_id": campaign_id,
            "total_investment": campaign.total_cost,
            "estimated_reach": total_reach,
            "estimated_engagement": total_engagement,
            "cost_per_reach": cost_per_reach,
            "cost_per_engagement": cost_per_engagement,
            "successful_partnerships": len([n for n in campaign.negotiations if n.status.value == "success"]),
            "active_contracts": len([c for c in campaign.contracts if c.status.value in ["signed", "executed"]])
        }
    
    @staticmethod
    async def get_top_creators_by_niche(session: AsyncSession, niche: str, limit: int = 10) -> List[Creator]:
        """Get top creators by niche based on engagement and followers"""
        result = await session.execute(
            select(Creator)
            .where(Creator.niche == niche)
            .order_by(desc(Creator.engagement_rate), desc(Creator.followers))
            .limit(limit)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_platform_performance_stats(session: AsyncSession) -> List[Dict[str, Any]]:
        """Get performance statistics by platform"""
        result = await session.execute(
            select(
                Creator.platform,
                func.count(Negotiation.id).label("total_negotiations"),
                func.count().filter(Negotiation.status == "success").label("successful_negotiations"),
                func.avg(Negotiation.final_rate).label("average_rate")
            )
            .join(Negotiation, Creator.id == Negotiation.creator_id)
            .group_by(Creator.platform)
        )
        
        platform_stats = []
        for row in result:
            success_rate = (row.successful_negotiations / row.total_negotiations) * 100 if row.total_negotiations > 0 else 0
            platform_stats.append({
                "platform": row.platform,
                "total_negotiations": row.total_negotiations,
                "successful_negotiations": row.successful_negotiations,
                "success_rate": success_rate,
                "average_rate": float(row.average_rate) if row.average_rate else 0
            })
        
        return platform_stats
