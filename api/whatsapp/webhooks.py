import logging
import hmac
import hashlib
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from fastapi.responses import PlainTextResponse
from typing import Dict, Any

from models.whatsapp import WhatsAppWebhook, WhatsAppMessage
from .enhanced_message_handler import EnhancedWhatsAppConversationHandler 
from config.settings import settings

logger = logging.getLogger(__name__)

whatsapp_router = APIRouter()
conversation_handler = EnhancedWhatsAppConversationHandler()  # Using enhanced handler

@whatsapp_router.get("/webhook")
async def verify_webhook(request: Request):
    """
    WhatsApp webhook verification endpoint
    """
    try:
        # Get verification parameters
        mode = request.query_params.get("hub.mode")
        token = request.query_params.get("hub.verify_token") 
        challenge = request.query_params.get("hub.challenge")
        
        # Verify the webhook
        if mode == "subscribe" and token == settings.whatsapp_verify_token:
            logger.info("✅ WhatsApp webhook verified successfully")
            return PlainTextResponse(challenge)
        else:
            logger.error("❌ WhatsApp webhook verification failed")
            raise HTTPException(status_code=403, detail="Verification failed")
            
    except Exception as e:
        logger.error(f"❌ Webhook verification error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@whatsapp_router.post("/webhook")
async def handle_whatsapp_webhook(
    webhook_data: WhatsAppWebhook,
    background_tasks: BackgroundTasks,
    request: Request
):
    """
    Handle incoming WhatsApp messages
    """
    try:
        # Verify webhook signature for security
        if not _verify_signature(request, await request.body()):
            raise HTTPException(status_code=403, detail="Invalid signature")
        
        logger.info("📱 WhatsApp webhook received")
        
        # Process each entry in the webhook
        for entry in webhook_data.entry:
            for change in entry.changes:
                if change.field == "messages":
                    # Process messages
                    value = change.value
                    
                    if value.messages:
                        for message in value.messages:
                            # Handle message in background
                            background_tasks.add_task(
                                conversation_handler.process_message,
                                message,
                                value.metadata.phone_number_id
                            )
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"❌ WhatsApp webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def _verify_signature(request: Request, body: bytes) -> bool:
    """
    Verify WhatsApp webhook signature for security
    """
    try:
        signature = request.headers.get("X-Hub-Signature-256", "")
        if not signature.startswith("sha256="):
            return False
            
        expected_signature = hmac.new(
            settings.whatsapp_app_secret.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        
        received_signature = signature[7:]  # Remove "sha256=" prefix
        
        return hmac.compare_digest(expected_signature, received_signature)
        
    except Exception as e:
        logger.error(f"❌ Signature verification error: {e}")
        return False