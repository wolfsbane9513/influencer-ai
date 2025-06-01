# main.py - Enhanced InfluencerFlow AI Platform
import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config.settings import settings

# Import API routers
try:
    # Enhanced routers (new)
    from api.enhanced_webhooks import enhanced_webhook_router
    from api.enhanced_monitoring import enhanced_monitoring_router
    ENHANCED_AVAILABLE = True
    print("✅ Enhanced endpoints loaded")
except ImportError as e:
    print(f"⚠️  Enhanced endpoints not available: {e}")
    ENHANCED_AVAILABLE = False

try:
    # Legacy routers (existing)
    from api.webhooks import webhook_router
    from api.monitoring import monitoring_router
    LEGACY_AVAILABLE = True
    print("✅ Legacy endpoints loaded")
except ImportError as e:
    print(f"⚠️  Legacy endpoints not available: {e}")
    LEGACY_AVAILABLE = False

# Global state to track active campaigns
active_campaigns = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    print("🚀 InfluencerFlow AI Platform starting up...")
    print(f"🔧 Debug mode: {settings.debug}")
    print(f"🎯 Demo mode: {settings.demo_mode}")
    
    if ENHANCED_AVAILABLE:
        print("🔥 Enhanced features available!")
    if LEGACY_AVAILABLE:
        print("📋 Legacy endpoints available!")
        
    yield
    print("👋 InfluencerFlow AI Platform shutting down...")

# Create FastAPI app
app = FastAPI(
    title="InfluencerFlow AI Platform",
    description="AI-powered influencer marketing campaign automation with enhanced ElevenLabs integration",
    version="2.0.0-enhanced" if ENHANCED_AVAILABLE else "1.0.0",
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

# Include routers based on availability
if ENHANCED_AVAILABLE:
    app.include_router(enhanced_webhook_router, prefix="/api/webhook", tags=["enhanced-webhooks"])
    app.include_router(enhanced_monitoring_router, prefix="/api/monitor", tags=["enhanced-monitoring"])

if LEGACY_AVAILABLE:
    # Legacy endpoints with different prefix to avoid conflicts
    app.include_router(webhook_router, prefix="/api/legacy/webhook", tags=["legacy-webhooks"])
    app.include_router(monitoring_router, prefix="/api/legacy/monitor", tags=["legacy-monitoring"])

@app.get("/")
async def root():
    """Enhanced health check endpoint"""
    
    available_features = []
    available_endpoints = {}
    
    if ENHANCED_AVAILABLE:
        available_features.extend([
            "🔥 Enhanced ElevenLabs integration",
            "🎯 AI-powered negotiation strategies", 
            "📊 Structured conversation analysis",
            "📝 Comprehensive contract generation"
        ])
        available_endpoints.update({
            "enhanced_campaign": "/api/webhook/enhanced-campaign",
            "test_enhanced": "/api/webhook/test-enhanced-campaign",
            "enhanced_monitoring": "/api/monitor/enhanced-campaigns",
            "system_status": "/api/webhook/system-status"
        })
    
    if LEGACY_AVAILABLE:
        available_features.append("📋 Legacy endpoints (backward compatibility)")
        available_endpoints.update({
            "legacy_campaign": "/api/legacy/webhook/campaign-created",
            "test_legacy": "/api/legacy/webhook/test-campaign",
            "legacy_monitoring": "/api/legacy/monitor/campaigns"
        })
    
    return {
        "message": "InfluencerFlow AI Platform is running",
        "version": "2.0.0-enhanced" if ENHANCED_AVAILABLE else "1.0.0",
        "status": "healthy",
        "demo_mode": settings.demo_mode,
        "active_campaigns": len(active_campaigns),
        "available_features": available_features,
        "available_endpoints": available_endpoints,
        "integration_status": {
            "enhanced_system": "✅ Available" if ENHANCED_AVAILABLE else "❌ Not loaded",
            "legacy_system": "✅ Available" if LEGACY_AVAILABLE else "❌ Not loaded",
            "groq_ai": "✅ Configured" if settings.groq_api_key else "⚠️  Missing API key",
            "elevenlabs": "✅ Configured" if settings.elevenlabs_api_key else "⚠️  Missing API key"
        }
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    
    services = {
        "api": "running",
        "database": "connected",  # TODO: Add actual DB health check
    }
    
    if settings.groq_api_key:
        services["groq"] = "configured"
    else:
        services["groq"] = "missing_key"
        
    if settings.elevenlabs_api_key:
        services["elevenlabs"] = "configured"
    else:
        services["elevenlabs"] = "missing_key"
    
    return {
        "status": "healthy",
        "version": "2.0.0-enhanced" if ENHANCED_AVAILABLE else "1.0.0",
        "services": services,
        "active_campaigns": len(active_campaigns),
        "settings": {
            "demo_mode": settings.demo_mode,
            "mock_calls": settings.mock_calls,
            "max_negotiation_duration": settings.max_negotiation_duration
        },
        "features": {
            "enhanced_available": ENHANCED_AVAILABLE,
            "legacy_available": LEGACY_AVAILABLE
        }
    }

@app.get("/api/status")
async def api_status():
    """API status endpoint"""
    return {
        "api_status": "operational",
        "enhanced_features": ENHANCED_AVAILABLE,
        "legacy_features": LEGACY_AVAILABLE,
        "timestamp": "2024-12-22T00:00:00Z"
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Endpoint not found",
        "message": "Check available endpoints at /",
        "available_systems": {
            "enhanced": ENHANCED_AVAILABLE,
            "legacy": LEGACY_AVAILABLE
        }
    }

if __name__ == "__main__":
    print(f"🚀 Starting InfluencerFlow AI Platform...")
    print(f"🔧 Host: {settings.host}")
    print(f"🔧 Port: {settings.port}")
    print(f"🔧 Debug: {settings.debug}")
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )