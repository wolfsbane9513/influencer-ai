# api/enhanced_campaign_endpoints.py
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

from agents.unified_campaign_orchestrator import UnifiedCampaignOrchestrator, WorkflowConfiguration
from agents.campaign_data_collector import DataCollectionMethod
from agents.enhanced_influencer_matcher import InfluencerSelectionStrategy
from agents.enhanced_negotiation_manager import HumanDecision, SponsorDecision
from models.campaign import CampaignWebhook

logger = logging.getLogger(__name__)

# Initialize the unified orchestrator
unified_orchestrator = UnifiedCampaignOrchestrator()

# Create router
enhanced_campaign_router = APIRouter()

# ================================
# WORKFLOW MANAGEMENT ENDPOINTS
# ================================

class WorkflowStartRequest(BaseModel):
    """Request to start a new workflow"""
    data_collection_method: DataCollectionMethod = DataCollectionMethod.MANUAL
    selection_strategy: InfluencerSelectionStrategy = InfluencerSelectionStrategy.BUDGET_OPTIMIZED
    max_influencers: Optional[int] = None
    require_human_review: bool = True
    require_sponsor_approval: bool = True
    auto_send_contracts: bool = True
    initial_data: Optional[Dict[str, Any]] = None

@enhanced_campaign_router.post("/start-enhanced-workflow")
async def start_enhanced_workflow(
    request: WorkflowStartRequest,
    background_tasks: BackgroundTasks
):
    """
    🚀 Start complete enhanced campaign workflow
    Supports all data collection methods and configurations
    """
    
    try:
        # Create workflow configuration
        config = WorkflowConfiguration(
            data_collection_method=request.data_collection_method,
            selection_strategy=request.selection_strategy,
            max_influencers=request.max_influencers,
            require_human_review=request.require_human_review,
            require_sponsor_approval=request.require_sponsor_approval,
            auto_send_contracts=request.auto_send_contracts,
            real_time_progress=True,
            send_notifications=True
        )
        
        # Start workflow in background
        workflow_future = asyncio.create_task(
            unified_orchestrator.start_unified_campaign_workflow(
                initial_data=request.initial_data,
                configuration=config
            )
        )
        
        # Get initial workflow state
        await asyncio.sleep(1)  # Allow workflow to initialize
        
        # Get workflow ID from active workflows
        active_workflows = unified_orchestrator.get_all_active_workflows()
        if active_workflows:
            workflow_state = active_workflows[-1]  # Most recent
            workflow_id = workflow_state.workflow_id
        else:
            workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return JSONResponse(
            status_code=202,
            content={
                "message": "🚀 Enhanced campaign workflow started",
                "workflow_id": workflow_id,
                "configuration": {
                    "data_collection": request.data_collection_method.value,
                    "selection_strategy": request.selection_strategy.value,
                    "human_review": request.require_human_review,
                    "sponsor_approval": request.require_sponsor_approval
                },
                "monitor_url": f"/api/enhanced/workflow/{workflow_id}/status",
                "estimated_duration": "15-45 minutes depending on approvals",
                "next_steps": [
                    "Data collection and validation",
                    "AI-powered influencer discovery",
                    "Sequential negotiations with human oversight",
                    "Sponsor approval workflow",
                    "Automated contract generation and delivery"
                ]
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start enhanced workflow: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to start enhanced workflow",
                "message": str(e)
            }
        )

@enhanced_campaign_router.post("/start-file-upload-workflow")
async def start_file_upload_workflow(
    file: UploadFile = File(...),
    selection_strategy: str = Form(default="budget_optimized"),
    max_influencers: Optional[int] = Form(default=None),
    require_human_review: bool = Form(default=True),
    background_tasks: BackgroundTasks = None
):
    """
    📄 Start workflow with file upload for campaign data
    """
    
    try:
        # Save uploaded file
        file_path = f"uploads/{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Create configuration for file upload
        config = WorkflowConfiguration(
            data_collection_method=DataCollectionMethod.FILE_UPLOAD,
            selection_strategy=InfluencerSelectionStrategy(selection_strategy),
            max_influencers=max_influencers,
            require_human_review=require_human_review,
            require_sponsor_approval=True,
            auto_send_contracts=True
        )
        
        # Start workflow with file
        workflow_state = await unified_orchestrator.start_unified_campaign_workflow(
            initial_data={"file_path": file_path},
            configuration=config
        )
        
        return {
            "message": "📄 File upload workflow started",
            "workflow_id": workflow_state.workflow_id,
            "file_processed": file.filename,
            "status": "processing",
            "monitor_url": f"/api/enhanced/workflow/{workflow_state.workflow_id}/status"
        }
        
    except Exception as e:
        logger.error(f"❌ File upload workflow failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"File upload workflow failed: {str(e)}"
        )

@enhanced_campaign_router.post("/start-conversational-workflow")
async def start_conversational_workflow(
    initial_prompt: Optional[str] = None,
    background_tasks: BackgroundTasks = None
):
    """
    🗣️ Start workflow with conversational AI data collection
    """
    
    config = WorkflowConfiguration(
        data_collection_method=DataCollectionMethod.CONVERSATIONAL,
        selection_strategy=InfluencerSelectionStrategy.BUDGET_OPTIMIZED,
        require_human_review=True,
        require_sponsor_approval=True
    )
    
    initial_data = {"conversation_prompt": initial_prompt} if initial_prompt else None
    
    workflow_state = await unified_orchestrator.start_unified_campaign_workflow(
        initial_data=initial_data,
        configuration=config
    )
    
    return {
        "message": "🗣️ Conversational workflow started",
        "workflow_id": workflow_state.workflow_id,
        "conversation_ready": True,
        "next_prompt": "Hi! Let's set up your influencer campaign. What product would you like to promote?",
        "monitor_url": f"/api/enhanced/workflow/{workflow_state.workflow_id}/status"
    }

# ================================
# WORKFLOW MONITORING ENDPOINTS
# ================================

@enhanced_campaign_router.get("/workflow/{workflow_id}/status")
async def get_workflow_status(workflow_id: str):
    """
    📊 Get real-time workflow status and progress
    """
    
    workflow_state = unified_orchestrator.get_workflow_status(workflow_id)
    
    if not workflow_state:
        raise HTTPException(
            status_code=404,
            detail=f"Workflow {workflow_id} not found"
        )
    
    # Calculate detailed progress
    phase_progress = {
        "data_collection": 0,
        "influencer_discovery": 0,
        "negotiations": 0,
        "approvals": 0,
        "contracts": 0
    }
    
    # Update phase progress based on completed phases
    for phase in workflow_state.completed_phases:
        if "data" in phase.value.lower():
            phase_progress["data_collection"] = 100
        elif "influencer" in phase.value.lower():
            phase_progress["influencer_discovery"] = 100
        elif "negotiation" in phase.value.lower():
            phase_progress["negotiations"] = 100
        elif "approval" in phase.value.lower():
            phase_progress["approvals"] = 100
        elif "contract" in phase.value.lower():
            phase_progress["contracts"] = 100
    
    return {
        "workflow_id": workflow_id,
        "current_phase": workflow_state.current_phase.value,
        "progress_percentage": workflow_state.progress_percentage,
        "current_activity": workflow_state.current_activity,
        "phase_progress": phase_progress,
        "campaign_info": {
            "campaign_id": workflow_state.campaign_id,
            "product_name": workflow_state.campaign_data.product_name if workflow_state.campaign_data else None,
            "brand_name": workflow_state.campaign_data.brand_name if workflow_state.campaign_data else None,
            "total_budget": workflow_state.campaign_data.total_budget if workflow_state.campaign_data else None
        },
        "influencer_status": {
            "primary_selected": len(workflow_state.influencer_pool.get("primary_selections", [])) if workflow_state.influencer_pool else 0,
            "active_negotiations": len(workflow_state.active_negotiations),
            "successful_negotiations": len(workflow_state.successful_negotiations),
            "contracts_generated": len(workflow_state.generated_contracts)
        },
        "timing": {
            "started_at": workflow_state.started_at.isoformat(),
            "estimated_completion": workflow_state.estimated_completion.isoformat() if workflow_state.estimated_completion else None,
            "duration_minutes": (datetime.now() - workflow_state.started_at).total_seconds() / 60
        },
        "is_complete": workflow_state.current_phase.value == "completed",
        "configuration": workflow_state.configuration.dict()
    }

@enhanced_campaign_router.get("/workflows")
async def list_all_workflows():
    """
    📋 List all active and recent workflows
    """
    
    workflows = unified_orchestrator.get_all_active_workflows()
    
    workflow_summaries = []
    for workflow in workflows:
        summary = {
            "workflow_id": workflow.workflow_id,
            "campaign_id": workflow.campaign_id,
            "current_phase": workflow.current_phase.value,
            "progress_percentage": workflow.progress_percentage,
            "started_at": workflow.started_at.isoformat(),
            "is_complete": workflow.current_phase.value == "completed",
            "configuration": {
                "data_collection_method": workflow.configuration.data_collection_method.value,
                "selection_strategy": workflow.configuration.selection_strategy.value,
                "require_human_review": workflow.configuration.require_human_review
            }
        }
        workflow_summaries.append(summary)
    
    return {
        "total_workflows": len(workflows),
        "active_workflows": len([w for w in workflows if w.current_phase.value not in ["completed", "failed"]]),
        "workflows": workflow_summaries
    }

@enhanced_campaign_router.get("/workflow/{workflow_id}/analytics")
async def get_workflow_analytics(workflow_id: str):
    """
    📈 Get comprehensive workflow analytics
    """
    
    analytics = unified_orchestrator.get_workflow_analytics(workflow_id)
    
    if "error" in analytics:
        raise HTTPException(status_code=404, detail=analytics["error"])
    
    return analytics

# ================================
# HUMAN REVIEW ENDPOINTS
# ================================

@enhanced_campaign_router.get("/human-reviews")
async def get_pending_human_reviews():
    """
    👤 Get all pending human reviews
    """
    
    pending_reviews = unified_orchestrator.negotiation_manager.get_human_review_queue()
    
    review_summaries = []
    for review in pending_reviews:
        summary = {
            "negotiation_id": review.negotiation_id,
            "creator_name": review.creator_name,
            "ai_recommendation": review.ai_recommendation,
            "priority_level": review.priority_level,
            "review_deadline": review.review_deadline.isoformat(),
            "call_analysis": {
                "negotiation_outcome": review.call_analysis.negotiation_outcome,
                "final_rate": review.call_analysis.final_rate_mentioned,
                "enthusiasm_level": review.call_analysis.creator_enthusiasm_level,
                "objections": review.call_analysis.objections_raised,
                "key_quotes": review.call_analysis.key_quotes[:2]  # First 2 quotes
            },
            "campaign_context": review.campaign_context,
            "budget_constraints": review.budget_constraints
        }
        review_summaries.append(summary)
    
    return {
        "pending_reviews": len(review_summaries),
        "reviews": review_summaries
    }

@enhanced_campaign_router.post("/human-review/{negotiation_id}/decision")
async def submit_human_review_decision(
    negotiation_id: str,
    decision: HumanDecision,
    notes: Optional[str] = None
):
    """
    👤 Submit human review decision
    """
    
    try:
        unified_orchestrator.negotiation_manager.submit_human_decision(
            negotiation_id=negotiation_id,
            decision=decision,
            notes=notes or ""
        )
        
        return {
            "message": f"Human review decision submitted: {decision.value}",
            "negotiation_id": negotiation_id,
            "decision": decision.value,
            "submitted_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit human review: {str(e)}"
        )

# ================================
# SPONSOR APPROVAL ENDPOINTS
# ================================

@enhanced_campaign_router.get("/sponsor-approvals")
async def get_pending_sponsor_approvals():
    """
    📊 Get all pending sponsor approvals
    """
    
    pending_approvals = unified_orchestrator.negotiation_manager.sponsor_approval_queue
    
    approval_summaries = []
    for approval in pending_approvals:
        summary = {
            "campaign_id": approval.campaign_id,
            "total_cost": approval.total_cost,
            "recommended_influencers": approval.recommended_influencers,
            "expected_roi": approval.expected_roi,
            "approval_deadline": approval.approval_deadline.isoformat(),
            "approval_urls": {
                "approve": approval.approval_url,
                "reject": approval.rejection_url,
                "revise": approval.revision_url
            }
        }
        approval_summaries.append(summary)
    
    return {
        "pending_approvals": len(approval_summaries),
        "approvals": approval_summaries
    }

@enhanced_campaign_router.post("/sponsor-approval/{campaign_id}/{decision}")
async def submit_sponsor_decision(
    campaign_id: str,
    decision: str,  # approved, rejected, needs_revision
    notes: Optional[str] = None
):
    """
    📊 Submit sponsor approval decision
    """
    
    try:
        sponsor_decision = SponsorDecision(decision)
        
        unified_orchestrator.negotiation_manager.submit_sponsor_decision(
            negotiation_id=campaign_id,  # Using campaign_id as negotiation_id for simplicity
            decision=sponsor_decision,
            notes=notes or ""
        )
        
        return {
            "message": f"Sponsor decision submitted: {decision}",
            "campaign_id": campaign_id,
            "decision": decision,
            "submitted_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit sponsor decision: {str(e)}"
        )

# ================================
# CONTRACT MANAGEMENT ENDPOINTS
# ================================

@enhanced_campaign_router.get("/contracts")
async def get_all_contracts():
    """
    📝 Get all contracts and their status
    """
    
    pending_contracts = unified_orchestrator.contract_generator.get_pending_contracts()
    analytics = unified_orchestrator.contract_generator.get_contract_analytics()
    
    contract_summaries = []
    for contract in pending_contracts:
        summary = {
            "contract_id": contract.contract_id,
            "campaign_id": contract.campaign_id,
            "creator_info": contract.creator_info,
            "final_rate": contract.final_rate,
            "status": contract.status.value,
            "delivery_method": contract.delivery_method.value,
            "created_at": contract.created_at.isoformat(),
            "sent_at": contract.sent_at.isoformat() if contract.sent_at else None,
            "signed_at": contract.signed_at.isoformat() if contract.signed_at else None
        }
        contract_summaries.append(summary)
    
    return {
        "analytics": analytics,
        "contracts": contract_summaries
    }

@enhanced_campaign_router.get("/contracts/{contract_id}")
async def get_contract_details(contract_id: str):
    """
    📝 Get detailed contract information
    """
    
    contract = unified_orchestrator.contract_generator.get_contract_status(contract_id)
    
    if not contract:
        raise HTTPException(
            status_code=404,
            detail=f"Contract {contract_id} not found"
        )
    
    return {
        "contract": contract.dict(),
        "download_url": f"/api/enhanced/contracts/{contract_id}/download",
        "status_history": [
            {
                "status": contract.status.value,
                "timestamp": contract.created_at.isoformat()
            }
        ]
    }

@enhanced_campaign_router.get("/contracts/{contract_id}/download")
async def download_contract(contract_id: str):
    """
    📄 Download contract PDF
    """
    
    contract = unified_orchestrator.contract_generator.get_contract_status(contract_id)
    
    if not contract:
        raise HTTPException(
            status_code=404,
            detail=f"Contract {contract_id} not found"
        )
    
    # Return contract file
    file_path = f"contracts/{contract_id}.pdf"
    
    try:
        return FileResponse(
            path=file_path,
            filename=f"Contract_{contract_id}.pdf",
            media_type="application/pdf"
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Contract file not found"
        )

@enhanced_campaign_router.post("/contracts/{contract_id}/mark-signed")
async def mark_contract_signed(contract_id: str):
    """
    ✅ Mark contract as signed
    """
    
    try:
        unified_orchestrator.contract_generator.mark_contract_signed(
            contract_id=contract_id,
            signed_at=datetime.now()
        )
        
        return {
            "message": "Contract marked as signed",
            "contract_id": contract_id,
            "signed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to mark contract as signed: {str(e)}"
        )

# ================================
# SYSTEM STATUS ENDPOINTS
# ================================

@enhanced_campaign_router.get("/system-status")
async def get_enhanced_system_status():
    """
    🏥 Get comprehensive system status
    """
    
    active_workflows = unified_orchestrator.get_all_active_workflows()
    pending_reviews = unified_orchestrator.negotiation_manager.get_human_review_queue()
    pending_approvals = unified_orchestrator.negotiation_manager.sponsor_approval_queue
    contract_analytics = unified_orchestrator.contract_generator.get_contract_analytics()
    
    return {
        "system_status": "operational",
        "enhanced_features": {
            "unified_workflow": True,
            "multi_data_collection": True,
            "human_in_the_loop": True,
            "sponsor_approval": True,
            "automated_contracts": True,
            "real_time_monitoring": True
        },
        "workflow_metrics": {
            "active_workflows": len([w for w in active_workflows if w.current_phase.value not in ["completed", "failed"]]),
            "completed_workflows": len([w for w in active_workflows if w.current_phase.value == "completed"]),
            "total_workflows": len(active_workflows)
        },
        "approval_metrics": {
            "pending_human_reviews": len(pending_reviews),
            "pending_sponsor_approvals": len(pending_approvals)
        },
        "contract_metrics": contract_analytics,
        "data_collection_methods": [method.value for method in DataCollectionMethod],
        "selection_strategies": [strategy.value for strategy in InfluencerSelectionStrategy],
        "endpoints": {
            "start_workflow": "/api/enhanced/start-enhanced-workflow",
            "file_upload": "/api/enhanced/start-file-upload-workflow",
            "conversational": "/api/enhanced/start-conversational-workflow",
            "monitor_workflow": "/api/enhanced/workflow/{workflow_id}/status",
            "human_reviews": "/api/enhanced/human-reviews",
            "sponsor_approvals": "/api/enhanced/sponsor-approvals",
            "contracts": "/api/enhanced/contracts"
        }
    }

# ================================
# DEMO AND TESTING ENDPOINTS
# ================================

@enhanced_campaign_router.post("/demo/fitness-campaign")
async def create_demo_fitness_campaign(background_tasks: BackgroundTasks):
    """
    🧪 Create demo fitness campaign with enhanced workflow
    """
    
    demo_data = {
        "product_name": "Enhanced FitPro Smart Tracker",
        "brand_name": "TechFit Solutions",
        "product_description": "AI-powered fitness tracking device with real-time coaching, heart rate monitoring, sleep analysis, and personalized workout recommendations. Perfect for serious fitness enthusiasts looking to optimize their performance.",
        "target_audience": "Fitness enthusiasts, athletes, and health-conscious individuals aged 22-40 who value data-driven fitness optimization and are willing to invest in premium fitness technology.",
        "campaign_goal": "Launch new product with authentic creator partnerships and establish market presence in premium fitness tech segment",
        "product_niche": "fitness",
        "total_budget": 18000.0
    }
    
    config = WorkflowConfiguration(
        data_collection_method=DataCollectionMethod.MANUAL,
        selection_strategy=InfluencerSelectionStrategy.BUDGET_OPTIMIZED,
        max_influencers=4,
        require_human_review=True,
        require_sponsor_approval=True,
        auto_send_contracts=True
    )
    
    workflow_state = await unified_orchestrator.start_unified_campaign_workflow(
        initial_data=demo_data,
        configuration=config
    )
    
    return {
        "message": "🧪 Demo enhanced fitness campaign created",
        "workflow_id": workflow_state.workflow_id,
        "campaign_details": demo_data,
        "configuration": config.dict(),
        "monitor_url": f"/api/enhanced/workflow/{workflow_state.workflow_id}/status",
        "estimated_completion": "20-30 minutes with human approvals"
    }

@enhanced_campaign_router.post("/demo/beauty-campaign")
async def create_demo_beauty_campaign(background_tasks: BackgroundTasks):
    """
    🧪 Create demo beauty campaign with file upload simulation
    """
    
    demo_data = {
        "product_name": "LuxeGlow Vitamin C Serum",
        "brand_name": "RadiantSkin Beauty",
        "product_description": "Premium anti-aging vitamin C serum with hyaluronic acid and peptides for brightening, firming, and deep hydration. Clinically tested for all skin types, dermatologist recommended.",
        "target_audience": "Beauty enthusiasts and skincare lovers aged 25-45 interested in premium anti-aging and brightening products, willing to invest in high-quality skincare",
        "campaign_goal": "Increase brand awareness and drive sales in the premium skincare market through authentic beauty influencer partnerships",
        "product_niche": "beauty",
        "total_budget": 14000.0
    }
    
    config = WorkflowConfiguration(
        data_collection_method=DataCollectionMethod.MANUAL,  # Simulating file upload
        selection_strategy=InfluencerSelectionStrategy.ENGAGEMENT_FOCUSED,
        max_influencers=3,
        require_human_review=True,
        require_sponsor_approval=True,
        auto_send_contracts=True
    )
    
    workflow_state = await unified_orchestrator.start_unified_campaign_workflow(
        initial_data=demo_data,
        configuration=config
    )
    
    return {
        "message": "🧪 Demo enhanced beauty campaign created",
        "workflow_id": workflow_state.workflow_id,
        "data_source": "Simulated file upload processing",
        "monitor_url": f"/api/enhanced/workflow/{workflow_state.workflow_id}/status"
    }

# ================================
# LEGACY COMPATIBILITY
# ================================

@enhanced_campaign_router.post("/legacy-campaign-created")
async def handle_legacy_campaign_webhook(
    campaign_webhook: CampaignWebhook,
    background_tasks: BackgroundTasks
):
    """
    🔄 Legacy compatibility endpoint for existing campaign webhooks
    Automatically upgrades to enhanced workflow
    """
    
    # Convert legacy webhook to enhanced workflow
    initial_data = {
        "product_name": campaign_webhook.product_name,
        "brand_name": campaign_webhook.brand_name,
        "product_description": campaign_webhook.product_description,
        "target_audience": campaign_webhook.target_audience,
        "campaign_goal": campaign_webhook.campaign_goal,
        "product_niche": campaign_webhook.product_niche,
        "total_budget": campaign_webhook.total_budget
    }
    
    config = WorkflowConfiguration(
        data_collection_method=DataCollectionMethod.MANUAL,
        selection_strategy=InfluencerSelectionStrategy.BUDGET_OPTIMIZED,
        require_human_review=False,  # Legacy mode - auto-approve
        require_sponsor_approval=False,
        auto_send_contracts=True
    )
    
    workflow_state = await unified_orchestrator.start_unified_campaign_workflow(
        initial_data=initial_data,
        configuration=config
    )
    
    return {
        "message": "🔄 Legacy campaign upgraded to enhanced workflow",
        "workflow_id": workflow_state.workflow_id,
        "legacy_campaign_id": campaign_webhook.campaign_id,
        "upgrade_features": [
            "Enhanced influencer matching",
            "Structured negotiation analysis",
            "Automated contract generation",
            "Real-time progress monitoring"
        ],
        "monitor_url": f"/api/enhanced/workflow/{workflow_state.workflow_id}/status"
    }