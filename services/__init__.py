# services/__init__.py
"""
InfluencerFlow AI Services
--------------------------
Core service exports used across the project.
"""

# Optional services
try:
    from .embeddings import EmbeddingService
except Exception:  # pragma: no cover - optional dependency may be missing
    EmbeddingService = None

from .pricing import PricingService
from .database import DatabaseService

# Legacy services (backward compatibility)
from .elevenlabs_voice_service import ElevenLabsVoiceService, VoiceServiceFactory

VoiceService = ElevenLabsVoiceService

__all__ = [
    "PricingService",
    "DatabaseService",
    "VoiceService",
    "VoiceServiceFactory",
]

if EmbeddingService is not None:
    __all__.append("EmbeddingService")
