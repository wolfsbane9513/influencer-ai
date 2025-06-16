"""
Real PostgreSQL database service for InfluencerFlow AI Platform.
This completely replaces the previous mock implementation.
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from config.database import DatabaseConfig
from models.database_models import Campaign, Creator, Negotiation, Contract, Payment, OutreachLog
from models.campaign import CampaignOrchestrationState, CampaignData, Creator as CampaignCreator
from database_repository import CampaignRepository, CreatorRepository, NegotiationRepository

logger = logging.getLogger(__name__)

class DatabaseService:
    """
    Complete database service with real PostgreSQL operations.
    This replaces the mock implementation entirely - no legacy code.
    """
    
    def __init__(self):
        self.db_config = DatabaseConfig()
        self._initialized = False
        logger.info("🗄️ Database service initialized with PostgreSQL")
    
    async def initialize(self):
        """Initialize database tables if not already done"""
        if not self._initialized:
            await self.db_config.create_tables()
            self._initialized = True
            logger.info("✅ Database tables initialized")
    
    async def get_session(self) -> AsyncSession:
        """Get async database session"""
        return self.db_config.AsyncSessionLocal()
    
    # ================================
    # CAMPAIGN OPERATIONS
    # ================================
    
    async def create_campaign(self, campaign_data: CampaignData) -> Campaign:
        """Create new campaign in database"""
        await self.initialize()
        
        async with self.get_session() as session:
            campaign = Campaign(
                id=campaign_data.id,
                product_name=campaign_data.product_name,
                brand_name=campaign_data.brand_name,
                product_description=campaign_data.product_description,
                target_audience=campaign_data.target_audience,
                campaign_goal=campaign_data.campaign_goal,
                product_niche=campaign_data.product_niche,
                total_budget=campaign_data.total_budget,
                status=campaign_data.status,
                campaign_code=campaign_data.campaign_code
            )
            session.add(campaign)
            await session.commit()
            await session.refresh(campaign)
            logger.info(f"✅ Campaign created: {campaign.id}")
            return campaign
    
    async def get_campaign(self, campaign_id: str) -> Optional[Campaign]:
        """Get campaign by ID with all relations"""
        await self.initialize()
        
        async with self.get_session() as session:
            result = await session.execute(
                select(Campaign)
                .options(
                    selectinload(Campaign.negotiations),
                    selectinload(Campaign.contracts),
                    selectinload(Campaign.outreach_logs)
                )
                .where(Campaign.id == campaign_id)
            )
            return result.scalar_one_or_none()
    
    async def update_campaign(self, campaign_id: str, updates: Dict[str, Any]) -> bool:
        """Update campaign with new data"""
        await self.initialize()
        
        async with self.get_session() as session:
            updates['updated_at'] = datetime.now()
            result = await session.execute(
                update(Campaign).where(Campaign.id == campaign_id).values(**updates)
            )
            await session.commit()
            logger.info(f"📝 Campaign updated: {campaign_id}")
            return result.rowcount > 0
    
    # ================================
    # CREATOR OPERATIONS
    # ================================
    
    async def create_or_update_creator(self, creator_data: CampaignCreator) -> Creator:
        """Create or update creator in database"""
        await self.initialize()
        
        async with self.get_session() as session:
            # Check if creator exists
            result = await session.execute(select(Creator).where(Creator.id == creator_data.id))
            creator = result.scalar_one_or_none()
            
            if creator:
                # Update existing creator
                creator.name = creator_data.name
                creator.platform = creator_data.platform
                creator.followers = creator_data.followers
                creator.niche = creator_data.niche
                creator.typical_rate = creator_data.typical_rate
                creator.engagement_rate = creator_data.engagement_rate
                creator.average_views = creator_data.average_views
                creator.availability = creator_data.availability
                creator.location = creator_data.location
                creator.phone_number = creator_data.phone_number
                creator.languages = creator_data.languages
                creator.specialties = creator_data.specialties
            else:
                # Create new creator
                creator = Creator(
                    id=creator_data.id,
                    name=creator_data.name,
                    platform=creator_data.platform,
                    followers=creator_data.followers,
                    niche=creator_data.niche,
                    typical_rate=creator_data.typical_rate,
                    engagement_rate=creator_data.engagement_rate,
                    average_views=creator_data.average_views,
                    availability=creator_data.availability,
                    location=creator_data.location,
                    phone_number=creator_data.phone_number,
                    languages=creator_data.languages,
                    specialties=creator_data.specialties
                )
                session.add(creator)
            
            await session.commit()
            await session.refresh(creator)
            logger.info(f"✅ Creator saved: {creator.id}")
            return creator
    
    async def get_creators_by_niche(self, niche: str) -> List[Creator]:
        """Get creators by niche"""
        await self.initialize()
        
        async with self.get_session() as session:
            result = await session.execute(
                select(Creator).where(Creator.niche == niche)
            )
            return result.scalars().all()
    
    async def search_creators(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search creators with advanced filters"""
        await self.initialize()
        
        async with self.get_session() as session:
            repo = CreatorRepository(session)
            creators = await repo.search_creators(**filters)
            return [
                {
                    "id": creator.id,
                    "name": creator.name,
                    "platform": creator.platform,
                    "followers": creator.followers,
                    "niche": creator.niche,
                    "typical_rate": creator.typical_rate,
                    "engagement_rate": creator.engagement_rate
                }
                for creator in creators
            ]
    
    # ================================
    # ORCHESTRATION SYNC (Main Method)
    # ================================
    
    async def sync_campaign_results(self, orchestration_state: CampaignOrchestrationState):
        """
        Sync campaign orchestration results to database.
        This is the main method called by the orchestrator.
        """
        await self.initialize()
        
        try:
            logger.info(f"💾 Syncing campaign {orchestration_state.campaign_id} to database")
            
            # Update campaign record
            await self._update_campaign_from_state(orchestration_state)
            
            # Sync discovered creators
            await self._sync_discovered_creators(orchestration_state)
            
            # Sync negotiations
            await self._sync_negotiations(orchestration_state)
            
            # Sync contracts
            await self._sync_contracts(orchestration_state)
            
            # Create outreach logs
            await self._create_outreach_logs(orchestration_state)
            
            logger.info("✅ Database sync completed")
            
        except Exception as e:
            logger.error(f"❌ Database sync failed: {e}")
            # Fallback to logging - maintains system stability
            await self._fallback_logging(orchestration_state)
            raise
    
    async def _update_campaign_from_state(self, state: CampaignOrchestrationState):
        """Update campaign with orchestration results"""
        updates = {
            "status": "completed" if state.completed_at else "active",
            "influencer_count": state.successful_negotiations,
            "total_cost": state.total_cost,
            "ai_strategy": state.ai_strategy
        }
        
        if state.completed_at:
            updates["completed_at"] = state.completed_at
        
        await self.update_campaign(state.campaign_id, updates)
    
    async def _sync_discovered_creators(self, state: CampaignOrchestrationState):
        """Sync discovered creators to database"""
        for creator in state.discovered_influencers:
            await self.create_or_update_creator(creator)
    
    async def _sync_negotiations(self, state: CampaignOrchestrationState):
        """Sync negotiations to database"""
        async with self.get_session() as session:
            for negotiation in state.negotiations:
                db_negotiation = Negotiation(
                    campaign_id=state.campaign_id,
                    creator_id=negotiation.creator_id,
                    status=negotiation.status,
                    initial_rate=negotiation.initial_rate,
                    final_rate=negotiation.final_rate,
                    negotiated_terms=negotiation.negotiated_terms,
                    call_status=negotiation.call_status,
                    email_status=negotiation.email_status,
                    call_duration_seconds=negotiation.call_duration_seconds,
                    call_recording_url=negotiation.call_recording_url,
                    call_transcript=negotiation.call_transcript,
                    last_contact_date=negotiation.last_contact_date
                )
                session.add(db_negotiation)
            
            await session.commit()
            logger.info(f"📞 Synced {len(state.negotiations)} negotiations")
    
    async def _sync_contracts(self, state: CampaignOrchestrationState):
        """Sync contracts to database"""
        async with self.get_session() as session:
            for contract in state.contracts:
                db_contract = Contract(
                    id=contract.contract_id,
                    campaign_id=contract.campaign_id,
                    creator_id=contract.creator_id,
                    compensation_amount=contract.compensation_amount,
                    deliverables=contract.deliverables,
                    timeline=contract.timeline,
                    usage_rights=contract.usage_rights,
                    status=contract.status,
                    contract_text=contract.contract_text,
                    legal_review_status=contract.legal_review_status,
                    amendments=contract.amendments
                )
                session.add(db_contract)
                
                # Create payment record if contract is signed
                if contract.status.value == "signed":
                    payment = Payment(
                        contract_id=contract.contract_id,
                        amount=contract.compensation_amount,
                        status="pending",
                        payment_method="bank_transfer",
                        due_date=datetime.now()
                    )
                    session.add(payment)
            
            await session.commit()
            logger.info(f"📝 Synced {len(state.contracts)} contracts")
    
    async def _create_outreach_logs(self, state: CampaignOrchestrationState):
        """Create outreach logs from negotiations"""
        async with self.get_session() as session:
            for negotiation in state.negotiations:
                log = OutreachLog(
                    campaign_id=state.campaign_id,
                    creator_id=negotiation.creator_id,
                    contact_type="call",
                    status=negotiation.call_status.value,
                    duration_minutes=negotiation.call_duration_seconds // 60,
                    recording_url=negotiation.call_recording_url,
                    transcript=negotiation.call_transcript,
                    sentiment="positive" if negotiation.status.value == "success" else "neutral",
                    notes=f"Negotiation {negotiation.status.value}"
                )
                session.add(log)
            
            await session.commit()
            logger.info(f"📊 Created {len(state.negotiations)} outreach logs")
    
    async def _fallback_logging(self, state: CampaignOrchestrationState):
        """Fallback logging if database operations fail"""
        logger.warning("📝 Using fallback logging due to database error")
        
        # Log campaign data
        logger.info(f"📝 Campaign: {state.campaign_id} - Status: {'completed' if state.completed_at else 'active'}")
        logger.info(f"💰 Total Cost: ${state.total_cost} - Successful: {state.successful_negotiations}")
        
        # Log negotiations
        for negotiation in state.negotiations:
            logger.info(f"📞 Negotiation: {negotiation.creator_id} - {negotiation.status.value} - ${negotiation.final_rate}")
    
    # ================================
    # ANALYTICS METHODS
    # ================================
    
    async def get_campaign_analytics(self, campaign_id: str) -> Dict[str, Any]:
        """Get comprehensive campaign analytics"""
        await self.initialize()
        
        async with self.get_session() as session:
            from database_queries import DatabaseQueries
            return await DatabaseQueries.get_campaign_analytics(session, campaign_id)
    
    async def get_campaign_roi_analysis(self, campaign_id: str) -> Dict[str, Any]:
        """Get ROI analysis for campaign"""
        await self.initialize()
        
        async with self.get_session() as session:
            from database_queries import DatabaseQueries
            return await DatabaseQueries.get_campaign_roi_analysis(session, campaign_id)
    
    # ================================
    # CLEANUP
    # ================================
    
    async def close(self):
        """Close database connections"""
        await self.db_config.close()
        logger.info("🔐 Database connections closed")