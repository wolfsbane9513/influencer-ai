# main.py - CORRECTED INTEGRATION
import asyncio
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Dict

from api.webhooks import webhook_router
from api.monitoring import monitoring_router
from agents.orchestrator import CampaignOrchestrator
from services.voice import VoiceService
from config.settings import settings

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global state management
active_campaigns: Dict[str, any] = {}
orchestrator: CampaignOrchestrator = None
voice_service: VoiceService = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    🚀 CORRECTED LIFESPAN MANAGEMENT
    
    Proper initialization and cleanup of services
    """
    
    global orchestrator, voice_service
    
    # Startup
    logger.info("🚀 Starting InfluencerFlow AI Platform...")
    
    try:
        # Initialize services with proper error handling
        voice_service = VoiceService()
        orchestrator = CampaignOrchestrator()
        
        # Test service connectivity
        voice_test = await voice_service.test_credentials()
        logger.info(f"📞 Voice service status: {voice_test.get('status', 'unknown')}")
        
        logger.info("✅ Platform initialization completed")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Platform initialization failed: {e}")
        raise
    
    finally:
        # Cleanup
        logger.info("🛑 Shutting down platform...")
        
        # Stop any active monitoring
        if orchestrator and hasattr(orchestrator, 'conversation_monitor'):
            orchestrator.conversation_monitor.stop_all_monitoring()
        
        # Clear active campaigns
        active_campaigns.clear()
        
        logger.info("✅ Platform shutdown completed")

# Create FastAPI app with corrected lifespan
app = FastAPI(
    title="InfluencerFlow AI Platform",
    description="Enhanced AI-powered influencer marketing automation with ElevenLabs integration",
    version="2.0.0-fixed",
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
app.include_router(webhook_router, prefix="/api/webhook", tags=["Enhanced Webhooks"])
app.include_router(monitoring_router, prefix="/api/monitor", tags=["Monitoring"])

@app.get("/")
async def root():
    """Root endpoint with platform status"""
    return {
        "service": "InfluencerFlow AI Platform",
        "version": "2.0.0-fixed",
        "status": "operational",
        "features": [
            "Fixed ElevenLabs integration",
            "Proper call state handling", 
            "Corrected contract generation",
            "Enhanced error handling"
        ],
        "fixes_applied": [
            "API response validation",
            "Conversation monitoring",
            "Contract generation logic",
            "Error handling and retries"
        ]
    }

@app.get("/health")
async def health_check():
    """
    🏥 HEALTH CHECK WITH SERVICE VALIDATION
    """
    
    health_status = {
        "status": "healthy",
        "timestamp": "2024-12-14T10:00:00Z",
        "services": {}
    }
    
    try:
        # Check voice service
        if voice_service:
            voice_test = await voice_service.test_credentials()
            health_status["services"]["voice_service"] = {
                "status": voice_test.get("status", "unknown"),
                "mode": "mock" if voice_service.use_mock else "live"
            }
        else:
            health_status["services"]["voice_service"] = {
                "status": "not_initialized",
                "mode": "unknown"
            }
        
        # Check orchestrator
        if orchestrator:
            health_status["services"]["orchestrator"] = {
                "status": "initialized",
                "active_campaigns": len(active_campaigns)
            }
        else:
            health_status["services"]["orchestrator"] = {
                "status": "not_initialized"
            }
        
        # Overall status
        service_statuses = [service.get("status") for service in health_status["services"].values()]
        if all(status in ["healthy", "initialized", "success", "mock_mode"] for status in service_statuses):
            health_status["status"] = "healthy"
        else:
            health_status["status"] = "degraded"
        
        return health_status
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-12-14T10:00:00Z"
        }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with proper logging"""
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return {
        "error": exc.detail,
        "status_code": exc.status_code,
        "type": "http_error"
    }

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions with proper logging"""
    logger.error(f"Unhandled Exception: {str(exc)}")
    return {
        "error": "Internal server error",
        "message": str(exc),
        "type": "server_error"
    }

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting InfluencerFlow AI Platform...")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )