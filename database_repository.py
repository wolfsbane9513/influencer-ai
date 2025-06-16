"""Repository pattern implementation for clean data access"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, desc
from sqlalchemy.orm import selectinload

from models.database_models import Campaign, Creator, Negotiation, Contract, Payment

class BaseRepository(ABC):
    """Base repository with common CRUD operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    @abstractmethod
    def get_model_class(self):
        """Return the SQLAlchemy model class"""
        pass
    
    async def create(self, **kwargs) -> Any:
        """Create new record"""
        model_class = self.get_model_class()
        instance = model_class(**kwargs)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance
    
    async def get_by_id(self, record_id: Any) -> Optional[Any]:
        """Get record by ID"""
        model_class = self.get_model_class()
        result = await self.session.execute(
            select(model_class).where(model_class.id == record_id)
        )
        return result.scalar_one_or_none()
    
    async def update_by_id(self, record_id: Any, **kwargs) -> bool:
        """Update record by ID"""
        model_class = self.get_model_class()
        result = await self.session.execute(
            update(model_class).where(model_class.id == record_id).values(**kwargs)
        )
        await self.session.commit()
        return result.rowcount > 0
    
    async def delete_by_id(self, record_id: Any) -> bool:
        """Delete record by ID"""
        model_class = self.get_model_class()
        result = await self.session.execute(
            delete(model_class).where(model_class.id == record_id)
        )
        await self.session.commit()
        return result.rowcount > 0

class CampaignRepository(BaseRepository):
    """Campaign-specific repository operations"""
    
    def get_model_class(self):
        return Campaign
    
    async def get_with_relations(self, campaign_id: str) -> Optional[Campaign]:
        """Get campaign with all related data"""
        result = await self.session.execute(
            select(Campaign)
            .options(
                selectinload(Campaign.negotiations),
                selectinload(Campaign.contracts),
                selectinload(Campaign.outreach_logs)
            )
            .where(Campaign.id == campaign_id)
        )
        return result.scalar_one_or_none()
    
    async def get_active_campaigns(self) -> List[Campaign]:
        """Get all active campaigns"""
        result = await self.session.execute(
            select(Campaign).where(Campaign.status == "active")
        )
        return result.scalars().all()
    
    async def get_campaigns_by_niche(self, niche: str) -> List[Campaign]:
        """Get campaigns by product niche"""
        result = await self.session.execute(
            select(Campaign).where(Campaign.product_niche == niche)
        )
        return result.scalars().all()

class CreatorRepository(BaseRepository):
    """Creator-specific repository operations"""
    
    def get_model_class(self):
        return Creator
    
    async def get_by_niche_and_platform(self, niche: str, platform: str) -> List[Creator]:
        """Get creators by niche and platform"""
        result = await self.session.execute(
            select(Creator).where(
                Creator.niche == niche,
                Creator.platform == platform
            )
        )
        return result.scalars().all()
    
    async def get_available_creators(self, min_followers: int = 0) -> List[Creator]:
        """Get available creators with minimum followers"""
        result = await self.session.execute(
            select(Creator).where(
                Creator.availability.in_(["excellent", "good"]),
                Creator.followers >= min_followers
            )
        )
        return result.scalars().all()
    
    async def search_creators(self, 
                             niche: Optional[str] = None,
                             platform: Optional[str] = None,
                             min_followers: Optional[int] = None,
                             max_rate: Optional[float] = None) -> List[Creator]:
        """Advanced creator search with filters"""
        query = select(Creator)
        conditions = []
        
        if niche:
            conditions.append(Creator.niche == niche)
        if platform:
            conditions.append(Creator.platform == platform)
        if min_followers:
            conditions.append(Creator.followers >= min_followers)
        if max_rate:
            conditions.append(Creator.typical_rate <= max_rate)
        
        if conditions:
            query = query.where(*conditions)
        
        result = await self.session.execute(query.order_by(desc(Creator.engagement_rate)))
        return result.scalars().all()

class NegotiationRepository(BaseRepository):
    """Negotiation-specific repository operations"""
    
    def get_model_class(self):
        return Negotiation
    
    async def get_by_campaign(self, campaign_id: str) -> List[Negotiation]:
        """Get all negotiations for a campaign"""
        result = await self.session.execute(
            select(Negotiation).where(Negotiation.campaign_id == campaign_id)
        )
        return result.scalars().all()
    
    async def get_successful_negotiations(self, campaign_id: str) -> List[Negotiation]:
        """Get successful negotiations for a campaign"""
        result = await self.session.execute(
            select(Negotiation).where(
                Negotiation.campaign_id == campaign_id,
                Negotiation.status == "success"
            )
        )
        return result.scalars().all()