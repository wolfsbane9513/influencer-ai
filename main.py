# main.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import uuid
import os
from datetime import datetime
import logging

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
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
negotiation_manager = NegotiationManager()

# API Endpoints

@app.get("/")
async def root():
    return {"message": "InfluencerFlow AI Platform API", "status": "running"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

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
            speaker="agency"  # Assuming agency is speaking to the AI
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

@app.get("/api/voice/download/{file_id}")
async def download_audio_response(file_id: str):
    """Download generated audio response"""
    try:
        # In a real implementation, you'd map file_id to actual file path
        # For demo, we'll assume file_id is the file path (not secure for production)
        
        if not os.path.exists(file_id):
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        # Read file and return as response
        with open(file_id, "rb") as audio_file:
            audio_content = audio_file.read()
        
        # Clean up temp file after reading
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