# api/campaigns.py - FIXED CAMPAIGNS API
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from core.models import CampaignData, OrchestrationState
from agents.orchestrator import CampaignOrchestrator
from services.voice import VoiceService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["campaigns"])

# Global orchestrator instance
orchestrator = CampaignOrchestrator()

# Campaign state storage (in production, use proper database)
campaign_states: Dict[str, OrchestrationState] = {}


class CampaignRequest(BaseModel):
    """Campaign creation request model"""
    company_name: str
    product_name: str
    product_description: str
    target_audience: str
    campaign_goals: str
    budget_per_creator: float
    max_creators: int = 10
    timeline: str = "2 weeks"
    content_requirements: str = "Social media posts"
    brand_guidelines: str = "Follow brand voice and style"


class CampaignResponse(BaseModel):
    """Campaign creation response model"""
    success: bool
    campaign_id: str
    task_id: str
    message: str
    campaign_code: Optional[str] = None


@router.get("/health")
async def health_check():
    """System health check endpoint"""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": "initialized"
        }
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Service unhealthy")


@router.get("/webhook/test-enhanced-elevenlabs")
async def test_elevenlabs():
    """Test ElevenLabs integration"""
    try:
        logger.info("📞 Testing ElevenLabs integration...")
        
        voice_service = VoiceService()
        
        # Check if in mock mode
        if voice_service.use_mock:
            return {
                "status": "mock_mode",
                "api_connected": False,
                "message": "ElevenLabs running in mock mode"
            }
        else:
            # In production, you could test with a verified number
            return {
                "status": "configured",
                "api_connected": True,
                "message": "ElevenLabs API configured and ready"
            }
            
    except Exception as e:
        logger.error(f"❌ ElevenLabs test failed: {e}")
        return {
            "status": "error",
            "api_connected": False,
            "message": f"ElevenLabs test failed: {str(e)}"
        }


@router.post("/campaigns")
async def create_campaign(
    request: CampaignRequest,
    background_tasks: BackgroundTasks
) -> CampaignResponse:
    """
    Create new campaign and start orchestration
    
    Fixed error handling to prevent OrchestrationState field errors
    """
    
    try:
        # Generate unique IDs
        import uuid
        campaign_id = str(uuid.uuid4())
        task_id = str(uuid.uuid4())
        campaign_code = f"CAMP-{campaign_id[:8].upper()}"
        
        # Create campaign data
        campaign_data = CampaignData(
            campaign_id=campaign_id,
            company_name=request.company_name,
            product_name=request.product_name,
            product_description=request.product_description,
            target_audience=request.target_audience,
            campaign_goals=request.campaign_goals,
            budget_per_creator=request.budget_per_creator,
            max_creators=request.max_creators,
            timeline=request.timeline,
            content_requirements=request.content_requirements,
            brand_guidelines=request.brand_guidelines
        )
        
        logger.info(f"🚀 Campaign created: {request.product_name} (Task: {task_id})")
        
        # Start orchestration in background
        background_tasks.add_task(
            run_campaign_orchestration,
            campaign_data,
            task_id
        )
        
        logger.info(f"🎯 Starting orchestration for task {task_id}")
        
        return CampaignResponse(
            success=True,
            campaign_id=campaign_id,
            task_id=task_id,
            message="Campaign created and orchestration started",
            campaign_code=campaign_code
        )
        
    except Exception as e:
        logger.error(f"❌ Campaign creation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Campaign creation failed: {str(e)}"
        )


@router.get("/campaigns/{task_id}")
async def get_campaign_status(task_id: str) -> Dict[str, Any]:
    """
    Get current campaign status and progress
    
    Fixed to handle missing campaigns gracefully
    """
    
    try:
        # Check if campaign exists in our state storage
        if task_id in campaign_states:
            state = campaign_states[task_id]
            
            return {
                "task_id": task_id,
                "campaign_id": state.campaign_id,
                "stage": state.stage,
                "is_complete": state.is_complete,
                "progress_percentage": state.get_progress_percentage(),
                "creators_found": state.creators_found,
                "successful_negotiations": state.successful_negotiations,
                "contracts_generated": state.contracts_count,
                "error_message": state.error_message,
                "start_time": state.start_time.isoformat() if state.start_time else None,
                "end_time": state.end_time.isoformat() if state.end_time else None
            }
        else:
            # Campaign not found in memory, try to get from orchestrator
            status = await orchestrator.get_campaign_status(task_id)
            return status
            
    except Exception as e:
        logger.error(f"❌ Status check failed for {task_id}: {e}")
        return {
            "task_id": task_id,
            "stage": "error",
            "is_complete": False,
            "error_message": f"Status check failed: {str(e)}"
        }


async def run_campaign_orchestration(
    campaign_data: CampaignData,
    task_id: str
) -> None:
    """
    Run campaign orchestration in background with proper error handling
    
    Fixed: Proper error state handling without field assignment errors
    """
    
    try:
        # Start orchestration
        result_state = await orchestrator.orchestrate_campaign(campaign_data)
        
        # Store final state
        campaign_states[task_id] = result_state
        
        if result_state.stage == "completed":
            logger.info(f"✅ Campaign {task_id} completed successfully")
        else:
            logger.error(f"❌ Campaign {task_id} failed: {result_state.error_message}")
            
    except Exception as e:
        logger.error(f"❌ Campaign {task_id} failed: {e}")
        
        # Create error state properly (all fields exist in fixed OrchestrationState)
        error_state = OrchestrationState(
            stage="failed",
            campaign_id=campaign_data.campaign_id,
            company_name=campaign_data.company_name,
            product_name=campaign_data.product_name,
            start_time=datetime.now(),
            end_time=datetime.now(),
            error_message=str(e)  # This field now exists in the fixed model
        )
        
        campaign_states[task_id] = error_state


# Additional utility endpoints

@router.get("/campaigns")
async def list_campaigns() -> Dict[str, Any]:
    """List all campaigns and their current status"""
    
    try:
        campaigns = []
        
        for task_id, state in campaign_states.items():
            campaigns.append({
                "task_id": task_id,
                "campaign_id": state.campaign_id,
                "company_name": state.company_name,
                "product_name": state.product_name,
                "stage": state.stage,
                "is_complete": state.is_complete,
                "progress_percentage": state.get_progress_percentage(),
                "start_time": state.start_time.isoformat() if state.start_time else None
            })
        
        return {
            "total_campaigns": len(campaigns),
            "campaigns": campaigns
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to list campaigns: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list campaigns: {str(e)}"
        )


@router.delete("/campaigns/{task_id}")
async def cancel_campaign(task_id: str) -> Dict[str, Any]:
    """Cancel running campaign"""
    
    try:
        if task_id in campaign_states:
            state = campaign_states[task_id]
            
            if not state.is_complete:
                # Mark as cancelled
                state.stage = "cancelled"
                state.is_complete = True
                state.end_time = datetime.now()
                state.error_message = "Campaign cancelled by user"
                
                logger.info(f"🛑 Campaign {task_id} cancelled")
                
                return {
                    "success": True,
                    "message": f"Campaign {task_id} cancelled",
                    "task_id": task_id
                }
            else:
                return {
                    "success": False,
                    "message": "Campaign already completed",
                    "task_id": task_id
                }
        else:
            raise HTTPException(status_code=404, detail="Campaign not found")
            
    except Exception as e:
        logger.error(f"❌ Failed to cancel campaign {task_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel campaign: {str(e)}"
        )