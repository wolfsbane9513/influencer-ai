# services/voice.py - CORRECT ELEVENLABS API IMPLEMENTATION

import asyncio
import logging
import json
import httpx
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class VoiceService:
    """
    🎙️ Fixed Voice Service with correct ElevenLabs API endpoints
    """
    
    def __init__(self):
        # Get settings
        try:
            from core.config import settings
            self.api_key = getattr(settings, 'elevenlabs_api_key', None)
            self.agent_id = getattr(settings, 'elevenlabs_agent_id', None)
            self.phone_number_id = getattr(settings, 'elevenlabs_phone_number_id', None)
            self.use_mock = getattr(settings, 'use_mock_services', True)
        except Exception:
            # Fallback if settings import fails
            self.api_key = None
            self.agent_id = None
            self.phone_number_id = None
            self.use_mock = True
        
        # CORRECT ElevenLabs API URL
        self.base_url = "https://api.elevenlabs.io/v1"
        
        # HTTP client for API calls
        if self.api_key:
            self.client = httpx.AsyncClient(
                timeout=30.0,
                headers={
                    "xi-api-key": self.api_key,
                    "Content-Type": "application/json"
                }
            )
        else:
            self.client = None
            self.use_mock = True
        
        logger.info(f"🎙️ Voice Service initialized (mock: {self.use_mock})")
    
    def _serialize_for_json(self, obj: Any) -> Any:
        """Convert objects to JSON-serializable format"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {key: self._serialize_for_json(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_for_json(item) for item in obj]
        else:
            return obj
    
    async def make_call(
        self,
        phone_number: str,
        campaign_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Make call method with correct ElevenLabs API
        """
        if self.use_mock or not self.api_key or not self.agent_id:
            # Mock call with realistic success rate
            import random
            await asyncio.sleep(1)  # Simulate call setup
            
            return {
                "success": True,
                "conversation_id": f"mock-conv-{random.randint(1000, 9999)}",
                "call_id": f"mock-call-{random.randint(1000, 9999)}",
                "status": "initiated",
                "mock_mode": True
            }
        
        # Real ElevenLabs call with CORRECT API endpoint
        try:
            # Fix datetime serialization
            serialized_context = self._serialize_for_json(campaign_context)
            
            # CORRECT ElevenLabs API payload structure
            call_data = {
                "agent_id": self.agent_id,
                "customer_phone_number": phone_number,
                "customer_phone_number_id": self.phone_number_id,
                "conversation_initiation_client_data": {
                    "dynamic_variables": serialized_context
                }
            }
            
            logger.info(f"📞 Making real ElevenLabs call to {phone_number}")
            logger.info(f"🔧 Using agent_id: {self.agent_id}")
            
            # CORRECT ElevenLabs API endpoint
            response = await self.client.post(
                f"{self.base_url}/convai/conversations",  # CORRECT endpoint
                json=call_data
            )
            
            if response.status_code == 200:
                data = response.json()
                conversation_id = data.get("conversation_id")
                logger.info(f"✅ ElevenLabs call initiated: {conversation_id}")
                logger.info(f"📞 Your phone should ring soon at {phone_number}")
                
                return {
                    "success": True,
                    "conversation_id": conversation_id,
                    "call_id": data.get("call_id"),
                    "status": "initiated",
                    "phone_number": phone_number
                }
            else:
                logger.error(f"ElevenLabs API error: {response.status_code} - {response.text}")
                
                # Log detailed error info for debugging
                if response.status_code == 404:
                    logger.error("❌ 404 Error: Check your ElevenLabs agent_id and phone_number_id")
                    logger.error(f"   Agent ID: {self.agent_id}")
                    logger.error(f"   Phone ID: {self.phone_number_id}")
                elif response.status_code == 401:
                    logger.error("❌ 401 Error: Check your ElevenLabs API key")
                elif response.status_code == 400:
                    logger.error("❌ 400 Error: Invalid request payload")
                    logger.error(f"   Payload: {call_data}")
                
                return {
                    "success": False,
                    "error": f"API error: {response.status_code} - {response.text}",
                    "phone_number": phone_number
                }
                
        except Exception as e:
            logger.error(f"Call failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "phone_number": phone_number
            }
    
    async def conduct_conversation(
        self,
        call_result: Dict[str, Any],
        opening_script: str = "",
        max_duration: int = 60
    ) -> Dict[str, Any]:
        """
        Conduct conversation and return results
        """
        if call_result.get("mock_mode"):
            # Mock conversation with realistic outcomes
            import random
            await asyncio.sleep(random.randint(2, 5))  # Simulate conversation time
            
            # Simulate realistic outcomes (70% success rate)
            success = random.choice([True, True, True, False])
            
            if success:
                agreed_rate = random.uniform(800, 2500)
                return {
                    "status": "completed",
                    "duration": random.randint(90, 240),
                    "transcript": f"Mock successful negotiation - agreed on ${agreed_rate:.2f}",
                    "mock_result": {
                        "negotiation_outcome": "accepted",
                        "agreed_rate": agreed_rate
                    }
                }
            else:
                return {
                    "status": "completed", 
                    "duration": random.randint(60, 120),
                    "transcript": "Mock failed negotiation",
                    "mock_result": {
                        "negotiation_outcome": "rejected",
                        "failure_reason": random.choice([
                            "Rate too low",
                            "Timeline too tight",
                            "Brand misalignment"
                        ])
                    }
                }
        
        # Real conversation monitoring
        conversation_id = call_result.get("conversation_id")
        if not conversation_id:
            return {"status": "failed", "error": "No conversation ID"}
        
        # Monitor real conversation status
        try:
            # Poll for conversation completion
            for _ in range(30):  # Wait up to 5 minutes
                await asyncio.sleep(10)
                
                status_response = await self.client.get(
                    f"{self.base_url}/convai/conversations/{conversation_id}"
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get("status", "unknown")
                    
                    if status == "completed":
                        return {
                            "status": "completed",
                            "conversation_id": conversation_id,
                            "transcript": status_data.get("transcript", ""),
                            "analysis": status_data.get("analysis", {}),
                            "duration": status_data.get("duration_seconds", 0)
                        }
                    elif status in ["failed", "error"]:
                        return {
                            "status": "failed",
                            "error": status_data.get("error", "Call failed"),
                            "conversation_id": conversation_id
                        }
                else:
                    logger.warning(f"Status check failed: {status_response.status_code}")
            
            # Timeout
            return {
                "status": "timeout",
                "conversation_id": conversation_id,
                "error": "Conversation monitoring timed out"
            }
            
        except Exception as e:
            logger.error(f"Conversation monitoring error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "conversation_id": conversation_id
            }