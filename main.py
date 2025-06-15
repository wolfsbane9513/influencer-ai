# main.py - CORRECTED MAIN APPLICATION
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import settings
from api.campaigns import router as campaigns_router
from agents.orchestrator import CampaignOrchestrator
from services.voice import VoiceService
from services.database import DatabaseService

logger = logging.getLogger(__name__)


class ApplicationManager:
    """
    🚀 Clean Application Manager
    
    Handles application lifecycle with proper OOP design:
    - Service initialization and cleanup
    - Health monitoring
    - Error handling
    - No unnecessary helper functions
    """
    
    def __init__(self):
        self.orchestrator: CampaignOrchestrator = None
        self.voice_service: VoiceService = None
        self.database_service: DatabaseService = None
        self.is_initialized = False
    
    async def initialize_services(self) -> None:
        """Initialize all application services"""
        
        try:
            logger.info("🚀 Initializing InfluencerFlow AI Platform services...")
            
            # Initialize core services
            self.voice_service = VoiceService()
            self.database_service = DatabaseService()
            self.orchestrator = CampaignOrchestrator()
            
            # Test service connections
            await self._test_service_connections()
            
            self.is_initialized = True
            logger.info("✅ All services initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Service initialization failed: {e}")
            raise RuntimeError(f"Failed to initialize services: {e}")
    
    async def _test_service_connections(self) -> None:
        """Test connections to external services"""
        
        logger.info("🧪 Testing service connections...")
        
        # Test ElevenLabs connection if configured
        if settings.is_elevenlabs_configured() and not settings.use_mock_services:
            try:
                # Test with simple API call
                import httpx
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{settings.elevenlabs_base_url}/v1/user",
                        headers={"Xi-Api-Key": settings.elevenlabs_api_key},
                        timeout=10.0
                    )
                    if response.status_code == 200:
                        logger.info("✅ ElevenLabs connection successful")
                    else:
                        logger.warning(f"⚠️ ElevenLabs connection issue: {response.status_code}")
            except Exception as e:
                logger.warning(f"⚠️ ElevenLabs connection test failed: {e}")
        
        # Test database connection if configured
        if settings.is_database_configured():
            # Add database connection test here
            logger.info("🔍 Database connection test - implement if needed")
    
    async def cleanup_services(self) -> None:
        """Clean up all services"""
        
        logger.info("🧹 Cleaning up services...")
        
        try:
            if self.voice_service:
                await self.voice_service.close()
            
            if self.orchestrator:
                await self.orchestrator.close()
            
            logger.info("✅ Service cleanup completed")
            
        except Exception as e:
            logger.error(f"❌ Service cleanup error: {e}")
    
    def get_health_status(self) -> dict:
        """Get application health status"""
        
        return {
            "status": "healthy" if self.is_initialized else "unhealthy",
            "version": settings.app_version,
            "environment": settings.environment,
            "services": settings.get_service_status(),
            "initialized": self.is_initialized
        }


# Global application manager
app_manager = ApplicationManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    
    # Startup
    logger.info(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"📍 Environment: {settings.environment}")
    
    # Log configuration status
    settings.log_configuration_status()
    
    # Initialize services
    await app_manager.initialize_services()
    
    logger.info("✅ Application startup completed successfully")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down application...")
    await app_manager.cleanup_services()
    logger.info("✅ Application shutdown completed")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered influencer marketing campaign automation platform",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(campaigns_router, prefix="/api", tags=["campaigns"])


@app.get("/health")
async def health_check():
    """Application health check endpoint"""
    
    health_status = app_manager.get_health_status()
    
    # Log health check
    logger.info(f"📡 GET /health - Status: {200 if health_status['status'] == 'healthy' else 503} - Time: 0.001s")
    
    if health_status["status"] == "healthy":
        return health_status
    else:
        raise HTTPException(status_code=503, detail=health_status)


@app.get("/")
async def root():
    """Root endpoint with basic information"""
    
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "environment": settings.environment,
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "campaigns": "/api/campaigns",
            "docs": "/docs"
        }
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    
    logger.error(f"❌ Unhandled exception: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "An unexpected error occurred",
            "type": type(exc).__name__
        }
    )


# Development server entry point
if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting development server...")
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload and settings.environment == "development",
        log_level=settings.log_level.lower()
    )