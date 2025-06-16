# api/enhanced_webhooks.py (UPDATE to include database)
"""
Enhanced webhooks with database integration
"""
import uuid
import asyncio
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

# Your existing imports
from models.campaign import CampaignWebhook, CampaignData, CampaignOrchestrationState
from agents.enhanced_orchestrator import EnhancedCampaignOrchestrator
from services.enhanced_voice import EnhancedVoiceService

# *** ADD DATABASE IMPORT ***
from services.database import DatabaseService

from config.settings import settings

logger = logging.getLogger(__name__)

enhanced_webhook_router = APIRouter()

# Initialize enhanced services
enhanced_orchestrator = EnhancedCampaignOrchestrator()
enhanced_voice_service = EnhancedVoiceService()
database_service = DatabaseService()  # *** ADD DATABASE SERVICE ***

@enhanced_webhook_router.post("/enhanced-campaign")
async def create_enhanced_campaign_with_db(
    campaign_webhook: CampaignWebhook,
    background_tasks: BackgroundTasks
):
    """
    🎯 ENHANCED CAMPAIGN CREATION WITH DATABASE INTEGRATION
    
    Creates campaign with:
    - Database persistence from start
    - Enhanced ElevenLabs integration
    - Real-time progress tracking
    - Advanced analytics
    """
    try:
        # Generate unique task ID
        task_id = str(uuid.uuid4())
        
        logger.info(f"🚀 Enhanced campaign webhook received: {campaign_webhook.product_name}")
        
        # *** STEP 1: Initialize database ***
        try:
            await database_service.initialize()
            logger.info("✅ Database initialized for enhanced campaign")
            database_enabled = True
        except Exception as e:
            logger.error(f"⚠️ Database initialization failed: {e}")
            database_enabled = False
        
        # Convert webhook to campaign data
        campaign_data = CampaignData(
            id=campaign_webhook.campaign_id,
            product_name=campaign_webhook.product_name,
            brand_name=campaign_webhook.brand_name,
            product_description=campaign_webhook.product_description,
            target_audience=campaign_webhook.target_audience,
            campaign_goal=campaign_webhook.campaign_goal,
            product_niche=campaign_webhook.product_niche,
            total_budget=campaign_webhook.total_budget,
            campaign_code=f"ENH-{campaign_webhook.campaign_id[:8].upper()}"
        )
        
        # *** STEP 2: Create campaign in database immediately ***
        if database_enabled:
            try:
                db_campaign = await database_service.create_campaign(campaign_data)
                logger.info(f"✅ Enhanced campaign created in database: {db_campaign.id}")
            except Exception as e:
                logger.error(f"❌ Failed to create campaign in database: {e}")
                database_enabled = False
        
        # Initialize enhanced orchestration state
        orchestration_state = CampaignOrchestrationState(
            campaign_id=campaign_data.id,
            campaign_data=campaign_data,
            current_stage="enhanced_webhook_received"
        )
        
        # Mark database status
        orchestration_state.database_enabled = database_enabled
        
        # Store in global state
        from main import active_campaigns
        active_campaigns[task_id] = orchestration_state
        
        # *** STEP 3: Inject database service into orchestrator ***
        if database_enabled and hasattr(enhanced_orchestrator, 'database_service'):
            enhanced_orchestrator.database_service = database_service
            logger.info("✅ Database service injected into enhanced orchestrator")
        
        # 🔥 START ENHANCED WORKFLOW WITH DATABASE
        background_tasks.add_task(
            enhanced_orchestrator.orchestrate_enhanced_campaign,  # ✅ CORRECT METHOD NAME
            campaign_data,  # ✅ Pass campaign_data, not orchestration_state
            task_id
        )
        
        return JSONResponse(
            status_code=202,
            content={
                "message": "🎯 Enhanced AI campaign workflow started WITH DATABASE",
                "task_id": task_id,
                "campaign_id": campaign_data.id,
                "brand_name": campaign_data.brand_name,
                "product_name": campaign_data.product_name,
                "estimated_duration_minutes": 8,
                "monitor_url": f"/api/monitor/enhanced-campaign/{task_id}",
                "status": "started",
                "database_enabled": database_enabled,
                "enhancements": [
                    "ElevenLabs dynamic variables integration",
                    "PostgreSQL database persistence",
                    "Structured conversation analysis", 
                    "AI-powered negotiation strategies",
                    "Real-time progress tracking",
                    "Advanced analytics and reporting"
                ],
                "database_features": [
                    "Campaign tracking from creation",
                    "Creator performance analytics",
                    "Negotiation history with transcripts",
                    "Contract and payment management",
                    "ROI analysis and reporting"
                ] if database_enabled else ["Limited to in-memory tracking"],
                "next_steps": [
                    f"Database: Campaign record {'created' if database_enabled else 'skipped'}",
                    "Discovery: Enhanced creator matching with database lookup",
                    "Strategy: AI-powered negotiation planning", 
                    "Negotiations: ElevenLabs calls with real-time database updates",
                    "Contracts: Automated generation with database storage",
                    "Analytics: Comprehensive performance reporting"
                ]
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Enhanced webhook processing failed: {str(e)}")
        
        # Try to log error to database
        try:
            if database_enabled and 'campaign_data' in locals():
                await database_service.update_campaign(
                    campaign_data.id,
                    {
                        "status": "failed", 
                        "ai_strategy": {"error": str(e), "stage": "webhook_processing"}
                    }
                )
        except:
            pass  # Don't fail twice
        
        raise HTTPException(
            status_code=500,
            detail=f"Enhanced campaign creation failed: {str(e)}"
        )

@enhanced_webhook_router.post("/test-enhanced-campaign")
async def create_test_enhanced_campaign(background_tasks: BackgroundTasks):
    """
    🧪 Create enhanced test campaign WITH DATABASE
    """
    test_campaign = CampaignWebhook(
        campaign_id=str(uuid.uuid4()),
        product_name="Enhanced FitPro Max",
        brand_name="Enhanced FitLife",
        product_description="Next-generation protein powder with AI-optimized nutrition profile for enhanced performance and recovery",
        target_audience="Serious athletes, bodybuilders, and fitness professionals aged 20-40 seeking premium nutrition solutions",
        campaign_goal="Launch premium product line with enhanced creator partnerships and database-tracked performance",
        product_niche="fitness",
        total_budget=18000.0
    )
    
    logger.info("🧪 Enhanced test campaign created with database integration")
    
    return await create_enhanced_campaign_with_db(test_campaign, background_tasks)

@enhanced_webhook_router.post("/test-enhanced-call")
async def test_enhanced_elevenlabs_call():
    """
    🧪 Test enhanced ElevenLabs call with database logging
    """
    try:
        # Enhanced test creator profile
        enhanced_test_creator = {
            "id": "enhanced_test_creator",
            "name": "Enhanced TestCreator Pro",
            "niche": "fitness",
            "followers": 150000,
            "engagement_rate": 4.8,
            "average_views": 75000,
            "location": "Enhanced Test Location",
            "languages": ["English"],
            "typical_rate": 4000,
            "specialties": ["enhanced content", "premium collaborations"]
        }
        
        enhanced_campaign_brief = """
        Enhanced Campaign Brief:
        Brand: Enhanced TestBrand Pro
        Product: Enhanced Test Product with Premium Features
        Description: Advanced test campaign for enhanced ElevenLabs integration with database tracking
        Target Audience: Premium test audience
        Goal: Validate enhanced calling system with database persistence
        Budget: $18,000 (premium tier)
        """
        
        # Use your phone number
        test_phone = "+918806859890"
        
        logger.info(f"🧪 Initiating enhanced test call with database logging")
        logger.info(f"   Enhanced FROM: +1 320 383 8447 (Twilio Premium)")
        logger.info(f"   Enhanced TO: {test_phone} (Your phone)")
        
        # *** Log call attempt to database ***
        if database_service:
            try:
                await database_service.initialize()
                
                # Create outreach log
                outreach_log = await database_service.create_outreach_log({
                    "campaign_id": "enhanced_test_campaign",
                    "creator_id": "enhanced_test_creator",
                    "contact_type": "test_call",
                    "status": "initiated",
                    "notes": f"Enhanced test call to {test_phone}"
                })
                
                logger.info(f"✅ Test call logged to database: {outreach_log.id}")
                
            except Exception as e:
                logger.error(f"❌ Failed to log test call: {e}")
        
        # Initiate enhanced call
        call_result = await enhanced_voice_service.initiate_negotiation_call(
            creator_phone=test_phone,
            creator_profile=enhanced_test_creator,
            campaign_brief=enhanced_campaign_brief,
            price_range="3000-5000"
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "enhanced_call_result": call_result,
                "message": f"Enhanced test call initiated! Check your phone {test_phone}",
                "call_flow": {
                    "from_number": "+1 320 383 8447 (Enhanced Twilio)",
                    "to_number": test_phone,
                    "expected": "Enhanced phone experience with improved audio quality"
                },
                "enhancements": [
                    "Dynamic variables integration",
                    "Enhanced conversation analysis",
                    "Database call logging",
                    "Improved error handling"
                ],
                "database_tracking": database_service is not None,
                "troubleshooting": {
                    "if_no_ring": "Check enhanced Twilio console logs",
                    "if_call_fails": "Verify enhanced ElevenLabs agent configuration",
                    "database_issues": "Check PostgreSQL connection"
                }
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Enhanced test call failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "message": "Enhanced test call failed",
                "type": "enhanced_call_error"
            }
        )

@enhanced_webhook_router.get("/test-enhanced-elevenlabs")
async def test_enhanced_elevenlabs_setup():
    """
    🧪 Test enhanced ElevenLabs setup with database validation
    """
    try:
        # Test enhanced voice service
        result = await enhanced_voice_service.test_credentials()
        
        # Test database connection
        database_status = "unknown"
        if database_service:
            try:
                await database_service.initialize()
                async with database_service.get_session() as session:
                    await session.execute("SELECT 1")
                database_status = "connected"
            except:
                database_status = "failed"
        
        return JSONResponse(
            status_code=200 if result["status"] == "success" else 400,
            content={
                "enhanced_elevenlabs_status": result,
                "database_status": database_status,
                "setup_instructions": {
                    "step_1": "Enhanced API key from https://elevenlabs.io/app/settings/api-keys",
                    "step_2": "Enhanced agent at https://elevenlabs.io/app/conversational-ai",
                    "step_3": "Enhanced phone number integration with dynamic variables",
                    "step_4": "Enhanced credentials in .env file",
                    "step_5": "Database setup for call tracking",
                    "required_env_vars": [
                        "ELEVENLABS_API_KEY=sk_your_enhanced_key_here",
                        "ELEVENLABS_AGENT_ID=your_enhanced_agent_id_here", 
                        "ELEVENLABS_PHONE_NUMBER_ID=your_enhanced_phone_id_here",
                        "DATABASE_URL=postgresql://user:password@localhost:5432/influencerflow"
                    ]
                },
                "current_settings": {
                    "api_key_set": bool(settings.elevenlabs_api_key),
                    "agent_id_set": bool(settings.elevenlabs_agent_id),
                    "phone_number_id_set": bool(settings.elevenlabs_phone_number_id),
                    "database_connected": database_status == "connected",
                    "mock_mode": enhanced_voice_service.use_mock
                },
                "enhancements": [
                    "Dynamic variables support",
                    "Enhanced conversation monitoring",
                    "Database call logging",
                    "Improved error handling",
                    "Real-time analytics"
                ]
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Enhanced ElevenLabs test failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "message": "Enhanced ElevenLabs test failed - check your enhanced setup"
            }
        )

@enhanced_webhook_router.get("/system-status")
async def enhanced_system_status():
    """📊 Enhanced system status with database metrics"""
    
    # Check database status and get metrics
    database_metrics = {}
    if database_service:
        try:
            await database_service.initialize()
            
            # Get basic database metrics
            async with database_service.get_session() as session:
                # Count campaigns
                campaigns_result = await session.execute("SELECT COUNT(*) FROM campaigns")
                campaigns_count = campaigns_result.scalar()
                
                # Count creators  
                creators_result = await session.execute("SELECT COUNT(*) FROM creators")
                creators_count = creators_result.scalar()
                
                database_metrics = {
                    "status": "connected",
                    "total_campaigns": campaigns_count,
                    "total_creators": creators_count
                }
        except Exception as e:
            database_metrics = {
                "status": "error",
                "error": str(e)
            }
    else:
        database_metrics = {"status": "not_initialized"}
    
    return {
        "service": "Enhanced InfluencerFlow Webhook Handler",
        "status": "healthy",
        "version": "2.1.0-enhanced-database",
        "database": database_metrics,
        "endpoints": {
            "enhanced_campaign": "/api/webhook/enhanced-campaign",
            "test_enhanced_campaign": "/api/webhook/test-enhanced-campaign",
            "test_enhanced_call": "/api/webhook/test-enhanced-call", 
            "test_enhanced_elevenlabs": "/api/webhook/test-enhanced-elevenlabs",
            "system_status": "/api/webhook/system-status"
        },
        "enhanced_capabilities": [
            "Enhanced ElevenLabs dynamic variables",
            "PostgreSQL database integration",
            "Real-time campaign tracking",
            "Advanced conversation analysis",
            "Creator performance analytics",
            "Automated contract generation",
            "Payment tracking and management",
            "ROI analysis and reporting"
        ],
        "integrations": {
            "groq_ai": bool(settings.groq_api_key),
            "elevenlabs_enhanced": bool(settings.elevenlabs_api_key),
            "postgresql": database_metrics.get("status") == "connected",
            "mock_mode": enhanced_voice_service.use_mock
        },
        "database_features": {
            "real_time_tracking": True,
            "campaign_analytics": True,
            "creator_management": True,
            "negotiation_history": True,
            "contract_management": True,
            "payment_tracking": True,
            "performance_reporting": True
        } if database_metrics.get("status") == "connected" else None
    }

# *** NEW: Database analytics endpoints ***
@enhanced_webhook_router.get("/analytics/campaigns")
async def get_campaign_analytics():
    """📊 Get campaign analytics from database"""
    try:
        if not database_service:
            raise HTTPException(status_code=500, detail="Database service not available")
        
        await database_service.initialize()
        
        async with database_service.get_session() as session:
            # Get campaign statistics
            campaigns_result = await session.execute("""
                SELECT 
                    COUNT(*) as total_campaigns,
                    COUNT(*) FILTER (WHERE status = 'completed') as completed_campaigns,
                    COUNT(*) FILTER (WHERE status = 'active') as active_campaigns,
                    AVG(total_cost) as avg_cost,
                    SUM(total_cost) as total_spent
                FROM campaigns
            """)
            stats = campaigns_result.fetchone()
            
            # Get recent campaigns
            recent_campaigns_result = await session.execute("""
                SELECT id, product_name, brand_name, status, total_cost, created_at
                FROM campaigns 
                ORDER BY created_at DESC 
                LIMIT 5
            """)
            recent_campaigns = recent_campaigns_result.fetchall()
            
        return {
            "campaign_statistics": {
                "total_campaigns": stats.total_campaigns,
                "completed_campaigns": stats.completed_campaigns,
                "active_campaigns": stats.active_campaigns,
                "average_cost": float(stats.avg_cost) if stats.avg_cost else 0,
                "total_spent": float(stats.total_spent) if stats.total_spent else 0
            },
            "recent_campaigns": [
                {
                    "id": campaign.id,
                    "product_name": campaign.product_name,
                    "brand_name": campaign.brand_name,
                    "status": campaign.status,
                    "total_cost": float(campaign.total_cost) if campaign.total_cost else 0,
                    "created_at": campaign.created_at.isoformat()
                }
                for campaign in recent_campaigns
            ]
        }
        
    except Exception as e:
        logger.error(f"❌ Campaign analytics failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analytics failed: {str(e)}")

@enhanced_webhook_router.get("/analytics/creators")
async def get_creator_analytics():
    """📊 Get creator performance analytics from database"""
    try:
        if not database_service:
            raise HTTPException(status_code=500, detail="Database service not available")
        
        await database_service.initialize()
        
        async with database_service.get_session() as session:
            # Get creator statistics by niche
            creators_by_niche_result = await session.execute("""
                SELECT 
                    niche,
                    COUNT(*) as creator_count,
                    AVG(followers) as avg_followers,
                    AVG(engagement_rate) as avg_engagement,
                    AVG(typical_rate) as avg_rate
                FROM creators 
                GROUP BY niche
                ORDER BY creator_count DESC
            """)
            creators_by_niche = creators_by_niche_result.fetchall()
            
            # Get top performers
            top_creators_result = await session.execute("""
                SELECT id, name, niche, followers, engagement_rate, typical_rate
                FROM creators 
                ORDER BY engagement_rate DESC, followers DESC
                LIMIT 10
            """)
            top_creators = top_creators_result.fetchall()
            
        return {
            "creators_by_niche": [
                {
                    "niche": row.niche,
                    "creator_count": row.creator_count,
                    "avg_followers": int(row.avg_followers) if row.avg_followers else 0,
                    "avg_engagement": float(row.avg_engagement) if row.avg_engagement else 0,
                    "avg_rate": float(row.avg_rate) if row.avg_rate else 0
                }
                for row in creators_by_niche
            ],
            "top_performers": [
                {
                    "id": creator.id,
                    "name": creator.name,
                    "niche": creator.niche,
                    "followers": creator.followers,
                    "engagement_rate": float(creator.engagement_rate),
                    "typical_rate": float(creator.typical_rate)
                }
                for creator in top_creators
            ]
        }
        
    except Exception as e:
        logger.error(f"❌ Creator analytics failed: {e}")
        raise HTTPException(status_code=500, detail=f"Creator analytics failed: {str(e)}")

@enhanced_webhook_router.get("/database/health")
async def database_health_check():
    """🏥 Comprehensive database health check"""
    try:
        if not database_service:
            return {
                "status": "not_initialized",
                "message": "Database service not available"
            }
        
        await database_service.initialize()
        
        health_checks = {}
        
        # Test basic connection
        async with database_service.get_session() as session:
            # Connection test
            start_time = datetime.now()
            result = await session.execute("SELECT 1")
            connection_time = (datetime.now() - start_time).total_seconds()
            health_checks["connection"] = {
                "status": "healthy",
                "response_time_ms": connection_time * 1000
            }
            
            # Table existence checks
            tables_result = await session.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = [row.table_name for row in tables_result.fetchall()]
            
            expected_tables = ["campaigns", "creators", "negotiations", "contracts", "payments", "outreach_logs"]
            missing_tables = [table for table in expected_tables if table not in tables]
            
            health_checks["schema"] = {
                "status": "healthy" if not missing_tables else "degraded",
                "existing_tables": tables,
                "missing_tables": missing_tables
            }
            
            # Data integrity checks
            campaigns_count = await session.execute("SELECT COUNT(*) FROM campaigns")
            creators_count = await session.execute("SELECT COUNT(*) FROM creators")
            
            health_checks["data"] = {
                "status": "healthy",
                "campaigns_count": campaigns_count.scalar(),
                "creators_count": creators_count.scalar()
            }
        
        overall_status = "healthy"
        if any(check.get("status") != "healthy" for check in health_checks.values()):
            overall_status = "degraded"
        
        return {
            "overall_status": overall_status,
            "checks": health_checks,
            "database_url": "postgresql://***:***@localhost:5432/influencerflow",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Database health check failed: {e}")
        return {
            "overall_status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }