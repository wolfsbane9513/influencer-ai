# api/monitoring.py - LEGACY MONITORING (Backward Compatibility)
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Legacy monitoring router
monitoring_router = APIRouter()

@monitoring_router.get("/campaign/{task_id}")
async def monitor_legacy_campaign_progress(task_id: str) -> Dict[str, Any]:
    """
    📊 Legacy campaign progress monitoring
    Basic monitoring for backward compatibility
    """
    from main import active_campaigns
    
    if task_id not in active_campaigns:
        raise HTTPException(
            status_code=404,
            detail={
                "error": f"Legacy campaign with task_id {task_id} not found",
                "available_campaigns": len(active_campaigns),
                "upgrade_note": "For enhanced monitoring, use /api/monitor/enhanced-campaign/"
            }
        )
    
    state = active_campaigns[task_id]
    
    # Basic progress calculation
    progress_percentage = _calculate_basic_progress(state)
    
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
        "basic_metrics": {
            "discovered_influencers": len(state.discovered_influencers),
            "total_negotiations": len(state.negotiations),
            "successful_negotiations": state.successful_negotiations,
            "total_cost": state.total_cost
        },
        "timing": {
            "started_at": state.started_at.isoformat(),
            "completed_at": state.completed_at.isoformat() if state.completed_at else None,
            "duration_minutes": (datetime.now() - state.started_at).total_seconds() / 60
        },
        "is_complete": state.completed_at is not None,
        "legacy_mode": True,
        "upgrade_available": {
            "enhanced_monitoring": "/api/monitor/enhanced-campaign/{task_id}",
            "features": ["Real-time updates", "AI insights", "Detailed analytics"]
        }
    }

@monitoring_router.get("/campaigns")
async def list_legacy_campaigns() -> Dict[str, Any]:
    """📋 List all legacy campaigns"""
    from main import active_campaigns
    
    legacy_campaigns = []
    enhanced_campaigns = []
    
    for task_id, state in active_campaigns.items():
        campaign_info = {
            "task_id": task_id,
            "campaign_id": state.campaign_id,
            "brand_name": state.campaign_data.brand_name,
            "product_name": state.campaign_data.product_name,
            "current_stage": state.current_stage,
            "progress_percentage": _calculate_basic_progress(state),
            "started_at": state.started_at.isoformat(),
            "is_complete": state.completed_at is not None
        }
        
        # Separate legacy from enhanced campaigns
        if getattr(state.campaign_data, 'campaign_code', '').startswith('EFC-'):
            enhanced_campaigns.append(campaign_info)
        else:
            legacy_campaigns.append(campaign_info)
    
    # Sort by start time (most recent first)
    legacy_campaigns.sort(key=lambda x: x["started_at"], reverse=True)
    enhanced_campaigns.sort(key=lambda x: x["started_at"], reverse=True)
    
    return {
        "summary": {
            "total_campaigns": len(active_campaigns),
            "legacy_campaigns": len(legacy_campaigns),
            "enhanced_campaigns": len(enhanced_campaigns)
        },
        "legacy_campaigns": legacy_campaigns,
        "enhanced_campaigns_available": len(enhanced_campaigns),
        "legacy_features": [
            "Basic campaign tracking",
            "Simple progress monitoring", 
            "Basic metrics reporting"
        ],
        "enhanced_features": [
            "AI-powered insights",
            "Real-time conversation monitoring",
            "Advanced analytics",
            "Automated workflows"
        ],
        "endpoints": {
            "legacy_monitoring": "/api/legacy/monitor/",
            "enhanced_monitoring": "/api/monitor/enhanced-campaign/",
            "upgrade_path": "/api/enhanced/"
        }
    }

@monitoring_router.get("/campaign/{task_id}/summary")
async def get_legacy_campaign_summary(task_id: str) -> Dict[str, Any]:
    """📊 Basic campaign summary"""
    from main import active_campaigns
    
    if task_id not in active_campaigns:
        raise HTTPException(404, "Legacy campaign not found")
    
    state = active_campaigns[task_id]
    
    # Basic summary calculation
    duration = (state.completed_at or datetime.now()) - state.started_at
    
    return {
        "task_id": task_id,
        "summary": {
            "campaign_name": f"{state.campaign_data.brand_name} - {state.campaign_data.product_name}",
            "total_budget": state.campaign_data.total_budget,
            "spent_amount": state.total_cost,
            "budget_utilization": (state.total_cost / state.campaign_data.total_budget) * 100 if state.campaign_data.total_budget > 0 else 0,
            "creators_contacted": len(state.negotiations),
            "successful_partnerships": state.successful_negotiations,
            "success_rate": f"{(state.successful_negotiations / max(len(state.negotiations), 1)) * 100:.1f}%",
            "duration_minutes": f"{duration.total_seconds() / 60:.1f}",
            "status": "completed" if state.completed_at else "in_progress"
        },
        "basic_breakdown": {
            "discovery_phase": "✅ Completed" if len(state.discovered_influencers) > 0 else "⏳ In Progress",
            "negotiation_phase": "✅ Completed" if len(state.negotiations) > 0 else "⏳ Pending",
            "completion_status": "✅ Completed" if state.completed_at else "⏳ In Progress"
        },
        "legacy_limitations": [
            "Basic metrics only",
            "No real-time insights", 
            "Limited analytics",
            "No AI-powered features"
        ],
        "upgrade_benefits": [
            "Detailed conversation analytics",
            "AI strategy insights",
            "Real-time monitoring",
            "Enhanced reporting"
        ],
        "enhanced_summary_url": f"/api/monitor/enhanced-campaign/{task_id}/detailed-summary"
    }

@monitoring_router.get("/system-status")
async def legacy_monitoring_system_status():
    """🔧 Legacy monitoring system status"""
    from main import active_campaigns
    
    legacy_count = 0
    enhanced_count = 0
    
    for state in active_campaigns.values():
        if getattr(state.campaign_data, 'campaign_code', '').startswith('EFC-'):
            enhanced_count += 1
        else:
            legacy_count += 1
    
    return {
        "system_status": "operational",
        "monitoring_type": "legacy",
        "note": "Basic monitoring for backward compatibility",
        "statistics": {
            "total_campaigns": len(active_campaigns),
            "legacy_campaigns": legacy_count,
            "enhanced_campaigns": enhanced_count
        },
        "legacy_capabilities": [
            "Basic progress tracking",
            "Simple metrics",
            "Campaign listing",
            "Status monitoring"
        ],
        "missing_features": [
            "Real-time updates",
            "AI insights",
            "Advanced analytics",
            "Conversation monitoring"
        ],
        "endpoints": {
            "monitor_campaign": "/api/legacy/monitor/campaign/{task_id}",
            "list_campaigns": "/api/legacy/monitor/campaigns",
            "campaign_summary": "/api/legacy/monitor/campaign/{task_id}/summary"
        },
        "upgrade_path": {
            "enhanced_monitoring": "/api/monitor/enhanced-campaign/",
            "benefits": "Full feature set with AI insights and real-time monitoring"
        }
    }

# Helper function
def _calculate_basic_progress(state) -> float:
    """Calculate basic progress percentage for legacy monitoring"""
    if state.current_stage == "legacy_webhook_received":
        return 10.0
    elif state.current_stage == "discovery":
        return 30.0
    elif state.current_stage == "negotiations":
        if len(state.discovered_influencers) > 0:
            negotiation_progress = (len(state.negotiations) / len(state.discovered_influencers)) * 50
            return 30.0 + negotiation_progress
        return 30.0
    elif state.current_stage == "completed":
        return 100.0
    elif state.current_stage == "failed":
        return 0.0
    else:
        return 20.0