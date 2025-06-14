# api/webhooks.py
import uuid
import asyncio
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from models.campaign import CampaignWebhook, CampaignData, CampaignOrchestrationState
from agents.campaign_orchestrator import CampaignOrchestrator
from services.elevenlabs_voice_service import VoiceServiceFactory
from core.exceptions import (
    InfluencerFlowException,
    ValidationError,
    create_error_context,
    handle_and_log_error,
)

from config.settings import settings
logger = logging.getLogger(__name__)

webhook_router = APIRouter()

# Initialize orchestrator and voice service
orchestrator = CampaignOrchestrator()
voice_service = VoiceServiceFactory.create_voice_service(
    api_key=settings.elevenlabs_api_key,
    agent_id=settings.elevenlabs_agent_id,
    phone_number_id=settings.elevenlabs_phone_number_id,
    use_mock=settings.mock_calls,
)

@webhook_router.post("/campaign-created")
async def handle_campaign_created(
    campaign_webhook: CampaignWebhook,
    background_tasks: BackgroundTasks
):
    """
    🎯 MAIN WEBHOOK ENDPOINT - Triggered when campaign is created
    This kicks off the entire AI workflow:
    Campaign → Discovery → ElevenLabs Calls → Results
    """
    try:
        # Generate unique task ID for tracking
        task_id = str(uuid.uuid4())
        
        logger.info(f"🚀 Campaign webhook received: {campaign_webhook.product_name}")
        
        # Convert webhook data to internal campaign format
        campaign_data = CampaignData(
            id=campaign_webhook.campaign_id,
            product_name=campaign_webhook.product_name,
            brand_name=campaign_webhook.brand_name,
            product_description=campaign_webhook.product_description,
            target_audience=campaign_webhook.target_audience,
            campaign_goal=campaign_webhook.campaign_goal,
            product_niche=campaign_webhook.product_niche,
            total_budget=campaign_webhook.total_budget,
            campaign_code=f"CAMP-{campaign_webhook.campaign_id[:8].upper()}"
        )
        
        # Initialize orchestration state
        orchestration_state = CampaignOrchestrationState(
            campaign_id=campaign_data.id,
            campaign_data=campaign_data,
            current_stage="webhook_received"
        )
        
        # Store in global state for monitoring
        from main import active_campaigns
        active_campaigns[task_id] = orchestration_state
        
        # 🔥 START THE AI WORKFLOW IN BACKGROUND
        background_tasks.add_task(
            orchestrator.orchestrate_campaign,
            orchestration_state,
            task_id
        )
        
        return JSONResponse(
            status_code=202,
            content={
                "message": "🎯 AI campaign workflow started",
                "task_id": task_id,
                "campaign_id": campaign_data.id,
                "brand_name": campaign_data.brand_name,
                "product_name": campaign_data.product_name,
                "estimated_duration_minutes": 5,
                "monitor_url": f"/api/monitor/campaign/{task_id}",
                "status": "started",
                "next_steps": [
                    "Discovery phase: Finding matching creators",
                    "Negotiation phase: ElevenLabs phone calls", 
                    "Results phase: Contract generation"
                ]
            }
        )
        
    except (InfluencerFlowException, ValidationError) as e:
        context = create_error_context(
            operation="handle_campaign_created",
            component="WebhookHandler",
            campaign_id=campaign_webhook.campaign_id,
        )
        error = await handle_and_log_error(e, context)
        raise HTTPException(status_code=422 if isinstance(e, ValidationError) else 500, detail=error)
    except Exception as e:
        context = create_error_context(
            operation="handle_campaign_created",
            component="WebhookHandler",
            campaign_id=campaign_webhook.campaign_id,
        )
        error = await handle_and_log_error(InfluencerFlowException(str(e)), context)
        raise HTTPException(status_code=500, detail=error)

@webhook_router.post("/test-campaign")
async def create_test_campaign(background_tasks: BackgroundTasks):
    """
    🧪 Create a test campaign for demo purposes
    This endpoint creates a realistic fitness campaign for testing
    """
    test_campaign = CampaignWebhook(
        campaign_id=str(uuid.uuid4()),
        product_name="FitPro Protein Powder",
        brand_name="FitLife Nutrition",
        product_description="Premium whey protein powder for muscle building and recovery, perfect for fitness enthusiasts and athletes looking to maximize their workout results",
        target_audience="Fitness enthusiasts, gym-goers, and athletes aged 18-35 who are serious about their workout routine and nutrition goals",
        campaign_goal="Increase brand awareness and drive sales in the fitness community through authentic creator partnerships",
        product_niche="fitness",
        total_budget=15000.0
    )
    
    logger.info("🧪 Test campaign created for demo")
    
    return await handle_campaign_created(test_campaign, background_tasks)

@webhook_router.post("/test-tech-campaign") 
async def create_test_tech_campaign(background_tasks: BackgroundTasks):
    """🧪 Create a tech campaign for testing different niches"""
    test_campaign = CampaignWebhook(
        campaign_id=str(uuid.uuid4()),
        product_name="TechPro Wireless Earbuds",
        brand_name="AudioMax",
        product_description="High-quality wireless earbuds with noise cancellation and superior sound quality for tech enthusiasts",
        target_audience="Tech enthusiasts, gamers, and professionals aged 20-40",
        campaign_goal="Launch new product and establish market presence",
        product_niche="tech",
        total_budget=12000.0
    )
    
    return await handle_campaign_created(test_campaign, background_tasks)

@webhook_router.get("/test-elevenlabs")
async def test_elevenlabs_setup():
    """
    🧪 Test ElevenLabs credentials and setup
    """
    try:
        # Test credentials
        result = await voice_service.test_credentials()
        
        return JSONResponse(
            status_code=200 if result["status"] == "success" else 400,
            content={
                "elevenlabs_status": result,
                "setup_instructions": {
                    "step_1": "Get API key from https://elevenlabs.io/app/settings/api-keys",
                    "step_2": "Create agent at https://elevenlabs.io/app/conversational-ai",
                    "step_3": "Set up phone number integration",
                    "step_4": "Add credentials to .env file",
                    "required_env_vars": [
                        "ELEVENLABS_API_KEY=sk_your_key_here",
                        "ELEVENLABS_AGENT_ID=your_agent_id_here",
                        "ELEVENLABS_PHONE_NUMBER_ID=your_phone_id_here"
                    ]
                },
                "current_settings": {
                    "api_key_set": bool(settings.elevenlabs_api_key),
                    "agent_id_set": bool(settings.elevenlabs_agent_id),
                    "phone_number_id_set": bool(settings.elevenlabs_phone_number_id),
                    "mock_mode": voice_service.use_mock
                }
            }
        )
        
    except InfluencerFlowException as e:
        context = create_error_context(
            operation="test_elevenlabs_setup",
            component="WebhookHandler",
        )
        error = await handle_and_log_error(e, context)
        return JSONResponse(status_code=400, content=error)
    except Exception as e:
        context = create_error_context(
            operation="test_elevenlabs_setup",
            component="WebhookHandler",
        )
        error = await handle_and_log_error(InfluencerFlowException(str(e)), context)
        return JSONResponse(status_code=500, content=error)

@webhook_router.post("/test-call")
async def test_single_call():
    """
    🧪 Test a single ElevenLabs call (for debugging)
    """
    try:
        # Mock creator profile for testing
        test_creator = {
            "id": "test_creator",
            "name": "TestCreator",
            "niche": "fitness",
            "followers": 100000,
            "engagement_rate": 5.2,
            "average_views": 50000,
            "location": "India",
            "languages": ["English"],
            "typical_rate": 3000
        }
        
        test_campaign_brief = """
        Brand: TestBrand
        Product: Test Product
        Description: This is a test campaign to verify ElevenLabs integration
        Target Audience: Test audience
        Goal: Test the calling system
        """
        
        # ✅ FIXED: Use your actual phone number (India)
        # FROM: +1 320 383 8447 (Twilio US number)
        # TO: +918806859890 (Your Indian number)
        test_phone = "+918806859890"  # Your actual phone number
        
        logger.info(f"🧪 Initiating test call")
        logger.info(f"   FROM: +1 320 383 8447 (Twilio US)")
        logger.info(f"   TO: {test_phone} (Your phone)")
        
        # Initiate call using the structured voice service
        conversation_id = await voice_service.initiate_call(
            phone_number=test_phone,
            conversation_context={
                "creator_profile": test_creator,
                "campaign_data": {"campaign_brief": test_campaign_brief},
                "pricing_strategy": {"initial_offer": 2000, "max_offer": 4000},
            },
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "conversation_id": conversation_id,
                "message": f"Test call initiated! Check your phone {test_phone}",
                "call_flow": {
                    "from_number": "+1 320 383 8447 (Twilio US)",
                    "to_number": test_phone,
                    "expected": "Your phone should ring in a few seconds",
                },
                "troubleshooting": {
                    "if_no_ring": "Check Twilio console logs",
                    "if_call_fails": "Verify ElevenLabs agent configuration",
                    "international_calls": "Ensure Twilio account can make international calls to India",
                },
            },
        )
        
    except InfluencerFlowException as e:
        context = create_error_context(
            operation="test_single_call",
            component="WebhookHandler",
        )
        error = await handle_and_log_error(e, context)
        return JSONResponse(status_code=400, content=error)
    except Exception as e:
        context = create_error_context(
            operation="test_single_call",
            component="WebhookHandler",
        )
        error = await handle_and_log_error(InfluencerFlowException(str(e)), context)
        return JSONResponse(status_code=500, content=error)

@webhook_router.get("/status")
async def webhook_status():
    """📊 Get webhook service status"""
    return {
        "service": "InfluencerFlow Webhook Handler",
        "status": "healthy",
        "version": "2.0.0",
        "endpoints": {
            "campaign_created": "/api/webhook/campaign-created",
            "test_campaign": "/api/webhook/test-campaign",
            "test_tech_campaign": "/api/webhook/test-tech-campaign",
            "test_elevenlabs": "/api/webhook/test-elevenlabs",
            "test_call": "/api/webhook/test-call"
        },
        "capabilities": [
            "Campaign workflow orchestration",
            "ElevenLabs phone call integration", 
            "Real-time progress monitoring",
            "Multi-niche creator matching"
        ],
        "integrations": {
            "groq_ai": bool(settings.groq_api_key),
            "elevenlabs": bool(settings.elevenlabs_api_key),
            "mock_mode": voice_service.use_mock
        }
    }
