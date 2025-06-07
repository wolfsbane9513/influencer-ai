# ====================================
# api/whatsapp/llm_parser.py
# ====================================

import json
import logging
from typing import Dict, Any, Optional, Tuple
from groq import AsyncGroq

from models.campaign import CampaignData
from config.settings import settings

logger = logging.getLogger(__name__)

class WhatsAppCampaignParser:
    """
    LLM-powered parser to extract campaign data from natural language
    """
    
    def __init__(self):
        self.groq_client = AsyncGroq(api_key=settings.groq_api_key)
        self.model = "llama-3.1-70b-versatile"  # Using your existing Groq setup
    
    async def parse_campaign_request(
        self, 
        user_message: str,
        conversation_history: list = None
    ) -> Tuple[Optional[CampaignData], str, bool]:
        """
        Parse natural language campaign request into structured CampaignData
        
        Returns:
            - CampaignData object (if complete)
            - Response message for user
            - is_complete flag
        """
        try:
            # Build conversation context
            conversation_context = self._build_conversation_context(
                user_message, 
                conversation_history or []
            )
            
            # Extract campaign parameters with LLM
            extraction_result = await self._extract_campaign_parameters(conversation_context)
            
            # Check if we have enough info to create campaign
            if extraction_result["is_complete"]:
                campaign_data = self._create_campaign_data(extraction_result["parameters"])
                return campaign_data, extraction_result["response"], True
            else:
                # Need more information - ask clarifying questions
                return None, extraction_result["response"], False
                
        except Exception as e:
            logger.error(f"❌ Campaign parsing error: {e}")
            return None, "Sorry, I had trouble understanding your request. Could you rephrase it?", False
    
    def _build_conversation_context(self, current_message: str, history: list) -> str:
        """Build conversation context for LLM"""
        context = ""
        
        # Add conversation history
        for msg in history[-3:]:  # Last 3 exchanges for context
            context += f"User: {msg.get('user', '')}\nAI: {msg.get('ai', '')}\n"
        
        # Add current message
        context += f"User: {current_message}\n"
        
        return context
    
    async def _extract_campaign_parameters(self, conversation_context: str) -> Dict[str, Any]:
        """Use LLM to extract campaign parameters"""
        
        system_prompt = """You are an expert campaign manager for influencer marketing. 
        Extract campaign parameters from user messages and determine if you have enough information to start a campaign.

        Required parameters for a complete campaign:
        - product_name: What product/service is being promoted
        - brand_name: The brand behind the campaign  
        - target_audience: Who should see this campaign
        - campaign_goal: What the campaign should achieve
        - product_niche: Category/industry (fitness, tech, fashion, etc.)
        - total_budget: Budget in USD
        - creator_count: How many creators needed (can estimate if not specified)

        Optional parameters that enhance the campaign:
        - product_description: Detailed description
        - deliverables: What creators should produce (posts, videos, etc.)
        - timeline: When campaign should run
        - platform_focus: Instagram, TikTok, YouTube preference

        Respond in JSON format:
        {
            "is_complete": boolean,
            "parameters": {
                "product_name": "string or null",
                "brand_name": "string or null", 
                "target_audience": "string or null",
                "campaign_goal": "string or null",
                "product_niche": "string or null",
                "total_budget": number or null,
                "creator_count": number or null,
                "product_description": "string or null",
                "deliverables": "string or null",
                "timeline": "string or null",
                "platform_focus": "string or null"
            },
            "missing_fields": ["list of missing required fields"],
            "response": "Natural response to user - either confirming details or asking for missing info"
        }

        Examples:
        User: "Get me 20 fitness creators, budget $15K for protein powder launch"
        → Ask for brand name, target audience details, campaign goals

        User: "Find tech reviewers for smartphone campaign, target Gen-Z"  
        → Ask for budget, specific product name, how many creators needed

        User: "Nike AF1 campaign, 50 creators, $10K budget, sneakerheads 18-30"
        → This might be complete! Confirm details and proceed.
        """
        
        try:
            response = await self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": conversation_context}
                ],
                model=self.model,
                temperature=0.1,
                max_tokens=1000
            )
            
            # Parse LLM response
            response_text = response.choices[0].message.content.strip()
            
            # Handle potential JSON formatting issues
            if response_text.startswith("```json"):
                response_text = response_text.split("```json")[1].split("```")[0]
            elif response_text.startswith("```"):
                response_text = response_text.split("```")[1].split("```")[0]
            
            result = json.loads(response_text)
            
            logger.info(f"✅ LLM extraction completed: {result['is_complete']}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parsing error: {e}")
            return {
                "is_complete": False,
                "parameters": {},
                "missing_fields": ["all"],
                "response": "I need more details about your campaign. Could you tell me the product name, budget, and target audience?"
            }
        except Exception as e:
            logger.error(f"❌ LLM extraction error: {e}")
            return {
                "is_complete": False,
                "parameters": {},
                "missing_fields": ["all"], 
                "response": "Could you provide more details about your campaign? I need the product, budget, and target audience to get started."
            }
    
    def _create_campaign_data(self, parameters: Dict[str, Any]) -> CampaignData:
        """Convert parsed parameters to CampaignData object"""
        
        # Map to your existing CampaignData structure
        campaign_data = CampaignData(
            product_name=parameters.get("product_name", "Unknown Product"),
            brand_name=parameters.get("brand_name", "Unknown Brand"),
            product_description=parameters.get("product_description") or f"Campaign for {parameters.get('product_name', 'product')}",
            target_audience=parameters.get("target_audience", "General audience"),
            campaign_goal=parameters.get("campaign_goal", "Increase brand awareness"),
            product_niche=parameters.get("product_niche", "general"),
            total_budget=float(parameters.get("total_budget", 10000))
        )
        
        logger.info(f"✅ Created CampaignData: {campaign_data.product_name} - ${campaign_data.total_budget}")
        return campaign_data

# ====================================
# api/whatsapp/enhanced_message_handler.py
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
from agents.enhanced_orchestrator import EnhancedCampaignOrchestrator

logger = logging.getLogger(__name__)

class EnhancedWhatsAppConversationHandler:
    """
    Enhanced conversation handler with LLM integration
    """
    
    def __init__(self):
        self.response_service = WhatsAppResponseService()
        self.state_manager = ConversationStateManager()
        self.llm_parser = WhatsAppCampaignParser()
        self.orchestration_bridge = OrchestrationBridge()
    
    async def process_message(
        self, 
        message: WhatsAppMessage, 
        phone_number_id: str
    ):
        """
        Process incoming WhatsApp message with LLM intelligence
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
                # Campaign is running, handle status requests
                await self._handle_status_request(user_phone, message_text, conversation_state)
            else:
                # Default handler
                await self._handle_general_message(user_phone, message_text, conversation_state)
                
        except Exception as e:
            logger.error(f"❌ Message processing error: {e}")
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

I can run complete influencer campaigns for you. Just tell me what you need:

Examples:
• "Get me 20 fitness creators, budget $15K for protein powder launch"
• "Find tech reviewers for iPhone campaign, target Gen-Z, $25K budget"
• "50 fashion influencers for Nike sneakers, budget $10K, focus on sneakerheads"

What campaign can I help you with?"""
            
            await self.response_service.send_message(user_phone, welcome_message)
    
    async def _handle_campaign_input_with_llm(
        self, 
        user_phone: str, 
        message_text: str, 
        conversation_state
    ):
        """Handle campaign input with LLM parsing"""
        
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
            # We have enough info to start the campaign!
            await self._launch_campaign(user_phone, campaign_data, conversation_state)
        else:
            # Continue gathering information
            await self.state_manager.update_conversation_stage(
                user_phone, 
                "campaign_input",
                conversation_state.campaign_data
            )
    
    async def _launch_campaign(
        self, 
        user_phone: str, 
        campaign_data: CampaignData, 
        conversation_state
    ):
        """Launch campaign using existing orchestration"""
        
        try:
            # Generate unique campaign ID
            campaign_id = str(uuid.uuid4())
            
            # Send confirmation message
            confirmation_msg = f"""🚀 Perfect! Launching your campaign:

**{campaign_data.product_name}** by {campaign_data.brand_name}
💰 Budget: ${campaign_data.total_budget:,.0f}
🎯 Target: {campaign_data.target_audience}
🏷️ Niche: {campaign_data.product_niche}

I'm now finding creators and will update you every step of the way!"""
            
            await self.response_service.send_message(user_phone, confirmation_msg)
            
            # Update conversation state
            await self.state_manager.update_conversation_stage(
                user_phone,
                "orchestration_running", 
                {"campaign_data": campaign_data.dict(), "campaign_id": campaign_id},
                campaign_id
            )
            
            # Trigger existing orchestration system
            await self.orchestration_bridge.launch_campaign(
                campaign_data, 
                campaign_id,
                user_phone,  # For progress updates
                self.response_service
            )
            
        except Exception as e:
            logger.error(f"❌ Campaign launch error: {e}")
            await self.response_service.send_message(
                user_phone,
                "Sorry, there was an issue launching your campaign. Please try again."
            )
    
    async def _handle_approval_response(
        self, 
        user_phone: str, 
        message_text: str, 
        conversation_state
    ):
        """Handle user approval responses during campaign"""
        
        # Parse approval response
        approved_items = self._parse_approval_response(message_text)
        
        if approved_items:
            await self.response_service.send_message(
                user_phone,
                f"✅ Got your approval for items: {', '.join(map(str, approved_items))}\n\nContinuing with the campaign..."
            )
            
            # Continue orchestration with approved items
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
        """Handle status requests during campaign execution"""
        
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
                "Your campaign is running! Type 'status' for updates or 'new campaign' to start fresh."
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
                "I'm here to help with influencer campaigns! Type 'new campaign' to start fresh or 'status' for updates."
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

# ====================================
# api/whatsapp/orchestration_bridge.py
# ====================================

import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from models.campaign import CampaignData
from agents.enhanced_orchestrator import CampaignOrchestrator  # Your existing orchestrator
from .response_service import WhatsAppResponseService

logger = logging.getLogger(__name__)

class OrchestrationBridge:
    """
    Bridge between WhatsApp conversation and existing orchestration system
    """
    
    def __init__(self):
        self.active_campaigns: Dict[str, CampaignOrchestrator] = {}
    
    async def launch_campaign(
        self,
        campaign_data: CampaignData,
        campaign_id: str,
        user_phone: str,
        response_service: WhatsAppResponseService
    ):
        """
        Launch campaign using existing orchestration system
        """
        try:
            logger.info(f"🚀 Launching campaign {campaign_id} for {user_phone}")
            
            # Create orchestrator instance
            orchestrator = CampaignOrchestrator()
            self.active_campaigns[campaign_id] = orchestrator
            
            # Set up progress callback for WhatsApp updates
            async def whatsapp_progress_callback(stage: str, message: str, data: Dict[str, Any] = None):
                await self._send_progress_update(user_phone, stage, message, data, response_service)
            
            # Launch campaign with progress updates
            await self._run_campaign_with_updates(
                orchestrator,
                campaign_data,
                campaign_id,
                whatsapp_progress_callback
            )
            
        except Exception as e:
            logger.error(f"❌ Campaign launch error: {e}")
            await response_service.send_message(
                user_phone,
                f"❌ Campaign launch failed: {str(e)}"
            )
    
    async def _run_campaign_with_updates(
        self,
        orchestrator: CampaignOrchestrator,
        campaign_data: CampaignData,
        campaign_id: str,
        progress_callback
    ):
        """
        Run campaign orchestration with progress updates
        """
        try:
            # Discovery phase
            await progress_callback("discovery", "🔍 Starting creator discovery...")
            
            # This triggers your existing orchestration
            # You'll need to modify your orchestrator to accept callbacks
            result = await orchestrator.run_campaign(
                campaign_data,
                progress_callback=progress_callback
            )
            
            await progress_callback("completed", f"✅ Campaign completed! {result.get('summary', '')}")
            
        except Exception as e:
            logger.error(f"❌ Orchestration error: {e}")
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
            elif stage == "negotiation":
                formatted_message = f"💬 **Negotiation Phase**\n{message}"
            elif stage == "approval_needed":
                # This triggers approval workflow
                formatted_message = self._format_approval_request(message, data)
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
        Handle user approval and continue orchestration
        """
        if campaign_id in self.active_campaigns:
            orchestrator = self.active_campaigns[campaign_id]
            # Continue orchestration with approved items
            # This will depend on your existing orchestrator structure
            await orchestrator.handle_approval(approved_items)
    
    async def get_campaign_status(self, campaign_id: str) -> str:
        """
        Get current campaign status
        """
        if campaign_id in self.active_campaigns:
            orchestrator = self.active_campaigns[campaign_id]
            status = await orchestrator.get_status()
            return f"📊 **Campaign Status**\n{status}"
        else:
            return "📊 **Campaign Status**\nNo active campaign found. Type 'new campaign' to start fresh."