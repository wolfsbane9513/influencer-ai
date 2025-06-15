# api/campaigns.py - FIXED UNIFIED CAMPAIGN API
import asyncio
import logging
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any

from core.models import (
    CampaignData, 
    OrchestrationState, 
    CampaignCreateRequest,
    CampaignStatusResponse
)
from agents.orchestrator import CampaignOrchestrator

logger = logging.getLogger(__name__)
router = APIRouter()

# Global state for campaign tracking
active_campaigns: Dict[str, OrchestrationState] = {}

# Single orchestrator instance
orchestrator = CampaignOrchestrator()

@router.post("/campaigns", response_model=Dict[str, Any])
async def create_campaign(
    campaign_request: CampaignCreateRequest,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    🚀 Unified Campaign Creation Endpoint
    
    Handles campaign creation with proper validation and background processing.
    """
    try:
        # Generate unique identifiers
        task_id = str(uuid.uuid4())
        campaign_id = str(uuid.uuid4())
        
        # Create campaign data object using the request converter
        campaign_data = campaign_request.to_campaign_data(campaign_id)
        
        # Generate campaign code
        campaign_code = campaign_data.generate_campaign_code()
        
        logger.info(f"🚀 Campaign created: {campaign_data.product_name} (Task: {task_id})")
        
        # Initialize orchestration state for tracking
        initial_state = OrchestrationState(
            campaign_id=campaign_id,
            campaign_data=campaign_data,
            current_stage="queued"
        )
        active_campaigns[task_id] = initial_state
        
        # Start orchestration in background
        background_tasks.add_task(
            run_campaign_orchestration,
            task_id,
            campaign_data
        )
        
        return {
            "task_id": task_id,
            "campaign_id": campaign_id,
            "campaign_code": campaign_code,
            "status": "started",
            "message": f"Campaign orchestration started for {campaign_data.product_name}",
            "estimated_duration_minutes": 8,
            "max_creators": campaign_data.max_creators,
            "budget_per_creator": campaign_data.get_budget_per_creator()
        }
        
    except Exception as e:
        logger.error(f"❌ Campaign creation failed: {e}")
        raise HTTPException(status_code=400, detail=f"Campaign creation failed: {str(e)}")

async def run_campaign_orchestration(task_id: str, campaign_data: CampaignData):
    """
    Background task for campaign orchestration
    
    Runs the complete campaign workflow and updates state for monitoring
    """
    try:
        logger.info(f"🎯 Starting orchestration for task {task_id}")
        
        # Update state to show orchestration started
        if task_id in active_campaigns:
            active_campaigns[task_id].current_stage = "starting"
        
        # Run complete orchestration
        result_state = await orchestrator.orchestrate_campaign(campaign_data)
        
        # Store final results
        active_campaigns[task_id] = result_state
        
        logger.info(f"✅ Campaign {task_id} completed successfully")
        logger.info(f"📊 Final metrics: {result_state.successful_negotiations} successful negotiations")
        
    except Exception as e:
        logger.error(f"❌ Campaign {task_id} failed: {e}")
        
        # Store error state
        if task_id in active_campaigns:
            error_state = active_campaigns[task_id]
            error_state.current_stage = "failed"
            # Add error_message attribute if it doesn't exist
            if not hasattr(error_state, 'error_message'):
                error_state.error_message = str(e)
            else:
                error_state.error_message = str(e)
            error_state.completed_at = datetime.now()

@router.get("/campaigns/{task_id}", response_model=CampaignStatusResponse)
async def get_campaign_status(task_id: str) -> CampaignStatusResponse:
    """
    📊 Get Campaign Status and Progress
    
    Returns detailed campaign status including progress metrics and current stage
    """
    if task_id not in active_campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    state = active_campaigns[task_id]
    
    # Use the model's class method to create response
    return CampaignStatusResponse.from_orchestration_state(task_id, state)

@router.get("/campaigns/{task_id}/detailed")
async def get_detailed_campaign_results(task_id: str) -> Dict[str, Any]:
    """
    📋 Get Detailed Campaign Results
    
    Returns comprehensive campaign results including all negotiations and contracts
    """
    if task_id not in active_campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    state = active_campaigns[task_id]
    
    # Get campaign metrics
    metrics = orchestrator.get_campaign_metrics(state)
    
    # Prepare detailed results
    detailed_results = {
        "campaign_info": {
            "task_id": task_id,
            "campaign_id": state.campaign_id,
            "campaign_code": getattr(state.campaign_data, 'campaign_code', 'N/A'),
            "product_name": getattr(state.campaign_data, 'product_name', state.campaign_data.name),
            "brand_name": getattr(state.campaign_data, 'brand_name', 'Unknown Brand'),
            "niche": getattr(state.campaign_data, 'product_niche', 'general'),
            "total_budget": state.campaign_data.total_budget
        },
        "status": {
            "current_stage": state.current_stage,
            "is_complete": state.completed_at is not None,
            "has_errors": hasattr(state, 'error_message') and state.error_message is not None,
            "started_at": state.started_at.isoformat(),
            "completed_at": state.completed_at.isoformat() if state.completed_at else None
        },
        "metrics": metrics,
        "creators": [
            {
                "id": getattr(creator, 'id', 'unknown'),
                "name": getattr(creator, 'name', 'Unknown Creator'),
                "handle": getattr(creator, 'handle', '@unknown'),
                "followers": getattr(creator, 'followers', 0),
                "engagement_rate": getattr(creator, 'engagement_rate', 0.0),
                "rate_per_post": getattr(creator, 'rate_per_post', 0.0),
                "match_score": getattr(creator, 'match_score', 0.0),
                "niche": getattr(creator, 'niche', 'general')
            }
            for creator in state.discovered_creators
        ],
        "negotiations": [
            {
                "creator_id": neg.creator_id,
                "creator_name": neg.creator_name,
                "status": neg.status.value,
                "call_status": getattr(neg, 'call_status', 'unknown').value if hasattr(getattr(neg, 'call_status', None), 'value') else str(getattr(neg, 'call_status', 'unknown')),
                "call_duration_seconds": getattr(neg, 'call_duration_seconds', 0),
                "original_rate": getattr(neg, 'original_rate', 0.0),
                "agreed_rate": neg.rate,  # Using unified rate property
                "discount_percentage": neg.get_discount_percentage() if hasattr(neg, 'get_discount_percentage') else 0.0,
                "sentiment_score": getattr(neg, 'sentiment_score', 0.0),
                "key_concerns": getattr(neg, 'key_concerns', []),
                "negotiated_at": neg.negotiated_at.isoformat() if neg.negotiated_at else datetime.now().isoformat(),
                "follow_up_required": getattr(neg, 'follow_up_required', False)
            }
            for neg in state.negotiations
        ],
        "contracts": [
            {
                "id": getattr(contract, 'id', 'unknown'),
                "creator_id": getattr(contract, 'creator_id', 'unknown'),
                "rate": getattr(contract, 'rate', 0.0),
                "deliverables": getattr(contract, 'deliverables', []),
                "deadline": getattr(contract, 'deadline', datetime.now()).isoformat() if hasattr(getattr(contract, 'deadline', None), 'isoformat') else str(getattr(contract, 'deadline', 'N/A')),
                "status": getattr(contract, 'status', 'draft'),
                "payment_schedule": getattr(contract, 'payment_schedule', 'upon_completion'),
                "created_at": getattr(contract, 'created_at', datetime.now()).isoformat() if hasattr(getattr(contract, 'created_at', None), 'isoformat') else str(getattr(contract, 'created_at', 'N/A'))
            }
            for contract in state.contracts
        ],
        "error_message": getattr(state, 'error_message', None)
    }
    
    return detailed_results

@router.get("/campaigns")
async def list_campaigns() -> Dict[str, Any]:
    """
    📋 List All Campaigns
    
    Returns summary of all campaigns with key metrics
    """
    campaigns_summary = []
    total_campaigns = len(active_campaigns)
    completed_campaigns = 0
    active_campaign_count = 0
    
    for task_id, state in active_campaigns.items():
        is_complete = state.completed_at is not None
        
        if is_complete:
            completed_campaigns += 1
        else:
            active_campaign_count += 1
        
        campaign_summary = {
            "task_id": task_id,
            "campaign_id": state.campaign_id,
            "campaign_code": getattr(state.campaign_data, 'campaign_code', 'N/A'),
            "brand_name": getattr(state.campaign_data, 'brand_name', 'Unknown Brand'),
            "product_name": getattr(state.campaign_data, 'product_name', state.campaign_data.name),
            "niche": getattr(state.campaign_data, 'product_niche', 'general'),
            "total_budget": state.campaign_data.total_budget,
            "current_stage": state.current_stage,
            "is_complete": is_complete,
            "successful_negotiations": state.successful_negotiations,
            "total_cost": state.total_cost,
            "started_at": state.started_at.isoformat(),
            "completed_at": state.completed_at.isoformat() if state.completed_at else None
        }
        campaigns_summary.append(campaign_summary)
    
    return {
        "total_campaigns": total_campaigns,
        "active_campaigns": active_campaign_count,
        "completed_campaigns": completed_campaigns,
        "campaigns": campaigns_summary
    }

# Legacy webhook endpoint for backward compatibility
@router.post("/webhook/enhanced-campaign")
async def legacy_webhook_endpoint(
    webhook_data: Dict[str, Any],
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    🔄 Legacy Webhook Endpoint (Deprecated)
    
    Maintains backward compatibility. Redirects to new unified endpoint.
    """
    logger.warning("⚠️ Using deprecated webhook endpoint. Please migrate to POST /campaigns")
    
    # Convert legacy format to new format
    try:
        campaign_request = CampaignCreateRequest(
            product_name=webhook_data["product_name"],
            brand_name=webhook_data["brand_name"],
            product_description=webhook_data["product_description"],
            target_audience=webhook_data["target_audience"],
            campaign_goal=webhook_data["campaign_goal"],
            product_niche=webhook_data["product_niche"],
            total_budget=webhook_data["total_budget"],
            max_creators=webhook_data.get("max_creators", 10),
            timeline_days=webhook_data.get("timeline_days", 30)
        )
        
        return await create_campaign(campaign_request, background_tasks)
        
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing required field: {e}")

@router.get("/webhook/test-enhanced-elevenlabs")
async def test_elevenlabs_integration():
    """
    📞 Test ElevenLabs Integration (For E2E Testing)
    """
    try:
        logger.info("📞 Testing ElevenLabs integration...")
        
        return {
            "status": "mock_mode",
            "message": "ElevenLabs integration ready",
            "api_connected": False,  # Mock mode
            "features": [
                "Dynamic variable injection",
                "Real-time conversation monitoring", 
                "Structured outcome analysis",
                "Mock conversation simulation"
            ]
        }
        
    except Exception as e:
        logger.error(f"❌ ElevenLabs integration test failed: {e}")
        return {
            "status": "error",
            "message": str(e),
            "api_connected": False
        }

@router.get("/monitor/campaign/{task_id}")
async def legacy_monitor_endpoint(task_id: str) -> Dict[str, Any]:
    """
    🔄 Legacy Monitor Endpoint (Deprecated)
    
    Maintains backward compatibility. Redirects to new endpoint.
    """
    logger.warning("⚠️ Using deprecated monitor endpoint. Please migrate to GET /campaigns/{task_id}")
    
    # Convert to new format
    response = await get_campaign_status(task_id)
    
    # Convert back to legacy format for compatibility
    return {
        "task_id": response.task_id,
        "campaign_id": response.campaign_id,
        "current_stage": response.current_stage,
        "progress": response.progress,
        "is_complete": response.is_complete,
        "started_at": response.started_at,
        "completed_at": response.completed_at,
        "error": response.error_message
    }