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
try:
    from .enhanced_voice import EnhancedVoiceService
except Exception:  # pragma: no cover - optional dependency may be missing
    EnhancedVoiceService = None

try:
    from .embeddings import EmbeddingService
except Exception:  # pragma: no cover - optional dependency may be missing
    EmbeddingService = None
from .pricing import PricingService
from .database import DatabaseService

# Legacy services (backward compatibility)
from .elevenlabs_voice_service import ElevenLabsVoiceService
VoiceService = ElevenLabsVoiceService

__all__ = [
    # Enhanced (recommended)
    "PricingService",
    "DatabaseService",

    # Legacy (backward compatibility)
    "VoiceService",
]

if EnhancedVoiceService is not None:
    __all__.insert(0, "EnhancedVoiceService")
if EmbeddingService is not None:
    __all__.insert(1 if EnhancedVoiceService is not None else 0, "EmbeddingService")
