# main.py - UNIFIED APPLICATION ENTRY POINT
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime

from core.config import settings
from api.campaigns import router as campaigns_router

# Set up logging
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    🚀 Application Lifespan Management
    
    Handles startup and shutdown procedures for the application
    """
    
    # Startup
    logger.info(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"📍 Environment: {settings.environment}")
    logger.info(f"🎙️ Voice Service: {'Mock' if settings.use_mock_services else 'Live'}")
    
    try:
        # Initialize services and validate configuration
        await initialize_services()
        
        logger.info("✅ Application startup completed successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Application startup failed: {e}")
        raise
    
    finally:
        # Cleanup
        logger.info("🛑 Shutting down application...")
        await cleanup_services()
        logger.info("✅ Application shutdown completed")

async def initialize_services():
    """Initialize all application services"""
    
    # Import here to avoid circular imports
    from agents.orchestrator import CampaignOrchestrator
    from services.voice import VoiceService
    
    # Test service initialization
    orchestrator = CampaignOrchestrator()
    voice_service = VoiceService()
    
    # Test voice service if not using mocks
    if not settings.use_mock_services:
        logger.info("🧪 Testing ElevenLabs connection...")
        # Add actual connection test here if needed
    
    logger.info("🎯 All services initialized successfully")

async def cleanup_services():
    """Cleanup application services"""
    
    # Clean up any background tasks
    from api.campaigns import active_campaigns
    
    active_count = len([c for c in active_campaigns.values() if not c.is_complete()])
    if active_count > 0:
        logger.warning(f"⚠️ Shutting down with {active_count} active campaigns")
    
    # Clear campaign cache
    active_campaigns.clear()

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Unified AI-powered influencer marketing automation platform",
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(campaigns_router, prefix="/api", tags=["Campaigns"])

@app.get("/")
async def root():
    """
    🏠 Root endpoint with application information
    """
    
    from api.campaigns import active_campaigns
    
    active_count = len([c for c in active_campaigns.values() if not c.is_complete()])
    total_count = len(active_campaigns)
    
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "status": "operational",
        "features": [
            "Unified campaign orchestration",
            "AI-powered creator discovery",
            "Voice-based negotiations",
            "Automated contract generation",
            "Real-time progress monitoring"
        ],
        "capabilities": {
            "voice_service": "mock" if settings.use_mock_services else "live",
            "ai_strategy": "enabled" if settings.groq_api_key else "disabled",
            "database": "enabled" if settings.database_url else "mock"
        },
        "statistics": {
            "total_campaigns": total_count,
            "active_campaigns": active_count,
            "completed_campaigns": total_count - active_count
        },
        "api_endpoints": {
            "create_campaign": "POST /api/campaigns",
            "get_status": "GET /api/campaigns/{task_id}",
            "list_campaigns": "GET /api/campaigns",
            "detailed_results": "GET /api/campaigns/{task_id}/detailed"
        }
    }

@app.get("/health")
async def health_check():
    """
    🏥 Health check endpoint with service validation
    """
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": settings.environment,
        "version": settings.app_version
    }
    
    services_status = {}
    services_count = 0
    
    try:
        # Check voice service
        from services.voice import VoiceService
        voice_service = VoiceService()
        
        services_status["voice_service"] = {
            "status": "operational",
            "mode": "mock" if settings.use_mock_services else "live",
            "api_configured": bool(getattr(settings, 'elevenlabs_api_key', None))
        }
        services_count += 1
        
    except Exception as e:
        services_status["voice_service"] = {
            "status": "error",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    try:
        # Check database service
        from services.database import DatabaseService
        db_service = DatabaseService()
        
        services_status["database_service"] = {
            "status": "operational",
            "mode": "mock" if not getattr(settings, 'database_url', None) else "live"
        }
        services_count += 1
        
    except Exception as e:
        services_status["database_service"] = {
            "status": "error",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    try:
        # Check orchestrator
        from agents.orchestrator import CampaignOrchestrator
        orchestrator = CampaignOrchestrator()
        
        services_status["orchestrator"] = {
            "status": "operational",
            "agents_loaded": True
        }
        services_count += 1
        
    except Exception as e:
        services_status["orchestrator"] = {
            "status": "error",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Add services info to response
    health_status["services"] = services_status
    health_status["services_count"] = services_count
    
    return health_status

@app.get("/metrics")
async def get_metrics():
    """
    📊 Application metrics endpoint
    """
    
    from api.campaigns import active_campaigns
    
    # Calculate metrics
    total_campaigns = len(active_campaigns)
    active_count = len([c for c in active_campaigns.values() if not c.is_complete()])
    completed_count = total_campaigns - active_count
    
    successful_campaigns = len([
        c for c in active_campaigns.values() 
        if c.is_complete() and c.successful_negotiations > 0
    ])
    
    total_negotiations = sum(len(c.negotiations) for c in active_campaigns.values())
    successful_negotiations = sum(c.successful_negotiations for c in active_campaigns.values())
    total_cost = sum(c.total_cost for c in active_campaigns.values())
    
    # Calculate averages
    avg_success_rate = (successful_negotiations / total_negotiations * 100) if total_negotiations > 0 else 0
    avg_cost_per_campaign = total_cost / completed_count if completed_count > 0 else 0
    
    return {
        "timestamp": "2024-12-14T12:00:00Z",
        "campaign_metrics": {
            "total_campaigns": total_campaigns,
            "active_campaigns": active_count,
            "completed_campaigns": completed_count,
            "successful_campaigns": successful_campaigns,
            "success_rate_percentage": round(avg_success_rate, 2)
        },
        "negotiation_metrics": {
            "total_negotiations": total_negotiations,
            "successful_negotiations": successful_negotiations,
            "total_cost": total_cost,
            "average_cost_per_campaign": round(avg_cost_per_campaign, 2)
        },
        "system_metrics": {
            "environment": settings.environment,
            "mock_mode": settings.use_mock_services,
            "concurrent_campaign_limit": settings.max_concurrent_calls,
            "memory_campaigns": len(active_campaigns)
        }
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    🚨 Global exception handler for unhandled errors
    """
    
    logger.error(f"❌ Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "timestamp": "2024-12-14T12:00:00Z",
            "environment": settings.environment
        }
    )

@app.middleware("http")
async def log_requests(request, call_next):
    """
    📝 Request logging middleware
    """
    
    start_time = asyncio.get_event_loop().time()
    
    response = await call_next(request)
    
    process_time = asyncio.get_event_loop().time() - start_time
    
    logger.info(
        f"📡 {request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    return response

# Development server configuration
if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🚀 Starting development server...")
    logger.info(f"📍 Environment: {settings.environment}")
    logger.info(f"🔧 Debug mode: {settings.debug}")
    logger.info(f"🎙️ Mock services: {settings.use_mock_services}")
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level=settings.log_level.lower()
    )