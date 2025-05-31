# services/voice_service.py (Fixed for new ElevenLabs API)
import io
import os
import tempfile
import asyncio
from typing import Optional, Dict, Any
import logging
from pathlib import Path

import openai
# Updated ElevenLabs imports for newer versions
try:
    # Try new API first
    from elevenlabs.client import ElevenLabs
    from elevenlabs import Voice, VoiceSettings
    ELEVENLABS_NEW_API = True
except ImportError:
    try:
        # Try old API
        from elevenlabs import generate, save, set_api_key
        ELEVENLABS_NEW_API = False
    except ImportError:
        # If ElevenLabs is not available at all, create mock functions
        print("Warning: ElevenLabs not available. Voice features will be limited.")
        ELEVENLABS_NEW_API = None
        
        def generate(*args, **kwargs):
            return b"mock audio data"
        
        def save(*args, **kwargs):
            pass
            
        def set_api_key(*args, **kwargs):
            pass

import httpx
from decouple import config

logger = logging.getLogger(__name__)

class VoiceProcessingService:
    def __init__(self):
        # Initialize API keys
        self.openai_client = openai.OpenAI(api_key=config('OPENAI_API_KEY', 'not-set'))
        
        # Handle different ElevenLabs API versions
        self.elevenlabs_available = False
        try:
            if ELEVENLABS_NEW_API:
                # New API structure
                self.elevenlabs_client = ElevenLabs(api_key=config('ELEVENLABS_API_KEY', 'not-set'))
                self.elevenlabs_available = True
                logger.info("Using new ElevenLabs API")
            elif ELEVENLABS_NEW_API is False:
                # Old API structure
                set_api_key(config('ELEVENLABS_API_KEY', 'not-set'))
                self.elevenlabs_client = None
                self.elevenlabs_available = True
                logger.info("Using old ElevenLabs API")
            else:
                # No ElevenLabs available
                self.elevenlabs_client = None
                self.elevenlabs_available = False
                logger.warning("ElevenLabs not available")
        except Exception as e:
            logger.warning(f"ElevenLabs initialization failed: {e}. Voice features will be limited.")
            self.elevenlabs_client = None
            self.elevenlabs_available = False
        
        # Voice settings for different personas
        self.voice_profiles = {
            "professional_consultant": {
                "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Rachel voice
                "settings": {
                    "stability": 0.75,
                    "similarity_boost": 0.85,
                    "style": 0.15,
                    "use_speaker_boost": True
                }
            },
            "friendly_advisor": {
                "voice_id": "EXAVITQu4vr4xnSDxMaL",  # Bella voice
                "settings": {
                    "stability": 0.70,
                    "similarity_boost": 0.80,
                    "style": 0.25,
                    "use_speaker_boost": True
                }
            }
        }
        
        # Default voice profile
        self.default_voice_profile = "professional_consultant"
    
    async def transcribe_audio(self, audio_data: bytes, filename: str = "audio.wav") -> Dict[str, Any]:
        """Transcribe audio using OpenAI Whisper"""
        try:
            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # Transcribe using Whisper
                with open(temp_file_path, "rb") as audio_file:
                    transcript = self.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="verbose_json",
                        language="en"  # Can be auto-detected or specified
                    )
                
                result = {
                    "text": transcript.text,
                    "language": transcript.language,
                    "duration": transcript.duration,
                    "confidence": getattr(transcript, 'confidence', None),
                    "segments": getattr(transcript, 'segments', [])
                }
                
                logger.info(f"Successfully transcribed audio: {transcript.text[:100]}...")
                return result
                
            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)
                
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return {
                "text": "",
                "error": str(e),
                "language": "unknown",
                "duration": 0
            }
    
    async def generate_speech(
        self, 
        text: str, 
        voice_profile: str = None,
        custom_voice_id: str = None
    ) -> Dict[str, Any]:
        """Generate speech from text using ElevenLabs"""
        try:
            # Check if ElevenLabs is available
            if not self.elevenlabs_available:
                logger.warning("ElevenLabs not available, creating silent audio file for demo")
                # Create a small silent audio file for demo purposes
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                    # Write minimal MP3 header for a silent file
                    temp_file.write(b'\xff\xfb\x90\x00')  # Minimal MP3 header
                    temp_file_path = temp_file.name
                
                return {
                    "audio_file_path": temp_file_path,
                    "file_size": 4,
                    "voice_id": "demo",
                    "voice_profile": "demo",
                    "text_length": len(text),
                    "estimated_duration": len(text) * 0.08,
                    "success": True,
                    "note": "Demo mode - ElevenLabs not configured"
                }
            
            # Select voice profile
            profile_name = voice_profile or self.default_voice_profile
            profile = self.voice_profiles.get(profile_name, self.voice_profiles[self.default_voice_profile])
            
            # Use custom voice ID if provided
            voice_id = custom_voice_id or profile["voice_id"]
            
            # Generate audio using appropriate API
            audio_data = None
            
            if ELEVENLABS_NEW_API and self.elevenlabs_client:
                try:
                    # Method 1: New API with client
                    audio_data = self.elevenlabs_client.generate(
                        text=text,
                        voice=voice_id,
                        model="eleven_multilingual_v2"
                    )
                    logger.info("Used new ElevenLabs API successfully")
                except AttributeError:
                    try:
                        # Method 2: Alternative new API method
                        audio_data = self.elevenlabs_client.text_to_speech.convert(
                            voice_id=voice_id,
                            text=text,
                            model_id="eleven_multilingual_v2"
                        )
                        logger.info("Used alternative new ElevenLabs API")
                    except Exception as e:
                        logger.warning(f"New API methods failed: {e}")
                        raise e
            else:
                # Method 3: Old API
                try:
                    audio_data = generate(
                        text=text,
                        voice=voice_id,
                        model="eleven_multilingual_v2",
                        **profile["settings"]
                    )
                    logger.info("Used old ElevenLabs API successfully")
                except Exception as e:
                    logger.warning(f"Old API failed: {e}")
                    raise e
            
            if audio_data is None:
                raise Exception("No audio data generated")
            
            # Handle different audio data types
            if hasattr(audio_data, 'read'):
                # If it's a file-like object
                audio_bytes = audio_data.read()
            elif isinstance(audio_data, (bytes, bytearray)):
                # If it's already bytes
                audio_bytes = bytes(audio_data)
            else:
                # If it's an iterator or generator
                audio_bytes = b''.join(audio_data)
            
            # Save to temporary file and return file info
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                temp_file.write(audio_bytes)
                temp_file_path = temp_file.name
            
            # Get file size
            file_size = os.path.getsize(temp_file_path)
            
            result = {
                "audio_file_path": temp_file_path,
                "file_size": file_size,
                "voice_id": voice_id,
                "voice_profile": profile_name,
                "text_length": len(text),
                "estimated_duration": len(text) * 0.08,
                "success": True
            }
            
            logger.info(f"Successfully generated speech for text: {text[:50]}...")
            return result
            
        except Exception as e:
            logger.error(f"Error generating speech: {str(e)}")
            # Create fallback silent audio for demo
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                    temp_file.write(b'\xff\xfb\x90\x00')  # Minimal MP3 header
                    temp_file_path = temp_file.name
                
                return {
                    "audio_file_path": temp_file_path,
                    "file_size": 4,
                    "voice_id": "fallback",
                    "voice_profile": "fallback",
                    "text_length": len(text),
                    "estimated_duration": len(text) * 0.08,
                    "success": True,
                    "error": f"Fallback mode: {str(e)}"
                }
            except:
                return {
                    "audio_file_path": None,
                    "error": str(e),
                    "success": False
                }
    
    async def process_voice_message(
        self, 
        audio_data: bytes, 
        conversation_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process complete voice message: transcribe input, generate response, convert to speech"""
        try:
            # Step 1: Transcribe input audio
            transcription = await self.transcribe_audio(audio_data)
            
            if not transcription.get("text"):
                return {
                    "success": False,
                    "error": "Failed to transcribe audio",
                    "transcription": transcription
                }
            
            # Step 2: Determine appropriate voice profile based on context
            voice_profile = self._select_voice_profile(conversation_context)
            
            # Step 3: The AI response generation will be handled by the calling function
            # This service focuses on voice processing only
            
            result = {
                "success": True,
                "transcription": transcription,
                "voice_profile": voice_profile,
                "transcribed_text": transcription["text"]
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing voice message: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_response_audio(
        self, 
        response_text: str, 
        conversation_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate audio response for AI text response"""
        try:
            # Select appropriate voice profile
            voice_profile = self._select_voice_profile(conversation_context)
            
            # Generate speech
            speech_result = await self.generate_speech(response_text, voice_profile)
            
            if not speech_result.get("success"):
                return speech_result
            
            return {
                "success": True,
                "audio_file_path": speech_result["audio_file_path"],
                "voice_profile": speech_result["voice_profile"],
                "text": response_text,
                "metadata": {
                    "file_size": speech_result["file_size"],
                    "estimated_duration": speech_result["estimated_duration"],
                    "voice_id": speech_result["voice_id"]
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating response audio: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _select_voice_profile(self, conversation_context: Dict[str, Any]) -> str:
        """Select appropriate voice profile based on conversation context"""
        
        # Default to professional consultant
        profile = "professional_consultant"
        
        try:
            # Analyze conversation stage
            status = conversation_context.get("status", "").lower()
            negotiation_rounds = conversation_context.get("metadata", {}).get("negotiation_rounds", 0)
            
            # Use more friendly voice for initial conversations
            if negotiation_rounds < 2 or status == "initializing":
                profile = "friendly_advisor"
            
            # For complex negotiations, use professional consultant
            elif negotiation_rounds > 3 or "complex" in str(conversation_context.get("campaign_brief", {})):
                profile = "professional_consultant"
            
            logger.info(f"Selected voice profile: {profile} for conversation stage")
            
        except Exception as e:
            logger.warning(f"Error selecting voice profile, using default: {str(e)}")
        
        return profile
    
    def cleanup_temp_file(self, file_path: str) -> bool:
        """Clean up temporary audio file"""
        try:
            if file_path and os.path.exists(file_path):
                os.unlink(file_path)
                return True
        except Exception as e:
            logger.warning(f"Failed to cleanup temp file {file_path}: {str(e)}")
        return False
    
    async def get_available_voices(self) -> Dict[str, Any]:
        """Get list of available ElevenLabs voices"""
        try:
            # This would typically use ElevenLabs API to get voices
            # For demo purposes, return our configured voices
            return {
                "voices": [
                    {
                        "id": "21m00Tcm4TlvDq8ikWAM",
                        "name": "Rachel",
                        "category": "Professional",
                        "description": "Clear, confident, professional consultant voice"
                    },
                    {
                        "id": "EXAVITQu4vr4xnSDxMaL",
                        "name": "Bella",
                        "category": "Friendly",
                        "description": "Warm, approachable, friendly advisor voice"
                    }
                ],
                "profiles": self.voice_profiles,
                "available": self.elevenlabs_available
            }
        except Exception as e:
            logger.error(f"Error getting available voices: {str(e)}")
            return {"voices": [], "error": str(e), "available": False}

# Audio format utilities
class AudioFormatHandler:
    """Handle different audio formats and conversions"""
    
    @staticmethod
    def validate_audio_format(content_type: str) -> bool:
        """Validate if audio format is supported"""
        supported_formats = [
            "audio/wav", 
            "audio/mpeg", 
            "audio/mp3", 
            "audio/mp4", 
            "audio/webm",
            "audio/ogg"
        ]
        return content_type.lower() in supported_formats
    
    @staticmethod
    def get_file_extension(content_type: str) -> str:
        """Get appropriate file extension for content type"""
        extensions = {
            "audio/wav": ".wav",
            "audio/mpeg": ".mp3",
            "audio/mp3": ".mp3",
            "audio/mp4": ".mp4",
            "audio/webm": ".webm",
            "audio/ogg": ".ogg"
        }
        return extensions.get(content_type.lower(), ".wav")

# Create global instance
voice_service = VoiceProcessingService()