# agents/contracts.py - CONTRACT AGENT
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import uuid

from core.models import Contract, NegotiationResult, CampaignData
from core.config import settings

logger = logging.getLogger(__name__)

class ContractAgent:
    """
    📝 Contract Agent
    
    Generates contracts from successful negotiations
    """
    
    def __init__(self):
        self.initialized = True
        logger.info("📝 Contract Agent initialized")
    
    async def generate_contract(
        self,
        negotiation: NegotiationResult,
        campaign_data: CampaignData
    ) -> Contract:
        """
        Generate contract from negotiation result
        
        Args:
            negotiation: Successful negotiation result
            campaign_data: Campaign details
            
        Returns:
            Generated contract
        """
        logger.info(f"📝 Generating contract for {negotiation.creator_name}")
        
        try:
            contract_id = str(uuid.uuid4())
            
            # Create contract
            contract = Contract(
                id=contract_id,
                creator_id=negotiation.creator_id,
                campaign_id=campaign_data.id,
                rate=negotiation.agreed_rate or 0,
                deliverables=[
                    f"1 {campaign_data.product_niche} post about {campaign_data.product_name}",
                    "2 Instagram stories featuring the product",
                    "Usage rights for 6 months"
                ],
                deadline=datetime.now() + timedelta(days=30),
                created_at=datetime.now()
            )
            
            logger.info(f"✅ Contract generated: {contract_id}")
            return contract
            
        except Exception as e:
            logger.error(f"❌ Contract generation failed: {e}")
            raise
    
    async def create_contract(self, negotiation: NegotiationResult, campaign_data: CampaignData) -> Contract:
        """Alternative method name for backward compatibility"""
        return await self.generate_contract(negotiation, campaign_data)
