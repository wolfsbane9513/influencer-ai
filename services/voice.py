import asyncio
import logging
from typing import Dict, Any, Optional

# Import settings with fallback
try:
    from config.settings import settings
except ImportError:
    from config.simple_settings import settings

logger = logging.getLogger(__name__)

class VoiceService:
    """Service for handling ElevenLabs voice calls and conversations"""
    
    def __init__(self):
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize ElevenLabs client"""
        try:
            if settings.elevenlabs_api_key and not settings.mock_calls:
                import elevenlabs
                self.client = elevenlabs
                logger.info("✅ ElevenLabs client initialized")
            else:
                logger.info("🎭 Using mock voice service")
                self.client = None
        except ImportError:
            logger.warning("⚠️  ElevenLabs not available, using mock service")
            self.client = None
        except Exception as e:
            logger.error(f"❌ ElevenLabs initialization failed: {e}")
            self.client = None
    
    async def initiate_call(self, phone_number: str, voice_id: str = None) -> Dict[str, Any]:
        """Initiate phone call"""
        try:
            if self.client and not settings.mock_calls:
                # Real ElevenLabs call implementation would go here
                # Note: ElevenLabs might not have direct phone calling - 
                # this is a placeholder for the demo
                logger.info(f"📞 Initiating real call to {phone_number}")
                
                # Placeholder for actual ElevenLabs phone call API
                call_session = {
                    "call_id": f"el_call_{phone_number[-4:]}",
                    "status": "connected",
                    "phone_number": phone_number,
                    "voice_id": voice_id or settings.elevenlabs_voice_id
                }
                
                return call_session
            else:
                # Mock call for demo
                logger.info(f"🎭 Mock call to {phone_number}")
                await asyncio.sleep(1)  # Simulate connection time
                
                return {
                    "call_id": f"mock_call_{phone_number[-4:]}",
                    "status": "connected",
                    "phone_number": phone_number,
                    "mock": True
                }
                
        except Exception as e:
            logger.error(f"❌ Call initiation failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def conduct_conversation(
        self,
        call_session: Dict[str, Any],
        opening_script: str,
        max_duration: int = 60
    ) -> Dict[str, Any]:
        """Conduct AI conversation"""
        try:
            if call_session.get("mock"):
                # Mock conversation
                return await self._mock_conversation(opening_script, max_duration)
            else:
                # Real ElevenLabs conversation
                return await self._real_conversation(call_session, opening_script, max_duration)
                
        except Exception as e:
            logger.error(f"❌ Conversation failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _mock_conversation(self, opening_script: str, max_duration: int) -> Dict[str, Any]:
        """Mock conversation for demo"""
        # Simulate conversation time
        conversation_time = min(max_duration, 30)  # Cap at 30s for demo
        await asyncio.sleep(conversation_time)
        
        return {
            "status": "completed",
            "duration": conversation_time,
            "transcript": f"AI: {opening_script}\nCreator: [Conversation details...]",
            "recording_url": "mock_recording.mp3"
        }
    
    async def _real_conversation(
        self,
        call_session: Dict[str, Any],
        opening_script: str,
        max_duration: int
    ) -> Dict[str, Any]:
        """Real ElevenLabs conversation - placeholder implementation"""
        # This would integrate with actual ElevenLabs conversation API
        # For now, return mock data
        return await self._mock_conversation(opening_script, max_duration)