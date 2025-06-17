# services/__init__.py
"""
InfluencerFlow AI Services - Enhanced & Legacy Support

Enhanced Services (Recommended):
- EnhancedVoiceService: ElevenLabs with dynamic variables
- Enhanced agents with structured data flow

Legacy Services (Backward Compatibility):
- Original services for existing integrations
"""

# Enhanced services (recommended)
from .enhanced_voice import EnhancedVoiceService
from .embeddings import EmbeddingService
from .pricing import PricingService
from .database import DatabaseService
from .email_service import EmailService, email_service
from .contract_service import ContractService, contract_service

# Legacy services (backward compatibility)
from .voice import VoiceService

__all__ = [
    # Enhanced (recommended)
    "EnhancedVoiceService",
    "EmbeddingService",
    "PricingService", 
    "DatabaseService",
    "EmailService",
    "email_service",
    "ContractService",
    "contract_service",
    
    # Legacy (backward compatibility)
    "VoiceService"
]