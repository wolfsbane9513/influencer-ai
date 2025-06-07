from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class WhatsAppText(BaseModel):
    """WhatsApp text message content"""
    body: str

class WhatsAppDocument(BaseModel):
    """WhatsApp document message content"""
    filename: str
    mime_type: str
    sha256: str
    id: str

class WhatsAppMessage(BaseModel):
    """WhatsApp message structure"""
    id: str
    from_number: str = Field(alias="from")
    timestamp: str
    type: str  # "text", "document", "image", etc.
    text: Optional[WhatsAppText] = None
    document: Optional[WhatsAppDocument] = None

class WhatsAppContact(BaseModel):
    """WhatsApp contact info"""
    profile: Dict[str, str]
    wa_id: str

class WhatsAppMetadata(BaseModel):
    """WhatsApp metadata"""
    display_phone_number: str
    phone_number_id: str

class WhatsAppValue(BaseModel):
    """WhatsApp webhook value"""
    messaging_product: str
    metadata: WhatsAppMetadata
    contacts: Optional[List[WhatsAppContact]] = None
    messages: Optional[List[WhatsAppMessage]] = None

class WhatsAppChange(BaseModel):
    """WhatsApp webhook change"""
    value: WhatsAppValue
    field: str

class WhatsAppEntry(BaseModel):
    """WhatsApp webhook entry"""
    id: str
    changes: List[WhatsAppChange]

class WhatsAppWebhook(BaseModel):
    """WhatsApp webhook payload"""
    object: str
    entry: List[WhatsAppEntry]