# services/voice_call_system.py - AI Agency Representative Calling System
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
import logging
import os

logger = logging.getLogger(__name__)

@dataclass
class CallSession:
    call_sid: str
    creator_id: str
    campaign_brief: Dict[str, Any]
    conversation_state: str  # "intro|negotiating|closing|completed"
    transcript: List[Dict[str, Any]]
    current_deal: Dict[str, Any]
    start_time: datetime
    creator_responses: List[str]
    ai_strategy: Dict[str, Any]

class AIAgencyRepresentative:
    """AI Agent that represents agencies in creator negotiations"""
    
    def __init__(self, twilio_client, openai_service, elevenlabs_service):
        self.twilio = twilio_client
        self.openai = openai_service
        self.elevenlabs = elevenlabs_service
        self.active_calls: Dict[str, CallSession] = {}
        self.webhook_base_url = os.getenv('NGROK_URL', 'http://localhost:8000')
        
    def generate_introduction_script(self, campaign_brief: Dict, creator_profile: Dict) -> str:
        """Generate personalized introduction for the creator"""
        
        prompt = f"""You are an AI assistant calling on behalf of {campaign_brief['brand_name']} agency. 
        Generate a professional, friendly 30-second introduction for {creator_profile['name']}:

        Campaign: {campaign_brief['campaign_type']} for {campaign_brief['product_name']}
        Creator: {creator_profile['name']} - {creator_profile['platform']} - {creator_profile['followers']:,} followers
        Key metrics: {creator_profile['engagement_rate']}% engagement, {creator_profile['average_views']:,} avg views
        Budget range: ${campaign_brief['budget_max']}

        Be warm, professional, and reference their specific metrics. Ask for 3-4 minutes to discuss.
        Keep it conversational and respectful of their time."""
        
        return self.openai.generate_response(prompt)
    
    async def initiate_creator_call(self, creator_id: str, campaign_brief: Dict) -> str:
        """Start a negotiation call with a creator"""
        
        try:
            # Get creator profile and phone
            creator = self.get_creator_profile(creator_id)
            
            # Generate call strategy
            call_strategy = self.generate_call_strategy(campaign_brief, creator)
            
            # Create call session
            call_session = CallSession(
                call_sid="",  # Will be set after Twilio call
                creator_id=creator_id,
                campaign_brief=campaign_brief,
                conversation_state="intro",
                transcript=[],
                current_deal=call_strategy["opening_deal"],
                start_time=datetime.now(),
                creator_responses=[],
                ai_strategy=call_strategy
            )
            
            # Generate introduction
            intro_script = self.generate_introduction_script(campaign_brief, creator)
            
            # Initiate Twilio call
            call = self.twilio.calls.create(
                to=creator['phone_number'],
                from_=os.getenv('TWILIO_PHONE_NUMBER'),
                url=f"{self.webhook_base_url}/api/voice/handle-call",
                method='POST',
                record=True,
                timeout=30,
                status_callback=f"{self.webhook_base_url}/api/voice/status-callback"
            )
            
            call_session.call_sid = call.sid
            self.active_calls[call.sid] = call_session
            
            logger.info(f"Initiated call to {creator['name']}: {call.sid}")
            return call.sid
            
        except Exception as e:
            logger.error(f"Failed to initiate call: {str(e)}")
            raise
    
    def generate_call_strategy(self, campaign_brief: Dict, creator: Dict) -> Dict:
        """Generate negotiation strategy for this specific creator"""
        
        typical_rate = creator['typical_rate']
        budget_max = campaign_brief['budget_max']
        
        # Calculate opening offer (80-90% of typical rate, within budget)
        opening_price = min(int(typical_rate * 0.85), budget_max - 200)
        
        return {
            "opening_deal": {
                "price": opening_price,
                "deliverables": campaign_brief['deliverables'],
                "timeline": campaign_brief['timeline'],
                "usage_rights": "6 months"
            },
            "max_budget": budget_max,
            "flexibility_areas": ["timeline", "deliverables", "usage_rights"],
            "key_selling_points": [
                f"Perfect audience match - {creator['engagement_rate']}% engagement",
                f"Strong viewership - {creator['average_views']:,} average views",
                f"Professional track record - {creator['performance_metrics']['avg_completion_rate']}% completion rate"
            ],
            "negotiation_approach": "collaborative",
            "cost_per_view": round(opening_price / creator['average_views'], 4)
        }
    
    async def handle_call_webhook(self, request_data: Dict) -> str:
        """Handle incoming Twilio webhook during call"""
        
        call_sid = request_data.get('CallSid')
        call_status = request_data.get('CallStatus')
        
        if call_sid not in self.active_calls:
            logger.error(f"Unknown call SID: {call_sid}")
            return self.generate_hangup_response()
        
        call_session = self.active_calls[call_sid]
        
        if call_status == 'in-progress':
            return await self.handle_active_call(call_session, request_data)
        elif call_status == 'completed':
            return await self.handle_call_completion(call_session)
        else:
            return self.generate_default_response()
    
    async def handle_active_call(self, call_session: CallSession, request_data: Dict) -> str:
        """Handle active call conversation"""
        
        response = VoiceResponse()
        
        # Check conversation state
        if call_session.conversation_state == "intro":
            return await self.handle_introduction(call_session, response)
        elif call_session.conversation_state == "negotiating":
            return await self.handle_negotiation(call_session, request_data, response)
        elif call_session.conversation_state == "closing":
            return await self.handle_closing(call_session, request_data, response)
        
        return str(response)
    
    async def handle_introduction(self, call_session: CallSession, response: VoiceResponse) -> str:
        """Handle introduction phase of call"""
        
        # Generate personalized introduction
        creator = self.get_creator_profile(call_session.creator_id)
        intro_text = self.generate_introduction_script(call_session.campaign_brief, creator)
        
        # Convert to speech using Twilio's built-in TTS for simplicity
        response.say(intro_text, voice='Polly.Joanna')
        
        # Gather response
        gather = response.gather(
            input=['speech'],
            timeout=10,
            speech_timeout='auto',
            action=f"{self.webhook_base_url}/api/voice/process-response",
            method='POST'
        )
        gather.say("I'm listening...")
        response.append(gather)
        
        # Update call state
        call_session.conversation_state = "negotiating"
        call_session.transcript.append({
            "timestamp": datetime.now().isoformat(),
            "speaker": "ai_agent",
            "content": intro_text,
            "type": "introduction"
        })
        
        return str(response)
    
    async def handle_negotiation(self, call_session: CallSession, request_data: Dict, response: VoiceResponse) -> str:
        """Handle negotiation phase"""
        
        # Get creator's speech response
        speech_result = request_data.get('SpeechResult', '')
        
        if speech_result:
            # Add creator response to transcript
            call_session.transcript.append({
                "timestamp": datetime.now().isoformat(),
                "speaker": "creator",
                "content": speech_result,
                "confidence": request_data.get('Confidence', 0.0)
            })
            
            # Generate AI negotiation response
            ai_response = await self.generate_negotiation_response(call_session, speech_result)
            
            # Play AI response using Twilio TTS
            response.say(ai_response['message'], voice='Polly.Joanna')
            
            # Check if deal is closed
            if ai_response.get('deal_status') == 'agreed':
                call_session.conversation_state = "closing"
                return await self.handle_deal_closing(call_session, response)
            elif ai_response.get('deal_status') == 'rejected':
                return await self.handle_deal_rejection(call_session, response)
            
            # Continue negotiation
            gather = response.gather(
                input=['speech'],
                timeout=15,
                speech_timeout='auto',
                action=f"{self.webhook_base_url}/api/voice/process-response",
                method='POST'
            )
            response.append(gather)
        
        return str(response)
    
    async def generate_negotiation_response(self, call_session: CallSession, creator_message: str) -> Dict:
        """Generate AI response to creator's negotiation point"""
        
        conversation_context = {
            "campaign_brief": call_session.campaign_brief,
            "creator_profile": self.get_creator_profile(call_session.creator_id),
            "current_deal": call_session.current_deal,
            "conversation_history": call_session.transcript,
            "ai_strategy": call_session.ai_strategy
        }
        
        # Use existing OpenAI service with enhanced prompt for phone conversation
        prompt = f"""You are an AI assistant representing {call_session.campaign_brief['brand_name']} agency 
        in a live phone conversation with creator {call_session.creator_id}. 

        Creator just said: "{creator_message}"

        Your role: Professional agency representative conducting a negotiation
        Current offer: ${call_session.current_deal['price']} for {call_session.current_deal['deliverables']}
        
        Respond naturally as if you're on a phone call:
        - Keep responses conversational and under 30 seconds
        - Reference specific data when making points
        - Be ready to adjust the deal if needed
        - Sound professional but friendly
        - Ask clarifying questions when appropriate
        
        Context: {json.dumps(conversation_context, indent=2)}
        """
        
        try:
            return self.openai.generate_negotiation_response(conversation_context, creator_message, "agency")
        except Exception as e:
            logger.error(f"Error generating negotiation response: {str(e)}")
            # Fallback response
            return {
                "message": "That's a great point. Let me see what we can do to make this work for both of us.",
                "insights": [],
                "strategy_notes": "Fallback response"
            }
    
    async def handle_deal_closing(self, call_session: CallSession, response: VoiceResponse) -> str:
        """Handle successful deal closing"""
        
        closing_message = f"""Perfect! Let me confirm the details: 
        ${call_session.current_deal['price']} for {', '.join(call_session.current_deal['deliverables'])}, 
        delivery by {call_session.current_deal['timeline']}. 
        I'll send you the contract within 2 hours. Thank you for the great conversation!"""
        
        response.say(closing_message, voice='Polly.Joanna')
        response.hangup()
        
        # Update call session
        call_session.conversation_state = "completed"
        call_session.transcript.append({
            "timestamp": datetime.now().isoformat(),
            "speaker": "ai_agent",
            "content": closing_message,
            "type": "deal_closure"
        })
        
        return str(response)
    
    async def handle_deal_rejection(self, call_session: CallSession, response: VoiceResponse) -> str:
        """Handle deal rejection"""
        
        rejection_message = "I understand this isn't the right fit. Thank you for your time, and feel free to reach out if circumstances change."
        
        response.say(rejection_message, voice='Polly.Joanna')
        response.hangup()
        
        call_session.conversation_state = "completed"
        call_session.transcript.append({
            "timestamp": datetime.now().isoformat(),
            "speaker": "ai_agent",
            "content": rejection_message,
            "type": "deal_rejection"
        })
        
        return str(response)
    
    def get_creator_profile(self, creator_id: str) -> Dict:
        """Get creator profile from your existing data service"""
        # Import here to avoid circular imports
        from services.data_service import data_service
        return data_service.get_creator_by_id(creator_id)
    
    async def get_call_transcript(self, call_sid: str) -> Dict:
        """Get complete call transcript and outcome"""
        
        if call_sid in self.active_calls:
            call_session = self.active_calls[call_sid]
            return {
                "call_sid": call_sid,
                "creator_id": call_session.creator_id,
                "campaign_brief": call_session.campaign_brief,
                "transcript": call_session.transcript,
                "final_deal": call_session.current_deal,
                "call_duration": (datetime.now() - call_session.start_time).total_seconds(),
                "status": call_session.conversation_state
            }
        
        return {"error": "Call not found"}
    
    async def update_call_status(self, call_sid: str, call_status: str, status_data: Dict) -> None:
        """Update call status from Twilio webhook"""
        if call_sid in self.active_calls:
            call_session = self.active_calls[call_sid]
            if call_status == 'completed':
                call_session.conversation_state = "completed"
            logger.info(f"Updated call {call_sid} status to {call_status}")
    
    async def handle_negotiation_response(self, call_sid: str, speech_result: str, confidence: float) -> str:
        """Handle creator's negotiation response"""
        if call_sid not in self.active_calls:
            response = VoiceResponse()
            response.say("Sorry, I lost track of our conversation.")
            response.hangup()
            return str(response)
        
        call_session = self.active_calls[call_sid]
        
        # Add creator response to transcript
        call_session.transcript.append({
            "timestamp": datetime.now().isoformat(),
            "speaker": "creator",
            "content": speech_result,
            "confidence": confidence
        })
        
        # Generate AI response
        ai_response = await self.generate_negotiation_response(call_session, speech_result)
        
        # Add AI response to transcript
        call_session.transcript.append({
            "timestamp": datetime.now().isoformat(),
            "speaker": "ai_agent",
            "content": ai_response["message"],
            "type": "negotiation"
        })
        
        # Update deal if necessary
        if "updated_deal" in ai_response:
            call_session.current_deal.update(ai_response["updated_deal"])
        
        response = VoiceResponse()
        response.say(ai_response["message"], voice='Polly.Joanna')
        
        # Continue or close based on response
        if ai_response.get("deal_status") == "agreed":
            call_session.conversation_state = "completed"
            response.say("Perfect! I'll send you the contract details via email. Thank you!")
            response.hangup()
        elif ai_response.get("deal_status") == "rejected":
            call_session.conversation_state = "completed"
            response.say("I understand. Thank you for your time!")
            response.hangup()
        else:
            # Continue negotiation
            gather = response.gather(
                input=['speech'],
                timeout=15,
                speech_timeout='auto',
                action=f"{self.webhook_base_url}/api/voice/process-response",
                method='POST'
            )
            gather.say("What are your thoughts?")
        
        return str(response)
    
    def generate_hangup_response(self) -> str:
        """Generate hangup response for unknown calls"""
        response = VoiceResponse()
        response.say("Sorry, I cannot find this conversation. Goodbye.")
        response.hangup()
        return str(response)
    
    def generate_default_response(self) -> str:
        """Generate default response"""
        response = VoiceResponse()
        response.say("Hello, please hold while I connect you.")
        return str(response)
    
    async def handle_call_completion(self, call_session: CallSession) -> str:
        """Handle call completion"""
        response = VoiceResponse()
        response.say("Thank you for the conversation!")
        call_session.conversation_state = "completed"
        return str(response)
    
    async def handle_closing(self, call_session: CallSession, request_data: Dict, response: VoiceResponse) -> str:
        """Handle closing phase"""
        response.say("Thank you for your time!")
        response.hangup()
        return str(response)