import logging
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class ConversationState:
    """Track conversation state for each WhatsApp user"""
    phone_number: str
    stage: str  # "campaign_input", "approval_pending", "completed" 
    campaign_data: Optional[Dict[str, Any]] = None
    task_id: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

class ConversationStateManager:
    """
    Manage conversation state for WhatsApp users
    In production, this would use Redis or database
    For MVP, using in-memory storage
    """
    
    def __init__(self):
        self.conversations: Dict[str, ConversationState] = {}
    
    async def get_conversation_state(self, phone_number: str) -> Optional[ConversationState]:
        """Get conversation state for phone number"""
        return self.conversations.get(phone_number)
    
    async def create_conversation(self, phone_number: str) -> ConversationState:
        """Create new conversation state"""
        conversation = ConversationState(
            phone_number=phone_number,
            stage="campaign_input"
        )
        self.conversations[phone_number] = conversation
        logger.info(f"📱 Created conversation state for {phone_number}")
        return conversation
    
    async def update_conversation_stage(
        self, 
        phone_number: str, 
        stage: str,
        campaign_data: Optional[Dict[str, Any]] = None,
        task_id: Optional[str] = None
    ):
        """Update conversation stage"""
        if phone_number in self.conversations:
            conversation = self.conversations[phone_number]
            conversation.stage = stage
            conversation.updated_at = datetime.now()
            
            if campaign_data:
                conversation.campaign_data = campaign_data
            if task_id:
                conversation.task_id = task_id
                
            logger.info(f"📱 Updated conversation {phone_number} to stage: {stage}")
    
    async def clear_conversation(self, phone_number: str):
        """Clear conversation state"""
        if phone_number in self.conversations:
            del self.conversations[phone_number]
            logger.info(f"📱 Cleared conversation state for {phone_number}")