# main.py - UPDATED VERSION with Better Import Handling and Enhanced Features
import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

# Global state to track active campaigns
active_campaigns = {}

def load_settings():
    """Load settings with proper fallback handling"""
    try:
        from config.settings import settings
        print("✅ Settings loaded successfully")
        return settings
    except ImportError as e:
        print(f"❌ Settings import failed: {e}")
        print("📋 Please ensure config/settings.py exists and dependencies are installed")
        exit(1)

def load_enhanced_endpoints():
    """Load enhanced endpoints with graceful fallback"""
    try:
        from api.enhanced_webhooks import enhanced_webhook_router
        from api.enhanced_monitoring import enhanced_monitoring_router
        print("✅ Enhanced endpoints loaded")
        return enhanced_webhook_router, enhanced_monitoring_router
    except ImportError as e:
        print(f"⚠️ Enhanced endpoints not available: {e}")
        return None, None

def load_legacy_endpoints():
    """Load legacy endpoints if available"""
    try:
        from api.webhooks import webhook_router
        from api.monitoring import monitoring_router
        print("✅ Legacy endpoints loaded")
        return webhook_router, monitoring_router
    except ImportError as e:
        print(f"⚠️ Legacy endpoints not available: {e}")
        return None, None

def load_enhanced_campaign_endpoints():
    """Load enhanced campaign endpoints"""
    try:
        from api.enhanced_campaign_endpoints import enhanced_campaign_router
        print("✅ Enhanced campaign endpoints loaded")
        return enhanced_campaign_router
    except ImportError as e:
        print(f"⚠️ Enhanced campaign endpoints not available: {e}")
        return None

# Load settings
settings = load_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager with comprehensive startup"""
    print("🚀 InfluencerFlow AI Platform starting up...")
    print(f"🔧 Debug mode: {settings.debug}")
    print(f"🎯 Demo mode: {settings.demo_mode}")
    
    # System status summary
    system_status = {
        "enhanced_endpoints": False,
        "legacy_endpoints": False,
        "enhanced_campaigns": False,
        "groq_configured": bool(getattr(settings, 'groq_api_key', None)),
        "elevenlabs_configured": bool(getattr(settings, 'elevenlabs_api_key', None))
    }
    
    # Try to load enhanced features
    enhanced_webhook_router, enhanced_monitoring_router = load_enhanced_endpoints()
    if enhanced_webhook_router and enhanced_monitoring_router:
        system_status["enhanced_endpoints"] = True
        print("🔥 Enhanced webhook & monitoring endpoints available!")
    
    # Try to load legacy features
    legacy_webhook_router, legacy_monitoring_router = load_legacy_endpoints()
    if legacy_webhook_router and legacy_monitoring_router:
        system_status["legacy_endpoints"] = True
        print("📋 Legacy endpoints available!")
    
    # Try to load enhanced campaign endpoints
    enhanced_campaign_router = load_enhanced_campaign_endpoints()
    if enhanced_campaign_router:
        system_status["enhanced_campaigns"] = True
        print("🎯 Enhanced campaign endpoints available!")
    
    # Print system capabilities
    print("\n📊 System Capabilities:")
    for capability, available in system_status.items():
        status = "✅ Available" if available else "❌ Not Available"
        print(f"   {capability}: {status}")
    
    print(f"\n🌐 Server will be available at: http://{settings.host}:{settings.port}")
    print("🔗 API Documentation: http://localhost:8000/docs")
    print("🔗 Alternative Docs: http://localhost:8000/redoc")
    
    yield
    
    print("👋 InfluencerFlow AI Platform shutting down...")
    print(f"📊 Total campaigns processed: {len(active_campaigns)}")

# Create FastAPI app with enhanced configuration
app = FastAPI(
    title="InfluencerFlow AI Platform",
    description="""
    🤖 AI-Powered Influencer Marketing Campaign Automation Platform
    
    **Key Features:**
    - Enhanced ElevenLabs voice negotiations with dynamic variables
    - Real-time conversation monitoring and analysis
    - Intelligent creator discovery and matching
    - Automated contract generation and delivery
    - Human-in-the-loop approval workflows
    - Comprehensive analytics and reporting
    
    **API Versions:**
    - Enhanced API (v2.0): `/api/enhanced/` - Latest features with full automation
    - Legacy API (v1.0): `/api/webhook/` - Backward compatibility
    
    **Quick Start:**
    1. Test system: `GET /health`
    2. Create campaign: `POST /api/enhanced/start-enhanced-workflow`
    3. Monitor progress: `GET /api/enhanced/workflow/{workflow_id}/status`
    """,
    version="2.0.0-enhanced",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware with proper configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with error handling
def safe_include_router(router, prefix: str, tags: list, name: str):
    """Safely include router with error handling"""
    if router:
        try:
            app.include_router(router, prefix=prefix, tags=tags)
            print(f"✅ {name} included at {prefix}")
        except Exception as e:
            print(f"❌ Failed to include {name}: {e}")
    else:
        print(f"⚠️ {name} not available")

# Try to include all available routers
enhanced_webhook_router, enhanced_monitoring_router = load_enhanced_endpoints()
safe_include_router(enhanced_webhook_router, "/api/webhook", ["enhanced-webhooks"], "Enhanced Webhooks")
safe_include_router(enhanced_monitoring_router, "/api/monitor", ["enhanced-monitoring"], "Enhanced Monitoring")

legacy_webhook_router, legacy_monitoring_router = load_legacy_endpoints()
safe_include_router(legacy_webhook_router, "/api/legacy/webhook", ["legacy-webhooks"], "Legacy Webhooks")
safe_include_router(legacy_monitoring_router, "/api/legacy/monitor", ["legacy-monitoring"], "Legacy Monitoring")

enhanced_campaign_router = load_enhanced_campaign_endpoints()
safe_include_router(enhanced_campaign_router, "/api/enhanced", ["enhanced-campaigns"], "Enhanced Campaign Endpoints")

# Core API endpoints
@app.get("/", tags=["core"])
async def root():
    """🏠 Root endpoint with system overview"""
    
    # Count active campaigns by type
    enhanced_count = len([c for c in active_campaigns.values() 
                         if getattr(c.campaign_data, 'campaign_code', '').startswith('EFC-')])
    legacy_count = len(active_campaigns) - enhanced_count
    
    return {
        "message": "🤖 InfluencerFlow AI Platform",
        "version": "2.0.0-enhanced",
        "status": "operational",
        "features": {
            "enhanced_workflows": True,
            "voice_negotiations": True,
            "ai_strategy_generation": True,
            "real_time_monitoring": True,
            "automated_contracts": True,
            "human_approval_workflows": True
        },
        "active_campaigns": {
            "total": len(active_campaigns),
            "enhanced": enhanced_count,
            "legacy": legacy_count
        },
        "api_endpoints": {
            "enhanced_api": "/api/enhanced/",
            "legacy_api": "/api/webhook/",
            "monitoring": "/api/monitor/",
            "documentation": "/docs",
            "health_check": "/health"
        },
        "quick_start": {
            "test_system": "GET /health",
            "create_campaign": "POST /api/enhanced/start-enhanced-workflow",
            "monitor_progress": "GET /api/enhanced/workflow/{workflow_id}/status"
        }
    }

@app.get("/health", tags=["core"])
async def health_check():
    """🏥 Comprehensive health check"""
    
    # Check service availability
    services = {
        "api": "running",
        "database": "mock",  # Would be actual DB check in production
        "active_campaigns": len(active_campaigns)
    }
    
    # Check API keys and configuration
    config_status = {}
    
    if hasattr(settings, 'groq_api_key') and settings.groq_api_key:
        config_status["groq"] = "configured"
    else:
        config_status["groq"] = "missing_key"
    
    if hasattr(settings, 'elevenlabs_api_key') and settings.elevenlabs_api_key:
        config_status["elevenlabs"] = "configured"
    else:
        config_status["elevenlabs"] = "missing_key"
    
    # Test enhanced services
    enhanced_services = {}
    
    try:
        from services.enhanced_voice import EnhancedVoiceService
        voice_service = EnhancedVoiceService()
        enhanced_services["enhanced_voice"] = "available"
    except ImportError:
        enhanced_services["enhanced_voice"] = "not_available"
    
    try:
        from agents.enhanced_orchestrator import EnhancedCampaignOrchestrator
        enhanced_services["enhanced_orchestrator"] = "available"
    except ImportError:
        enhanced_services["enhanced_orchestrator"] = "not_available"
    
    return {
        "status": "healthy",
        "timestamp": "2024-12-19T10:30:00Z",
        "version": "2.0.0-enhanced",
        "services": services,
        "configuration": config_status,
        "enhanced_services": enhanced_services,
        "settings": {
            "demo_mode": settings.demo_mode,
            "mock_calls": getattr(settings, 'mock_calls', False),
            "debug": settings.debug,
            "host": settings.host,
            "port": settings.port
        },
        "capabilities": {
            "elevenlabs_integration": config_status["elevenlabs"] == "configured",
            "groq_ai_strategy": config_status["groq"] == "configured",
            "enhanced_workflows": enhanced_services.get("enhanced_orchestrator") == "available",
            "voice_negotiations": enhanced_services.get("enhanced_voice") == "available"
        }
    }

@app.get("/debug", tags=["core"])
async def debug_info():
    """🔍 Debug information for troubleshooting"""
    
    debug_info = {
        "python_version": "3.13+",
        "fastapi_version": "0.115+",
        "settings_loaded": True,
        "active_campaigns": len(active_campaigns),
        "environment": {
            "demo_mode": settings.demo_mode,
            "debug": settings.debug,
            "host": settings.host,
            "port": settings.port
        }
    }
    
    # Check imports with detailed error reporting
    import_status = {}
    
    # Test core models
    try:
        from models.campaign import CampaignWebhook, CampaignData, CampaignOrchestrationState
        import_status["models"] = "✅ Available"
    except ImportError as e:
        import_status["models"] = f"❌ Failed: {e}"
    
    # Test enhanced orchestrator
    try:
        from agents.enhanced_orchestrator import EnhancedCampaignOrchestrator
        import_status["enhanced_orchestrator"] = "✅ Available"
    except ImportError as e:
        import_status["enhanced_orchestrator"] = f"❌ Failed: {e}"
    
    # Test enhanced voice service
    try:
        from services.enhanced_voice import EnhancedVoiceService
        import_status["enhanced_voice"] = "✅ Available"
    except ImportError as e:
        import_status["enhanced_voice"] = f"❌ Failed: {e}"
    
    # Test other services
    try:
        from services.embeddings import EmbeddingService
        import_status["embeddings"] = "✅ Available"
    except ImportError as e:
        import_status["embeddings"] = f"❌ Failed: {e}"
    
    try:
        from services.pricing import PricingService
        import_status["pricing"] = "✅ Available"
    except ImportError as e:
        import_status["pricing"] = f"❌ Failed: {e}"
    
    debug_info["import_status"] = import_status
    
    # Add troubleshooting recommendations
    failed_imports = [k for k, v in import_status.items() if "❌" in v]
    
    if failed_imports:
        debug_info["troubleshooting"] = {
            "failed_imports": failed_imports,
            "recommendations": [
                "Run: python -m pip install -r requirements.txt",
                "Check if all Python files are present",
                "Verify Python path and virtual environment",
                "Run: python fix_imports.py (if available)"
            ]
        }
    else:
        debug_info["troubleshooting"] = {
            "status": "All imports successful",
            "recommendations": ["System ready for use"]
        }
    
    return debug_info

@app.get("/system-overview", tags=["core"])
async def system_overview():
    """📊 Comprehensive system overview"""
    
    # Analyze active campaigns
    campaign_stats = {
        "total": len(active_campaigns),
        "by_stage": {},
        "by_type": {"enhanced": 0, "legacy": 0},
        "success_metrics": {"total_successful": 0, "total_failed": 0}
    }
    
    for campaign_state in active_campaigns.values():
        # Count by stage
        stage = getattr(campaign_state, 'current_stage', 'unknown')
        campaign_stats["by_stage"][stage] = campaign_stats["by_stage"].get(stage, 0) + 1
        
        # Count by type
        is_enhanced = getattr(campaign_state.campaign_data, 'campaign_code', '').startswith('EFC-')
        if is_enhanced:
            campaign_stats["by_type"]["enhanced"] += 1
        else:
            campaign_stats["by_type"]["legacy"] += 1
        
        # Success metrics
        if hasattr(campaign_state, 'successful_negotiations'):
            campaign_stats["success_metrics"]["total_successful"] += campaign_state.successful_negotiations
        if hasattr(campaign_state, 'failed_negotiations'):
            campaign_stats["success_metrics"]["total_failed"] += campaign_state.failed_negotiations
    
    return {
        "platform": "InfluencerFlow AI",
        "version": "2.0.0-enhanced",
        "status": "operational",
        "uptime": "Active",
        "campaign_statistics": campaign_stats,
        "system_capabilities": {
            "enhanced_workflows": True,
            "voice_negotiations": bool(getattr(settings, 'elevenlabs_api_key', None)),
            "ai_strategy_generation": bool(getattr(settings, 'groq_api_key', None)),
            "automated_contracts": True,
            "real_time_monitoring": True,
            "human_approval_workflows": True
        },
        "api_health": {
            "enhanced_endpoints": "/api/enhanced/",
            "monitoring_endpoints": "/api/monitor/",
            "legacy_endpoints": "/api/webhook/",
            "documentation": "/docs"
        },
        "configuration": {
            "demo_mode": settings.demo_mode,
            "mock_calls": getattr(settings, 'mock_calls', False),
            "debug_mode": settings.debug
        }
    }

@app.get("/api-status", tags=["core"])
async def api_status():
    """🔌 API endpoints status check"""
    
    endpoints_status = {}
    
    # Check if enhanced endpoints are available
    try:
        enhanced_webhook_router, enhanced_monitoring_router = load_enhanced_endpoints()
        endpoints_status["enhanced_webhooks"] = "✅ Available" if enhanced_webhook_router else "❌ Not Available"
        endpoints_status["enhanced_monitoring"] = "✅ Available" if enhanced_monitoring_router else "❌ Not Available"
    except Exception as e:
        endpoints_status["enhanced_endpoints"] = f"❌ Error: {e}"
    
    # Check enhanced campaign endpoints
    try:
        enhanced_campaign_router = load_enhanced_campaign_endpoints()
        endpoints_status["enhanced_campaigns"] = "✅ Available" if enhanced_campaign_router else "❌ Not Available"
    except Exception as e:
        endpoints_status["enhanced_campaigns"] = f"❌ Error: {e}"
    
    # Check legacy endpoints
    try:
        legacy_webhook_router, legacy_monitoring_router = load_legacy_endpoints()
        endpoints_status["legacy_webhooks"] = "✅ Available" if legacy_webhook_router else "❌ Not Available"
        endpoints_status["legacy_monitoring"] = "✅ Available" if legacy_monitoring_router else "❌ Not Available"
    except Exception as e:
        endpoints_status["legacy_endpoints"] = f"❌ Error: {e}"
    
    return {
        "api_status": "operational",
        "endpoints": endpoints_status,
        "available_routes": {
            "core": ["/", "/health", "/debug", "/system-overview"],
            "enhanced": [
                "/api/enhanced/start-enhanced-workflow",
                "/api/enhanced/workflow/{id}/status",
                "/api/enhanced/human-reviews",
                "/api/enhanced/contracts"
            ],
            "monitoring": [
                "/api/monitor/enhanced-campaign/{id}",
                "/api/monitor/enhanced-campaigns"
            ],
            "webhooks": [
                "/api/webhook/enhanced-campaign",
                "/api/webhook/test-enhanced-campaign"
            ]
        },
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_schema": "/openapi.json"
        }
    }

if __name__ == "__main__":
    print("🚀 Starting InfluencerFlow AI Platform...")
    print(f"🔧 Configuration:")
    print(f"   Host: {settings.host}")
    print(f"   Port: {settings.port}")
    print(f"   Debug: {settings.debug}")
    print(f"   Demo Mode: {settings.demo_mode}")
    
    # Print feature availability
    print(f"\n🎯 Feature Status:")
    print(f"   Groq AI: {'✅ Configured' if getattr(settings, 'groq_api_key', None) else '❌ Not Configured'}")
    print(f"   ElevenLabs: {'✅ Configured' if getattr(settings, 'elevenlabs_api_key', None) else '❌ Not Configured'}")
    
    print(f"\n📚 After startup, visit:")
    print(f"   API Documentation: http://{settings.host}:{settings.port}/docs")
    print(f"   Health Check: http://{settings.host}:{settings.port}/health")
    print(f"   System Overview: http://{settings.host}:{settings.port}/system-overview")
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug"
    )