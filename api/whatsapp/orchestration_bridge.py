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

# ====================================
# api/whatsapp/enhanced_message_handler.py - UPDATED POST CLEANUP
# ====================================

import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from models.whatsapp import WhatsAppMessage
from models.campaign import CampaignData
from .response_service import WhatsAppResponseService
from .conversation_state import ConversationStateManager
from .llm_parser import WhatsAppCampaignParser
from .orchestration_bridge import OrchestrationBridge

logger = logging.getLogger(__name__)

class EnhancedWhatsAppConversationHandler:
    """
    Enhanced conversation handler with LLM integration
    Updated to work with cleaned up enhanced-only codebase
    """
    
    def __init__(self):
        self.response_service = WhatsAppResponseService()
        self.state_manager = ConversationStateManager()
        self.llm_parser = WhatsAppCampaignParser()
        self.orchestration_bridge = OrchestrationBridge()  # Uses enhanced orchestrator
    
    async def process_message(
        self, 
        message: WhatsAppMessage, 
        phone_number_id: str
    ):
        """
        Process incoming WhatsApp message with enhanced LLM intelligence
        """
        try:
            user_phone = message.from_number
            message_text = self._extract_message_text(message)
            
            logger.info(f"📱 Processing message from {user_phone}: {message_text[:50]}...")
            
            # Get conversation state
            conversation_state = await self.state_manager.get_conversation_state(user_phone)
            
            # Route message based on conversation state
            if conversation_state is None:
                # New conversation
                await self._handle_new_conversation(user_phone, message_text)
            elif conversation_state.stage == "campaign_input":
                # Building campaign requirements with LLM
                await self._handle_campaign_input_with_llm(user_phone, message_text, conversation_state)
            elif conversation_state.stage == "approval_pending":
                # User is approving creators/decisions
                await self._handle_approval_response(user_phone, message_text, conversation_state)
            elif conversation_state.stage == "orchestration_running":
                # Enhanced campaign is running, handle status requests
                await self._handle_status_request(user_phone, message_text, conversation_state)
            else:
                # Default handler
                await self._handle_general_message(user_phone, message_text, conversation_state)
                
        except Exception as e:
            logger.error(f"❌ Enhanced message processing error: {e}")
            await self.response_service.send_message(
                user_phone,
                "Sorry, I encountered an error. Please try again or type 'restart' for a fresh start."
            )
    
    def _extract_message_text(self, message: WhatsAppMessage) -> str:
        """Extract text from WhatsApp message"""
        if message.type == "text":
            return message.text.body
        elif message.type == "document":
            return f"[Document: {message.document.filename}]"
        else:
            return f"[{message.type.upper()} message]"
    
    async def _handle_new_conversation(self, user_phone: str, message_text: str):
        """Handle new conversation with immediate LLM parsing"""
        
        # Create new conversation state
        conversation_state = await self.state_manager.create_conversation(user_phone)
        
        # Try to parse the initial message immediately
        if len(message_text) > 20:  # Substantial campaign request
            await self._handle_campaign_input_with_llm(user_phone, message_text, conversation_state)
        else:
            # Send welcome message for short messages
            welcome_message = """🎯 Welcome to InfluencerFlow AI!

I can run complete influencer campaigns for you using our enhanced AI system. Just tell me what you need:

**Examples:**
• "Get me 20 fitness creators, budget $15K for protein powder launch"
• "Find tech reviewers for iPhone campaign, target Gen-Z, $25K budget" 
• "50 fashion influencers for Nike sneakers, budget $10K, focus on sneakerheads"

What campaign can I help you with? 🚀"""
            
            await self.response_service.send_message(user_phone, welcome_message)
    
    async def _handle_campaign_input_with_llm(
        self, 
        user_phone: str, 
        message_text: str, 
        conversation_state
    ):
        """Handle campaign input with enhanced LLM parsing"""
        
        # Get conversation history for context
        conversation_history = conversation_state.campaign_data.get("conversation_history", []) if conversation_state.campaign_data else []
        
        # Parse with LLM
        campaign_data, ai_response, is_complete = await self.llm_parser.parse_campaign_request(
            message_text,
            conversation_history
        )
        
        # Update conversation history
        new_history_entry = {"user": message_text, "ai": ai_response}
        if conversation_state.campaign_data:
            conversation_state.campaign_data.setdefault("conversation_history", []).append(new_history_entry)
        else:
            conversation_state.campaign_data = {"conversation_history": [new_history_entry]}
        
        # Send AI response
        await self.response_service.send_message(user_phone, ai_response)
        
        if is_complete:
            # We have enough info to start the enhanced campaign!
            await self._launch_enhanced_campaign(user_phone, campaign_data, conversation_state)
        else:
            # Continue gathering information
            await self.state_manager.update_conversation_stage(
                user_phone, 
                "campaign_input",
                conversation_state.campaign_data
            )
    
    async def _launch_enhanced_campaign(
        self, 
        user_phone: str, 
        campaign_data: CampaignData, 
        conversation_state
    ):
        """Launch enhanced campaign using enhanced orchestration"""
        
        try:
            # Generate unique campaign ID
            campaign_id = str(uuid.uuid4())
            
            # Send confirmation message
            confirmation_msg = f"""🚀 Perfect! Launching your enhanced campaign:

**{campaign_data.product_name}** by {campaign_data.brand_name}
💰 Budget: ${campaign_data.total_budget:,.0f}
🎯 Target: {campaign_data.target_audience}
🏷️ Niche: {campaign_data.product_niche}

I'm now using our enhanced AI system to find creators and will update you every step of the way! ⚡"""
            
            await self.response_service.send_message(user_phone, confirmation_msg)
            
            # Update conversation state
            await self.state_manager.update_conversation_stage(
                user_phone,
                "orchestration_running", 
                {"campaign_data": campaign_data.dict(), "campaign_id": campaign_id},
                campaign_id
            )
            
            # Trigger enhanced orchestration system
            await self.orchestration_bridge.launch_campaign(
                campaign_data, 
                campaign_id,
                user_phone,  # For progress updates
                self.response_service
            )
            
        except Exception as e:
            logger.error(f"❌ Enhanced campaign launch error: {e}")
            await self.response_service.send_message(
                user_phone,
                "Sorry, there was an issue launching your enhanced campaign. Please try again."
            )
    
    async def _handle_approval_response(
        self, 
        user_phone: str, 
        message_text: str, 
        conversation_state
    ):
        """Handle user approval responses during enhanced campaign"""
        
        # Parse approval response
        approved_items = self._parse_approval_response(message_text)
        
        if approved_items:
            await self.response_service.send_message(
                user_phone,
                f"✅ Got your approval for items: {', '.join(map(str, approved_items))}\n\nContinuing with the enhanced campaign..."
            )
            
            # Continue enhanced orchestration with approved items
            await self.orchestration_bridge.handle_approval(
                conversation_state.task_id,
                approved_items,
                user_phone,
                self.response_service
            )
        else:
            await self.response_service.send_message(
                user_phone,
                "I didn't understand your selection. Please reply with numbers (e.g., '1,3,5') or 'all' to approve everything."
            )
    
    async def _handle_status_request(
        self, 
        user_phone: str, 
        message_text: str, 
        conversation_state
    ):
        """Handle status requests during enhanced campaign execution"""
        
        if "status" in message_text.lower():
            status = await self.orchestration_bridge.get_campaign_status(conversation_state.task_id)
            await self.response_service.send_message(user_phone, status)
        elif "new" in message_text.lower() and "campaign" in message_text.lower():
            # Start new campaign
            await self.state_manager.clear_conversation(user_phone)
            await self._handle_new_conversation(user_phone, "")
        else:
            await self.response_service.send_message(
                user_phone,
                "Your enhanced campaign is running! Type 'status' for updates or 'new campaign' to start fresh."
            )
    
    async def _handle_general_message(
        self, 
        user_phone: str, 
        message_text: str, 
        conversation_state
    ):
        """Handle general conversation"""
        
        if "restart" in message_text.lower() or "new" in message_text.lower():
            await self.state_manager.clear_conversation(user_phone)
            await self._handle_new_conversation(user_phone, "")
        else:
            await self.response_service.send_message(
                user_phone,
                "I'm here to help with enhanced influencer campaigns! Type 'new campaign' to start fresh or 'status' for updates."
            )
    
    def _parse_approval_response(self, message_text: str) -> list:
        """Parse user approval response"""
        import re
        
        message_lower = message_text.lower()
        
        # Handle "all" or "approve all"
        if "all" in message_lower:
            return ["all"]
        
        # Handle "none" or "reject all"  
        if "none" in message_lower or "reject" in message_lower:
            return ["none"]
        
        # Extract numbers for "1,3,5" format
        numbers = re.findall(r'\b\d+\b', message_text)
        return [int(n) for n in numbers] if numbers else []