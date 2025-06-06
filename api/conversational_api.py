# api/conversational_api.py
import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from services.whatsapp_ai import WhatsAppAIService
from services.document_processor import DocumentProcessor, BriefValidator
from services.payment_service import PaymentService, PaymentAnalytics
from config.settings import settings

logger = logging.getLogger(__name__)

conversational_router = APIRouter()

# Initialize services
whatsapp_ai = WhatsAppAIService()
document_processor = DocumentProcessor()
payment_service = PaymentService()
payment_analytics = PaymentAnalytics(payment_service)

# Pydantic models for API
class WhatsAppWebhook(BaseModel):
    object: str
    entry: list

class PaymentWebhook(BaseModel):
    provider: str
    event_type: str
    data: Dict[str, Any]

class CampaignBrief(BaseModel):
    content: str
    format: str = "text"

# ================================
# WHATSAPP AI ENDPOINTS
# ================================

@conversational_router.post("/whatsapp/webhook")
async def handle_whatsapp_webhook(webhook_data: WhatsAppWebhook):
    """
    📱 WhatsApp Webhook Handler - Main conversational AI entry point
    
    This is where the magic happens - natural language campaign management via WhatsApp
    """
    
    try:
        logger.info("📱 WhatsApp webhook received")
        
        # Extract message data from webhook
        for entry in webhook_data.entry:
            changes = entry.get("changes", [])
            
            for change in changes:
                if change.get("field") == "messages":
                    value = change.get("value", {})
                    messages = value.get("messages", [])
                    
                    for message in messages:
                        # Process each message through AI
                        result = await whatsapp_ai.handle_whatsapp_message(message)
                        
                        if result["status"] == "error":
                            logger.error(f"❌ Message processing failed: {result['error']}")
        
        return {"status": "received", "processed": True}
        
    except Exception as e:
        logger.error(f"❌ WhatsApp webhook failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@conversational_router.get("/whatsapp/webhook")
async def verify_whatsapp_webhook(
    hub_mode: str = None,
    hub_verify_token: str = None, 
    hub_challenge: str = None
):
    """
    ✅ WhatsApp webhook verification endpoint
    """
    
    verify_token = getattr(settings, 'whatsapp_verify_token', 'influencerflow_2024')
    
    if hub_mode == "subscribe" and hub_verify_token == verify_token:
        logger.info("✅ WhatsApp webhook verified successfully")
        return int(hub_challenge)
    else:
        logger.warning("❌ WhatsApp webhook verification failed")
        raise HTTPException(status_code=403, detail="Verification failed")

@conversational_router.post("/whatsapp/test-message")
async def test_whatsapp_ai(message_text: str, user_phone: str = "+918806859890"):
    """
    🧪 Test WhatsApp AI processing without actual WhatsApp integration
    """
    
    try:
        # Simulate WhatsApp message format
        mock_message = {
            "from": user_phone,
            "type": "text",
            "text": {
                "body": message_text
            }
        }
        
        # Process through AI
        result = await whatsapp_ai.handle_whatsapp_message(mock_message)
        
        return {
            "status": "processed",
            "input_message": message_text,
            "ai_response": result,
            "test_mode": True
        }
        
    except Exception as e:
        logger.error(f"❌ WhatsApp AI test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ================================
# DOCUMENT PROCESSING ENDPOINTS  
# ================================

@conversational_router.post("/documents/upload-brief")
async def upload_campaign_brief(
    file: UploadFile = File(...),
    user_phone: str = Form("+918806859890")
):
    """
    📄 Upload and process campaign brief document
    
    This endpoint processes campaign briefs and extracts structured data
    """
    
    try:
        logger.info(f"📄 Processing uploaded brief: {file.filename}")
        
        # Read file content
        file_content = await file.read()
        
        # Process document
        processing_result = await document_processor.process_document(
            file_content=file_content,
            mime_type=file.content_type,
            filename=file.filename
        )
        
        if processing_result["status"] == "error":
            raise HTTPException(status_code=422, detail=processing_result)
        
        # Validate extracted data
        validation_result = BriefValidator.validate_campaign_brief(
            processing_result["extracted_data"]
        )
        
        # If user_phone provided, store in WhatsApp session
        if user_phone:
            session = whatsapp_ai._get_user_session(user_phone)
            session["uploaded_brief"] = processing_result["extracted_data"]
            session["brief_validation"] = validation_result
        
        return {
            "status": "processed",
            "document_info": {
                "filename": file.filename,
                "size_bytes": len(file_content),
                "mime_type": file.content_type
            },
            "extraction_result": processing_result,
            "validation_result": validation_result,
            "next_steps": _generate_brief_next_steps(processing_result, validation_result)
        }
        
    except Exception as e:
        logger.error(f"❌ Document processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@conversational_router.post("/documents/parse-text-brief")
async def parse_text_brief(brief: CampaignBrief):
    """
    📝 Parse campaign brief from text content
    """
    
    try:
        # Convert text to bytes for processing
        text_bytes = brief.content.encode('utf-8')
        
        # Process as text document
        processing_result = await document_processor.process_document(
            file_content=text_bytes,
            mime_type="text/plain",
            filename="text_brief.txt"
        )
        
        if processing_result["status"] == "error":
            return JSONResponse(
                status_code=422,
                content=processing_result
            )
        
        # Validate extracted data
        validation_result = BriefValidator.validate_campaign_brief(
            processing_result["extracted_data"]
        )
        
        return {
            "status": "processed",
            "extraction_result": processing_result,
            "validation_result": validation_result,
            "ai_recommendations": _generate_ai_recommendations(processing_result["extracted_data"])
        }
        
    except Exception as e:
        logger.error(f"❌ Text brief parsing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@conversational_router.get("/documents/supported-formats")
async def get_supported_formats():
    """
    📋 Get supported document formats for brief upload
    """
    
    return {
        "supported_formats": {
            "PDF": {
                "mime_type": "application/pdf",
                "description": "PDF documents with campaign briefs",
                "max_size_mb": 10
            },
            "DOCX": {
                "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "description": "Word documents with campaign details", 
                "max_size_mb": 10
            },
            "TXT": {
                "mime_type": "text/plain",
                "description": "Plain text campaign briefs",
                "max_size_mb": 5
            }
        },
        "ai_extraction_features": [
            "Product and brand name detection",
            "Budget extraction from various formats",
            "Target audience identification", 
            "Creator requirements parsing",
            "Timeline and deliverable extraction",
            "Automatic campaign categorization"
        ],
        "validation_features": [
            "Completeness scoring",
            "Missing field detection",
            "Budget reasonableness checks",
            "Requirement clarity validation"
        ]
    }

# ================================
# PAYMENT SYSTEM ENDPOINTS
# ================================

@conversational_router.post("/payments/create-campaign-plan")
async def create_campaign_payment_plan(
    campaign_id: str,
    creator_negotiations: list,
    payment_terms: Dict[str, Any] = None
):
    """
    💰 Create payment plan for successful campaign negotiations
    """
    
    try:
        # Convert negotiations to proper format
        from models.campaign import NegotiationState, NegotiationStatus
        
        negotiations = []
        for neg_data in creator_negotiations:
            negotiation = NegotiationState(
                creator_id=neg_data["creator_id"],
                campaign_id=campaign_id,
                status=NegotiationStatus.SUCCESS,
                final_rate=neg_data["final_rate"],
                negotiated_terms=neg_data.get("negotiated_terms", {}),
                conversation_id=neg_data.get("conversation_id")
            )
            negotiations.append(negotiation)
        
        # Create payment plan
        payment_plan_result = await payment_service.create_campaign_payment_plan(
            campaign_id, negotiations, payment_terms
        )
        
        return {
            "status": "created",
            "campaign_id": campaign_id,
            "payment_plan": payment_plan_result,
            "creators_included": len(negotiations),
            "total_amount": sum(neg.final_rate for neg in negotiations),
            "next_actions": [
                "Collect creator bank details",
                "Set up milestone triggers",
                "Configure payment automation"
            ]
        }
        
    except Exception as e:
        logger.error(f"❌ Payment plan creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@conversational_router.post("/payments/trigger-milestone")
async def trigger_milestone_payment(
    campaign_id: str,
    creator_id: str, 
    milestone_trigger: str,
    verification_data: Dict[str, Any] = None
):
    """
    🎯 Trigger milestone payment when conditions are met
    """
    
    try:
        result = await payment_service.trigger_milestone_payment(
            campaign_id, creator_id, milestone_trigger, verification_data
        )
        
        if result["status"] == "error":
            raise HTTPException(status_code=422, detail=result["error"])
        
        return {
            "status": "processed",
            "milestone_payment": result,
            "notification_sent": True,  # Would trigger notifications
            "next_milestone": _get_next_milestone(campaign_id, creator_id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Milestone payment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@conversational_router.get("/payments/campaign/{campaign_id}/status")
async def get_campaign_payment_status(campaign_id: str):
    """
    📊 Get comprehensive payment status for campaign
    """
    
    try:
        status = await payment_service.get_campaign_payment_status(campaign_id)
        
        if status["status"] == "not_found":
            raise HTTPException(status_code=404, detail="Campaign payment plan not found")
        
        return {
            "campaign_payment_status": status,
            "analytics": payment_analytics.generate_campaign_payment_report(campaign_id),
            "actionable_insights": _generate_payment_insights(status)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Payment status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@conversational_router.get("/payments/creator/{creator_id}/dashboard")
async def get_creator_payment_dashboard(creator_id: str):
    """
    👤 Get payment dashboard for creator
    """
    
    try:
        dashboard_data = await payment_service.get_creator_payment_dashboard(creator_id)
        creator_analytics = payment_analytics.get_creator_payment_analytics(creator_id)
        
        return {
            "creator_id": creator_id,
            "payment_dashboard": dashboard_data,
            "analytics": creator_analytics,
            "recommendations": _generate_creator_recommendations(dashboard_data)
        }
        
    except Exception as e:
        logger.error(f"❌ Creator dashboard failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@conversational_router.post("/payments/webhook/{provider}")
async def handle_payment_webhook(provider: str, webhook_data: PaymentWebhook):
    """
    🔗 Handle payment provider webhooks (Stripe, Razorpay)
    """
    
    try:
        result = await payment_service.handle_payment_webhook(
            provider, webhook_data.dict()
        )
        
        return {
            "status": "processed",
            "provider": provider,
            "webhook_result": result,
            "processed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Payment webhook failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ================================
# CONVERSATIONAL WORKFLOW ENDPOINTS
# ================================

@conversational_router.post("/ai/campaign-from-conversation")
async def create_campaign_from_conversation(
    user_phone: str,
    conversation_history: list = None
):
    """
    🤖 Create campaign from natural language conversation
    
    This endpoint demonstrates the power of conversational AI - create entire campaigns from chat
    """
    
    try:
        # Get user session
        session = whatsapp_ai._get_user_session(user_phone)
        
        # Check if we have campaign data from conversation
        campaign_data = session.get("current_campaign", {})
        
        if not campaign_data:
            return {
                "status": "incomplete",
                "message": "No campaign data found in conversation. Start by telling me about your product and budget.",
                "example": "Try: 'Create a fitness campaign for SmartFit Pro tracker, budget $15K'"
            }
        
        # Validate campaign data
        required_fields = ["product_name", "brand_name", "total_budget", "product_niche"]
        missing_fields = [field for field in required_fields if not campaign_data.get(field)]
        
        if missing_fields:
            return {
                "status": "incomplete",
                "campaign_data": campaign_data,
                "missing_fields": missing_fields,
                "message": f"Still need: {', '.join(missing_fields)}"
            }
        
        # Create campaign using existing enhanced workflow
        from models.campaign import CampaignWebhook
        from api.enhanced_webhooks import handle_enhanced_campaign_created
        from fastapi import BackgroundTasks
        
        campaign_webhook = CampaignWebhook(
            campaign_id=f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            product_name=campaign_data["product_name"],
            brand_name=campaign_data["brand_name"],
            product_description=campaign_data.get("product_description", f"{campaign_data['product_name']} campaign"),
            target_audience=campaign_data.get("target_audience", "General audience"),
            campaign_goal=campaign_data.get("campaign_goal", "Increase brand awareness"),
            product_niche=campaign_data["product_niche"],
            total_budget=float(campaign_data["total_budget"])
        )
        
        background_tasks = BackgroundTasks()
        result = await handle_enhanced_campaign_created(campaign_webhook, background_tasks)
        
        # Store in session
        session["active_campaign"] = {
            "id": campaign_webhook.campaign_id,
            "task_id": result.json()["task_id"],
            "created_from": "conversation",
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "status": "created",
            "message": "🎯 Campaign created from conversation!",
            "campaign_details": campaign_data,
            "workflow_started": True,
            "ai_workflow_result": result.json(),
            "monitor_url": f"/api/monitor/enhanced-campaign/{result.json()['task_id']}"
        }
        
    except Exception as e:
        logger.error(f"❌ Conversational campaign creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@conversational_router.get("/ai/conversation-session/{user_phone}")
async def get_conversation_session(user_phone: str):
    """
    📱 Get current conversation session state
    """
    
    try:
        session = whatsapp_ai._get_user_session(user_phone)
        
        return {
            "user_phone": user_phone,
            "session_data": session,
            "current_campaign": session.get("current_campaign", {}),
            "active_campaign": session.get("active_campaign"),
            "conversation_length": len(session.get("conversation_history", [])),
            "last_activity": session.get("last_activity", session.get("created_at"))
        }
        
    except Exception as e:
        logger.error(f"❌ Session retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@conversational_router.post("/ai/simulate-conversation")
async def simulate_conversation_flow(
    messages: list,
    user_phone: str = "+918806859890"
):
    """
    🎭 Simulate entire conversation flow for testing
    """
    
    try:
        conversation_results = []
        
        for i, message_text in enumerate(messages):
            # Process each message
            mock_message = {
                "from": user_phone,
                "type": "text", 
                "text": {"body": message_text}
            }
            
            result = await whatsapp_ai.handle_whatsapp_message(mock_message)
            
            conversation_results.append({
                "message_index": i + 1,
                "user_input": message_text,
                "ai_response": result,
                "timestamp": datetime.now().isoformat()
            })
            
            # Small delay to simulate real conversation
            await asyncio.sleep(0.5)
        
        # Get final session state
        final_session = whatsapp_ai._get_user_session(user_phone)
        
        return {
            "status": "completed",
            "conversation_flow": conversation_results,
            "final_session_state": final_session,
            "campaign_created": bool(final_session.get("active_campaign")),
            "total_messages": len(messages)
        }
        
    except Exception as e:
        logger.error(f"❌ Conversation simulation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ================================
# HELPER FUNCTIONS
# ================================

def _generate_brief_next_steps(processing_result: Dict[str, Any], validation_result: Dict[str, Any]) -> list:
    """Generate next steps based on brief processing results"""
    
    next_steps = []
    
    if validation_result["is_valid"]:
        next_steps.append("Brief is complete - ready to create campaign")
        next_steps.append("Review extracted data for accuracy")
        next_steps.append("Start AI workflow with enhanced orchestration")
    else:
        next_steps.append("Complete missing required fields")
        next_steps.extend(validation_result["suggestions"])
    
    return next_steps

def _generate_ai_recommendations(extracted_data: Dict[str, Any]) -> list:
    """Generate AI recommendations for campaign optimization"""
    
    recommendations = []
    
    budget = extracted_data.get("total_budget", 0)
    niche = extracted_data.get("product_niche", "")
    
    if budget < 5000:
        recommendations.append("Consider increasing budget for better creator reach")
    
    if niche == "fitness":
        recommendations.append("Focus on micro-influencers for authentic fitness content")
    elif niche == "tech":
        recommendations.append("Target tech reviewers with strong engagement")
    
    if not extracted_data.get("creator_requirements"):
        recommendations.append("Add specific creator requirements for better matching")
    
    return recommendations

def _generate_payment_insights(payment_status: Dict[str, Any]) -> list:
    """Generate actionable insights from payment status"""
    
    insights = []
    
    progress = payment_status["payment_summary"]["progress_percentage"]
    
    if progress < 25:
        insights.append("Campaign just started - ensure creator onboarding is complete")
    elif progress < 75:
        insights.append("Mid-campaign - monitor content delivery closely")
    else:
        insights.append("Campaign near completion - prepare final payments")
    
    if payment_status["overdue_payments"]:
        insights.append(f"{len(payment_status['overdue_payments'])} payments overdue - immediate action needed")
    
    return insights

def _generate_creator_recommendations(dashboard_data: Dict[str, Any]) -> list:
    """Generate recommendations for creators"""
    
    recommendations = []
    
    earnings = dashboard_data["earnings_summary"]
    
    if earnings["pending_payments"] > 0:
        recommendations.append("Complete pending milestones to receive payments")
    
    if earnings["total_campaigns"] < 3:
        recommendations.append("Build portfolio with more campaigns for better rates")
    
    return recommendations

def _get_next_milestone(campaign_id: str, creator_id: str) -> Optional[Dict[str, Any]]:
    """Get next milestone for creator in campaign"""
    
    # Would implement actual lookup
    return {
        "milestone_name": "Content Delivery",
        "due_date": (datetime.now().date() + timedelta(days=3)).isoformat(),
        "trigger": "content_approved"
    }