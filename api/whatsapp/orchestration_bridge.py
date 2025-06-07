# ====================================
# api/whatsapp/orchestration_bridge.py - UPDATED POST CLEANUP
# ====================================

import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from models.campaign import CampaignData
from agents.enhanced_orchestrator import EnhancedCampaignOrchestrator  # UPDATED: Enhanced only
from .response_service import WhatsAppResponseService

logger = logging.getLogger(__name__)

class OrchestrationBridge:
    """
    Bridge between WhatsApp conversation and enhanced orchestration system
    Updated to use only enhanced/production agents after cleanup
    """
    
    def __init__(self):
        self.active_campaigns: Dict[str, EnhancedCampaignOrchestrator] = {}
    
    async def launch_campaign(
        self,
        campaign_data: CampaignData,
        campaign_id: str,
        user_phone: str,
        response_service: WhatsAppResponseService
    ):
        """
        Launch campaign using enhanced orchestration system
        """
        try:
            logger.info(f"🚀 Launching enhanced campaign {campaign_id} for {user_phone}")
            
            # Create enhanced orchestrator instance
            orchestrator = EnhancedCampaignOrchestrator()  # Using enhanced version
            self.active_campaigns[campaign_id] = orchestrator
            
            # Set up progress callback for WhatsApp updates
            async def whatsapp_progress_callback(stage: str, message: str, data: Dict[str, Any] = None):
                await self._send_progress_update(user_phone, stage, message, data, response_service)
            
            # Launch enhanced campaign with progress updates
            await self._run_enhanced_campaign_with_updates(
                orchestrator,
                campaign_data,
                campaign_id,
                whatsapp_progress_callback
            )
            
        except Exception as e:
            logger.error(f"❌ Enhanced campaign launch error: {e}")
            await response_service.send_message(
                user_phone,
                f"❌ Campaign launch failed: {str(e)}"
            )
    
    async def _run_enhanced_campaign_with_updates(
        self,
        orchestrator: EnhancedCampaignOrchestrator,
        campaign_data: CampaignData,
        campaign_id: str,
        progress_callback
    ):
        """
        Run enhanced campaign orchestration with progress updates
        """
        try:
            # Convert to enhanced orchestration state
            from models.campaign import CampaignOrchestrationState
            
            orchestration_state = CampaignOrchestrationState(
                campaign_id=campaign_data.id,
                campaign_data=campaign_data
            )
            
            # Discovery phase
            await progress_callback("discovery", "🔍 Starting enhanced creator discovery...")
            
            # Run enhanced orchestration with task ID
            result = await orchestrator.orchestrate_enhanced_campaign(
                orchestration_state,
                campaign_id  # task_id for monitoring
            )
            
            # Format completion message
            summary = result.get_campaign_summary()
            completion_msg = f"""🎉 Campaign completed successfully!
            
📊 **Results:**
• Successful partnerships: {summary['successful_partnerships']}
• Total cost: ${summary['spent_amount']:,.0f}
• Success rate: {summary['success_rate']}
• Duration: {summary['duration']}

Your campaign is now live! 🚀"""
            
            await progress_callback("completed", completion_msg)
            
        except Exception as e:
            logger.error(f"❌ Enhanced orchestration error: {e}")
            await progress_callback("error", f"❌ Campaign error: {str(e)}")
        finally:
            # Cleanup
            if campaign_id in self.active_campaigns:
                del self.active_campaigns[campaign_id]
    
    async def _send_progress_update(
        self,
        user_phone: str,
        stage: str,
        message: str,
        data: Dict[str, Any],
        response_service: WhatsAppResponseService
    ):
        """
        Send formatted progress update to WhatsApp
        """
        try:
            # Format update based on stage
            if stage == "discovery":
                formatted_message = f"🔍 **Discovery Phase**\n{message}"
            elif stage == "negotiations":
                formatted_message = f"💬 **Negotiation Phase**\n{message}"
            elif stage == "approval_needed":
                # This triggers approval workflow
                formatted_message = self._format_approval_request(message, data)
            elif stage == "contracts":
                formatted_message = f"📝 **Contract Phase**\n{message}"
            elif stage == "completed":
                formatted_message = f"🎉 **Campaign Complete**\n{message}"
            else:
                formatted_message = message
            
            await response_service.send_message(user_phone, formatted_message)
            
        except Exception as e:
            logger.error(f"❌ Progress update error: {e}")
    
    def _format_approval_request(self, message: str, data: Dict[str, Any]) -> str:
        """
        Format approval request for WhatsApp
        """
        if not data or "creators" not in data:
            return message
        
        creators = data["creators"]
        approval_text = f"📋 **Approval Needed**\n{message}\n\n"
        
        for i, creator in enumerate(creators[:10], 1):  # Max 10 for readability
            name = creator.get("name", "Unknown")
            followers = creator.get("followers", "Unknown")
            rate = creator.get("rate", "TBD")
            approval_text += f"{i}. **{name}** ({followers} followers) - ${rate}\n"
        
        approval_text += f"\nReply with numbers to approve (e.g., '1,3,5') or 'all' to approve everyone."
        
        return approval_text
    
    async def handle_approval(
        self,
        campaign_id: str,
        approved_items: list,
        user_phone: str,
        response_service: WhatsAppResponseService
    ):
        """
        Handle user approval and continue enhanced orchestration
        """
        if campaign_id in self.active_campaigns:
            orchestrator = self.active_campaigns[campaign_id]
            # Enhanced orchestrator handles approvals differently
            # You may need to modify the enhanced orchestrator to support mid-flow approvals
            logger.info(f"📋 Approved items for campaign {campaign_id}: {approved_items}")
    
    async def get_campaign_status(self, campaign_id: str) -> str:
        """
        Get current enhanced campaign status
        """
        # Check active campaigns tracker from main.py
        from main import active_campaigns
        
        if campaign_id in active_campaigns:
            state = active_campaigns[campaign_id]
            summary = state.get_progress_summary()
            
            status_msg = f"""📊 **Campaign Status**

🎯 **{summary['campaign_id']}**
📍 Stage: {summary['current_stage']}
👥 Discovered: {summary['discovered_count']} creators
✅ Successful: {summary['successful']} negotiations
❌ Failed: {summary['failed']} negotiations
💰 Cost so far: ${summary['total_cost']:,.0f}
⏱️ Duration: {summary['duration_minutes']:.1f} minutes

{f"🔄 Currently: {summary['current_influencer']}" if summary.get('current_influencer') else ""}"""
            
            return status_msg
        else:
            return "📊 **Campaign Status**\nNo active campaign found. Type 'new campaign' to start fresh."
