# main.py
import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Try to import settings, fallback to simple version
try:
    from config.settings import settings
    print("✅ Using pydantic Settings")
except ImportError as e:
    print(f"⚠️  Pydantic settings failed: {e}")
    try:
        from config.simple_settings import settings
        print("✅ Using SimpleSettings fallback")
    except ImportError as e2:
        print(f"❌ Both settings failed: {e2}")
        print("📋 Please run: python fix_imports.py")
        exit(1)
from api.webhooks import webhook_router
from api.monitoring import monitoring_router

# Global state to track active campaigns
active_campaigns = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    print("🚀 InfluencerFlow AI Platform starting up...")
    print(f"🔧 Debug mode: {settings.debug}")
    print(f"🎯 Demo mode: {settings.demo_mode}")
    yield
    print("👋 InfluencerFlow AI Platform shutting down...")

# Create FastAPI app
app = FastAPI(
    title="InfluencerFlow AI Platform",
    description="AI-powered influencer marketing campaign automation",
    version="1.0.0",
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

# Include routers
app.include_router(webhook_router, prefix="/api/webhook", tags=["webhooks"])
app.include_router(monitoring_router, prefix="/api/monitor", tags=["monitoring"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "InfluencerFlow AI Platform is running",
        "version": "1.0.0",
        "status": "healthy",
        "demo_mode": settings.demo_mode,
        "active_campaigns": len(active_campaigns)
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "api": "running",
            "database": "connected",  # TODO: Add actual DB health check
            "groq": "configured" if settings.groq_api_key else "missing_key",
            "elevenlabs": "configured" if settings.elevenlabs_api_key else "missing_key"
        },
        "active_campaigns": len(active_campaigns),
        "settings": {
            "demo_mode": settings.demo_mode,
            "mock_calls": settings.mock_calls,
            "max_negotiation_duration": settings.max_negotiation_duration
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )

# api/webhooks.py
import uuid
import asyncio
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from models.campaign import CampaignWebhook, CampaignData, CampaignOrchestrationState
from agents.orchestrator import CampaignOrchestrator

# Import settings with fallback
try:
    from config.settings import settings
except ImportError:
    from config.simple_settings import settings

webhook_router = APIRouter()

# Initialize orchestrator
orchestrator = CampaignOrchestrator()

@webhook_router.post("/campaign-created")
async def handle_campaign_created(
    campaign_webhook: CampaignWebhook,
    background_tasks: BackgroundTasks
):
    """
    Webhook endpoint triggered when a new campaign is created.
    Starts the AI agent orchestration process.
    """
    try:
        # Generate unique task ID for tracking
        task_id = str(uuid.uuid4())
        
        # Convert webhook data to internal campaign format
        campaign_data = CampaignData(
            id=campaign_webhook.campaign_id,
            product_name=campaign_webhook.product_name,
            brand_name=campaign_webhook.brand_name,
            product_description=campaign_webhook.product_description,
            target_audience=campaign_webhook.target_audience,
            campaign_goal=campaign_webhook.campaign_goal,
            product_niche=campaign_webhook.product_niche,
            total_budget=campaign_webhook.total_budget,
            campaign_code=f"CAMP-{campaign_webhook.campaign_id[:8].upper()}"
        )
        
        # Initialize orchestration state
        orchestration_state = CampaignOrchestrationState(
            campaign_id=campaign_data.id,
            campaign_data=campaign_data,
            current_stage="webhook_received"
        )
        
        # Store in global state for monitoring
        from main import active_campaigns
        active_campaigns[task_id] = orchestration_state
        
        # Start orchestration in background
        background_tasks.add_task(
            orchestrator.orchestrate_campaign,
            orchestration_state,
            task_id
        )
        
        return JSONResponse(
            status_code=202,
            content={
                "message": "Campaign orchestration started",
                "task_id": task_id,
                "campaign_id": campaign_data.id,
                "estimated_duration_minutes": 5,
                "monitor_url": f"/api/monitor/campaign/{task_id}",
                "status": "started"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start campaign orchestration: {str(e)}"
        )

@webhook_router.post("/test-campaign")
async def create_test_campaign(background_tasks: BackgroundTasks):
    """
    Create a test campaign for demo purposes
    """
    test_campaign = CampaignWebhook(
        campaign_id=str(uuid.uuid4()),
        product_name="FitPro Protein Powder",
        brand_name="FitLife Nutrition",
        product_description="Premium whey protein powder for muscle building and recovery, perfect for fitness enthusiasts and athletes",
        target_audience="Fitness enthusiasts, gym-goers, and athletes aged 18-35 who are serious about their workout routine and nutrition",
        campaign_goal="Increase brand awareness and drive sales in the fitness community",
        product_niche="fitness",
        total_budget=15000.0
    )
    
    return await handle_campaign_created(test_campaign, background_tasks)

# api/monitoring.py
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

monitoring_router = APIRouter()

@monitoring_router.get("/campaign/{task_id}")
async def monitor_campaign_progress(task_id: str) -> Dict[str, Any]:
    """
    Monitor the progress of a campaign orchestration
    """
    from main import active_campaigns
    
    if task_id not in active_campaigns:
        raise HTTPException(
            status_code=404,
            detail=f"Campaign with task_id {task_id} not found"
        )
    
    state = active_campaigns[task_id]
    
    return {
        "task_id": task_id,
        "campaign_id": state.campaign_id,
        "current_stage": state.current_stage,
        "current_influencer": state.current_influencer,
        "progress": {
            "discovered_influencers": len(state.discovered_influencers),
            "completed_negotiations": len(state.negotiations),
            "successful_negotiations": state.successful_negotiations,
            "failed_negotiations": state.failed_negotiations,
        },
        "estimated_completion_minutes": state.estimated_completion_minutes,
        "total_cost": state.total_cost,
        "started_at": state.started_at.isoformat(),
        "completed_at": state.completed_at.isoformat() if state.completed_at else None,
        "is_complete": state.completed_at is not None
    }

@monitoring_router.get("/campaigns")
async def list_active_campaigns():
    """
    List all active campaign orchestrations
    """
    from main import active_campaigns
    
    campaigns = []
    for task_id, state in active_campaigns.items():
        campaigns.append({
            "task_id": task_id,
            "campaign_id": state.campaign_id,
            "brand_name": state.campaign_data.brand_name,
            "product_name": state.campaign_data.product_name,
            "current_stage": state.current_stage,
            "started_at": state.started_at.isoformat(),
            "is_complete": state.completed_at is not None
        })
    
    return {
        "active_campaigns": len(active_campaigns),
        "campaigns": campaigns
    }