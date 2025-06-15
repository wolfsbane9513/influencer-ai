# agents/contracts.py - FIXED CONTRACT AGENT
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from core.models import CampaignData
from agents.negotiation import NegotiationResult

logger = logging.getLogger(__name__)


@dataclass
class ContractTerms:
    """Contract terms and conditions"""
    creator_id: str
    creator_name: str
    company_name: str
    product_name: str
    compensation: float
    deliverables: str
    timeline: str
    usage_rights: str
    exclusivity_period: str
    payment_schedule: str
    revision_rounds: int = 2
    cancellation_policy: str = "7 days notice"
    
    def __str__(self) -> str:
        return f"Contract: {self.creator_name} - {self.company_name} (${self.compensation})"


@dataclass 
class Contract:
    """Generated contract document"""
    contract_id: str
    terms: ContractTerms
    contract_text: str
    generated_at: datetime
    status: str = "draft"
    
    def __str__(self) -> str:
        return f"Contract {self.contract_id}: {self.terms.creator_name}"


class ContractAgent:
    """
    📝 Fixed Contract Agent
    
    Generates legal contracts based on successful negotiations:
    - Clean OOP design with single responsibility
    - Proper error handling and validation
    - Resource cleanup with close() method
    - No unnecessary helper functions
    """
    
    def __init__(self):
        """Initialize contract agent"""
        
        # Contract templates and configuration
        self.default_usage_rights = "Non-exclusive usage rights for 12 months"
        self.default_exclusivity = "30 days exclusivity in product category"
        self.default_payment_terms = "50% upfront, 50% upon delivery"
        
        logger.info("📝 Contract Agent initialized")
    
    async def generate_contract(
        self,
        negotiation_result: NegotiationResult,
        campaign_data: CampaignData
    ) -> Contract:
        """
        Generate contract from successful negotiation
        
        Args:
            negotiation_result: Successful negotiation outcome
            campaign_data: Campaign context and requirements
            
        Returns:
            Generated contract with terms and legal text
        """
        
        if not negotiation_result.is_successful():
            raise ValueError(f"Cannot generate contract for failed negotiation: {negotiation_result.status}")
        
        logger.info(f"📝 Generating contract for creator {negotiation_result.creator_id}")
        
        try:
            # Step 1: Extract contract terms from negotiation
            terms = self._extract_contract_terms(negotiation_result, campaign_data)
            
            # Step 2: Generate contract text
            contract_text = self._generate_contract_text(terms)
            
            # Step 3: Create contract object
            contract = Contract(
                contract_id=self._generate_contract_id(terms),
                terms=terms,
                contract_text=contract_text,
                generated_at=datetime.now(),
                status="draft"
            )
            
            logger.info(f"✅ Contract generated: {contract.contract_id}")
            return contract
            
        except Exception as e:
            logger.error(f"❌ Contract generation failed for {negotiation_result.creator_id}: {e}")
            raise
    
    def _extract_contract_terms(
        self,
        negotiation_result: NegotiationResult,
        campaign_data: CampaignData
    ) -> ContractTerms:
        """Extract contract terms from negotiation outcome"""
        
        # Get negotiated values or use defaults
        compensation = negotiation_result.final_rate or campaign_data.budget_per_creator
        deliverables = negotiation_result.deliverables or campaign_data.content_requirements
        timeline = negotiation_result.timeline or campaign_data.timeline
        
        return ContractTerms(
            creator_id=negotiation_result.creator_id,
            creator_name=negotiation_result.creator_id,  # In real app, lookup creator name
            company_name=campaign_data.company_name,
            product_name=campaign_data.product_name,
            compensation=compensation,
            deliverables=deliverables,
            timeline=timeline,
            usage_rights=self.default_usage_rights,
            exclusivity_period=self.default_exclusivity,
            payment_schedule=self.default_payment_terms
        )
    
    def _generate_contract_text(self, terms: ContractTerms) -> str:
        """Generate formal contract text from terms"""
        
        contract_date = datetime.now().strftime("%B %d, %Y")
        
        contract_text = f"""
INFLUENCER MARKETING AGREEMENT

This Influencer Marketing Agreement ("Agreement") is entered into on {contract_date} between:

COMPANY: {terms.company_name}
INFLUENCER: {terms.creator_name} (ID: {terms.creator_id})

PRODUCT: {terms.product_name}

1. SCOPE OF WORK
The Influencer agrees to create and publish the following content:
{terms.deliverables}

2. COMPENSATION
Total compensation: ${terms.compensation:,.2f}
Payment schedule: {terms.payment_schedule}

3. TIMELINE
Content delivery timeline: {terms.timeline}
Campaign duration: As specified in timeline

4. USAGE RIGHTS
{terms.usage_rights}

5. EXCLUSIVITY
{terms.exclusivity_period}

6. CONTENT GUIDELINES
- Content must align with brand guidelines provided by Company
- All content subject to Company approval before publication
- Maximum {terms.revision_rounds} rounds of revisions included
- Content must include appropriate disclosure hashtags (#ad, #sponsored, etc.)

7. PAYMENT TERMS
- {terms.payment_schedule}
- Payments due within 30 days of invoice
- Late payments subject to 1.5% monthly fee

8. CANCELLATION
Either party may cancel with {terms.cancellation_policy}
Compensation for completed work remains due.

9. LEGAL TERMS
- This agreement governed by applicable local laws
- Any disputes resolved through binding arbitration
- Force majeure clause applies for unforeseen circumstances

10. SIGNATURES
By proceeding with this campaign, both parties agree to these terms.

Company Representative: ___________________ Date: ___________
Influencer: ___________________ Date: ___________

Contract ID: {self._generate_contract_id(terms)}
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        
        return contract_text.strip()
    
    def _generate_contract_id(self, terms: ContractTerms) -> str:
        """Generate unique contract identifier"""
        
        timestamp = datetime.now().strftime("%Y%m%d")
        creator_prefix = terms.creator_id[:8].upper()
        
        return f"INFL-{timestamp}-{creator_prefix}"
    
    async def validate_contract(self, contract: Contract) -> Dict[str, Any]:
        """
        Validate contract terms and completeness
        
        Args:
            contract: Contract to validate
            
        Returns:
            Validation results with any issues found
        """
        
        issues = []
        warnings = []
        
        # Check required fields
        if not contract.terms.compensation or contract.terms.compensation <= 0:
            issues.append("Invalid compensation amount")
        
        if not contract.terms.deliverables:
            issues.append("Missing deliverables specification")
        
        if not contract.terms.timeline:
            issues.append("Missing timeline information")
        
        # Check for reasonable values
        if contract.terms.compensation > 50000:
            warnings.append("High compensation amount - verify budget approval")
        
        if "tbd" in contract.terms.deliverables.lower():
            warnings.append("Deliverables contain placeholder text")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "contract_id": contract.contract_id
        }
    
    async def finalize_contract(self, contract: Contract) -> Contract:
        """
        Finalize contract and mark as ready for signature
        
        Args:
            contract: Draft contract to finalize
            
        Returns:
            Finalized contract
        """
        
        try:
            # Validate contract first
            validation = await self.validate_contract(contract)
            
            if not validation["valid"]:
                raise ValueError(f"Contract validation failed: {validation['issues']}")
            
            # Update contract status
            contract.status = "ready_for_signature"
            
            logger.info(f"✅ Contract finalized: {contract.contract_id}")
            return contract
            
        except Exception as e:
            logger.error(f"❌ Contract finalization failed: {e}")
            raise
    
    async def close(self) -> None:
        """Clean up contract agent resources"""
        try:
            # Contract agent doesn't hold persistent resources, but good practice
            logger.info("✅ Contract Agent resources cleaned up")
        except Exception as e:
            logger.error(f"❌ Error cleaning up contract agent: {e}")


# Utility functions for contract management

async def generate_contracts_for_campaign(
    contract_agent: ContractAgent,
    successful_negotiations: list,
    campaign_data: CampaignData
) -> list:
    """
    Generate contracts for all successful negotiations in a campaign
    
    Args:
        contract_agent: Contract agent instance
        successful_negotiations: List of successful negotiation results
        campaign_data: Campaign context
        
    Returns:
        List of generated contracts
    """
    
    contracts = []
    
    for negotiation in successful_negotiations:
        try:
            contract = await contract_agent.generate_contract(negotiation, campaign_data)
            contracts.append(contract)
        except Exception as e:
            logger.error(f"❌ Failed to generate contract for {negotiation.creator_id}: {e}")
    
    return contracts


def export_contract_summary(contracts: list) -> Dict[str, Any]:
    """
    Export summary of generated contracts
    
    Args:
        contracts: List of Contract objects
        
    Returns:
        Summary data for reporting
    """
    
    if not contracts:
        return {
            "total_contracts": 0,
            "total_value": 0,
            "contracts": []
        }
    
    total_value = sum(contract.terms.compensation for contract in contracts)
    
    contract_summaries = []
    for contract in contracts:
        contract_summaries.append({
            "contract_id": contract.contract_id,
            "creator_id": contract.terms.creator_id,
            "creator_name": contract.terms.creator_name,
            "compensation": contract.terms.compensation,
            "deliverables": contract.terms.deliverables,
            "timeline": contract.terms.timeline,
            "status": contract.status,
            "generated_at": contract.generated_at.isoformat()
        })
    
    return {
        "total_contracts": len(contracts),
        "total_value": total_value,
        "average_compensation": total_value / len(contracts),
        "contracts": contract_summaries
    }