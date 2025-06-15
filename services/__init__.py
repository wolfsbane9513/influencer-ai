# services/__init__.py
"""

- VoiceService: ElevenLabs with dynamic variables

- Original services for existing integrations
"""

from .enhanced_voice import VoiceService
from .embeddings import EmbeddingService
from .pricing import PricingService
from .database import DatabaseService

from .voice import VoiceService

__all__ = [
    "VoiceService",
    "EmbeddingService",
    "PricingService", 
    "DatabaseService",
    
    "VoiceService"
]