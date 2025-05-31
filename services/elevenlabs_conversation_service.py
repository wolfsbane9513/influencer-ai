# services/elevenlabs_conversation_service.py - Simplified Working Version
import httpx
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import os
import uuid

# Environment loading
try:
    from decouple import config
    ELEVENLABS_API_KEY = config('ELEVENLABS_API_KEY', default=None)
    ELEVENLABS_AGENT_ID = config('ELEVENLABS_AGENT_ID', default=None)
except ImportError:
    ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
    ELEVENLABS_AGENT_ID = os.getenv('ELEVENLABS_AGENT_ID')

logger = logging.getLogger(__name__)

class ElevenLabsConversationalAI:
    """
    Simplified ElevenLabs Conversational AI service that integrates with the fixed conversation manager
    """
    
    def __init__(self):
        self.api_key = ELEVENLABS_API_KEY
        self.agent_id = ELEVENLABS_AGENT_ID
        self.base_url = "https://api.elevenlabs.io/v1"
        
        if not self.api_key:
            logger.warning("ELEVENLABS_API_KEY not configured - ElevenLabs features will be limited")
        
        logger.info("ElevenLabs service initialized")
    
    async def initiate_phone_call(self, phone_number: str, conversation_id: str, creator_data: Dict) -> Dict[str, Any]:
        """
        Initiate a real phone call using ElevenLabs Conversational AI
        Note: This requires a working ElevenLabs agent with phone capabilities
        """
        if not self.api_key or not self.agent_id:
            raise ValueError("ElevenLabs API key and agent ID are required for phone calls")
        
        try:
            # Create conversation with dynamic variables for this specific creator/campaign
            conversation_config = {
                "agent_id": self.agent_id,
                "phone_number": phone_number,
                "dynamic_variables": {
                    "creator_name": creator_data.get("name", "Creator"),
                    "follower_count": str(creator_data.get("followers", "N/A")),
                    "engagement_rate": str(creator_data.get("engagement_rate", "N/A")),
                    "platform": creator_data.get("platform", "Social Media"),
                    "initial_offer": str(creator_data.get("initial_offer", "3000")),
                    "max_budget": str(creator_data.get("max_budget", "4000")),
                    "brand_name": creator_data.get("brand_name", "TechBrand Agency"),
                    "campaign_type": creator_data.get("campaign_type", "Product Review"),
                    "deliverables": creator_data.get("deliverables", "video review"),
                    "conversation_id": conversation_id
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/convai/conversations/phone",
                    headers={
                        "xi-api-key": self.api_key,
                        "Content-Type": "application/json"
                    },
                    json=conversation_config,
                    timeout=30.0
                )
                
                if response.status_code in [200, 201]:
                    call_data = response.json()
                    logger.info(f"ElevenLabs phone call initiated: {call_data}")
                    return {
                        "success": True,
                        "elevenlabs_conversation_id": call_data.get("conversation_id"),
                        "call_status": "initiated",
                        "phone_number": phone_number,
                        "creator_name": creator_data.get("name")
                    }
                else:
                    logger.error(f"ElevenLabs call failed: {response.status_code} - {response.text}")
                    raise Exception(f"Phone call initiation failed: HTTP {response.status_code}")
                    
        except httpx.TimeoutException:
            logger.error("ElevenLabs API timeout")
            raise Exception("ElevenLabs API request timed out")
        except Exception as e:
            logger.error(f"ElevenLabs phone call error: {str(e)}")
            raise Exception(f"Failed to initiate phone call: {str(e)}")
    
    async def get_call_status(self, elevenlabs_conversation_id: str) -> Dict[str, Any]:
        """Get the status of an active ElevenLabs phone call"""
        if not self.api_key:
            return {"error": "ElevenLabs API key not configured"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/convai/conversations/{elevenlabs_conversation_id}",
                    headers={"xi-api-key": self.api_key},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    call_data = response.json()
                    return {
                        "status": call_data.get("status", "unknown"),
                        "duration": call_data.get("duration_seconds", 0),
                        "call_active": call_data.get("status") == "active",
                        "elevenlabs_data": call_data
                    }
                else:
                    return {"error": f"Failed to get call status: HTTP {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"Error getting call status: {str(e)}")
            return {"error": str(e)}
    
    async def end_call(self, elevenlabs_conversation_id: str) -> bool:
        """End an active ElevenLabs phone call"""
        if not self.api_key:
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/convai/conversations/{elevenlabs_conversation_id}/end",
                    headers={"xi-api-key": self.api_key},
                    timeout=10.0
                )
                
                return response.status_code in [200, 201]
                
        except Exception as e:
            logger.error(f"Error ending call: {str(e)}")
            return False
    
    def is_configured(self) -> bool:
        """Check if ElevenLabs is properly configured"""
        return bool(self.api_key and self.agent_id)
    
    def get_configuration_status(self) -> Dict[str, Any]:
        """Get current configuration status"""
        return {
            "api_key_configured": bool(self.api_key),
            "agent_id_configured": bool(self.agent_id),
            "agent_id": self.agent_id,
            "ready_for_calls": self.is_configured(),
            "base_url": self.base_url
        }

# Global instance
elevenlabs_conversation_service = ElevenLabsConversationalAI()