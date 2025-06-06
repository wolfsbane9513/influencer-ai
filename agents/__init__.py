# agents/__init__.py
"""
InfluencerFlow AI Agents - Enhanced & Legacy Support
"""

# Enhanced agents (recommended)
from .enhanced_orchestrator import EnhancedCampaignOrchestrator
from .enhanced_negotiation import EnhancedNegotiationAgent, NegotiationResultValidator
from .enhanced_contracts import EnhancedContractAgent, ContractStatusManager

# Legacy agents (backward compatibility)  

from .discovery import InfluencerDiscoveryAgent

__all__ = [
    # Enhanced (recommended)
    "EnhancedCampaignOrchestrator",
    "EnhancedNegotiationAgent",
    "NegotiationResultValidator",
    "EnhancedContractAgent", 
    "ContractStatusManager",
    
    # Legacy & shared
    "CampaignOrchestrator",  # Backward compatibility wrapper
    "NegotiationAgent",
    "ContractAgent",
    "InfluencerDiscoveryAgent"
]