# services/negotiation.py
from .openai_service import OpenAINegotiationService
from typing import Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class NegotiationManager:
    def __init__(self):
        self.ai_service = OpenAINegotiationService()
    
    def process_negotiation_message(
        self, 
        conversation_context: Dict[str, Any], 
        message: str, 
        speaker: str
    ) -> Dict[str, Any]:
        """Main method to process negotiation messages"""
        
        try:
            # Generate AI response using OpenAI service
            response = self.ai_service.generate_negotiation_response(
                conversation_context, message, speaker
            )
            
            # Add timestamp and metadata
            response.update({
                "timestamp": datetime.now().isoformat(),
                "speaker": "ai_agent",
                "conversation_id": conversation_context["conversation_id"]
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing negotiation message: {str(e)}")
            return {
                "message": "I apologize for the technical difficulty. Let me refocus on your negotiation needs.",
                "insights": [],
                "strategy_notes": "Error occurred - manual intervention may be needed.",
                "timestamp": datetime.now().isoformat(),
                "speaker": "ai_agent"
            }