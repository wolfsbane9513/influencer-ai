# services/whatsapp_ai.py
import asyncio
import logging
import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
import requests
from pathlib import Path

from groq import Groq
from config.settings import settings

logger = logging.getLogger(__name__)

class WhatsAppAIService:
    """
    🎯 WHATSAPP AI SERVICE - Conversational Campaign Management
    
    Core Features:
    - Natural language campaign creation
    - Document upload and parsing
    - Autonomous workflow execution
    - Human-like conversation flow
    - End-to-end campaign management via chat
    """
    
    def __init__(self):
        self.groq_client = Groq(api_key=settings.groq_api_key) if settings.groq_api_key else None
        self.whatsapp_token = getattr(settings, 'whatsapp_token', None)
        self.whatsapp_phone_id = getattr(settings, 'whatsapp_phone_id', None)
        self.base_url = "https://graph.facebook.com/v18.0"
        
        # Conversation state management
        self.user_sessions = {}
        
        # AI Personality
        self.ai_personality = {
            "name": "Alex",
            "style": "Professional but friendly, gets things done",
            "tone": "Confident, efficient, human-like",
            "expertise": "Influencer marketing campaigns"
        }
        
    async def handle_whatsapp_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        📱 Main WhatsApp message handler - processes all incoming messages
        """
        
        try:
            # Extract message details
            user_phone = message_data.get("from", "")
            message_text = message_data.get("text", {}).get("body", "")
            message_type = message_data.get("type", "text")
            
            logger.info(f"📱 WhatsApp message from {user_phone}: {message_text[:50]}...")
            
            # Handle different message types
            if message_type == "text":
                response = await self._handle_text_message(user_phone, message_text)
            elif message_type == "document":
                response = await self._handle_document_upload(user_phone, message_data.get("document", {}))
            elif message_type == "interactive":
                response = await self._handle_interactive_response(user_phone, message_data.get("interactive", {}))
            else:
                response = await self._handle_unsupported_message(user_phone, message_type)
            
            # Send response back to user
            await self._send_whatsapp_message(user_phone, response)
            
            return {"status": "processed", "response_sent": True}
            
        except Exception as e:
            logger.error(f"❌ WhatsApp message handling failed: {e}")
            await self._send_error_message(user_phone, "Sorry, something went wrong. Please try again.")
            return {"status": "error", "error": str(e)}
    
    async def _handle_text_message(self, user_phone: str, message_text: str) -> Dict[str, Any]:
        """
        💬 Process text messages with natural language understanding
        """
        
        # Get or create user session
        session = self._get_user_session(user_phone)
        
        # Analyze message intent using AI
        intent_analysis = await self._analyze_message_intent(message_text, session)
        
        # Route to appropriate handler based on intent
        if intent_analysis["intent"] == "campaign_creation":
            return await self._handle_campaign_creation(user_phone, message_text, intent_analysis)
        elif intent_analysis["intent"] == "creator_search":
            return await self._handle_creator_search_request(user_phone, message_text, intent_analysis)
        elif intent_analysis["intent"] == "campaign_status":
            return await self._handle_campaign_status_check(user_phone, message_text, intent_analysis)
        elif intent_analysis["intent"] == "approval_request":
            return await self._handle_approval_flow(user_phone, message_text, intent_analysis)
        elif intent_analysis["intent"] == "general_query":
            return await self._handle_general_query(user_phone, message_text, intent_analysis)
        else:
            return await self._handle_unknown_intent(user_phone, message_text)
    
    async def _analyze_message_intent(self, message_text: str, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        🧠 Analyze message intent using Groq AI
        """
        
        if not self.groq_client:
            return self._fallback_intent_analysis(message_text)
        
        # Context from previous conversation
        context = session.get("conversation_history", [])[-3:]  # Last 3 messages
        
        prompt = f"""
        You are Alex, an AI assistant for influencer marketing campaigns. Analyze this message and determine the user's intent.

        Previous context: {json.dumps(context) if context else "None"}
        
        User message: "{message_text}"
        
        Return a JSON response with:
        {{
            "intent": "campaign_creation|creator_search|campaign_status|approval_request|general_query|unknown",
            "confidence": 0.0-1.0,
            "extracted_data": {{}},
            "suggested_action": "string",
            "requires_clarification": boolean
        }}
        
        Intent definitions:
        - campaign_creation: User wants to create a new campaign
        - creator_search: User wants to find creators for existing campaign  
        - campaign_status: User asking about campaign progress
        - approval_request: User responding to approval requests
        - general_query: General questions about platform/features
        - unknown: Unclear intent
        
        Extract relevant data like budget, niche, location, timeline etc.
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                return json.loads(result_text[json_start:json_end])
            else:
                return self._fallback_intent_analysis(message_text)
                
        except Exception as e:
            logger.error(f"❌ Intent analysis failed: {e}")
            return self._fallback_intent_analysis(message_text)
    
    def _fallback_intent_analysis(self, message_text: str) -> Dict[str, Any]:
        """Fallback intent analysis using keywords"""
        
        message_lower = message_text.lower()
        
        # Campaign creation keywords
        if any(word in message_lower for word in ["campaign", "create", "new", "launch", "start"]):
            return {
                "intent": "campaign_creation",
                "confidence": 0.7,
                "extracted_data": {},
                "suggested_action": "gather_campaign_details",
                "requires_clarification": True
            }
        
        # Creator search keywords
        elif any(word in message_lower for word in ["find", "search", "creators", "influencers", "get me"]):
            return {
                "intent": "creator_search", 
                "confidence": 0.8,
                "extracted_data": {},
                "suggested_action": "process_creator_search",
                "requires_clarification": False
            }
        
        # Status check keywords
        elif any(word in message_lower for word in ["status", "progress", "update", "how", "when"]):
            return {
                "intent": "campaign_status",
                "confidence": 0.6,
                "extracted_data": {},
                "suggested_action": "check_campaign_status",
                "requires_clarification": False
            }
        
        else:
            return {
                "intent": "general_query",
                "confidence": 0.5,
                "extracted_data": {},
                "suggested_action": "provide_help",
                "requires_clarification": True
            }
    
    async def _handle_campaign_creation(self, user_phone: str, message_text: str, intent_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        🚀 Handle campaign creation requests
        """
        
        session = self._get_user_session(user_phone)
        
        # Check if we have enough information to create campaign
        extracted_data = intent_analysis.get("extracted_data", {})
        
        # Extract campaign details from message
        campaign_details = await self._extract_campaign_details(message_text)
        
        # Merge with session data
        current_campaign = session.get("current_campaign", {})
        current_campaign.update(campaign_details)
        session["current_campaign"] = current_campaign
        
        # Check if we have minimum required information
        required_fields = ["product_name", "brand_name", "total_budget", "product_niche"]
        missing_fields = [field for field in required_fields if not current_campaign.get(field)]
        
        if missing_fields:
            return await self._request_missing_campaign_info(missing_fields, current_campaign)
        else:
            return await self._execute_campaign_creation(user_phone, current_campaign)
    
    async def _extract_campaign_details(self, message_text: str) -> Dict[str, Any]:
        """
        📝 Extract campaign details from natural language
        """
        
        if not self.groq_client:
            return self._fallback_extract_details(message_text)
        
        prompt = f"""
        Extract campaign details from this message. Return JSON only.
        
        Message: "{message_text}"
        
        Extract these fields if mentioned:
        {{
            "product_name": "string",
            "brand_name": "string", 
            "product_description": "string",
            "target_audience": "string",
            "campaign_goal": "string",
            "product_niche": "fitness|tech|beauty|gaming|food|lifestyle",
            "total_budget": number,
            "timeline": "string",
            "creator_count": number,
            "special_requirements": "string"
        }}
        
        Only include fields that are clearly mentioned. Budget should be extracted from patterns like "$10K", "10000", "ten thousand" etc.
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=300
            )
            
            result_text = response.choices[0].message.content.strip()
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                return json.loads(result_text[json_start:json_end])
            else:
                return self._fallback_extract_details(message_text)
                
        except Exception as e:
            logger.error(f"❌ Campaign detail extraction failed: {e}")
            return self._fallback_extract_details(message_text)
    
    def _fallback_extract_details(self, message_text: str) -> Dict[str, Any]:
        """Fallback detail extraction using regex"""
        
        details = {}
        
        # Extract budget
        budget_patterns = [
            r'\$(\d+)k',  # $10k
            r'\$(\d+),?(\d{3})',  # $10,000
            r'budget.*?(\d+)',  # budget 10000
        ]
        
        for pattern in budget_patterns:
            match = re.search(pattern, message_text.lower())
            if match:
                if 'k' in pattern:
                    details["total_budget"] = int(match.group(1)) * 1000
                else:
                    details["total_budget"] = int(match.group(1))
                break
        
        # Extract niche
        niches = ["fitness", "tech", "beauty", "gaming", "food", "lifestyle"]
        for niche in niches:
            if niche in message_text.lower():
                details["product_niche"] = niche
                break
        
        return details
    
    async def _request_missing_campaign_info(self, missing_fields: List[str], current_campaign: Dict[str, Any]) -> Dict[str, Any]:
        """
        ❓ Request missing campaign information
        """
        
        field_questions = {
            "product_name": "What's the name of your product?",
            "brand_name": "What's your brand name?", 
            "total_budget": "What's your total campaign budget? (e.g., $10K)",
            "product_niche": "What niche is this for? (fitness, tech, beauty, gaming, food, lifestyle)",
            "product_description": "Can you describe your product briefly?",
            "target_audience": "Who's your target audience?",
            "campaign_goal": "What's the main goal of this campaign?"
        }
        
        next_question = field_questions.get(missing_fields[0], "Can you provide more details?")
        
        # Show what we have so far
        current_info = []
        for key, value in current_campaign.items():
            if value:
                current_info.append(f"• {key.replace('_', ' ').title()}: {value}")
        
        current_summary = "\n".join(current_info) if current_info else "No details captured yet"
        
        return {
            "type": "text",
            "text": f"Got it! I'm setting up your campaign.\n\n*Current Details:*\n{current_summary}\n\n*Next:* {next_question}"
        }
    
    async def _execute_campaign_creation(self, user_phone: str, campaign_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        🚀 Execute the campaign creation process
        """
        
        # Create campaign using existing enhanced orchestrator
        from models.campaign import CampaignWebhook
        from api.enhanced_webhooks import handle_enhanced_campaign_created
        from fastapi import BackgroundTasks
        
        try:
            # Convert to campaign webhook format
            campaign_webhook = CampaignWebhook(
                campaign_id=f"wa_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                product_name=campaign_details["product_name"],
                brand_name=campaign_details["brand_name"],
                product_description=campaign_details.get("product_description", f"{campaign_details['product_name']} campaign"),
                target_audience=campaign_details.get("target_audience", "General audience"),
                campaign_goal=campaign_details.get("campaign_goal", "Increase brand awareness"),
                product_niche=campaign_details["product_niche"],
                total_budget=float(campaign_details["total_budget"])
            )
            
            # Start the enhanced campaign workflow
            background_tasks = BackgroundTasks()
            result = await handle_enhanced_campaign_created(campaign_webhook, background_tasks)
            
            # Store campaign info in user session
            session = self._get_user_session(user_phone)
            session["active_campaign"] = {
                "id": campaign_webhook.campaign_id,
                "task_id": result.json()["task_id"],
                "created_at": datetime.now().isoformat()
            }
            
            return {
                "type": "text",
                "text": f"🎯 *Campaign Created!*\n\n*{campaign_details['product_name']}* by {campaign_details['brand_name']}\nBudget: ${campaign_details['total_budget']:,}\nNiche: {campaign_details['product_niche']}\n\n🔥 *AI workflow started:*\n• Finding perfect creators\n• Starting negotiations\n• Generating contracts\n\nI'll update you as we progress! Usually takes 5-8 minutes for the full workflow.\n\nType 'status' anytime to check progress."
            }
            
        except Exception as e:
            logger.error(f"❌ Campaign creation failed: {e}")
            return {
                "type": "text", 
                "text": f"❌ Campaign creation failed: {str(e)}\n\nPlease try again or contact support."
            }
    
    async def _handle_creator_search_request(self, user_phone: str, message_text: str, intent_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        🔍 Handle creator search requests
        """
        
        # Extract search criteria
        search_criteria = await self._extract_search_criteria(message_text)
        
        # Perform creator search using existing discovery agent
        from agents.discovery import InfluencerDiscoveryAgent
        from models.campaign import CampaignData
        
        try:
            discovery_agent = InfluencerDiscoveryAgent()
            
            # Create mock campaign data from search criteria
            mock_campaign = CampaignData(
                id="search_temp",
                product_name=search_criteria.get("product_name", "Search Product"),
                brand_name=search_criteria.get("brand_name", "Search Brand"),
                product_description=search_criteria.get("description", "Creator search"),
                target_audience=search_criteria.get("target_audience", "General audience"),
                campaign_goal="Find creators",
                product_niche=search_criteria.get("niche", "fitness"),
                total_budget=search_criteria.get("budget", 10000)
            )
            
            # Find matches
            matches = await discovery_agent.find_matches(mock_campaign, max_results=5)
            
            # Format response
            creators_text = []
            for i, match in enumerate(matches[:3], 1):
                creator = match.creator
                creators_text.append(
                    f"{i}. *{creator.name}*\n"
                    f"   Platform: {creator.platform.value}\n"
                    f"   Followers: {creator.followers//1000}K\n" 
                    f"   Engagement: {creator.engagement_rate}%\n"
                    f"   Rate: ${creator.typical_rate:,}\n"
                    f"   Match: {match.similarity_score:.0%}"
                )
            
            return {
                "type": "text",
                "text": f"🎯 *Found {len(matches)} creators for you:*\n\n" + "\n\n".join(creators_text) + f"\n\nWant me to start outreach? Reply with 'yes' or 'reach out to all'."
            }
            
        except Exception as e:
            logger.error(f"❌ Creator search failed: {e}")
            return {
                "type": "text",
                "text": "❌ Creator search failed. Please try again with more specific criteria."
            }
    
    async def _extract_search_criteria(self, message_text: str) -> Dict[str, Any]:
        """Extract search criteria from message"""
        
        # Simple extraction for now
        criteria = {}
        
        # Extract niche
        niches = ["fitness", "tech", "beauty", "gaming", "food", "lifestyle"]
        for niche in niches:
            if niche in message_text.lower():
                criteria["niche"] = niche
                break
        
        # Extract follower count
        follower_patterns = [
            r'(\d+)k followers',
            r'(\d+)k\+',
            r'over (\d+)k'
        ]
        
        for pattern in follower_patterns:
            match = re.search(pattern, message_text.lower())
            if match:
                criteria["min_followers"] = int(match.group(1)) * 1000
                break
        
        return criteria
    
    async def _handle_campaign_status_check(self, user_phone: str, message_text: str, intent_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        📊 Handle campaign status requests
        """
        
        session = self._get_user_session(user_phone)
        active_campaign = session.get("active_campaign")
        
        if not active_campaign:
            return {
                "type": "text",
                "text": "You don't have any active campaigns. Want to create one? Just tell me about your product and budget!"
            }
        
        try:
            # Get campaign status from monitoring API
            from main import active_campaigns
            
            task_id = active_campaign["task_id"]
            
            if task_id in active_campaigns:
                state = active_campaigns[task_id]
                
                # Format status response
                progress = self._calculate_progress_percentage(state)
                stage_emoji = {
                    "discovery": "🔍",
                    "negotiations": "📞", 
                    "contracts": "📝",
                    "completed": "✅"
                }
                
                emoji = stage_emoji.get(state.current_stage, "⏳")
                
                status_text = f"{emoji} *Campaign Status*\n\n"
                status_text += f"*Stage:* {state.current_stage.title()}\n"
                status_text += f"*Progress:* {progress:.0f}%\n"
                
                if state.current_stage == "negotiations":
                    status_text += f"*Current:* {state.current_influencer or 'Processing'}\n"
                    status_text += f"*Completed calls:* {len(state.negotiations)}\n"
                    status_text += f"*Successful:* {state.successful_negotiations}\n"
                
                if state.completed_at:
                    status_text += f"\n✅ *Campaign completed!*\n"
                    status_text += f"*Results:* {state.successful_negotiations} partnerships secured\n"
                    status_text += f"*Total cost:* ${state.total_cost:,.2f}\n"
                    status_text += f"*Budget used:* {(state.total_cost/state.campaign_data.total_budget)*100:.1f}%"
                
                return {
                    "type": "text",
                    "text": status_text
                }
            else:
                return {
                    "type": "text",
                    "text": "Campaign not found in active list. It may have completed or failed. Check your campaign history."
                }
                
        except Exception as e:
            logger.error(f"❌ Status check failed: {e}")
            return {
                "type": "text",
                "text": "❌ Couldn't get campaign status. Please try again."
            }
    
    def _calculate_progress_percentage(self, state) -> float:
        """Calculate campaign progress percentage"""
        
        stage_progress = {
            "initializing": 10,
            "discovery": 25,
            "negotiations": 70,
            "contracts": 90,
            "completed": 100
        }
        
        base_progress = stage_progress.get(state.current_stage, 0)
        
        # Add sub-progress for negotiations
        if state.current_stage == "negotiations" and state.discovered_influencers:
            negotiation_progress = (len(state.negotiations) / len(state.discovered_influencers)) * 45
            return 25 + negotiation_progress
        
        return base_progress
    
    async def _handle_document_upload(self, user_phone: str, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        📄 Handle document uploads (campaign briefs, etc.)
        """
        
        document_id = document_data.get("id")
        filename = document_data.get("filename", "")
        mime_type = document_data.get("mime_type", "")
        
        logger.info(f"📄 Document upload: {filename} ({mime_type})")
        
        try:
            # Download document from WhatsApp
            document_content = await self._download_whatsapp_document(document_id)
            
            if not document_content:
                return {
                    "type": "text",
                    "text": "❌ Couldn't download the document. Please try again."
                }
            
            # Process document based on type
            if mime_type == "application/pdf":
                extracted_data = await self._process_pdf_brief(document_content)
            elif mime_type in ["text/plain", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
                extracted_data = await self._process_text_brief(document_content)
            else:
                return {
                    "type": "text", 
                    "text": f"📄 Received {filename}. Currently I support PDF and text files for campaign briefs. Can you share the details as text instead?"
                }
            
            # Store in user session
            session = self._get_user_session(user_phone)
            session["uploaded_brief"] = extracted_data
            
            # Create campaign from brief
            if extracted_data:
                return await self._create_campaign_from_brief(user_phone, extracted_data)
            else:
                return {
                    "type": "text",
                    "text": "📄 Got your document! I couldn't extract campaign details automatically. Can you tell me:\n• Product name\n• Budget\n• Target niche?"
                }
                
        except Exception as e:
            logger.error(f"❌ Document processing failed: {e}")
            return {
                "type": "text",
                "text": "❌ Document processing failed. Please share the campaign details as text instead."
            }
    
    async def _download_whatsapp_document(self, document_id: str) -> Optional[bytes]:
        """Download document from WhatsApp API"""
        
        try:
            # Get document URL
            url_response = requests.get(
                f"{self.base_url}/{document_id}",
                headers={"Authorization": f"Bearer {self.whatsapp_token}"},
                timeout=30
            )
            
            if url_response.status_code != 200:
                return None
            
            document_url = url_response.json().get("url")
            
            # Download document content
            content_response = requests.get(
                document_url,
                headers={"Authorization": f"Bearer {self.whatsapp_token}"},
                timeout=30
            )
            
            if content_response.status_code == 200:
                return content_response.content
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Document download failed: {e}")
            return None
    
    async def _process_pdf_brief(self, pdf_content: bytes) -> Dict[str, Any]:
        """Process PDF campaign brief"""
        
        # This would use a PDF processing library like PyPDF2 or pdfplumber
        # For now, return mock data
        return {
            "source": "pdf_upload",
            "product_name": "Extracted Product Name",
            "brand_name": "Extracted Brand",
            "total_budget": 15000,
            "product_niche": "fitness",
            "raw_text": "PDF content would be extracted here"
        }
    
    async def _create_campaign_from_brief(self, user_phone: str, brief_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create campaign from uploaded brief"""
        
        return {
            "type": "text",
            "text": f"📄 *Brief processed!*\n\nExtracted details:\n• Product: {brief_data.get('product_name', 'N/A')}\n• Brand: {brief_data.get('brand_name', 'N/A')}\n• Budget: ${brief_data.get('total_budget', 0):,}\n• Niche: {brief_data.get('product_niche', 'N/A')}\n\nLooks good? Reply 'yes' to start the campaign or 'edit' to modify details."
        }
    
    def _get_user_session(self, user_phone: str) -> Dict[str, Any]:
        """Get or create user session"""
        
        if user_phone not in self.user_sessions:
            self.user_sessions[user_phone] = {
                "created_at": datetime.now().isoformat(),
                "conversation_history": [],
                "current_campaign": {},
                "preferences": {}
            }
        
        return self.user_sessions[user_phone]
    
    async def _send_whatsapp_message(self, to_phone: str, message_data: Dict[str, Any]) -> bool:
        """Send message back to WhatsApp user"""
        
        if not self.whatsapp_token:
            logger.info(f"📱 Mock WhatsApp response to {to_phone}: {message_data}")
            return True
        
        try:
            payload = {
                "messaging_product": "whatsapp",
                "to": to_phone,
                "type": message_data["type"],
                message_data["type"]: {"body": message_data["text"]} if message_data["type"] == "text" else message_data
            }
            
            response = requests.post(
                f"{self.base_url}/{self.whatsapp_phone_id}/messages",
                headers={
                    "Authorization": f"Bearer {self.whatsapp_token}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=30
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"❌ WhatsApp message send failed: {e}")
            return False
    
    async def _send_error_message(self, to_phone: str, error_text: str):
        """Send error message to user"""
        await self._send_whatsapp_message(to_phone, {"type": "text", "text": error_text})
    
    # Additional handlers for completeness
    async def _handle_approval_flow(self, user_phone: str, message_text: str, intent_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Handle approval responses"""
        return {"type": "text", "text": "Approval flow not implemented yet."}
    
    async def _handle_general_query(self, user_phone: str, message_text: str, intent_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general queries"""
        return {
            "type": "text", 
            "text": f"Hey! I'm Alex, your AI campaign manager. I can help you:\n\n🎯 Create influencer campaigns\n🔍 Find perfect creators\n📊 Track campaign progress\n📄 Process campaign briefs\n\nJust tell me what you need! For example:\n• \"Create a fitness campaign, budget $10K\"\n• \"Find me tech creators with 100K+ followers\"\n• \"What's my campaign status?\""
        }
    
    async def _handle_unknown_intent(self, user_phone: str, message_text: str) -> Dict[str, Any]:
        """Handle unknown intents"""
        return {
            "type": "text",
            "text": "I'm not sure what you mean. Try:\n• \"Create campaign\" to start a new campaign\n• \"Find creators\" to search for influencers\n• \"Status\" to check progress\n• \"Help\" for more options"
        }