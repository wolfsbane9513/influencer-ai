# api/webhooks.py - LEGACY ENDPOINTS (Backward Compatibility)
import uuid
import asyncio
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, Any

from models.campaign import CampaignWebhook, CampaignData, CampaignOrchestrationState

logger = logging.getLogger(__name__)

# Legacy webhook router
webhook_router = APIRouter()

@webhook_router.post("/campaign-created")
async def handle_legacy_campaign_created(
    campaign_webhook: CampaignWebhook,
    background_tasks: BackgroundTasks
):
    """
    📋 LEGACY CAMPAIGN WEBHOOK - Basic backward compatibility
    
    This endpoint provides basic compatibility for existing integrations.
    For enhanced features, use /api/enhanced/enhanced-campaign
    """
    try:
        # Generate unique task ID for tracking
        task_id = str(uuid.uuid4())
        
        logger.info(f"📋 Legacy campaign webhook received: {campaign_webhook.product_name}")
        
        # Convert to campaign data
        campaign_data = CampaignData(
            id=campaign_webhook.campaign_id,
            product_name=campaign_webhook.product_name,
            brand_name=campaign_webhook.brand_name,
            product_description=campaign_webhook.product_description,
            target_audience=campaign_webhook.target_audience,
            campaign_goal=campaign_webhook.campaign_goal,
            product_niche=campaign_webhook.product_niche,
            total_budget=campaign_webhook.total_budget
        )
        
        # Initialize basic orchestration state
        orchestration_state = CampaignOrchestrationState(
            campaign_id=campaign_data.id,
            campaign_data=campaign_data,
            current_stage="legacy_webhook_received"
        )
        
        # Store in global state for monitoring
        from main import active_campaigns
        active_campaigns[task_id] = orchestration_state
        
        # Start basic workflow
        background_tasks.add_task(
            legacy_campaign_workflow,
            orchestration_state,
            task_id
        )
        
        return JSONResponse(
            status_code=202,
            content={
                "message": "📋 Legacy campaign workflow started",
                "task_id": task_id,
                "campaign_id": campaign_data.id,
                "status": "started",
                "note": "This is a legacy endpoint. Consider upgrading to /api/enhanced/ for full features",
                "monitor_url": f"/api/legacy/monitor/campaign/{task_id}",
                "enhanced_upgrade": "/api/enhanced/enhanced-campaign"
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Legacy webhook processing failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Legacy campaign workflow failed to start",
                "message": str(e)
            }
        )

async def legacy_campaign_workflow(
    orchestration_state: CampaignOrchestrationState,
    task_id: str
):
    """
    🔄 Basic legacy workflow - simplified version
    """
    try:
        from main import active_campaigns
        
        logger.info(f"🔄 Starting legacy workflow for {orchestration_state.campaign_id}")
        
        # Phase 1: Discovery (simplified)
        orchestration_state.current_stage = "discovery"
        active_campaigns[task_id] = orchestration_state
        await asyncio.sleep(2)  # Simulate processing
        
        # Mock discovery results
        from agents.discovery import InfluencerDiscoveryAgent
        discovery_agent = InfluencerDiscoveryAgent()
        matches = await discovery_agent.find_matches(orchestration_state.campaign_data, max_results=2)
        orchestration_state.discovered_influencers = matches
        
        # Phase 2: Basic negotiations (mock)
        orchestration_state.current_stage = "negotiations"
        active_campaigns[task_id] = orchestration_state
        
        for match in matches:
            orchestration_state.current_influencer = match.creator.name
            await asyncio.sleep(3)  # Simulate call
            
            # Mock negotiation result
            from models.campaign import NegotiationState, NegotiationStatus
            negotiation = NegotiationState(
                creator_id=match.creator.id,
                campaign_id=orchestration_state.campaign_id,
                status=NegotiationStatus.SUCCESS,
                final_rate=match.estimated_rate,
                completed_at=datetime.now()
            )
            
            orchestration_state.add_negotiation_result(negotiation)
        
        # Phase 3: Completion
        orchestration_state.current_stage = "completed"
        orchestration_state.completed_at = datetime.now()
        active_campaigns[task_id] = orchestration_state
        
        logger.info(f"✅ Legacy workflow completed for {orchestration_state.campaign_id}")
        
    except Exception as e:
        logger.error(f"❌ Legacy workflow failed: {e}")
        orchestration_state.current_stage = "failed"
        active_campaigns[task_id] = orchestration_state

@webhook_router.post("/test-campaign")
async def create_test_legacy_campaign(background_tasks: BackgroundTasks):
    """🧪 Create test campaign for legacy system"""
    
    test_campaign = CampaignWebhook(
        campaign_id=str(uuid.uuid4()),
        product_name="Legacy Test Product",
        brand_name="Legacy Test Brand",
        product_description="Testing legacy webhook system with basic functionality",
        target_audience="Test audience for legacy system validation",
        campaign_goal="Validate backward compatibility",
        product_niche="fitness",
        total_budget=5000.0
    )
    
    logger.info("🧪 Legacy test campaign created")
    
    return await handle_legacy_campaign_created(test_campaign, background_tasks)

@webhook_router.get("/status")
async def legacy_webhook_status():
    """📊 Legacy webhook system status"""
    
    from main import active_campaigns
    
    legacy_campaigns = []
    for task_id, state in active_campaigns.items():
        # Identify legacy campaigns (those without enhanced features)
        if not getattr(state.campaign_data, 'campaign_code', '').startswith('EFC-'):
            legacy_campaigns.append({
                "task_id": task_id,
                "campaign_id": state.campaign_id,
                "stage": state.current_stage,
                "brand": state.campaign_data.brand_name,
                "product": state.campaign_data.product_name
            })
    
    return {
        "status": "operational",
        "message": "Legacy webhook system running",
        "note": "Consider upgrading to enhanced endpoints for full features",
        "active_legacy_campaigns": len(legacy_campaigns),
        "campaigns": legacy_campaigns,
        "endpoints": {
            "create_campaign": "/api/legacy/webhook/campaign-created",
            "test_campaign": "/api/legacy/webhook/test-campaign",
            "monitor": "/api/legacy/monitor/",
            "enhanced_upgrade": "/api/enhanced/"
        },
        "upgrade_benefits": [
            "ElevenLabs voice negotiations",
            "AI strategy generation", 
            "Real-time monitoring",
            "Enhanced contract generation",
            "Human approval workflows"
        ]
    }