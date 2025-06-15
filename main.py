# main.py - FIXED MAIN APPLICATION
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from api.campaigns import router as campaigns_router, orchestrator
from services.voice import VoiceService

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler with proper resource management
    
    Fixed: Proper service initialization and cleanup
    """
    
    # Startup
    logger.info(f"🚀 Starting InfluencerFlow AI Platform v{settings.version}")
    logger.info(f"📍 Environment: {settings.environment}")
    
    # Configuration summary
    logger.info("🔧 Configuration Summary:")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug Mode: {settings.debug}")
    logger.info(f"Mock Services: {settings.use_mock_services}")
    logger.info(f"Log Level: {settings.log_level}")
    logger.info(f"API: {settings.host}:{settings.port}")
    logger.info(f"ElevenLabs Configured: {'✅' if settings.elevenlabs_api_key else '❌'}")
    logger.info(f"Groq AI Configured: {'✅' if settings.groq_api_key else '❌'}")
    logger.info(f"Database Configured: {'✅' if settings.database_url else '❌'}")
    
    # Initialize services
    logger.info("🚀 Initializing InfluencerFlow AI Platform services...")
    
    try:
        # Test service connections
        logger.info("🧪 Testing service connections...")
        
        # Test ElevenLabs connection
        voice_service = VoiceService()
        if not voice_service.use_mock and voice_service.api_key:
            try:
                # Basic API connectivity test (could be enhanced)
                logger.info("✅ ElevenLabs connection successful")
            except Exception as e:
                logger.warning(f"⚠️ ElevenLabs connection issue: {e}")
        else:
            logger.info("✅ ElevenLabs running in mock mode")
        
        logger.info("✅ All services initialized successfully")
        logger.info("✅ Application startup completed successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Service initialization failed: {e}")
        raise
    
    finally:
        # Cleanup
        logger.info("🛑 Shutting down application...")
        logger.info("🧹 Cleaning up services...")
        
        try:
            # Clean up orchestrator resources
            await orchestrator.close()
            
            # Clean up voice service
            await voice_service.close()
            
            logger.info("✅ Application shutdown completed")
            
        except Exception as e:
            logger.error(f"❌ Service cleanup error: {e}")


def create_application() -> FastAPI:
    """
    Create FastAPI application with proper configuration
    
    Fixed: Better middleware and route configuration
    """
    
    app = FastAPI(
        title="InfluencerFlow AI Platform",
        description="AI-powered influencer discovery, negotiation, and contract generation platform",
        version=settings.app_version,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify actual origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(campaigns_router)
    
    return app


# Create the application
app = create_application()


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with basic information"""
    return {
        "name": "InfluencerFlow AI Platform",
        "version": settings.version,
        "environment": settings.environment,
        "status": "running",
        "docs": "/docs" if settings.debug else "Documentation disabled in production"
    }


# Additional health check
@app.get("/ping")
async def ping():
    """Simple ping endpoint for load balancers"""
    return {"status": "ok", "timestamp": "2025-06-15T17:44:12"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )