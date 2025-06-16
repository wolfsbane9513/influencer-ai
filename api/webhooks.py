# api/webhooks.py (UPDATED with Database Integration)
import uuid
import asyncio
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from models.campaign import CampaignWebhook, CampaignData, CampaignOrchestrationState
from agents.orchestrator import CampaignOrchestrator
from services.voice import VoiceService
from services.database import DatabaseService  # ← ADD DATABASE SERVICE

from config.settings import settings
logger = logging.getLogger(__name__)

webhook_router = APIRouter()

# Initialize services with database
orchestrator = CampaignOrchestrator()
voice_service = VoiceService()
database_service = DatabaseService()  # ← ADD DATABASE SERVICE

@webhook_router.post("/campaign-created")
async def handle_campaign_created(
    campaign_webhook: CampaignWebhook,
    background_tasks: BackgroundTasks
):
    """
    🎯 MAIN WEBHOOK ENDPOINT WITH DATABASE INTEGRATION
    This kicks off the entire AI workflow with real-time database storage:
    Campaign → Database → Discovery → ElevenLabs Calls → Database → Results
    """
    try:
        # Generate unique task ID for tracking
        task_id = str(uuid.uuid4())
        
        logger.info(f"🚀 Campaign webhook received: {campaign_webhook.product_name}")
        
        # *** STEP 1: Initialize database first ***
        try:
            await database_service.initialize()
            logger.info("✅ Database initialized for campaign")
            database_enabled = True
        except Exception as e:
            logger.error(f"⚠️ Database initialization failed: {e}")
            logger.info("📋 Continuing without database (fallback mode)")
            database_enabled = False
        
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
        
        # *** STEP 2: Create campaign in database immediately ***
        if database_enabled:
            try:
                db_campaign = await database_service.create_campaign(campaign_data)
                logger.info(f"✅ Campaign created in database: {db_campaign.id}")
            except Exception as e:
                logger.error(f"❌ Failed to create campaign in database: {e}")
                # Continue without database
                database_enabled = False
        
        # Initialize orchestration state
        orchestration_state = CampaignOrchestrationState(
            campaign_id=campaign_data.id,
            campaign_data=campaign_data,
            current_stage="webhook_received"
        )
        
        # Store database status in state
        orchestration_state.database_enabled = database_enabled
        
        # Store in global state for monitoring
        from main import active_campaigns
        active_campaigns[task_id] = orchestration_state
        
        # 🔥 START THE AI WORKFLOW IN BACKGROUND WITH DATABASE INTEGRATION
        background_tasks.add_task(
            orchestrator.orchestrate_campaign,
            orchestration_state,
            task_id
        )
        
        return JSONResponse(
            status_code=202,
            content={
                "message": "🎯 AI campaign workflow started WITH DATABASE",
                "task_id": task_id,
                "campaign_id": campaign_data.id,
                "brand_name": campaign_data.brand_name,
                "product_name": campaign_data.product_name,
                "estimated_duration_minutes": 5,
                "monitor_url": f"/api/monitor/campaign/{task_id}",
                "status": "started",
                "database_enabled": database_enabled,
                "features": [
                    "Real-time database storage",
                    "Live progress tracking",
                    "Creator performance analytics",
                    "Campaign ROI analysis"
                ] if database_enabled else [
                    "In-memory tracking",
                    "Basic progress monitoring"
                ],
                "next_steps": [
                    "Database: Campaign record created" if database_enabled else "Memory: Campaign initialized",
                    "Discovery phase: Finding matching creators (stored in DB)" if database_enabled else "Discovery phase: Finding matching creators",
                    "Negotiation phase: ElevenLabs phone calls (tracked in DB)" if database_enabled else "Negotiation phase: ElevenLabs phone calls", 
                    "Results phase: Contract generation (stored in DB)" if database_enabled else "Results phase: Contract generation"
                ]
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Webhook processing failed: {str(e)}")
        
        # Try to log error to database if possible
        try:
            if database_enabled and 'campaign_data' in locals():
                await database_service.update_campaign(
                    campaign_data.id,
                    {"status": "failed", "ai_strategy": {"error": str(e)}}
                )
        except:
            pass  # Don't fail twice
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start campaign workflow: {str(e)}"
        )

@webhook_router.post("/test-campaign")
async def create_test_campaign(background_tasks: BackgroundTasks):
    """
    🧪 Create a test campaign for demo purposes WITH DATABASE
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
    
    logger.info("🧪 Test campaign created for demo with database integration")
    
    return await handle_campaign_created(test_campaign, background_tasks)

@webhook_router.post("/test-tech-campaign") 
async def create_test_tech_campaign(background_tasks: BackgroundTasks):
    """🧪 Create a tech campaign for testing different niches WITH DATABASE"""
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
        
    except Exception as e:
        logger.error(f"❌ ElevenLabs test failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "message": "ElevenLabs test failed - check your setup"
            }
        )

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
        
        # Initiate call
        call_result = await voice_service.initiate_negotiation_call(
            creator_phone=test_phone,
            creator_profile=test_creator,
            campaign_brief=test_campaign_brief,
            price_range="2000-4000"
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "test_call_result": call_result,
                "message": f"Test call initiated! Check your phone {test_phone}",
                "call_flow": {
                    "from_number": "+1 320 383 8447 (Twilio US)",
                    "to_number": test_phone,
                    "expected": "Your phone should ring in a few seconds"
                },
                "troubleshooting": {
                    "if_no_ring": "Check Twilio console logs",
                    "if_call_fails": "Verify ElevenLabs agent configuration",
                    "international_calls": "Ensure Twilio account can make international calls to India"
                }
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Test call failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "message": "Test call failed"
            }
        )

# *** NEW: Database-specific endpoints ***
@webhook_router.get("/database-status")
async def get_database_status():
    """📊 Get database connection status and statistics"""
    try:
        # Test database connection
        await database_service.initialize()
        
        # Test basic query
        async with database_service.get_session() as session:
            result = await session.execute("SELECT 1")
            connection_test = result.scalar()
        
        return JSONResponse(
            status_code=200,
            content={
                "database_status": "connected",
                "connection_test": "passed",
                "database_url": "postgresql://***:***@localhost:5432/influencerflow",
                "features": [
                    "Real-time campaign tracking",
                    "Creator performance analytics", 
                    "Negotiation history",
                    "Contract management",
                    "Payment tracking"
                ],
                "available_tables": [
                    "campaigns",
                    "creators", 
                    "negotiations",
                    "contracts",
                    "payments",
                    "outreach_logs"
                ]
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Database status check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "database_status": "disconnected",
                "error": str(e),
                "fallback_mode": "Memory-only operation",
                "troubleshooting": {
                    "check_postgresql": "Ensure PostgreSQL is running",
                    "check_connection": "Verify DATABASE_URL in .env",
                    "start_database": "docker-compose up -d postgres"
                }
            }
        )

@webhook_router.post("/seed-sample-data")
async def seed_sample_database_data():
    """🌱 Seed database with sample data for testing"""
    try:
        await database_service.initialize()
        
        # Create sample creators
        from models.campaign import Creator as CampaignCreator, Platform, Availability
        
        sample_creators = [
            CampaignCreator(
                id="fitness_guru_mike",
                name="Mike FitnessGuru",
                platform=Platform.YOUTUBE,
                followers=250000,
                niche="fitness",
                typical_rate=5000.0,
                engagement_rate=4.2,
                average_views=50000,
                last_campaign_date="2024-11-15",
                availability=Availability.EXCELLENT,
                location="California, USA",
                phone_number="+1-555-0123",
                languages=["English"],
                specialties=["fitness coaching", "nutrition"]
            ),
            CampaignCreator(
                id="tech_reviewer_sarah",
                name="Sarah TechReviews",
                platform=Platform.YOUTUBE,
                followers=180000,
                niche="tech",
                typical_rate=3500.0,
                engagement_rate=3.8,
                average_views=40000,
                last_campaign_date="2024-12-01",
                availability=Availability.GOOD,
                location="New York, USA",
                phone_number="+1-555-0456",
                languages=["English"],
                specialties=["tech reviews", "gadgets"]
            ),
            CampaignCreator(
                id="beauty_influencer_anna",
                name="Anna BeautyTips",
                platform=Platform.INSTAGRAM,
                followers=320000,
                niche="beauty",
                typical_rate=4200.0,
                engagement_rate=5.1,
                average_views=60000,
                last_campaign_date="2024-11-20",
                availability=Availability.EXCELLENT,
                location="Los Angeles, USA",
                phone_number="+1-555-0789",
                languages=["English", "Spanish"],
                specialties=["makeup tutorials", "skincare"]
            )
        ]
        
        # Store creators in database
        created_count = 0
        for creator in sample_creators:
            try:
                await database_service.create_or_update_creator(creator)
                created_count += 1
            except Exception as e:
                logger.error(f"Failed to create creator {creator.name}: {e}")
        
        return JSONResponse(
            status_code=200,
            content={
                "message": f"✅ Sample data seeded successfully",
                "creators_created": created_count,
                "total_attempted": len(sample_creators),
                "database_ready": True,
                "next_steps": [
                    "Create test campaigns with POST /api/webhook/test-campaign",
                    "Monitor campaigns with GET /api/monitor/campaign/{task_id}",
                    "View analytics with GET /api/webhook/database-status"
                ]
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Sample data seeding failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "message": "Sample data seeding failed"
            }
        )

@webhook_router.get("/status")
async def webhook_status():
    """📊 Get webhook service status WITH DATABASE INFO"""
    
    # Check database status
    try:
        await database_service.initialize()
        async with database_service.get_session() as session:
            await session.execute("SELECT 1")
        database_status = "connected"
    except:
        database_status = "disconnected"
    
    return {
        "service": "InfluencerFlow Webhook Handler",
        "status": "healthy",
        "version": "2.1.0",  # Updated version with database
        "database_status": database_status,
        "endpoints": {
            # Existing endpoints
            "campaign_created": "/api/webhook/campaign-created",
            "test_campaign": "/api/webhook/test-campaign", 
            "test_tech_campaign": "/api/webhook/test-tech-campaign",
            "test_elevenlabs": "/api/webhook/test-elevenlabs",
            "test_call": "/api/webhook/test-call",
            # New database endpoints
            "database_status": "/api/webhook/database-status",
            "seed_sample_data": "/api/webhook/seed-sample-data"
        },
        "capabilities": [
            "Campaign workflow orchestration",
            "ElevenLabs phone call integration", 
            "Real-time progress monitoring",
            "Multi-niche creator matching",
            "PostgreSQL database integration",  # New capability
            "Real-time analytics",  # New capability
            "Creator performance tracking"  # New capability
        ],
        "integrations": {
            "groq_ai": bool(settings.groq_api_key),
            "elevenlabs": bool(settings.elevenlabs_api_key),
            "postgresql": database_status == "connected",
            "mock_mode": voice_service.use_mock
        },
        "database_features": {
            "real_time_tracking": True,
            "campaign_analytics": True,
            "creator_management": True,
            "negotiation_history": True,
            "contract_management": True,
            "payment_tracking": True
        } if database_status == "connected" else None
    }