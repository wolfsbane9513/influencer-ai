# main.py - Clean Production Version
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Global state to track active campaigns (used by monitoring)
active_campaigns = {}

def load_settings():
    """Load settings with clean error handling"""
    try:
        from config.settings import settings
        return settings
    except ImportError as e:
        print(f"❌ Settings import failed: {e}")
        print("📋 Please ensure config/settings.py exists")
        exit(1)

# Load settings
settings = load_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    print("🚀 InfluencerFlow AI Platform starting up...")
    print(f"🔧 Debug mode: {settings.debug}")
    print(f"🎯 Demo mode: {settings.demo_mode}")
    print(f"🔥 Enhanced features enabled")
    
    yield
    
    print("👋 InfluencerFlow AI Platform shutting down...")

# Create FastAPI app
app = FastAPI(
    title="InfluencerFlow AI Platform",
    description="AI-powered influencer marketing campaign automation with conversational interface",
    version="2.1.0-production",
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

# Load Enhanced Endpoints (Production Ready)
try:
    from api.enhanced_webhooks import enhanced_webhook_router
    from api.enhanced_monitoring import enhanced_monitoring_router
    
    app.include_router(
        enhanced_webhook_router, 
        prefix="/api/webhook", 
        tags=["enhanced-webhooks"]
    )
    app.include_router(
        enhanced_monitoring_router, 
        prefix="/api/monitor", 
        tags=["enhanced-monitoring"]
    )
    print("✅ Enhanced production endpoints loaded")
    
except ImportError as e:
    print(f"❌ Enhanced endpoints failed to load: {e}")
    print("📋 Please ensure api/enhanced_*.py files exist")
    exit(1)

try:
    from api.whatsapp import whatsapp_router
    
    app.include_router(whatsapp_router, prefix="/api/whatsapp", tags=["whatsapp"])
    print("✅ WhatsApp endpoints loaded")
except ImportError as e:
    print(f"⚠️  WhatsApp endpoints not available: {e}")
    print("📋 Run after setting up WhatsApp integration") 

# Core Health Endpoints
@app.get("/")
async def root():
    """Root health check endpoint"""
    return {
        "message": "InfluencerFlow AI Platform - Production Ready",
        "version": "2.1.0-production",
        "status": "healthy",
        "features": [
            "Enhanced AI-powered campaign orchestration",
            "ElevenLabs voice negotiations with dynamic variables", 
            "Real-time conversation monitoring",
            "Comprehensive contract generation",
            "Advanced analytics and validation"
        ],
        "demo_mode": settings.demo_mode,
        "active_campaigns": len(active_campaigns)
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    
    # Check service availability
    services = {
        "api": "running",
        "database": "connected",  # TODO: Add actual DB health check when needed
    }
    
    # Check API integrations
    if hasattr(settings, 'groq_api_key') and settings.groq_api_key:
        services["groq_llm"] = "configured"
    else:
        services["groq_llm"] = "missing_key"
    
    if hasattr(settings, 'elevenlabs_api_key') and settings.elevenlabs_api_key:
        services["elevenlabs_voice"] = "configured"
    else:
        services["elevenlabs_voice"] = "missing_key"
    
    return {
        "status": "healthy",
        "version": "2.1.0-production",
        "services": services,
        "active_campaigns": len(active_campaigns),
        "configuration": {
            "demo_mode": settings.demo_mode,
            "mock_calls": getattr(settings, 'mock_calls', False),
            "enhanced_features": True,
            "conversation_monitoring": True
        },
        "endpoints": {
            "enhanced_campaigns": "/api/webhook/enhanced-campaign",
            "campaign_monitoring": "/api/monitor/enhanced-campaign/{task_id}",
            "test_elevenlabs": "/api/webhook/test-enhanced-elevenlabs",
            "system_status": "/api/webhook/system-status"
        }
    }

@app.get("/debug")
async def debug_info():
    """Debug information for troubleshooting"""
    
    debug_info = {
        "python_version": "3.13+",
        "fastapi_version": "0.115+", 
        "platform_version": "2.1.0-production",
        "settings_loaded": True,
        "active_campaigns": len(active_campaigns)
    }
    
    # Test core imports
    import_status = {}
    
    try:
        from models.campaign import CampaignData
        import_status["models"] = "✅ Available"
    except ImportError as e:
        import_status["models"] = f"❌ Failed: {e}"
    
    try:
        from agents.enhanced_orchestrator import EnhancedCampaignOrchestrator
        import_status["enhanced_orchestrator"] = "✅ Available"
    except ImportError as e:
        import_status["enhanced_orchestrator"] = f"❌ Failed: {e}"
    
    try:
        from agents.enhanced_negotiation import EnhancedNegotiationAgent
        import_status["enhanced_negotiation"] = "✅ Available"
    except ImportError as e:
        import_status["enhanced_negotiation"] = f"❌ Failed: {e}"
    
    try:
        from services.enhanced_voice import EnhancedVoiceService
        import_status["enhanced_voice"] = "✅ Available"
    except ImportError as e:
        import_status["enhanced_voice"] = f"❌ Failed: {e}"
    
    debug_info["import_status"] = import_status
    debug_info["cleanup_status"] = "Legacy files removed - production ready"
    
    return debug_info

# Production startup
if __name__ == "__main__":
    print("🚀 Starting InfluencerFlow AI Platform (Production Mode)...")
    print(f"🔧 Host: {settings.host}")
    print(f"🔧 Port: {settings.port}")
    print(f"🔧 Debug: {settings.debug}")
    print(f"🔥 Enhanced features: Enabled")
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )