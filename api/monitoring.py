# api/monitoring.py
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

monitoring_router = APIRouter()

@monitoring_router.get("/campaign/{task_id}")
async def monitor_campaign_progress(task_id: str) -> Dict[str, Any]:
    """
    🔍 Real-time campaign progress monitoring
    Returns detailed progress information for live demo tracking
    """
    from main import active_campaigns
    
    if task_id not in active_campaigns:
        raise HTTPException(
            status_code=404,
            detail=f"Campaign with task_id {task_id} not found. Check if the campaign was started correctly."
        )
    
    state = active_campaigns[task_id]
    
    # Calculate progress percentage based on current stage
    progress_percentage = _calculate_progress_percentage(state)
    
    # Get stage-specific details
    stage_details = _get_stage_details(state)
    
    # Estimate remaining time
    estimated_remaining = _estimate_remaining_time(state)
    
    return {
        "task_id": task_id,
        "campaign_id": state.campaign_id,
        "campaign_info": {
            "brand_name": state.campaign_data.brand_name,
            "product_name": state.campaign_data.product_name,
            "total_budget": state.campaign_data.total_budget,
            "niche": state.campaign_data.product_niche
        },
        "current_stage": state.current_stage,
        "current_influencer": state.current_influencer,
        "progress_percentage": progress_percentage,
        "progress_details": {
            "discovered_influencers": len(state.discovered_influencers),
            "completed_negotiations": len(state.negotiations),
            "successful_negotiations": state.successful_negotiations,
            "failed_negotiations": state.failed_negotiations,
            "total_cost": state.total_cost,
            "remaining_budget": state.campaign_data.total_budget - state.total_cost
        },
        "stage_details": stage_details,
        "timing": {
            "started_at": state.started_at.isoformat(),
            "completed_at": state.completed_at.isoformat() if state.completed_at else None,
            "estimated_completion_minutes": state.estimated_completion_minutes,
            "estimated_remaining": estimated_remaining,
            "duration_so_far": (datetime.now() - state.started_at).total_seconds() / 60
        },
        "is_complete": state.completed_at is not None,
        "live_updates": _get_live_updates(state)
    }

@monitoring_router.get("/campaigns")
async def list_active_campaigns() -> Dict[str, Any]:
    """📋 List all active and recent campaign orchestrations"""
    from main import active_campaigns
    
    campaigns = []
    active_count = 0
    completed_count = 0
    
    for task_id, state in active_campaigns.items():
        is_complete = state.completed_at is not None
        
        if is_complete:
            completed_count += 1
        else:
            active_count += 1
        
        campaign_info = {
            "task_id": task_id,
            "campaign_id": state.campaign_id,
            "brand_name": state.campaign_data.brand_name,
            "product_name": state.campaign_data.product_name,
            "niche": state.campaign_data.product_niche,
            "current_stage": state.current_stage,
            "progress_percentage": _calculate_progress_percentage(state),
            "successful_negotiations": state.successful_negotiations,
            "total_cost": state.total_cost,
            "started_at": state.started_at.isoformat(),
            "is_complete": is_complete,
            "duration_minutes": (
                (state.completed_at or datetime.now()) - state.started_at
            ).total_seconds() / 60
        }
        campaigns.append(campaign_info)
    
    # Sort by start time (most recent first)
    campaigns.sort(key=lambda x: x["started_at"], reverse=True)
    
    return {
        "summary": {
            "total_campaigns": len(campaigns),
            "active_campaigns": active_count,
            "completed_campaigns": completed_count
        },
        "campaigns": campaigns
    }

@monitoring_router.get("/campaign/{task_id}/summary")
async def get_campaign_summary(task_id: str) -> Dict[str, Any]:
    """📊 Get detailed campaign summary and results"""
    from main import active_campaigns
    
    if task_id not in active_campaigns:
        raise HTTPException(404, "Campaign not found")
    
    state = active_campaigns[task_id]
    
    # Get detailed summary using the model method
    summary = state.get_campaign_summary()
    
    # Add detailed negotiation breakdown
    negotiation_details = []
    for negotiation in state.negotiations:
        details = {
            "creator_id": negotiation.creator_id,
            "status": negotiation.status,
            "final_rate": negotiation.final_rate,
            "call_duration": negotiation.call_duration_seconds,
            "failure_reason": negotiation.failure_reason,
            "conversation_id": negotiation.conversation_id
        }
        negotiation_details.append(details)
    
    # Add discovered creators info
    creator_matches = []
    for match in state.discovered_influencers:
        creator_info = {
            "name": match.creator.name,
            "platform": match.creator.platform,
            "followers": match.creator.followers,
            "similarity_score": match.similarity_score,
            "estimated_rate": match.estimated_rate,
            "match_reasons": match.match_reasons
        }
        creator_matches.append(creator_info)
    
    return {
        "task_id": task_id,
        "campaign_summary": summary,
        "discovered_creators": creator_matches,
        "negotiation_details": negotiation_details,
        "performance_metrics": _calculate_performance_metrics(state)
    }

@monitoring_router.get("/health")
async def monitoring_health():
    """🏥 Health check for monitoring service"""
    from main import active_campaigns
    
    return {
        "service": "Campaign Monitoring API",
        "status": "healthy",
        "active_campaigns": len(active_campaigns),
        "endpoints": [
            "/api/monitor/campaign/{task_id}",
            "/api/monitor/campaigns", 
            "/api/monitor/campaign/{task_id}/summary"
        ],
        "capabilities": [
            "Real-time progress tracking",
            "Campaign summary generation",
            "Performance metrics calculation",
            "Live demo monitoring"
        ]
    }

# Helper functions for monitoring logic

def _calculate_progress_percentage(state) -> float:
    """Calculate overall progress percentage"""
    if state.current_stage == "webhook_received":
        return 5.0
    elif state.current_stage == "discovery":
        return 15.0
    elif state.current_stage == "negotiations":
        # Progress through negotiations (20% to 80%)
        total_discovered = len(state.discovered_influencers)
        completed_negotiations = len(state.negotiations)
        if total_discovered > 0:
            negotiation_progress = (completed_negotiations / total_discovered) * 60
            return 20.0 + negotiation_progress
        return 20.0
    elif state.current_stage == "contracts":
        return 90.0
    elif state.current_stage == "completed":
        return 100.0
    else:
        return 0.0

def _get_stage_details(state) -> Dict[str, Any]:
    """Get details specific to current stage"""
    if state.current_stage == "discovery":
        return {
            "description": "AI is analyzing creators and finding the best matches",
            "action": "Searching creator database and calculating similarity scores"
        }
    elif state.current_stage == "negotiations":
        return {
            "description": f"Conducting phone negotiations via ElevenLabs - Currently calling: {state.current_influencer}",
            "action": "Making live phone calls to creators",
            "completed_calls": len(state.negotiations),
            "total_calls": len(state.discovered_influencers)
        }
    elif state.current_stage == "contracts":
        return {
            "description": "Generating contracts for successful negotiations",
            "action": "Creating legal agreements and payment schedules"
        }
    elif state.current_stage == "completed":
        return {
            "description": "Campaign workflow completed",
            "action": "All processes finished - results available"
        }
    else:
        return {
            "description": "Initializing campaign workflow",
            "action": "Setting up AI agents and preparing for discovery"
        }

def _estimate_remaining_time(state) -> str:
    """Estimate remaining time based on current progress"""
    if state.current_stage == "discovery":
        return "30-60 seconds"
    elif state.current_stage == "negotiations":
        remaining_calls = len(state.discovered_influencers) - len(state.negotiations)
        return f"{remaining_calls * 1.5:.0f} minutes" if remaining_calls > 0 else "Completing final call"
    elif state.current_stage == "contracts":
        return "30 seconds"
    elif state.current_stage == "completed":
        return "Complete"
    else:
        return "2-5 minutes"

def _get_live_updates(state) -> List[str]:
    """Get recent live updates for demo engagement"""
    updates = []
    
    if state.current_stage == "discovery":
        updates.append(f"🔍 Analyzing {len(state.discovered_influencers)} potential creators")
    
    if state.negotiations:
        latest = state.negotiations[-1]
        if latest.status == "success":
            updates.append(f"✅ Successfully negotiated with {latest.creator_id} - ${latest.final_rate}")
        elif latest.status == "failed":
            updates.append(f"❌ Negotiation failed with {latest.creator_id} - {latest.failure_reason}")
    
    if state.current_influencer:
        updates.append(f"📞 Currently in call with: {state.current_influencer}")
    
    return updates

def _calculate_performance_metrics(state) -> Dict[str, Any]:
    """Calculate campaign performance metrics"""
    total_negotiations = len(state.negotiations)
    
    if total_negotiations == 0:
        return {"status": "No negotiations completed yet"}
    
    success_rate = (state.successful_negotiations / total_negotiations) * 100
    avg_cost = state.total_cost / max(state.successful_negotiations, 1)
    cost_per_negotiation = state.total_cost / total_negotiations
    budget_efficiency = (state.total_cost / state.campaign_data.total_budget) * 100
    
    return {
        "success_rate": f"{success_rate:.1f}%",
        "average_creator_cost": f"${avg_cost:,.2f}",
        "cost_per_negotiation": f"${cost_per_negotiation:,.2f}",
        "budget_utilization": f"{budget_efficiency:.1f}%",
        "roi_indicators": {
            "cost_efficiency": "High" if success_rate > 60 else "Medium" if success_rate > 30 else "Low",
            "budget_management": "Good" if budget_efficiency < 80 else "Over budget"
        }
    }
