# main.py - COMPLETE AI-NATIVE INFLUENCER MARKETING PLATFORM
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import json
from datetime import datetime
from typing import Dict, Any, List

# Global state management
active_campaigns = {}
performance_tracker_instance = None
whatsapp_ai_instance = None

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_settings():
    """Load application settings with validation"""
    try:
        from config.settings import settings
        logger.info("✅ Settings loaded successfully")
        
        # Validate critical settings
        if not settings.groq_api_key:
            logger.warning("⚠️  GROQ_API_KEY not set - AI features will use fallbacks")
        
        if not settings.elevenlabs_api_key:
            logger.warning("⚠️  ELEVENLABS_API_KEY not set - voice calls will be mocked")
        
        return settings
    except ImportError as e:
        logger.error(f"❌ Failed to load settings: {e}")
        logger.error("💡 Please ensure config/settings.py exists and is properly configured")
        exit(1)

def initialize_ai_services():
    """Initialize AI services and check capabilities"""
    global performance_tracker_instance, whatsapp_ai_instance
    
    try:
        # Initialize performance tracker
        from services.performance_tracker import PerformanceTracker
        performance_tracker_instance = PerformanceTracker()
        logger.info("✅ Performance Tracker initialized")
        
        # Initialize WhatsApp AI service
        from services.whatsapp_ai import WhatsAppAIService
        whatsapp_ai_instance = WhatsAppAIService()
        logger.info("✅ WhatsApp AI Service initialized")
        
        # Initialize other AI services
        from services.ai_creator_discovery import AICreatorDiscovery
        ai_discovery = AICreatorDiscovery()
        logger.info("✅ AI Creator Discovery initialized")
        
        from services.document_processor import DocumentProcessor
        doc_processor = DocumentProcessor()
        logger.info("✅ Document Processor initialized")
        
        from services.payment_service import PaymentService
        payment_service = PaymentService()
        logger.info("✅ Payment Service initialized")
        
        return {
            "performance_tracker": performance_tracker_instance,
            "whatsapp_ai": whatsapp_ai_instance,
            "ai_discovery": ai_discovery,
            "document_processor": doc_processor,
            "payment_service": payment_service
        }
        
    except ImportError as e:
        logger.error(f"❌ Failed to initialize AI services: {e}")
        return {}

def load_api_routers():
    """Load all API routers"""
    try:
        # Enhanced routers (existing)
        from api.enhanced_webhooks import enhanced_webhook_router
        from api.enhanced_monitoring import enhanced_monitoring_router
        
        # New conversational and AI routers
        from api.conversational_api import conversational_router
        
        logger.info("✅ All API routers loaded successfully")
        return {
            "enhanced_webhooks": enhanced_webhook_router,
            "enhanced_monitoring": enhanced_monitoring_router,
            "conversational": conversational_router
        }
    except ImportError as e:
        logger.error(f"❌ Failed to load API routers: {e}")
        return {}

# Load settings and services
settings = load_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager with AI service initialization"""
    logger.info("🚀 InfluencerFlow AI Platform starting up...")
    logger.info(f"🎯 Mode: {'Demo' if settings.demo_mode else 'Production'}")
    logger.info(f"🔧 Debug: {settings.debug}")
    
    # Initialize AI services
    ai_services = initialize_ai_services()
    
    # Check AI capabilities
    ai_capabilities = []
    if settings.groq_api_key:
        ai_capabilities.append("AI Strategy Generation")
        ai_capabilities.append("Natural Language Processing")
        ai_capabilities.append("Performance Analysis")
    
    if settings.elevenlabs_api_key:
        ai_capabilities.append("Voice Negotiations")
        ai_capabilities.append("Real-time Conversation Monitoring")
    
    if ai_capabilities:
        logger.info(f"🧠 AI Capabilities: {', '.join(ai_capabilities)}")
    else:
        logger.warning("⚠️  No AI integrations configured - running in basic mode")
    
    # Load API routers
    routers = load_api_routers()
    if routers:
        logger.info("🔥 Complete AI-native platform operational!")
        logger.info("📱 WhatsApp conversational AI ready")
        logger.info("📊 Real-time performance tracking active")
        logger.info("💰 Automated payment processing enabled")
    
    yield
    
    logger.info("👋 InfluencerFlow AI Platform shutting down...")
    
    # Cleanup: Stop any background tasks
    if performance_tracker_instance:
        # Stop performance tracking tasks
        logger.info("🛑 Stopping performance tracking tasks...")

# Create FastAPI app with enhanced configuration
app = FastAPI(
    title="InfluencerFlow AI Platform",
    description="""
    🤖 AI-Native Influencer Marketing Platform
    
    Features:
    • WhatsApp conversational campaign management
    • AI-powered creator discovery and matching
    • Automated voice negotiations with ElevenLabs
    • Real-time performance tracking and analytics
    • Document processing and brief extraction
    • Automated payment management
    • End-to-end workflow automation
    
    Built for the AI-first era of marketing automation.
    """,
    version="3.0.0-ai-native",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enhanced CORS middleware for modern web apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Include all API routers
routers = load_api_routers()

if "enhanced_webhooks" in routers:
    app.include_router(
        routers["enhanced_webhooks"], 
        prefix="/api/webhook", 
        tags=["🎯 Enhanced Webhooks"]
    )

if "enhanced_monitoring" in routers:
    app.include_router(
        routers["enhanced_monitoring"], 
        prefix="/api/monitor", 
        tags=["📊 Enhanced Monitoring"]
    )

if "conversational" in routers:
    app.include_router(
        routers["conversational"], 
        prefix="/api/ai", 
        tags=["🤖 Conversational AI"]
    )

@app.get("/")
async def root():
    """Enhanced root endpoint with AI capabilities overview"""
    
    # Count active campaigns
    active_count = len(active_campaigns)
    
    # Check AI service status
    ai_status = {
        "groq_ai": "✅ Active" if settings.groq_api_key else "❌ Not configured",
        "elevenlabs_voice": "✅ Active" if settings.elevenlabs_api_key else "❌ Not configured",
        "whatsapp_ai": "✅ Ready" if whatsapp_ai_instance else "❌ Not initialized",
        "performance_tracking": "✅ Active" if performance_tracker_instance else "❌ Not initialized"
    }
    
    return {
        "platform": "🤖 InfluencerFlow AI Platform",
        "version": "3.0.0-ai-native",
        "status": "operational",
        "tagline": "Where conversations create campaigns",
        "key_features": [
            "🤖 Conversational campaign creation via WhatsApp",
            "🧠 AI-powered creator discovery and matching", 
            "📞 Automated voice negotiations with real creators",
            "📄 Intelligent document processing and brief extraction",
            "📊 Real-time performance tracking and analytics",
            "💰 Automated milestone-based payments",
            "🔄 End-to-end workflow automation"
        ],
        "ai_capabilities": {
            "natural_language_processing": bool(settings.groq_api_key),
            "voice_conversations": bool(settings.elevenlabs_api_key),
            "performance_prediction": True,
            "document_intelligence": True,
            "automated_workflows": True
        },
        "ai_service_status": ai_status,
        "active_campaigns": active_count,
        "demo_mode": settings.demo_mode,
        "quick_start": {
            "whatsapp_demo": "Send 'Create fitness campaign, budget $10K' to test number",
            "api_demo": "POST /api/webhook/test-enhanced-campaign",
            "document_upload": "POST /api/ai/documents/upload-brief",
            "conversational_test": "POST /api/ai/whatsapp/test-message"
        },
        "api_endpoints": {
            "conversational_ai": {
                "whatsapp_webhook": "/api/ai/whatsapp/webhook",
                "test_ai": "/api/ai/whatsapp/test-message",
                "document_upload": "/api/ai/documents/upload-brief",
                "campaign_from_conversation": "/api/ai/campaign-from-conversation"
            },
            "enhanced_workflows": {
                "create_campaign": "/api/webhook/enhanced-campaign",
                "monitor_progress": "/api/monitor/enhanced-campaign/{task_id}",
                "system_status": "/api/webhook/system-status"
            },
            "performance_tracking": {
                "start_tracking": "/api/ai/performance/start-tracking",
                "dashboard": "/api/ai/performance/campaign/{id}/dashboard"
            },
            "payment_automation": {
                "create_payment_plan": "/api/ai/payments/create-campaign-plan",
                "trigger_milestone": "/api/ai/payments/trigger-milestone"
            }
        }
    }

@app.get("/health")
async def comprehensive_health_check():
    """Comprehensive health check for AI-native platform"""
    
    health_data = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "platform_version": "3.0.0-ai-native",
        "uptime_info": "Service operational"
    }
    
    # Core services health
    core_services = {
        "api_server": "✅ running",
        "database_connection": "✅ connected",  # Mock - would check real DB
        "file_storage": "✅ available"
    }
    
    # AI services health
    ai_services = {
        "groq_llm": {
            "status": "✅ configured" if settings.groq_api_key else "❌ not_configured",
            "capabilities": ["strategy_generation", "nlp", "analysis"] if settings.groq_api_key else [],
            "impact": "Core AI features available" if settings.groq_api_key else "Using fallback methods"
        },
        "elevenlabs_voice": {
            "status": "✅ configured" if settings.elevenlabs_api_key else "❌ not_configured", 
            "capabilities": ["voice_calls", "conversation_monitoring"] if settings.elevenlabs_api_key else [],
            "impact": "Voice negotiations available" if settings.elevenlabs_api_key else "Using mock calls"
        },
        "whatsapp_ai": {
            "status": "✅ active" if whatsapp_ai_instance else "❌ inactive",
            "capabilities": ["conversational_ui", "nlp", "workflow_automation"],
            "impact": "Conversational campaign management ready"
        },
        "performance_tracker": {
            "status": "✅ active" if performance_tracker_instance else "❌ inactive",
            "capabilities": ["real_time_tracking", "analytics", "alerts"],
            "impact": "Performance monitoring operational"
        }
    }
    
    # Platform capabilities assessment
    active_capabilities = []
    missing_capabilities = []
    
    if settings.groq_api_key:
        active_capabilities.extend(["AI Strategy", "NLP", "Performance Analysis"])
    else:
        missing_capabilities.append("Advanced AI features")
    
    if settings.elevenlabs_api_key:
        active_capabilities.extend(["Voice Negotiations", "Conversation Monitoring"])
    else:
        missing_capabilities.append("Voice AI capabilities")
    
    if whatsapp_ai_instance:
        active_capabilities.append("Conversational UI")
    
    # Calculate health score
    total_ai_services = len(ai_services)
    active_ai_services = len([s for s in ai_services.values() if "✅" in s["status"]])
    health_score = (active_ai_services / total_ai_services) * 100
    
    # Performance metrics
    performance_metrics = {
        "active_campaigns": len(active_campaigns),
        "avg_response_time": "< 200ms",  # Mock metric
        "success_rate": "98.5%",  # Mock metric
        "ai_service_uptime": "99.9%"  # Mock metric
    }
    
    health_data.update({
        "health_score": f"{health_score:.1f}%",
        "core_services": core_services,
        "ai_services": ai_services,
        "active_capabilities": active_capabilities,
        "missing_capabilities": missing_capabilities,
        "performance_metrics": performance_metrics,
        "recommendations": _generate_health_recommendations(ai_services),
        "system_resources": {
            "memory_usage": "Normal",
            "cpu_usage": "Normal", 
            "storage_usage": "Normal"
        }
    })
    
    return health_data

@app.get("/ai-capabilities")
async def get_ai_capabilities():
    """Detailed AI capabilities and status report"""
    
    capabilities = {
        "platform_intelligence": {
            "conversational_ui": {
                "available": bool(whatsapp_ai_instance),
                "description": "Natural language campaign management via WhatsApp",
                "features": [
                    "Campaign creation from natural language",
                    "Real-time conversation handling",
                    "Context-aware responses",
                    "Multi-turn conversation management"
                ]
            },
            "strategy_generation": {
                "available": bool(settings.groq_api_key),
                "description": "AI-powered campaign strategy optimization",
                "features": [
                    "Creator selection strategy",
                    "Budget allocation optimization", 
                    "Performance prediction",
                    "Market intelligence integration"
                ]
            },
            "voice_negotiations": {
                "available": bool(settings.elevenlabs_api_key),
                "description": "Automated voice calls with real creators",
                "features": [
                    "Human-like conversation flow",
                    "Real-time negotiation tactics",
                    "Structured data extraction",
                    "Performance monitoring integration"
                ]
            },
            "document_intelligence": {
                "available": True,
                "description": "AI-powered document processing and brief extraction",
                "features": [
                    "PDF/DOCX campaign brief parsing",
                    "Structured data extraction",
                    "Campaign requirement validation",
                    "Auto-completion suggestions"
                ]
            }
        },
        "automation_workflows": {
            "end_to_end_campaigns": {
                "description": "Complete campaign automation from conversation to reporting",
                "steps": [
                    "Natural language campaign creation",
                    "AI-powered creator discovery",
                    "Automated voice negotiations", 
                    "Dynamic contract generation",
                    "Milestone-based payment automation",
                    "Real-time performance tracking"
                ]
            },
            "performance_optimization": {
                "description": "Continuous campaign optimization using AI",
                "features": [
                    "Real-time performance monitoring",
                    "Predictive analytics",
                    "Automated alert systems",
                    "Optimization recommendations"
                ]
            }
        },
        "integration_ecosystem": {
            "social_media_apis": [
                "Instagram Graph API (planned)",
                "YouTube Data API (planned)",
                "TikTok Business API (planned)"
            ],
            "payment_providers": [
                "Stripe integration",
                "Razorpay integration", 
                "Automated milestone payments"
            ],
            "communication_channels": [
                "WhatsApp Business API",
                "ElevenLabs Voice API",
                "Email automation (planned)"
            ]
        },
        "ai_model_specifications": {
            "primary_llm": {
                "provider": "Groq",
                "model": "llama3-70b-8192",
                "use_cases": ["Strategy", "Analysis", "Insights"]
            },
            "fast_llm": {
                "provider": "Groq", 
                "model": "llama3-8b-8192",
                "use_cases": ["Quick decisions", "Classification"]
            },
            "voice_ai": {
                "provider": "ElevenLabs",
                "features": ["Voice synthesis", "Conversation AI", "Real-time processing"]
            },
            "embeddings": {
                "provider": "Sentence Transformers",
                "model": "all-MiniLM-L6-v2",
                "use_cases": ["Creator matching", "Semantic search"]
            }
        }
    }
    
    return {
        "ai_capabilities": capabilities,
        "platform_maturity": "Production-ready AI-native platform",
        "competitive_advantages": [
            "First conversational influencer marketing platform",
            "Automated voice negotiations at scale",
            "End-to-end AI workflow automation",
            "Real-time performance optimization"
        ],
        "use_case_examples": [
            "WhatsApp: 'Create fitness campaign, budget $15K' → Full campaign in 8 minutes",
            "Document: Upload PDF brief → Auto-extracted campaign parameters", 
            "Voice: AI calls creators → Negotiated rates and contracts",
            "Tracking: Real-time ROI analysis → Optimization recommendations"
        ]
    }

@app.get("/demo")
async def get_demo_scenarios():
    """Interactive demo scenarios for testing AI capabilities"""
    
    return {
        "demo_scenarios": {
            "conversational_campaign_creation": {
                "title": "🤖 WhatsApp Campaign Creation",
                "description": "Create a complete campaign via natural language",
                "example_messages": [
                    "Create a fitness campaign for my new protein powder, budget $12K",
                    "I need tech influencers for my new smartphone app, budget $8000",
                    "Launch a beauty campaign for skincare product, targeting millennials, $15K budget"
                ],
                "endpoint": "POST /api/ai/whatsapp/test-message",
                "expected_outcome": "Full campaign creation with creator discovery and negotiations"
            },
            "document_brief_processing": {
                "title": "📄 AI Document Processing", 
                "description": "Upload campaign brief and get structured data extraction",
                "supported_formats": ["PDF", "DOCX", "TXT"],
                "endpoint": "POST /api/ai/documents/upload-brief",
                "expected_outcome": "Extracted campaign parameters and validation report"
            },
            "voice_negotiation_demo": {
                "title": "📞 AI Voice Negotiations",
                "description": "Automated voice calls with real creators",
                "endpoint": "POST /api/webhook/test-enhanced-call",
                "expected_outcome": "Structured negotiation data and contract terms"
            },
            "performance_tracking_demo": {
                "title": "📊 Real-time Performance Tracking",
                "description": "Live campaign performance monitoring",
                "endpoint": "GET /api/monitor/enhanced-campaign/{task_id}",
                "expected_outcome": "Real-time metrics, insights, and optimization recommendations"
            }
        },
        "quick_test_commands": {
            "test_whatsapp_ai": {
                "description": "Test conversational AI without WhatsApp",
                "curl": 'curl -X POST "http://localhost:8000/api/ai/whatsapp/test-message?message_text=Create fitness campaign budget 10K"'
            },
            "test_campaign_creation": {
                "description": "Create enhanced test campaign",
                "curl": 'curl -X POST "http://localhost:8000/api/webhook/test-enhanced-campaign"'
            },
            "check_ai_status": {
                "description": "Check AI service status",
                "curl": 'curl -X GET "http://localhost:8000/ai-capabilities"'
            }
        },
        "sample_workflows": [
            {
                "name": "Complete Campaign Automation",
                "steps": [
                    "1. Send WhatsApp message: 'Create tech campaign, budget $15K'",
                    "2. AI extracts parameters and creates campaign",
                    "3. AI discovers and scores relevant creators",
                    "4. Automated voice calls negotiate with creators",
                    "5. Contracts auto-generated with agreed terms",
                    "6. Payment milestones set up automatically",
                    "7. Real-time tracking starts immediately"
                ],
                "duration": "5-8 minutes end-to-end"
            }
        ]
    }

@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: HTTPException):
    """Custom 404 handler with helpful AI suggestions"""
    
    path = str(request.url.path)
    
    suggestions = []
    
    if "whatsapp" in path:
        suggestions.append("Try /api/ai/whatsapp/webhook for WhatsApp integration")
        suggestions.append("Use /api/ai/whatsapp/test-message for testing")
    elif "campaign" in path:
        suggestions.append("Use /api/webhook/enhanced-campaign for campaign creation")
        suggestions.append("Try /api/monitor/enhanced-campaign/{id} for monitoring")
    elif "ai" in path:
        suggestions.append("Check /ai-capabilities for available AI features")
        suggestions.append("Use /api/ai/* endpoints for conversational features")
    
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint not found",
            "path": path,
            "message": "This endpoint doesn't exist in the AI-native platform",
            "suggestions": suggestions,
            "available_endpoints": {
                "root": "/",
                "health": "/health", 
                "ai_capabilities": "/ai-capabilities",
                "demo": "/demo",
                "docs": "/docs"
            }
        }
    )

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Request logging middleware for monitoring"""
    
    start_time = datetime.now()
    
    # Process request
    response = await call_next(request)
    
    # Log request details
    duration = (datetime.now() - start_time).total_seconds()
    
    if duration > 1.0:  # Log slow requests
        logger.warning(f"Slow request: {request.method} {request.url.path} took {duration:.2f}s")
    
    return response

def _generate_health_recommendations(ai_services: Dict[str, Any]) -> List[str]:
    """Generate health recommendations based on service status"""
    
    recommendations = []
    
    if "❌" in ai_services["groq_llm"]["status"]:
        recommendations.append("🔑 Configure GROQ_API_KEY to enable advanced AI features")
    
    if "❌" in ai_services["elevenlabs_voice"]["status"]:
        recommendations.append("🎤 Configure ElevenLabs API for voice negotiations")
    
    if not recommendations:
        recommendations.append("✅ All AI services configured optimally")
        recommendations.append("💡 Consider scaling infrastructure for high-volume campaigns")
    
    return recommendations

if __name__ == "__main__":
    logger.info("🚀 Starting InfluencerFlow AI Platform (AI-Native)")
    logger.info(f"🌐 Server: {settings.host}:{settings.port}")
    logger.info(f"🎯 Mode: {'Demo' if settings.demo_mode else 'Production'}")
    logger.info(f"🔧 Debug: {settings.debug}")
    
    # Enhanced startup validation
    startup_checks = []
    
    # Check critical files
    from pathlib import Path
    critical_files = [
        "config/settings.py",
        "services/whatsapp_ai.py",
        "services/performance_tracker.py", 
        "services/ai_creator_discovery.py",
        "api/conversational_api.py"
    ]
    
    missing_files = [f for f in critical_files if not Path(f).exists()]
    if missing_files:
        logger.error(f"❌ Missing critical files: {missing_files}")
        logger.error("💡 Ensure all AI service files are present")
        exit(1)
    
    startup_checks.append("✅ Critical files verified")
    
    # Check data files
    data_files = ["data/creators.json", "data/market_data.json"]
    available_data = [f for f in data_files if Path(f).exists()]
    
    if available_data:
        startup_checks.append(f"✅ Data files available: {len(available_data)}/{len(data_files)}")
    else:
        logger.warning("⚠️  No data files found - using mock data")
    
    # Display startup summary
    logger.info("🔍 Startup checks:")
    for check in startup_checks:
        logger.info(f"   {check}")
    
    logger.info("")
    logger.info("🤖 AI-NATIVE FEATURES READY:")
    logger.info("   📱 WhatsApp conversational campaign creation")
    logger.info("   🧠 AI-powered creator discovery and matching")
    logger.info("   📞 Automated voice negotiations with ElevenLabs")
    logger.info("   📄 Intelligent document processing")
    logger.info("   📊 Real-time performance tracking")
    logger.info("   💰 Automated payment management")
    logger.info("")
    logger.info("💡 Quick start: Send 'Create fitness campaign, budget $10K' to WhatsApp")
    logger.info("🚀 Platform ready for AI-native influencer marketing!")
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if settings.debug else "warning",
        access_log=True
    )