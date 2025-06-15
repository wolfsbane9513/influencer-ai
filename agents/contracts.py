# agents/contracts.py - FIXED CONTRACT AGENT
import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional

from core.models import Contract, NegotiationResult, CampaignData

logger = logging.getLogger(__name__)

class ContractAgent:
    """
    📝 Fixed Contract Agent
    
    Clean, maintainable implementation for generating contracts.
    Compatible with orchestrator expectations.
    """
    
    def __init__(self):
        """Initialize contract agent"""
        logger.info("📝 Contract Agent initialized")
    
    async def generate_contract(
        self,
        negotiation_result: NegotiationResult,
        campaign_data: CampaignData
    ) -> Contract:
        """
        Generate contract from successful negotiation
        
        Args:
            negotiation_result: Result of successful negotiation
            campaign_data: Campaign information
            
        Returns:
            Contract object
        """
        try:
            logger.info(f"📝 Generating contract for {negotiation_result.creator_name}")
            
            # Generate contract ID
            contract_id = str(uuid.uuid4())
            
            # Calculate deadline (30 days from now)
            deadline = datetime.now() + timedelta(days=30)
            
            # Get agreed rate
            rate = negotiation_result.rate or 1000.0
            
            # Generate deliverables
            deliverables = self._generate_deliverables(negotiation_result, campaign_data)
            
            # Create contract
            contract = Contract(
                id=contract_id,
                creator_id=negotiation_result.creator_id,
                campaign_id=campaign_data.id,
                rate=rate,
                deliverables=deliverables,
                deadline=deadline,
                status="draft",
                payment_schedule="50% upfront, 50% on delivery",
                negotiation_id=getattr(negotiation_result, 'conversation_id', None)
            )
            
            logger.info(f"✅ Contract generated: {contract_id} - ${rate:.2f}")
            return contract
            
        except Exception as e:
            logger.error(f"❌ Contract generation failed: {e}")
            raise
    
    def _generate_deliverables(
        self,
        negotiation_result: NegotiationResult,
        campaign_data: CampaignData
    ) -> list:
        """Generate contract deliverables based on negotiation"""
        
        # Use negotiated deliverables if available
        if negotiation_result.negotiated_deliverables:
            return negotiation_result.negotiated_deliverables
        
        # Generate default deliverables based on campaign
        product_name = getattr(campaign_data, 'product_name', campaign_data.name)
        
        default_deliverables = [
            f"1 main post featuring {product_name}",
            "2 Instagram/social stories showcasing the product",
            "Usage rights for organic content (6 months)",
            "Performance metrics report within 7 days of posting"
        ]
        
        return default_deliverables
    
    def validate_contract_terms(self, contract: Contract) -> bool:
        """Validate contract terms"""
        try:
            # Basic validation
            if not contract.rate or contract.rate <= 0:
                logger.warning("⚠️ Invalid contract rate")
                return False
            
            if not contract.deliverables:
                logger.warning("⚠️ No deliverables specified")
                return False
            
            if contract.deadline < datetime.now():
                logger.warning("⚠️ Contract deadline is in the past")
                return False
            
            logger.info("✅ Contract validation passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Contract validation failed: {e}")
            return False
    
    def get_contract_template(self, contract_type: str = "standard") -> str:
        """Get contract template"""
        templates = {
            "standard": """
INFLUENCER COLLABORATION AGREEMENT

This agreement is between [BRAND_NAME] and [CREATOR_NAME] for the promotion of [PRODUCT_NAME].

DELIVERABLES:
{deliverables}

COMPENSATION: ${rate}

TIMELINE: Content to be delivered by {deadline}

USAGE RIGHTS: 6 months organic usage rights

PAYMENT TERMS: {payment_schedule}
            """,
            "premium": """
PREMIUM INFLUENCER PARTNERSHIP AGREEMENT

[Detailed premium contract template]
            """
        }
        
        return templates.get(contract_type, templates["standard"])
    
    def generate_contract_content(self, contract: Contract) -> str:
        """Generate full contract content"""
        template = self.get_contract_template()
        
        deliverables_text = "\n".join([f"- {d}" for d in contract.deliverables])
        
        content = template.format(
            deliverables=deliverables_text,
            rate=contract.rate,
            deadline=contract.deadline.strftime("%Y-%m-%d"),
            payment_schedule=contract.payment_schedule
        )
        
        return content