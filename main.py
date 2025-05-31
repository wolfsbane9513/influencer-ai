# main.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Response, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import uuid
import os
from datetime import datetime
import logging
from decouple import config

# Twilio imports - Fixed for correct API structure
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import models and services
from models.conversation import CampaignBrief, DealParams, NegotiationRequest
from services.negotiation import NegotiationManager
from services.data_service import data_service
from services.conversation_manager import conversation_manager, MessageRole, ConversationStatus
from services.voice_service import voice_service, AudioFormatHandler

app = FastAPI(title="InfluencerFlow AI", version="1.0.0")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
negotiation_manager = NegotiationManager()

class TwilioService:
    """Service class to handle Twilio operations"""
    
    def __init__(self):
        self.client = None
        self.phone_number = None
        self.is_configured = False
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Twilio client with proper error handling"""
        try:
            account_sid = config('TWILIO_ACCOUNT_SID', default=None)
            auth_token = config('TWILIO_AUTH_TOKEN', default=None)
            self.phone_number = config('TWILIO_PHONE_NUMBER', default=None)
            
            if not account_sid or not auth_token:
                logger.warning("Twilio credentials not found in environment variables")
                return
            
            # Correct Twilio client initialization (positional arguments)
            self.client = Client(account_sid, auth_token)
            
            # Test the client by fetching account info
            account = self.client.api.accounts(account_sid).fetch()
            logger.info(f"Twilio client initialized successfully for account: {account.friendly_name}")
            
            if not self.phone_number:
                logger.warning("TWILIO_PHONE_NUMBER not configured")
            else:
                self.is_configured = True
                logger.info(f"Twilio service fully configured with phone number: {self.phone_number}")
            
        except Exception as e:
            logger.error(f"Twilio client initialization failed: {e}")
            self.client = None
            self.is_configured = False
    
    def create_call(self, to_number: str, webhook_url: str, status_callback: str = None):
        """Create a Twilio call"""
        if not self.is_configured:
            raise Exception("Twilio service not properly configured")
        
        return self.client.calls.create(
            to=to_number,
            from_=self.phone_number,
            url=webhook_url,
            method='POST',
            record=True,
            timeout=30,
            status_callback=status_callback
        )
    
    def get_call_status(self, call_sid: str):
        """Get call status from Twilio"""
        if not self.client:
            raise Exception("Twilio client not initialized")
        
        return self.client.calls(call_sid).fetch()

# Initialize Twilio service
twilio_service = TwilioService()

class CallManager:
    """Manages active voice calls and their state"""
    
    def __init__(self):
        self.active_calls: Dict[str, Dict[str, Any]] = {}
    
    def create_call_session(self, call_sid: str, creator_id: str, campaign_brief: dict, strategy: dict) -> dict:
        """Create a new call session"""
        call_session = {
            "call_sid": call_sid,
            "conversation_id": str(uuid.uuid4()),
            "creator_id": creator_id,
            "creator_profile": data_service.get_creator_by_id(creator_id),
            "campaign_brief": campaign_brief,
            "strategy": strategy,
            "conversation_state": "intro",
            "transcript": [],
            "current_deal": strategy["opening_deal"],
            "start_time": datetime.now(),
            "intro_script": self._generate_intro_script(campaign_brief, creator_id)
        }
        
        self.active_calls[call_sid] = call_session
        return call_session
    
    def get_call_session(self, call_sid: str) -> Optional[dict]:
        """Get call session by SID"""
        return self.active_calls.get(call_sid)
    
    def update_call_state(self, call_sid: str, state: str):
        """Update call state"""
        if call_sid in self.active_calls:
            self.active_calls[call_sid]["conversation_state"] = state
    
    def add_transcript_entry(self, call_sid: str, speaker: str, content: str, metadata: dict = None):
        """Add entry to call transcript"""
        if call_sid in self.active_calls:
            entry = {
                "timestamp": datetime.now().isoformat(),
                "speaker": speaker,
                "content": content,
                **(metadata or {})
            }
            self.active_calls[call_sid]["transcript"].append(entry)
    
    def _generate_intro_script(self, campaign_brief: dict, creator_id: str) -> str:
        """Generate introduction script for the call"""
        creator = data_service.get_creator_by_id(creator_id)
        if not creator:
            return "Hello, I'm calling about a collaboration opportunity."
        
        creator_name = creator['name'].split('_')[-1] if '_' in creator['name'] else creator['name']
        
        return f"""Hi {creator_name}, this is Alex, an AI assistant calling on behalf of {campaign_brief['brand_name']}. 

I hope I'm catching you at a good time. We have an exciting {campaign_brief.get('product_name', 'product')} campaign that would be perfect for your {creator['platform']} audience. 

Based on your analytics, your content averages {creator['average_views']:,} views with {creator['engagement_rate']}% engagement - exactly the demographic we're targeting.

Do you have 3-4 minutes to discuss a potential collaboration? We're looking at a budget around ${campaign_brief.get('budget_max', 4000)} for this campaign."""

# Initialize call manager
call_manager = CallManager()

# Data models for voice calling
class CallRequest(BaseModel):
    creator_id: str
    campaign_brief: dict
    brand_name: str
    contact_person: str
    urgency: str = "normal"

class CallStatus(BaseModel):
    call_sid: str
    status: str
    duration: Optional[int] = None
    transcript: list = []
    current_deal: dict = {}

# API Endpoints

@app.get("/")
async def root():
    return {"message": "InfluencerFlow AI Platform API", "status": "running"}

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy", 
        "timestamp": datetime.now(),
        "twilio_configured": twilio_service.is_configured,
        "ngrok_url": config('NGROK_URL', default='http://localhost:8000'),
        "services": {
            "negotiation": True,
            "voice": True,
            "data": True,
            "conversation": True
        }
    }

@app.post("/api/campaign/brief")
async def create_campaign_brief(brief: CampaignBrief):
    """Initialize a new campaign with requirements and budget"""
    try:
        # Get creator profile
        creator = get_creator_profile(brief.creator_name)
        if not creator:
            raise HTTPException(status_code=404, detail="Creator not found")
        
        # Generate initial negotiation strategy
        strategy = generate_negotiation_strategy(brief, creator)
        
        # Create conversation using conversation manager
        conversation_id = conversation_manager.create_conversation(
            campaign_brief=brief.dict(),
            creator_profile=creator,
            initial_strategy=strategy
        )
        
        # Update status to negotiating
        conversation_manager.update_conversation_status(
            conversation_id, 
            ConversationStatus.NEGOTIATING,
            "Campaign brief created and ready for negotiation"
        )
        
        return {
            "conversation_id": conversation_id,
            "strategy": strategy,
            "creator_profile": creator,
            "initial_offer": strategy["opening_price"],
            "conversation_summary": conversation_manager.get_conversation_summary(conversation_id)
        }
        
    except Exception as e:
        logger.error(f"Error creating campaign brief: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/negotiate")
async def negotiate(request: NegotiationRequest):
    """Process negotiation message and return AI response"""
    try:
        conversation_id = request.conversation_id
        
        # Get conversation from conversation manager
        conversation = conversation_manager.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Add user message to conversation
        conversation_manager.add_message(
            conversation_id,
            MessageRole.CREATOR if request.speaker == "creator" else MessageRole.AGENCY,
            request.message
        )
        
        # Build conversation context for AI
        conversation_context = {
            **conversation,
            "messages": conversation_manager.get_messages(conversation_id)
        }
        
        # Generate AI response
        ai_response = generate_ai_response(conversation_context, request.message)
        
        # Add AI response to conversation
        conversation_manager.add_message(
            conversation_id,
            MessageRole.AI_AGENT,
            ai_response["message"],
            {"insights": ai_response.get("insights", []), "strategy_notes": ai_response.get("strategy_notes", "")}
        )
        
        # Update deal parameters if changed
        if "updated_deal" in ai_response:
            conversation_manager.update_deal_parameters(
                conversation_id,
                ai_response["updated_deal"],
                ai_response.get("rationale", "AI suggested deal update")
            )
        
        # Get updated conversation data
        updated_conversation = conversation_manager.get_conversation(conversation_id)
        negotiation_insights = conversation_manager.get_negotiation_insights(conversation_id)
        
        return {
            "message": ai_response["message"],
            "deal_params": updated_conversation["deal_params"],
            "insights": ai_response.get("insights", []),
            "strategy_notes": ai_response.get("strategy_notes", ""),
            "conversation_id": conversation_id,
            "negotiation_insights": negotiation_insights,
            "conversation_summary": conversation_manager.get_conversation_summary(conversation_id)
        }
        
    except Exception as e:
        logger.error(f"Error in negotiation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/negotiate/voice")
async def negotiate_voice(conversation_id: str, audio_file: UploadFile = File(...)):
    """Process voice input for negotiation"""
    try:
        # Get conversation from conversation manager
        conversation = conversation_manager.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Validate audio format
        if not AudioFormatHandler.validate_audio_format(audio_file.content_type):
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported audio format: {audio_file.content_type}"
            )
        
        # Read audio data
        audio_content = await audio_file.read()
        
        if len(audio_content) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")
        
        # Process voice input using voice service
        voice_result = await voice_service.process_voice_message(
            audio_content, 
            conversation
        )
        
        if not voice_result.get("success"):
            raise HTTPException(
                status_code=400, 
                detail=f"Voice processing failed: {voice_result.get('error', 'Unknown error')}"
            )
        
        transcribed_text = voice_result["transcribed_text"]
        
        # Process as regular negotiation
        request = NegotiationRequest(
            conversation_id=conversation_id,
            message=transcribed_text,
            speaker="agency"
        )
        
        # Get AI response
        negotiation_response = await negotiate(request)
        
        # Generate audio response
        audio_response = await voice_service.generate_response_audio(
            negotiation_response["message"],
            conversation
        )
        
        # Prepare response
        response_data = {
            **negotiation_response,
            "voice_processing": {
                "transcription": voice_result["transcription"],
                "transcribed_text": transcribed_text,
                "voice_profile_used": voice_result["voice_profile"]
            }
        }
        
        # Add audio response if successful
        if audio_response.get("success"):
            response_data["audio_response"] = {
                "file_path": audio_response["audio_file_path"],
                "metadata": audio_response["metadata"],
                "voice_profile": audio_response["voice_profile"]
            }
        else:
            response_data["audio_response"] = {
                "error": audio_response.get("error", "Failed to generate audio response"),
                "success": False
            }
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in voice negotiation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# VOICE CALLING ENDPOINTS

@app.post("/api/voice/initiate-creator-call")
async def initiate_creator_call(call_request: CallRequest):
    """Initiate AI agent call to creator for negotiation"""
    try:
        if not twilio_service.is_configured:
            raise HTTPException(
                status_code=500, 
                detail="Twilio calling not configured. Please set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER environment variables."
            )
        
        # Validate creator exists and has phone number
        creator = data_service.get_creator_by_id(call_request.creator_id)
        if not creator:
            raise HTTPException(status_code=404, detail="Creator not found")
        
        if not creator.get('phone_number'):
            raise HTTPException(status_code=400, detail="Creator phone number not available")
        
        # Generate conversation strategy
        strategy = generate_negotiation_strategy_for_call(call_request.campaign_brief, creator)
        
        # Prepare webhook URLs
        webhook_base = config('NGROK_URL', default='http://localhost:8000')
        webhook_url = f"{webhook_base}/api/voice/handle-call"
        status_callback_url = f"{webhook_base}/api/voice/status-callback"
        
        # Initiate Twilio call
        call = twilio_service.create_call(
            to_number=creator['phone_number'],
            webhook_url=webhook_url,
            status_callback=status_callback_url
        )
        
        # Prepare campaign brief
        enhanced_brief = {
            **call_request.campaign_brief,
            "brand_name": call_request.brand_name,
            "contact_person": call_request.contact_person,
            "urgency": call_request.urgency,
            "call_initiated_at": datetime.now().isoformat()
        }
        
        # Create call session
        call_session = call_manager.create_call_session(
            call_sid=call.sid,
            creator_id=call_request.creator_id,
            campaign_brief=enhanced_brief,
            strategy=strategy
        )
        
        logger.info(f"Initiated call to {creator['name']}: {call.sid}")
        
        return {
            "success": True,
            "call_sid": call.sid,
            "conversation_id": call_session["conversation_id"],
            "creator_name": creator['name'],
            "estimated_duration": "3-5 minutes",
            "status": "initiating",
            "message": f"AI agent is calling {creator['name']} to discuss your campaign"
        }
        
    except Exception as e:
        logger.error(f"Failed to initiate creator call: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/voice/call-status/{call_sid}")
async def get_call_status(call_sid: str):
    """Get real-time status of ongoing call"""
    try:
        if not twilio_service.is_configured:
            raise HTTPException(status_code=500, detail="Twilio not configured")
        
        # Get call status from Twilio
        call = twilio_service.get_call_status(call_sid)
        
        # Get conversation details from call manager
        call_session = call_manager.get_call_session(call_sid)
        
        return {
            "call_sid": call_sid,
            "status": call.status,
            "duration": call.duration,
            "start_time": call.start_time.isoformat() if call.start_time else None,
            "end_time": call.end_time.isoformat() if call.end_time else None,
            "conversation_state": call_session.get("conversation_state", "unknown") if call_session else "unknown",
            "live_transcript": call_session.get("transcript", []) if call_session else [],
            "current_deal": call_session.get("current_deal", {}) if call_session else {},
            "creator_name": call_session.get("creator_profile", {}).get("name", "Unknown") if call_session else "Unknown"
        }
        
    except Exception as e:
        logger.error(f"Failed to get call status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/voice/handle-call")
async def handle_twilio_webhook(request: Request):
    """Handle Twilio webhook during active call"""
    try:
        # Get form data from Twilio webhook
        form_data = await request.form()
        request_data = dict(form_data)
        
        call_sid = request_data.get('CallSid')
        call_status = request_data.get('CallStatus')
        
        logger.info(f"Webhook received for call {call_sid}: {call_status}")
        
        call_session = call_manager.get_call_session(call_sid)
        if not call_session:
            logger.error(f"Unknown call SID: {call_sid}")
            response = VoiceResponse()
            response.say("Sorry, I cannot find this conversation. Goodbye.")
            response.hangup()
            return Response(content=str(response), media_type="application/xml")
        
        if call_status == 'in-progress':
            return await handle_active_call(call_session, request_data)
        elif call_status == 'completed':
            return await handle_call_completion(call_session)
        else:
            # Initial call connection
            response = VoiceResponse()
            response.say("Hello, this is Alex from " + call_session["campaign_brief"]["brand_name"])
            return Response(content=str(response), media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Webhook handling error: {str(e)}")
        # Return basic TwiML to prevent call failure
        response = VoiceResponse()
        response.say("Sorry, there was a technical issue. Goodbye.")
        response.hangup()
        return Response(content=str(response), media_type="application/xml")

async def handle_active_call(call_session: Dict, request_data: Dict) -> Response:
    """Handle active call conversation with improved speech recognition"""
    response = VoiceResponse()
    call_sid = call_session["call_sid"]
    
    if call_session["conversation_state"] == "intro":
        # Play introduction
        intro_text = call_session["intro_script"]
        response.say(intro_text, voice='Polly.Joanna')
        
        # Improved gather configuration for better speech recognition
        gather = response.gather(
            input=['speech'],
            speechTimeout='auto',  # Automatically detect when speech ends
            timeout=15,  # Overall timeout
            enhanced=True,  # Use enhanced recognition
            speechModel='phone_call',  # Best model for phone calls
            language='en-US',  # Specify language
            hints='yes,no,okay,sure,interested,not interested,tell me more,what,price,budget,timeline,friday,week,month,agree,disagree',  # Common negotiation words
            action=f"{config('NGROK_URL', default='http://localhost:8000')}/api/voice/process-response",
            method='POST',
            partialResultCallback=f"{config('NGROK_URL', default='http://localhost:8000')}/api/voice/partial-result",
            partialResultCallbackMethod='POST'
        )
        gather.say("Please share your thoughts on this collaboration opportunity.", voice='Polly.Joanna')
        response.append(gather)
        
        # Fallback if no speech detected
        response.say("I didn't hear anything. Let me try calling you back later. Goodbye!", voice='Polly.Joanna')
        response.hangup()
        
        # Update state and transcript
        call_manager.update_call_state(call_sid, "negotiating")
        call_manager.add_transcript_entry(
            call_sid, 
            "ai_agent", 
            intro_text, 
            {"type": "introduction"}
        )
        
        logger.info(f"Set up gather for call {call_sid} with ngrok URL: {config('NGROK_URL', default='http://localhost:8000')}")
        
    return Response(content=str(response), media_type="application/xml")

@app.post("/api/voice/process-response")
async def process_creator_response(request: Request):
    """Process creator's speech response during negotiation with better error handling"""
    try:
        form_data = await request.form()
        request_data = dict(form_data)
        
        call_sid = request_data.get('CallSid')
        speech_result = request_data.get('SpeechResult', '')
        confidence = float(request_data.get('Confidence', 0.0))
        
        logger.info(f"Processing speech for call {call_sid}")
        logger.info(f"Speech result: '{speech_result}' (confidence: {confidence})")
        logger.info(f"Full request data: {request_data}")
        
        call_session = call_manager.get_call_session(call_sid)
        if not call_session:
            logger.error(f"Call session not found for {call_sid}")
            response = VoiceResponse()
            response.say("Sorry, I lost track of our conversation. Let me call you back.")
            response.hangup()
            return Response(content=str(response), media_type="application/xml")
        
        # Check if we got valid speech
        if not speech_result or speech_result.strip() == '':
            logger.warning(f"No speech result received for call {call_sid}")
            response = VoiceResponse()
            
            # Try again with more encouraging prompt
            gather = response.gather(
                input=['speech'],
                speechTimeout='auto',
                timeout=10,
                enhanced=True,
                speechModel='phone_call',
                language='en-US',
                hints='yes,no,okay,sure,interested,price,budget,timeline',
                action=f"{config('NGROK_URL', default='http://localhost:8000')}/api/voice/process-response",
                method='POST'
            )
            gather.say("I'm sorry, I didn't catch that. Could you please speak a bit louder and tell me what you think about this collaboration?", voice='Polly.Joanna')
            response.append(gather)
            
            # Fallback after second attempt
            response.say("I'm having trouble hearing you. Let me call you back later. Goodbye!", voice='Polly.Joanna')
            response.hangup()
            
            return Response(content=str(response), media_type="application/xml")
        
        # Add creator response to transcript
        call_manager.add_transcript_entry(
            call_sid,
            "creator",
            speech_result,
            {"confidence": confidence, "raw_speech": speech_result}
        )
        
        # Generate AI negotiation response
        logger.info(f"Generating AI response for: '{speech_result}'")
        ai_response = await generate_negotiation_response_for_call(call_session, speech_result)
        
        # Add AI response to transcript
        call_manager.add_transcript_entry(
            call_sid,
            "ai_agent",
            ai_response["message"],
            {"type": "negotiation", "ai_confidence": "high"}
        )
        
        # Update deal parameters if changed
        if "updated_deal" in ai_response:
            call_session["current_deal"].update(ai_response["updated_deal"])
            logger.info(f"Updated deal parameters: {ai_response['updated_deal']}")
        
        response = VoiceResponse()
        
        # Speak the AI response
        response.say(ai_response["message"], voice='Polly.Joanna')
        
        # Check if negotiation should continue
        deal_status = ai_response.get("deal_status", "continue")
        logger.info(f"Deal status: {deal_status}")
        
        if deal_status == "agreed":
            call_manager.update_call_state(call_sid, "completed")
            response.say("Perfect! I'll send you the contract details via email within the hour. Thank you for the great conversation!", voice='Polly.Joanna')
            response.hangup()
        elif deal_status == "rejected":
            call_manager.update_call_state(call_sid, "completed")
            response.say("I understand this isn't the right fit right now. Thank you for your time, and feel free to reach out if circumstances change. Have a great day!", voice='Polly.Joanna')
            response.hangup()
        else:
            # Continue negotiation with better prompts
            gather = response.gather(
                input=['speech'],
                speechTimeout='auto',
                timeout=20,  # Give more time for thoughtful responses
                enhanced=True,
                speechModel='phone_call',
                language='en-US',
                hints='yes,no,okay,deal,agreed,not interested,price,budget,timeline,friday,week,month,sure,sounds good,let me think',
                action=f"{config('NGROK_URL', default='http://localhost:8000')}/api/voice/process-response",
                method='POST'
            )
            gather.say("What are your thoughts on this?", voice='Polly.Joanna')
            response.append(gather)
            
            # Fallback if they don't respond
            response.say("Thank you for considering our proposal. I'll follow up via email. Have a great day!", voice='Polly.Joanna')
            response.hangup()
        
        logger.info(f"Sent TwiML response for call {call_sid}")
        return Response(content=str(response), media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error processing speech response: {str(e)}")
        logger.exception("Full exception details:")
        
        # Graceful error handling
        response = VoiceResponse()
        response.say("I'm experiencing a technical issue. Let me call you back shortly. Thank you for your patience!", voice='Polly.Joanna')
        response.hangup()
        return Response(content=str(response), media_type="application/xml")

@app.post("/api/voice/partial-result")
async def handle_partial_speech_result(request: Request):
    """Handle partial speech results for real-time feedback"""
    try:
        form_data = await request.form()
        request_data = dict(form_data)
        
        call_sid = request_data.get('CallSid')
        unstable_speech = request_data.get('UnstableSpeechResult', '')
        
        logger.info(f"Partial speech for {call_sid}: '{unstable_speech}'")
        
        # You could use this for real-time UI updates
        # For now, just log it
        
        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"Error handling partial speech result: {str(e)}")
        return {"error": str(e)}

@app.get("/api/debug/ngrok-status")
async def debug_ngrok_status():
    """Debug endpoint to check ngrok configuration"""
    ngrok_url = config('NGROK_URL', default='http://localhost:8000')
    
    return {
        "ngrok_url_from_env": ngrok_url,
        "webhook_urls": {
            "handle_call": f"{ngrok_url}/api/voice/handle-call",
            "process_response": f"{ngrok_url}/api/voice/process-response",
            "partial_result": f"{ngrok_url}/api/voice/partial-result",
            "status_callback": f"{ngrok_url}/api/voice/status-callback"
        },
        "recommendations": [
            "Ensure NGROK_URL in .env matches your current ngrok URL",
            "Restart server after updating NGROK_URL",
            "Test webhook URLs are accessible from internet"
        ]
    }

@app.get("/api/voice/transcript/{call_sid}")
async def get_full_transcript(call_sid: str):
    """Get complete call transcript and negotiation outcome"""
    try:
        call_session = call_manager.get_call_session(call_sid)
        if not call_session:
            raise HTTPException(status_code=404, detail="Call transcript not found")
        
        return {
            "call_sid": call_sid,
            "conversation_id": call_session["conversation_id"],
            "creator_id": call_session["creator_id"],
            "campaign_brief": call_session["campaign_brief"],
            "transcript": call_session["transcript"],
            "final_deal": call_session["current_deal"],
            "call_duration": (datetime.now() - call_session["start_time"]).total_seconds(),
            "status": call_session["conversation_state"],
            "creator_name": call_session["creator_profile"]["name"]
        }
        
    except Exception as e:
        logger.error(f"Failed to get transcript: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/voice/status-callback")
async def call_status_callback(request: Request):
    """Handle call status updates from Twilio"""
    try:
        form_data = await request.form()
        status_data = dict(form_data)
        
        call_sid = status_data.get('CallSid')
        call_status = status_data.get('CallStatus')
        
        logger.info(f"Call status update: {call_sid} -> {call_status}")
        
        if call_status == 'completed':
            call_manager.update_call_state(call_sid, "completed")
        
        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"Status callback error: {str(e)}")
        return {"error": str(e)}

# OTHER ENDPOINTS

@app.get("/api/voice/download/{file_id}")
async def download_audio_response(file_id: str):
    """Download generated audio response"""
    try:
        if not os.path.exists(file_id):
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        with open(file_id, "rb") as audio_file:
            audio_content = audio_file.read()
        
        voice_service.cleanup_temp_file(file_id)
        
        return Response(
            content=audio_content,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=response.mp3"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading audio file: {str(e)}")
        raise HTTPException(status_code=500, detail="Error downloading audio file")

@app.get("/api/voice/voices")
async def get_available_voices():
    """Get available voice options"""
    return await voice_service.get_available_voices()

@app.get("/api/creators/{creator_id}")
async def get_creator(creator_id: str):
    """Get creator profile and performance data"""
    creator = get_creator_profile(creator_id)
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found")
    return creator

@app.get("/api/creators")
async def list_creators():
    """Get list of all available creators"""
    return get_all_creators()

@app.get("/api/market-data")
async def get_market_data():
    """Get industry benchmarks and pricing data"""
    return data_service.get_market_data()

@app.get("/api/conversation/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get full conversation history"""
    conversation = conversation_manager.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {
        **conversation,
        "messages": conversation_manager.get_messages(conversation_id),
        "conversation_summary": conversation_manager.get_conversation_summary(conversation_id),
        "negotiation_insights": conversation_manager.get_negotiation_insights(conversation_id)
    }

@app.get("/api/conversation/{conversation_id}/summary")
async def get_conversation_summary(conversation_id: str):
    """Get conversation summary"""
    summary = conversation_manager.get_conversation_summary(conversation_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return summary

@app.get("/api/conversation/{conversation_id}/insights")
async def get_negotiation_insights(conversation_id: str):
    """Get negotiation insights and recommendations"""
    insights = conversation_manager.get_negotiation_insights(conversation_id)
    if not insights:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return insights

# Helper functions

def get_creator_profile(creator_name: str) -> Optional[Dict]:
    """Get creator profile by name"""
    return data_service.get_creator_by_name(creator_name)

def get_all_creators() -> List[Dict]:
    """Return all mock creator profiles"""
    return data_service.get_all_creators()

def generate_negotiation_strategy(brief: CampaignBrief, creator: Dict) -> Dict:
    """Generate initial negotiation strategy based on brief and creator"""
    creator_rate = creator["typical_rate"]
    budget = brief.budget
    
    # Calculate opening offer (80-90% of typical rate)
    opening_price = min(int(creator_rate * 0.85), budget + 500)
    
    return {
        "opening_price": opening_price,
        "max_budget": budget + 800,
        "flexibility_areas": ["timeline", "deliverables", "usage_rights"],
        "key_selling_points": [
            f"High engagement rate: {creator['engagement_rate']}%",
            f"Consistent viewership: {creator['average_views']:,} avg views",
            f"Strong performance metrics: {creator['performance_metrics']['avg_completion_rate']}% completion rate"
        ],
        "negotiation_approach": "professional_consultant",
        "data_points": {
            "cost_per_view": round(opening_price / creator["average_views"], 4),
            "engagement_value": round(opening_price / (creator["average_views"] * creator["engagement_rate"] / 100), 2)
        }
    }

def generate_negotiation_strategy_for_call(campaign_brief: Dict, creator: Dict) -> Dict:
    """Generate negotiation strategy for phone calls"""
    typical_rate = creator['typical_rate']
    budget_max = campaign_brief.get('budget_max', typical_rate + 500)
    
    # Calculate opening offer (80-90% of typical rate, within budget)
    opening_price = min(int(typical_rate * 0.85), budget_max - 200)
    
    return {
        "opening_deal": {
            "price": opening_price,
            "deliverables": campaign_brief.get('deliverables', ['video_review', 'instagram_post']),
            "timeline": campaign_brief.get('timeline', '2 weeks'),
            "usage_rights": "6 months"
        },
        "max_budget": budget_max,
        "flexibility_areas": ["timeline", "deliverables", "usage_rights"],
        "key_selling_points": [
            f"Perfect audience match - {creator['engagement_rate']}% engagement",
            f"Strong viewership - {creator['average_views']:,} average views",
            f"Professional track record - {creator['performance_metrics']['avg_completion_rate']}% completion rate"
        ],
        "cost_per_view": round(opening_price / creator['average_views'], 4)
    }

async def generate_negotiation_response_for_call(call_session: Dict, creator_message: str) -> Dict:
    """Generate AI response to creator's negotiation point during phone call"""
    
    # Build conversation context
    conversation_context = {
        "campaign_brief": call_session["campaign_brief"],
        "creator_profile": call_session["creator_profile"],
        "current_deal": call_session["current_deal"],
        "conversation_history": call_session["transcript"],
        "strategy": call_session["strategy"]
    }
    
    # Use existing negotiation manager with phone-specific adaptation
    try:
        response = negotiation_manager.process_negotiation_message(
            conversation_context, creator_message, "creator"
        )
        
        # Adapt response for phone conversation (shorter, more conversational)
        if len(response["message"]) > 200:
            # Truncate long responses for phone calls
            response["message"] = response["message"][:200] + "..."
        
        return response
    except Exception as e:
        logger.error(f"Error generating call response: {str(e)}")
        # Fallback response for phone calls
        return {
            "message": "That's a great point. Let me see what we can do to make this work for both of us. What's most important to you in this collaboration?",
            "insights": [],
            "strategy_notes": "Fallback response during call"
        }

async def handle_call_completion(call_session: Dict) -> Response:
    """Handle call completion"""
    response = VoiceResponse()
    response.say("Thank you for the conversation!")
    call_manager.update_call_state(call_session["call_sid"], "completed")
    return Response(content=str(response), media_type="application/xml")

def generate_ai_response(conversation: Dict, user_message: str) -> Dict:
    """Generate AI negotiation response using OpenAI service"""
    try:
        response = negotiation_manager.process_negotiation_message(
            conversation, user_message, "creator"
        )
        return response
    except Exception as e:
        logger.error(f"Error in AI response generation: {str(e)}")
        # Fallback response
        creator_profile = conversation["creator_profile"]
        return {
            "message": f"I understand your position. Let me analyze {creator_profile['name']}'s metrics and propose an alternative that works for both parties.",
            "insights": [f"Creator typically charges ${creator_profile['typical_rate']:,}"],
            "strategy_notes": "Fallback response due to technical issue"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)