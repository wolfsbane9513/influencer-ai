import logging
import aiohttp
import json
from typing import Dict, Any, Optional

from config.settings import settings

logger = logging.getLogger(__name__)

class WhatsAppResponseService:
    """
    Service for sending messages via WhatsApp Business API
    """
    
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v18.0"
        self.phone_number_id = settings.whatsapp_phone_number_id
        self.access_token = settings.whatsapp_access_token
    
    async def send_message(
        self, 
        to_phone: str, 
        message_text: str,
        message_type: str = "text"
    ) -> bool:
        """
        Send text message via WhatsApp Business API
        """
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "messaging_product": "whatsapp",
                "to": to_phone,
                "type": message_type,
                "text": {
                    "body": message_text
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"✅ WhatsApp message sent to {to_phone}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ WhatsApp API error {response.status}: {error_text}")
                        return False
                        
        except Exception as e:
            logger.error(f"❌ Error sending WhatsApp message: {e}")
            return False
    
    async def send_interactive_message(
        self, 
        to_phone: str, 
        message_text: str,
        buttons: list
    ) -> bool:
        """
        Send interactive message with buttons (for approvals)
        """
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            interactive_buttons = []
            for i, button_text in enumerate(buttons[:3]):  # WhatsApp max 3 buttons
                interactive_buttons.append({
                    "type": "reply",
                    "reply": {
                        "id": f"btn_{i}",
                        "title": button_text[:20]  # Max 20 chars
                    }
                })
            
            data = {
                "messaging_product": "whatsapp",
                "to": to_phone,
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {
                        "text": message_text
                    },
                    "action": {
                        "buttons": interactive_buttons
                    }
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status == 200:
                        logger.info(f"✅ Interactive WhatsApp message sent to {to_phone}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ WhatsApp interactive API error {response.status}: {error_text}")
                        return False
                        
        except Exception as e:
            logger.error(f"❌ Error sending interactive WhatsApp message: {e}")
            return False
