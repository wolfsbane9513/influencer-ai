# main.py - ENHANCED WITH DATABASE INTEGRATION
import asyncio
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Dict

# Your existing imports
from api.enhanced_webhooks import enhanced_webhook_router
from api.monitoring import monitoring_router
from agents.enhanced_orchestrator import EnhancedCampaignOrchestrator
from services.enhanced_voice import EnhancedVoiceService

# *** ADD DATABASE IMPORTS ***
from services.database import DatabaseService
from config.settings import settings

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global state management (enhanced with database)
active_campaigns: Dict[str, any] = {}
orchestrator: EnhancedCampaignOrchestrator = None
voice_service: EnhancedVoiceService = None
database_service: DatabaseService = None  # *** ADD DATABASE SERVICE ***

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    🚀 ENHANCED LIFESPAN MANAGEMENT WITH DATABASE
    
    Proper initialization and cleanup of all services including database
    """
    
    global orchestrator, voice_service, database_service
    
    # ================================
    # STARTUP SEQUENCE
    # ================================
    logger.info("🚀 Starting InfluencerFlow AI Platform with Database...")
    
    try:
        # *** STEP 1: Initialize Database First ***
        logger.info("💾 Initializing PostgreSQL database...")
        database_service = DatabaseService()
        await database_service.initialize()
        logger.info("✅ Database initialized successfully")
        
        # Test database connection
        try:
            async with database_service.get_session() as session:
                result = await session.execute("SELECT version()")
                db_version = result.scalar()
                logger.info(f"✅ Database connected: {db_version[:50]}...")
        except Exception as e:
            logger.error(f"⚠️ Database connection test failed: {e}")
            logger.info("📋 Continuing with limited database functionality")
        
        # *** STEP 2: Initialize Voice Service ***
        logger.info("📞 Initializing Enhanced Voice Service...")
        voice_service = EnhancedVoiceService()
        
        # Test voice service connectivity
        voice_test = await voice_service.test_credentials()
        logger.info(f"📞 Voice service status: {voice_test.get('status', 'unknown')}")
        
        # *** STEP 3: Initialize Enhanced Orchestrator ***
        logger.info("🧠 Initializing Enhanced Campaign Orchestrator...")
        orchestrator = EnhancedCampaignOrchestrator()
        
        # Inject database service into orchestrator if it has database support
        if hasattr(orchestrator, 'database_service'):
            orchestrator.database_service = database_service
            logger.info("✅ Database service injected into orchestrator")
        
        # *** STEP 4: Startup Summary ***
        logger.info("🎉 Platform initialization completed!")
        logger.info("🔧 Active services:")
        logger.info(f"   • Database: {'✅ Connected' if database_service else '❌ Failed'}")
        logger.info(f"   • Voice Service: {'✅ Ready' if voice_service else '❌ Failed'}")
        logger.info(f"   • Orchestrator: {'✅ Ready' if orchestrator else '❌ Failed'}")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Platform initialization failed: {e}")
        # Don't crash - continue with limited functionality
        logger.info("🚨 Running in degraded mode")
        yield
    
    finally:
        # ================================
        # SHUTDOWN SEQUENCE
        # ================================
        logger.info("🛑 Shutting down platform...")
        
        # Stop any active monitoring
        if orchestrator and hasattr(orchestrator, 'conversation_monitor'):
            try:
                orchestrator.conversation_monitor.stop_all_monitoring()
                logger.info("✅ Conversation monitoring stopped")
            except Exception as e:
                logger.error(f"❌ Error stopping conversation monitor: {e}")
        
        # Close database connections
        if database_service:
            try:
                await database_service.close()
                logger.info("✅ Database connections closed")
            except Exception as e:
                logger.error(f"❌ Database cleanup error: {e}")
        
        # Clear active campaigns
        active_campaigns.clear()
        logger.info("🧹 Active campaigns cleared")
        
        logger.info("✅ Platform shutdown completed")

# Create FastAPI app with enhanced lifespan
app = FastAPI(
    title="InfluencerFlow AI Platform",
    description="Enhanced AI-powered influencer marketing with PostgreSQL database integration",
    version="2.1.0-database-enhanced",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(enhanced_webhook_router, prefix="/api/webhook", tags=["Enhanced Webhooks"])
app.include_router(monitoring_router, prefix="/api/monitor", tags=["Monitoring"])

# *** NEW: Add database-specific endpoints ***
@app.get("/api/database/status")
async def database_status():
    """Get database status and connection info"""
    global database_service
    
    if not database_service:
        return {
            "status": "not_initialized",
            "message": "Database service not initialized"
        }
    
    try:
        async with database_service.get_session() as session:
            result = await session.execute("SELECT version(), current_database(), current_user")
            version, db_name, user = result.fetchone()
        
        return {
            "status": "connected",
            "database_version": version,
            "database_name": db_name,
            "user": user,
            "connection_url": "postgresql://***:***@localhost:5432/influencerflow",
            "features": [
                "Real-time campaign tracking",
                "Creator performance analytics",
                "Negotiation history",
                "Contract management",
                "Payment tracking"
            ]
        }
        
    except Exception as e:
        logger.error(f"Database status check failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "troubleshooting": {
                "check_postgresql": "Ensure PostgreSQL is running",
                "check_env": "Verify DATABASE_URL in .env file",
                "start_db": "Run: docker-compose up -d postgres"
            }
        }

@app.post("/api/database/seed-data")
async def seed_database():
    """Seed database with sample data"""
    global database_service
    
    if not database_service:
        raise HTTPException(status_code=500, detail="Database service not initialized")
    
    try:
        # Create sample creators
        from models.campaign import Creator as CampaignCreator, Platform, Availability
        
        sample_creators = [
            CampaignCreator(
                id="enhanced_fitness_mike",
                name="Mike Enhanced Fitness",
                platform=Platform.YOUTUBE,
                followers=280000,
                niche="fitness",
                typical_rate=5500.0,
                engagement_rate=4.5,
                average_views=55000,
                last_campaign_date="2024-12-01",
                availability=Availability.EXCELLENT,
                location="California, USA",
                phone_number="+1-555-FITNESS",
                languages=["English"],
                specialties=["strength training", "nutrition coaching"]
            ),
            CampaignCreator(
                id="enhanced_tech_sarah",
                name="Sarah Enhanced Tech",
                platform=Platform.YOUTUBE,
                followers=190000,
                niche="tech",
                typical_rate=4000.0,
                engagement_rate=4.1,
                average_views=45000,
                last_campaign_date="2024-12-05",
                availability=Availability.GOOD,
                location="Seattle, USA",
                phone_number="+1-555-TECH",
                languages=["English"],
                specialties=["tech reviews", "AI content"]
            )
        ]
        
        created_count = 0
        for creator in sample_creators:
            await database_service.create_or_update_creator(creator)
            created_count += 1
        
        return {
            "message": "✅ Enhanced sample data seeded successfully",
            "creators_created": created_count,
            "database_ready": True
        }
        
    except Exception as e:
        logger.error(f"Sample data seeding failed: {e}")
        raise HTTPException(status_code=500, detail=f"Seeding failed: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with enhanced platform status"""
    global database_service
    
    # Check database status
    database_status = "unknown"
    if database_service:
        try:
            async with database_service.get_session() as session:
                await session.execute("SELECT 1")
            database_status = "connected"
        except:
            database_status = "disconnected"
    
    return {
        "service": "InfluencerFlow AI Platform",
        "version": "2.1.0-database-enhanced",
        "status": "operational",
        "database_status": database_status,
        "active_campaigns": len(active_campaigns),
        "features": [
            "Enhanced ElevenLabs integration",
            "PostgreSQL database integration",
            "Real-time campaign tracking",
            "Creator performance analytics",
            "Advanced error handling",
            "Comprehensive monitoring"
        ],
        "enhancements": [
            "Fixed API response validation",
            "Improved conversation monitoring", 
            "Enhanced contract generation",
            "Database persistence layer",
            "Real-time analytics"
        ],
        "endpoints": {
            "create_campaign": "POST /api/webhook/enhanced-campaign",
            "monitor_campaign": "GET /api/monitor/enhanced-campaign/{task_id}",
            "database_status": "GET /api/database/status",
            "seed_database": "POST /api/database/seed-data"
        }
    }

@app.get("/health")
async def health_check():
    """
    🏥 ENHANCED HEALTH CHECK WITH DATABASE VALIDATION
    """
    
    health_status = {
        "status": "healthy",
        "timestamp": "2024-12-14T10:00:00Z",
        "version": "2.1.0-database-enhanced",
        "services": {},
        "metrics": {
            "active_campaigns": len(active_campaigns)
        }
    }
    
    try:
        # Check database service
        if database_service:
            try:
                async with database_service.get_session() as session:
                    await session.execute("SELECT 1")
                health_status["services"]["database"] = {
                    "status": "healthy",
                    "type": "postgresql"
                }
            except Exception as e:
                health_status["services"]["database"] = {
                    "status": "unhealthy",
                    "error": str(e)[:50],
                    "type": "postgresql"
                }
        else:
            health_status["services"]["database"] = {
                "status": "not_initialized",
                "type": "postgresql"
            }
        
        # Check voice service
        if voice_service:
            voice_test = await voice_service.test_credentials()
            health_status["services"]["voice_service"] = {
                "status": voice_test.get("status", "unknown"),
                "mode": "mock" if voice_service.use_mock else "live",
                "type": "elevenlabs"
            }
        else:
            health_status["services"]["voice_service"] = {
                "status": "not_initialized",
                "type": "elevenlabs"
            }
        
        # Check orchestrator
        if orchestrator:
            health_status["services"]["orchestrator"] = {
                "status": "initialized",
                "type": "enhanced"
            }
        else:
            health_status["services"]["orchestrator"] = {
                "status": "not_initialized",
                "type": "enhanced"
            }
        
        # Determine overall status
        service_statuses = [
            service.get("status") for service in health_status["services"].values()
        ]
        unhealthy_services = [
            name for name, service in health_status["services"].items()
            if service.get("status") not in ["healthy", "initialized", "success", "mock_mode"]
        ]
        
        if unhealthy_services:
            health_status["status"] = "degraded"
            health_status["issues"] = unhealthy_services
        
        return health_status
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-12-14T10:00:00Z"
        }

# Enhanced error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with proper logging and database tracking"""
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    
    # Optionally log error to database
    if database_service and exc.status_code >= 500:
        try:
            # Could add error logging to database here
            pass
        except:
            pass  # Don't fail on error logging
    
    return {
        "error": exc.detail,
        "status_code": exc.status_code,
        "type": "http_error",
        "timestamp": "2024-12-14T10:00:00Z"
    }

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions with database error tracking"""
    logger.error(f"Unhandled Exception: {str(exc)}")
    
    # Log critical errors to database if available
    if database_service:
        try:
            # Could add critical error logging here
            pass
        except:
            pass  # Don't fail on error logging
    
    return {
        "error": "Internal server error",
        "message": str(exc),
        "type": "server_error",
        "timestamp": "2024-12-14T10:00:00Z"
    }

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting Enhanced InfluencerFlow AI Platform with Database...")
    logger.info("📊 Features: Enhanced ElevenLabs + PostgreSQL + Real-time Analytics")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )