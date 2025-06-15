# api/campaigns.py - UNIFIED CAMPAIGN API
import asyncio
import logging
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import Dict, Any, List

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
    Replaces both legacy and enhanced endpoints with single, clean implementation.
    
    Args:
        campaign_request: Campaign creation request data
        background_tasks: FastAPI background tasks for async processing
        
    Returns:
        Dict containing task_id and campaign details for tracking
    """
    
    try:
        # Generate unique identifiers
        task_id = str(uuid.uuid4())
        campaign_id = str(uuid.uuid4())
        
        # Create campaign data object
        campaign_data = CampaignData(
            id=campaign_id,
            product_name=campaign_request.product_name,
            brand_name=campaign_request.brand_name,
            product_description=campaign_request.product_description,
            target_audience=campaign_request.target_audience,
            campaign_goal=campaign_request.campaign_goal,
            product_niche=campaign_request.product_niche,
            total_budget=campaign_request.total_budget,
            max_creators=campaign_request.max_creators,
            timeline_days=campaign_request.timeline_days
        )
        
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
    
    # Calculate progress metrics
    progress = {
        "creators_discovered": len(state.discovered_creators),
        "negotiations_completed": len(state.negotiations),
        "successful_negotiations": state.successful_negotiations,
        "contracts_generated": len(state.contracts),
        "total_cost": state.total_cost,
        "budget_utilization_percentage": state.get_budget_utilization(),
        "success_rate_percentage": state.get_success_rate(),
        "duration_minutes": state.get_total_duration() / 60
    }
    
    return CampaignStatusResponse(
        task_id=task_id,
        campaign_id=state.campaign_id,
        current_stage=state.current_stage,
        is_complete=state.is_complete(),
        progress=progress,
        started_at=state.started_at.isoformat(),
        completed_at=state.completed_at.isoformat() if state.completed_at else None,
        error_message=state.error_message
    )

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
            "campaign_code": state.campaign_data.campaign_code,
            "product_name": state.campaign_data.product_name,
            "brand_name": state.campaign_data.brand_name,
            "niche": state.campaign_data.product_niche,
            "total_budget": state.campaign_data.total_budget
        },
        "status": {
            "current_stage": state.current_stage,
            "is_complete": state.is_complete(),
            "has_errors": state.has_errors(),
            "started_at": state.started_at.isoformat(),
            "completed_at": state.completed_at.isoformat() if state.completed_at else None
        },
        "metrics": metrics,
        "creators": [
            {
                "id": creator.id,
                "name": creator.name,
                "handle": creator.handle,
                "followers": creator.followers,
                "engagement_rate": creator.engagement_rate,
                "rate_per_post": creator.rate_per_post,
                "match_score": creator.match_score,
                "niche": creator.niche
            }
            for creator in state.discovered_creators
        ],
        "negotiations": [
            {
                "creator_id": neg.creator_id,
                "creator_name": neg.creator_name,
                "status": neg.status.value,
                "call_status": neg.call_status.value,
                "call_duration_seconds": neg.call_duration_seconds,
                "original_rate": neg.original_rate,
                "agreed_rate": neg.agreed_rate,
                "discount_percentage": neg.get_discount_percentage(),
                "sentiment_score": neg.sentiment_score,
                "key_concerns": neg.key_concerns,
                "negotiated_at": neg.negotiated_at.isoformat(),
                "follow_up_required": neg.follow_up_required
            }
            for neg in state.negotiations
        ],
        "contracts": [
            {
                "id": contract.id,
                "creator_id": contract.creator_id,
                "rate": contract.rate,
                "deliverables": contract.deliverables,
                "deadline": contract.deadline.isoformat(),
                "status": contract.status.value,
                "days_until_deadline": contract.days_until_deadline(),
                "payment_schedule": contract.payment_schedule,
                "created_at": contract.created_at.isoformat()
            }
            for contract in state.contracts
        ],
        "phase_timings": state.phase_timings,
        "warnings": state.warnings,
        "error_message": state.error_message
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
        is_complete = state.is_complete()
        
        if is_complete:
            completed_campaigns += 1
        else:
            active_campaign_count += 1
        
        campaign_summary = {
            "task_id": task_id,
            "campaign_id": state.campaign_id,
            "campaign_code": state.campaign_data.campaign_code,
            "brand_name": state.campaign_data.brand_name,
            "product_name": state.campaign_data.product_name,
            "niche": state.campaign_data.product_niche,
            "current_stage": state.current_stage,
            "is_complete": is_complete,
            "successful_negotiations": state.successful_negotiations,
            "total_cost": state.total_cost,
            "budget_utilization": state.get_budget_utilization(),
            "success_rate": state.get_success_rate(),
            "started_at": state.started_at.isoformat(),
            "duration_minutes": state.get_total_duration() / 60,
            "has_errors": state.has_errors()
        }
        campaigns_summary.append(campaign_summary)
    
    # Sort by start time (most recent first)
    campaigns_summary.sort(key=lambda x: x["started_at"], reverse=True)
    
    return {
        "summary": {
            "total_campaigns": total_campaigns,
            "active_campaigns": active_campaign_count,
            "completed_campaigns": completed_campaigns,
            "success_rate_average": sum(c["success_rate"] for c in campaigns_summary) / total_campaigns if total_campaigns > 0 else 0
        },
        "campaigns": campaigns_summary
    }

@router.delete("/campaigns/{task_id}")
async def cancel_campaign(task_id: str) -> Dict[str, Any]:
    """
    ❌ Cancel Campaign
    
    Cancels an active campaign and marks it as cancelled
    """
    
    if task_id not in active_campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    state = active_campaigns[task_id]
    
    if state.is_complete():
        raise HTTPException(status_code=400, detail="Cannot cancel completed campaign")
    
    # Mark as cancelled
    state.current_stage = "cancelled"
    state.completed_at = datetime.now()
    state.error_message = "Campaign cancelled by user"
    
    logger.info(f"❌ Campaign {task_id} cancelled by user")
    
    return {
        "task_id": task_id,
        "status": "cancelled",
        "message": "Campaign has been cancelled"
    }

# Legacy endpoint aliases for backward compatibility
@router.post("/webhook/campaign-created")
async def legacy_campaign_webhook(
    webhook_data: Dict[str, Any],
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    🔄 Legacy Webhook Endpoint (Deprecated)
    
    Maintains backward compatibility with existing integrations.
    Redirects to new unified endpoint.
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