# agents/__init__.py
"""
InfluencerFlow AI Agents - Enhanced & Legacy Support
"""

# Enhanced agents (recommended)
from .campaign_orchestrator import CampaignOrchestrator
from .enhanced_negotiation import EnhancedNegotiationAgent, NegotiationResultValidator
from .enhanced_contracts import EnhancedContractAgent, ContractStatusManager

# Legacy agents (backward compatibility)  
from .negotiation import NegotiationAgent
from .contracts import ContractAgent
from .discovery import InfluencerDiscoveryAgent

__all__ = [
    # Enhanced (recommended)
    "EnhancedNegotiationAgent",
    "NegotiationResultValidator",
    "EnhancedContractAgent",
    "ContractStatusManager",

    # Legacy & shared
    "CampaignOrchestrator",  # Primary orchestrator
    "NegotiationAgent",
    "ContractAgent",
    "InfluencerDiscoveryAgent"
]