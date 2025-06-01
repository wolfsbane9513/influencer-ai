# main.py - FIXED VERSION with Better Import Handling
import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Global state to track active campaigns
active_campaigns = {}

def load_settings():
    """Load settings with fallback"""
    try:
        from config.settings import settings
        print("✅ Using SimpleSettings fallback")
        return settings
    except ImportError as e2:
        print(f"❌ Both settings failed: {e2}")
        print("📋 Please run: python fix_imports.py")
        exit(1)

def load_enhanced_endpoints():
    """Load enhanced endpoints with graceful fallback"""
    try:
        from api.enhanced_webhooks import enhanced_webhook_router
        from api.enhanced_monitoring import enhanced_monitoring_router
        print("✅ Enhanced endpoints loaded")
        return enhanced_webhook_router, enhanced_monitoring_router
    except ImportError as e:
        print(f"⚠️  Enhanced endpoints not available: {e}")
        return None, None

def load_legacy_endpoints():
    """Load legacy endpoints with graceful fallback"""
    try:
        from api.webhooks import webhook_router
        from api.monitoring import monitoring_router
        print("✅ Legacy endpoints loaded")
        return webhook_router, monitoring_router
    except ImportError as e:
        print(f"⚠️  Legacy endpoints not available: {e}")
        return None, None

# Load settings
settings = load_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    print("🚀 InfluencerFlow AI Platform starting up...")
    print(f"🔧 Debug mode: {settings.debug}")
    print(f"🎯 Demo mode: {settings.demo_mode}")
    
    # Try to load enhanced features
    enhanced_webhook_router, enhanced_monitoring_router = load_enhanced_endpoints()
    if enhanced_webhook_router and enhanced_monitoring_router:
        print("🔥 Enhanced features available!")
    
    # Try to load legacy features
    legacy_webhook_router, legacy_monitoring_router = load_legacy_endpoints()
    if legacy_webhook_router and legacy_monitoring_router:
        print("📋 Legacy endpoints available!")
    
    yield
    print("👋 InfluencerFlow AI Platform shutting down...")

# Create FastAPI app
app = FastAPI(
    title="InfluencerFlow AI Platform",
    description="AI-powered influencer marketing campaign automation",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Try to include enhanced routers
try:
    from api.enhanced_webhooks import enhanced_webhook_router
    from api.enhanced_monitoring import enhanced_monitoring_router
    
    app.include_router(enhanced_webhook_router, prefix="/api/webhook", tags=["enhanced-webhooks"])
    app.include_router(enhanced_monitoring_router, prefix="/api/monitor", tags=["enhanced-monitoring"])
    print("✅ Enhanced endpoints loaded")
except ImportError as e:
    print(f"⚠️  Enhanced endpoints not available: {e}")

# Try to include legacy routers
try:
    from api.webhooks import webhook_router
    from api.monitoring import monitoring_router
    
    app.include_router(webhook_router, prefix="/api/webhook", tags=["webhooks"])
    app.include_router(monitoring_router, prefix="/api/monitor", tags=["monitoring"])
    print("✅ Legacy endpoints loaded")
except ImportError as e:
    print(f"⚠️  Legacy endpoints not available: {e}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "InfluencerFlow AI Platform is running",
        "version": "2.0.0",
        "status": "healthy",
        "demo_mode": settings.demo_mode,
        "active_campaigns": len(active_campaigns)
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    
    # Check service availability
    services = {
        "api": "running",
        "database": "connected",  # TODO: Add actual DB health check
    }
    
    # Check API keys
    if hasattr(settings, 'groq_api_key') and settings.groq_api_key:
        services["groq"] = "configured"
    else:
        services["groq"] = "missing_key"
    
    if hasattr(settings, 'elevenlabs_api_key') and settings.elevenlabs_api_key:
        services["elevenlabs"] = "configured"
    else:
        services["elevenlabs"] = "missing_key"
    
    return {
        "status": "healthy",
        "services": services,
        "active_campaigns": len(active_campaigns),
        "settings": {
            "demo_mode": settings.demo_mode,
            "mock_calls": getattr(settings, 'mock_calls', False),
            "max_negotiation_duration": getattr(settings, 'max_negotiation_duration', 45)
        }
    }

@app.get("/debug")
async def debug_info():
    """Debug information for troubleshooting"""
    
    debug_info = {
        "python_version": "3.13+",
        "fastapi_version": "0.115+",
        "settings_loaded": True,
        "active_campaigns": len(active_campaigns)
    }
    
    # Check imports
    import_status = {}
    
    # Test core imports
    try:
        from models.campaign import CampaignWebhook
        import_status["models"] = "✅ Available"
    except ImportError as e:
        import_status["models"] = f"❌ Failed: {e}"
    
    try:
        from agents.orchestrator import CampaignOrchestrator
        import_status["orchestrator"] = "✅ Available"
    except ImportError as e:
        import_status["orchestrator"] = f"❌ Failed: {e}"
    
    try:
        from agents.negotiation import NegotiationAgent
        import_status["negotiation_agent"] = "✅ Available"
    except ImportError as e:
        import_status["negotiation_agent"] = f"❌ Failed: {e}"
    
    try:
        from services.voice import VoiceService
        import_status["voice_service"] = "✅ Available"
    except ImportError as e:
        import_status["voice_service"] = f"❌ Failed: {e}"
    
    debug_info["import_status"] = import_status
    
    return debug_info

if __name__ == "__main__":
    print("🚀 Starting InfluencerFlow AI Platform...")
    print(f"🔧 Host: {settings.host}")
    print(f"🔧 Port: {settings.port}")
    print(f"🔧 Debug: {settings.debug}")
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )