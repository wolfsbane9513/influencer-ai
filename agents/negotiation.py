# agents/negotiation.py - NEGOTIATION AGENT
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from core.models import Creator, CampaignData, NegotiationResult, NegotiationStatus
from core.config import settings

logger = logging.getLogger(__name__)

class NegotiationAgent:
    """
    🤝 Negotiation Agent
    
    Handles negotiations with creators using voice calls and AI analysis
    """
    
    def __init__(self):
        self.initialized = True
        logger.info("🤝 Negotiation Agent initialized")
    
    async def negotiate_with_creator(
        self,
        creator: Creator,
        campaign_data: CampaignData,
        voice_service: Optional[Any] = None
    ) -> NegotiationResult:
        """
        Negotiate with creator using voice service
        
        Args:
            creator: Creator to negotiate with
            campaign_data: Campaign details
            voice_service: Voice service for calls (optional)
            
        Returns:
            NegotiationResult with outcome
        """
        logger.info(f"🤝 Starting negotiation with {creator.name}")
        
        try:
            # For now, simulate successful negotiation
            # In real implementation, this would use voice_service to make actual calls
            
            # Simulate negotiation logic
            agreed_rate = creator.rate_per_post * 0.9  # 10% discount simulation
            
            result = NegotiationResult(
                creator_id=creator.id,
                creator_name=creator.name,
                status=NegotiationStatus.SUCCESS,
                agreed_rate=agreed_rate,
                original_rate=creator.rate_per_post,
                negotiated_terms=["10% discount applied", "Standard deliverables agreed"],
                negotiated_deliverables=[f"1 {campaign_data.product_niche} post", "2 stories"],
                call_duration_seconds=180,  # 3 minutes simulation
                negotiated_at=datetime.now()
            )
            
            logger.info(f"✅ Negotiation successful with {creator.name}: ${agreed_rate}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Negotiation failed with {creator.name}: {e}")
            
            return NegotiationResult(
                creator_id=creator.id,
                creator_name=creator.name,
                status=NegotiationStatus.FAILED,
                negotiated_at=datetime.now()
            )
    
    async def conduct_negotiation(self, creator: Creator, campaign_data: CampaignData) -> NegotiationResult:
        """Alternative method name for backward compatibility"""
        return await self.negotiate_with_creator(creator, campaign_data)
