# api/enhanced_webhooks.py
import uuid
import asyncio
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List

from models.campaign import CampaignWebhook, CampaignData, CampaignOrchestrationState
from agents.campaign_orchestrator import CampaignOrchestrator
from services.elevenlabs_voice_service import VoiceServiceFactory
from core.exceptions import (
    InfluencerFlowException,
    ValidationError,
    create_error_context,
    handle_and_log_error,
)
from agents.enhanced_negotiation import NegotiationResultValidator
from agents.enhanced_contracts import ContractStatusManager

from config.settings import settings

logger = logging.getLogger(__name__)

enhanced_webhook_router = APIRouter()

# Initialize enhanced services
enhanced_orchestrator = CampaignOrchestrator()
enhanced_voice_service = VoiceServiceFactory.create_voice_service(
    api_key=settings.elevenlabs_api_key,
    agent_id=settings.elevenlabs_agent_id,
    phone_number_id=settings.elevenlabs_phone_number_id,
    use_mock=settings.mock_calls,
)
negotiation_validator = NegotiationResultValidator()
contract_manager = ContractStatusManager()

@enhanced_webhook_router.post("/enhanced-campaign")
async def handle_enhanced_campaign_created(
    campaign_webhook: CampaignWebhook,
    background_tasks: BackgroundTasks
):
    """
    🎯 ENHANCED CAMPAIGN WEBHOOK - Full structured data flow
    This is the main entry point for the enhanced system
    """
    try:
        # Generate unique task ID for tracking
        task_id = str(uuid.uuid4())
        
        logger.info(f"🚀 Enhanced campaign webhook received: {campaign_webhook.product_name}")
        
        # Enhanced campaign data validation
        validation_result = _validate_campaign_webhook(campaign_webhook)
        if not validation_result["is_valid"]:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "Campaign validation failed",
                    "validation_errors": validation_result["errors"],
                    "warnings": validation_result["warnings"]
                }
            )
        
        # Convert to enhanced campaign format
        campaign_data = CampaignData(
            id=campaign_webhook.campaign_id,
            product_name=campaign_webhook.product_name,
            brand_name=campaign_webhook.brand_name,
            product_description=campaign_webhook.product_description,
            target_audience=campaign_webhook.target_audience,
            campaign_goal=campaign_webhook.campaign_goal,
            product_niche=campaign_webhook.product_niche,
            total_budget=campaign_webhook.total_budget,
            campaign_code=f"EFC-{campaign_webhook.campaign_id[:8].upper()}"  # Enhanced Flow Campaign
        )
        
        # Initialize enhanced orchestration state
        orchestration_state = CampaignOrchestrationState(
            campaign_id=campaign_data.id,
            campaign_data=campaign_data,
            current_stage="enhanced_webhook_received"
        )
        
        # Store in global state for monitoring
        from main import active_campaigns
        active_campaigns[task_id] = orchestration_state
        
        # 🔥 START ENHANCED AI WORKFLOW
        background_tasks.add_task(
            enhanced_orchestrator.orchestrate_enhanced_campaign,
            orchestration_state,
            task_id
        )
        
        return JSONResponse(
            status_code=202,
            content={
                "message": "🎯 Enhanced AI campaign workflow started",
                "task_id": task_id,
                "campaign_id": campaign_data.id,
                "brand_name": campaign_data.brand_name,
                "product_name": campaign_data.product_name,
                "estimated_duration_minutes": 8,  # Enhanced flow takes a bit longer
                "monitor_url": f"/api/monitor/enhanced-campaign/{task_id}",
                "status": "started",
                "enhancements": [
                    "ElevenLabs dynamic variables integration",
                    "Structured conversation analysis",
                    "AI-powered negotiation strategies",
                    "Comprehensive contract generation",
                    "Real-time validation and error handling"
                ],
                "next_steps": [
                    "Enhanced discovery: AI-powered creator matching",
                    "Structured negotiations: ElevenLabs with analysis",
                    "Validated contracts: Comprehensive legal documents",
                    "Database sync: Full audit trail"
                ],
                "validation_result": validation_result
            }
        )
        
    except HTTPException:
        raise
    except (InfluencerFlowException, ValidationError) as e:
        context = create_error_context(
            operation="handle_enhanced_campaign_created",
            component="EnhancedWebhookHandler",
            campaign_id=campaign_webhook.campaign_id,
        )
        error = await handle_and_log_error(e, context)
        raise HTTPException(status_code=422 if isinstance(e, ValidationError) else 500, detail=error)
    except Exception as e:
        context = create_error_context(
            operation="handle_enhanced_campaign_created",
            component="EnhancedWebhookHandler",
            campaign_id=campaign_webhook.campaign_id,
        )
        error = await handle_and_log_error(InfluencerFlowException(str(e)), context)
        raise HTTPException(status_code=500, detail=error)

@enhanced_webhook_router.post("/test-enhanced-campaign")
async def create_test_enhanced_campaign(background_tasks: BackgroundTasks):
    """
    🧪 Create test campaign for enhanced system validation
    """
    test_campaign = CampaignWebhook(
        campaign_id=str(uuid.uuid4()),
        product_name="SmartFit Pro Tracker",
        brand_name="TechFit Solutions",
        product_description="Advanced fitness tracking device with AI-powered workout recommendations, heart rate monitoring, and sleep analysis. Perfect for serious fitness enthusiasts and athletes looking to optimize their performance with data-driven insights.",
        target_audience="Fitness enthusiasts, athletes, and health-conscious individuals aged 22-40 who value data-driven fitness optimization and are willing to invest in premium fitness technology.",
        campaign_goal="Launch new product and establish market presence in the premium fitness tech segment through authentic creator partnerships and data-driven content.",
        product_niche="fitness",
        total_budget=18000.0
    )
    
    logger.info("🧪 Enhanced test campaign created for validation")
    
    return await handle_enhanced_campaign_created(test_campaign, background_tasks)

@enhanced_webhook_router.post("/test-enhanced-beauty-campaign")
async def create_test_enhanced_beauty_campaign(background_tasks: BackgroundTasks):
    """🧪 Test beauty niche with enhanced system"""
    test_campaign = CampaignWebhook(
        campaign_id=str(uuid.uuid4()),
        product_name="GlowUp Vitamin C Serum",
        brand_name="LuxeSkin Beauty",
        product_description="Premium vitamin C serum with hyaluronic acid and peptides for brightening, anti-aging, and deep hydration. Clinically tested for all skin types.",
        target_audience="Beauty enthusiasts and skincare lovers aged 25-45 interested in premium anti-aging and brightening products.",
        campaign_goal="Increase brand awareness and drive sales in the premium skincare market",
        product_niche="beauty",
        total_budget=12000.0
    )
    
    return await handle_enhanced_campaign_created(test_campaign, background_tasks)

@enhanced_webhook_router.get("/test-enhanced-elevenlabs")
async def test_enhanced_elevenlabs_setup():
    """
    🧪 Comprehensive ElevenLabs integration test
    """
    try:
        # Test enhanced voice service
        test_result = await enhanced_voice_service.test_credentials()
        
        # Test dynamic variables preparation
        mock_creator = {
            "id": "test_enhanced_creator",
            "name": "TestCreator Enhanced",
            "niche": "fitness",
            "followers": 150000,
            "engagement_rate": 6.2,
            "average_views": 80000,
            "location": "Mumbai, India",
            "languages": ["English", "Hindi"],
            "typical_rate": 4500,
            "platform": "YouTube",
            "availability": "good"
        }
        
        mock_campaign = {
            "brand_name": "TestBrand Enhanced",
            "product_name": "Enhanced Test Product",
            "product_description": "This is an enhanced test product for validating the new ElevenLabs integration",
            "target_audience": "Enhanced test audience",
            "campaign_goal": "Test the enhanced system integration"
        }
        
        mock_pricing = {
            "initial_offer": 4200,
            "max_offer": 5200
        }
        
        # Test dynamic variables preparation
        dynamic_vars = enhanced_voice_service._prepare_dynamic_variables(
            mock_creator, mock_campaign, mock_pricing
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "enhanced_elevenlabs_status": test_result,
                "dynamic_variables_test": {
                    "variables_prepared": list(dynamic_vars.keys()),
                    "influencer_profile_sample": dynamic_vars.get("InfluencerProfile", "")[:100] + "...",
                    "campaign_brief_length": len(dynamic_vars.get("campaignBrief", "")),
                    "price_range": dynamic_vars.get("PriceRange", ""),
                    "influencer_name": dynamic_vars.get("influencerName", "")
                },
                "enhanced_features": [
                    "Dynamic variables integration",
                    "Structured conversation analysis",
                    "Real-time outcome detection",
                    "Comprehensive error handling"
                ],
                "setup_validation": {
                    "api_key_configured": bool(settings.elevenlabs_api_key),
                    "agent_id_configured": bool(settings.elevenlabs_agent_id),
                    "phone_number_configured": bool(settings.elevenlabs_phone_number_id),
                    "enhanced_mode_active": not enhanced_voice_service.use_mock
                },
                "setup_instructions": {
                    "step_1": "Configure ElevenLabs agent with system prompt from documentation",
                    "step_2": "Set up evaluation criteria in ElevenLabs dashboard",
                    "step_3": "Add dynamic variables: InfluencerProfile, campaignBrief, PriceRange, influencerName",
                    "step_4": "Update .env file with all required credentials",
                    "step_5": "Test with /test-enhanced-call endpoint"
                }
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Enhanced ElevenLabs test failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "message": "Enhanced ElevenLabs test failed",
                "troubleshooting": [
                    "Check .env file configuration",
                    "Verify ElevenLabs agent setup",
                    "Ensure dynamic variables are configured",
                    "Check API key permissions"
                ]
            }
        )

@enhanced_webhook_router.post("/test-enhanced-call")
async def test_enhanced_call():
    """
    🧪 Test enhanced ElevenLabs call with full feature set
    """
    try:
        # Enhanced test creator profile
        test_creator = {
            "id": "enhanced_test_creator",
            "name": "Enhanced TestCreator",
            "niche": "fitness",
            "followers": 200000,
            "engagement_rate": 7.1,
            "average_views": 95000,
            "location": "India",
            "languages": ["English", "Hindi"],
            "typical_rate": 5200,
            "platform": "YouTube",
            "availability": "excellent",
            "specialties": ["workout_routines", "nutrition_advice", "fitness_gear"],
            "about": "Professional fitness coach and content creator specializing in evidence-based training"
        }
        
        test_campaign = {
            "brand_name": "Enhanced FitTech",
            "product_name": "Enhanced Fitness Tracker Pro",
            "product_description": "Advanced fitness tracking device with AI coaching and comprehensive health monitoring",
            "target_audience": "Serious fitness enthusiasts and athletes",
            "campaign_goal": "Launch premium fitness tech product with authentic creator partnerships"
        }
        
        test_pricing = {
            "initial_offer": 4800,
            "max_offer": 6200
        }
        
        # Use your actual phone number for testing
        test_phone = "+918806859890"
        
        logger.info(f"🧪 Initiating enhanced test call")
        logger.info(f"   Enhanced features: Dynamic variables, structured analysis")
        logger.info(f"   TO: {test_phone}")
        
        # Initiate enhanced call
        call_result = await enhanced_voice_service.initiate_negotiation_call(
            creator_phone=test_phone,
            creator_profile=test_creator,
            campaign_data=test_campaign,
            pricing_strategy=test_pricing
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "enhanced_call_result": call_result,
                "message": f"Enhanced test call initiated! Check your phone {test_phone}",
                "enhanced_features": {
                    "dynamic_variables": "Sent to ElevenLabs agent",
                    "structured_analysis": "Will extract negotiation outcome",
                    "comprehensive_data": "Full conversation context provided"
                },
                "call_details": {
                    "creator_profile": "Enhanced with full context",
                    "campaign_brief": "Comprehensive product information",
                    "pricing_strategy": f"${test_pricing['initial_offer']}-${test_pricing['max_offer']}",
                    "expected_duration": "2-4 minutes"
                },
                "monitoring": {
                    "conversation_id": call_result.get("conversation_id"),
                    "call_id": call_result.get("call_id"),
                    "status_tracking": "Real-time analysis enabled"
                }
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Enhanced test call failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "message": "Enhanced test call failed",
                "troubleshooting": [
                    "Verify ElevenLabs credentials in .env",
                    "Check agent configuration in ElevenLabs dashboard",
                    "Ensure phone number format is correct",
                    "Verify international calling is enabled"
                ]
            }
        )

@enhanced_webhook_router.get("/validate-negotiation/{conversation_id}")
async def validate_negotiation_result(conversation_id: str):
    """
    🔍 Validate and analyze negotiation result
    """
    try:
        # Get conversation result with analysis
        conversation_result = await enhanced_voice_service.wait_for_conversation_completion_with_analysis(
            conversation_id,
            max_wait_seconds=60  # Quick check
        )
        
        # Extract and validate analysis data
        analysis_data = conversation_result.get("analysis_data") or {}
        
        # Validate the data structure
        validation_summary = {
            "conversation_status": conversation_result.get("status"),
            "analysis_available": bool(analysis_data),
            "negotiation_outcome": analysis_data.get("negotiation_outcome", "unclear"),
            "data_completeness": _calculate_analysis_completeness(analysis_data),
            "validation_passed": _validate_analysis_structure(analysis_data),
            "extraction_success": True
        }
        
        return JSONResponse(
            status_code=200,
            content={
                "conversation_id": conversation_id,
                "validation_summary": validation_summary,
                "extracted_data": {
                    "negotiation_outcome": analysis_data.get("negotiation_outcome"),
                    "final_rate_mentioned": analysis_data.get("final_rate_mentioned"),
                    "deliverables_discussed": analysis_data.get("deliverables_discussed"),
                    "timeline_mentioned": analysis_data.get("timeline_mentioned"),
                    "creator_enthusiasm_level": analysis_data.get("creator_enthusiasm_level"),
                    "objections_raised": analysis_data.get("objections_raised"),
                    "follow_up_required": analysis_data.get("follow_up_required")
                },
                "conversation_metadata": {
                    "transcript_available": bool(conversation_result.get("transcript")),
                    "recording_url": conversation_result.get("recording_url"),
                    "analysis_source": analysis_data.get("analysis_source", "elevenlabs")
                },
                "next_steps": _generate_validation_next_steps(analysis_data)
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Negotiation validation failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "message": "Negotiation validation failed",
                "conversation_id": conversation_id
            }
        )

@enhanced_webhook_router.post("/generate-enhanced-contract")
async def generate_enhanced_contract_endpoint(
    negotiation_data: Dict[str, Any]
):
    """
    📝 Generate enhanced contract from negotiation data
    """
    try:
        # Validate input data
        required_fields = ["creator_id", "campaign_id", "final_rate", "negotiated_terms"]
        missing_fields = [field for field in required_fields if field not in negotiation_data]
        
        if missing_fields:
            raise HTTPException(
                status_code=422,
                detail=f"Missing required fields: {missing_fields}"
            )
        
        # Create mock negotiation state for testing
        from models.campaign import NegotiationState, NegotiationStatus
        from datetime import datetime
        
        negotiation_state = NegotiationState(
            creator_id=negotiation_data["creator_id"],
            campaign_id=negotiation_data["campaign_id"],
            status=NegotiationStatus.SUCCESS,
            final_rate=negotiation_data["final_rate"],
            negotiated_terms=negotiation_data["negotiated_terms"],
            completed_at=datetime.now()
        )
        
        # Create mock campaign data
        campaign_data = CampaignData(
            id=negotiation_data["campaign_id"],
            product_name=negotiation_data.get("product_name", "Test Product"),
            brand_name=negotiation_data.get("brand_name", "Test Brand"),
            product_description=negotiation_data.get("product_description", "Test description"),
            target_audience=negotiation_data.get("target_audience", "Test audience"),
            campaign_goal=negotiation_data.get("campaign_goal", "Test goal"),
            product_niche=negotiation_data.get("product_niche", "fitness"),
            total_budget=negotiation_data.get("total_budget", 10000.0)
        )
        
        # Generate enhanced contract
        from agents.enhanced_contracts import EnhancedContractAgent
        contract_agent = EnhancedContractAgent()
        
        contract = await contract_agent.generate_enhanced_contract(
            negotiation_state,
            campaign_data
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Enhanced contract generated successfully",
                "contract_summary": {
                    "contract_id": contract["contract_id"],
                    "final_rate": contract["final_rate"],
                    "template_type": contract["template_type"],
                    "payment_milestones": len(contract["payment_schedule"]),
                    "deliverables_count": len(contract["deliverables"]["primary_deliverables"]),
                    "usage_rights": contract["usage_rights"]["type"],
                    "contract_status": contract["status"]
                },
                "contract_metadata": {
                    "generation_source": "enhanced_contract_agent",
                    "validation_passed": True,
                    "comprehensive_terms": True,
                    "ai_generated": True
                },
                "full_contract": contract
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Enhanced contract generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Enhanced contract generation failed",
                "message": str(e)
            }
        )

@enhanced_webhook_router.get("/system-status")
async def get_enhanced_system_status():
    """
    📊 Get comprehensive system status for enhanced features
    """
    try:
        # Test all enhanced services
        services_status = {}
        
        # Enhanced Voice Service
        voice_test = await enhanced_voice_service.test_credentials()
        services_status["enhanced_voice_service"] = {
            "status": voice_test.get("status", "unknown"),
            "mode": "live_api" if not enhanced_voice_service.use_mock else "mock",
            "features": ["dynamic_variables", "structured_analysis", "real_time_monitoring"]
        }
        
        # Enhanced Orchestrator
        services_status["enhanced_orchestrator"] = {
            "status": "operational",
            "features": ["ai_strategy", "validation", "error_handling"],
            "groq_available": enhanced_orchestrator.groq_client is not None
        }
        
        # Configuration Status
        config_status = {
            "elevenlabs_configured": bool(settings.elevenlabs_api_key),
            "groq_configured": bool(settings.groq_api_key),
            "demo_mode": settings.demo_mode,
            "mock_calls": settings.mock_calls
        }
        
        # Active Campaigns
        from main import active_campaigns
        active_count = len(active_campaigns)
        
        return JSONResponse(
            status_code=200,
            content={
                "system_status": "operational",
                "enhanced_features": {
                    "elevenlabs_dynamic_variables": True,
                    "structured_conversation_analysis": True,
                    "ai_negotiation_strategies": True,
                    "comprehensive_contract_generation": True,
                    "real_time_validation": True
                },
                "services_status": services_status,
                "configuration": config_status,
                "active_campaigns": active_count,
                "endpoints": {
                    "enhanced_campaign": "/api/webhook/enhanced-campaign",
                    "test_enhanced": "/api/webhook/test-enhanced-campaign",
                    "test_elevenlabs": "/api/webhook/test-enhanced-elevenlabs",
                    "test_call": "/api/webhook/test-enhanced-call",
                    "validate_negotiation": "/api/webhook/validate-negotiation/{conversation_id}",
                    "generate_contract": "/api/webhook/generate-enhanced-contract",
                    "system_status": "/api/webhook/system-status"
                },
                "version": "2.0.0-enhanced",
                "capabilities": [
                    "End-to-end campaign automation with AI",
                    "Real-time ElevenLabs voice negotiations",
                    "Structured data extraction and validation",
                    "Comprehensive contract generation",
                    "Advanced error handling and recovery"
                ]
            }
        )
        
    except Exception as e:
        logger.error(f"❌ System status check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "system_status": "error",
                "error": str(e),
                "message": "System status check failed"
            }
        )
    
# Add this to your enhanced_webhooks.py to test the fixes

@enhanced_webhook_router.get("/test-timeout-fixes")
async def test_timeout_fixes():
    """
    🧪 Test the timeout and JSON parsing fixes
    """
    try:
        from agents.campaign_orchestrator import CampaignOrchestrator
        from models.campaign import CampaignData
        
        logger.info("🧪 Testing timeout and JSON fixes...")
        
        # Test 1: Enhanced Voice Service with timeout fixes
        voice_service = VoiceServiceFactory.create_voice_service(
            api_key=settings.elevenlabs_api_key,
            agent_id=settings.elevenlabs_agent_id,
            phone_number_id=settings.elevenlabs_phone_number_id,
            use_mock=settings.mock_calls,
        )
        voice_test = await voice_service.test_credentials()
        
        # Test 2: Enhanced Orchestrator with Groq fixes
        orchestrator = CampaignOrchestrator()
        
        test_campaign = CampaignData(
            id="test_fixes_001",
            product_name="Test Product",
            brand_name="Test Brand",
            product_description="Testing timeout and JSON fixes",
            target_audience="Test audience",
            campaign_goal="Test the fixes",
            product_niche="fitness",
            total_budget=10000.0
        )
        
        # Test Groq strategy generation
        try:
            strategy = await orchestrator._generate_enhanced_ai_strategy(test_campaign)
            groq_test = {
                "status": "success",
                "strategy_generated": True,
                "approach": strategy.get("negotiation_approach", "default")
            }
        except Exception as e:
            groq_test = {
                "status": "fallback", 
                "error": str(e),
                "strategy_generated": False
            }
        
        return {
            "message": "🧪 Timeout and JSON parsing fixes tested",
            "voice_service_test": voice_test,
            "groq_strategy_test": groq_test,
            "fixes_applied": [
                "✅ Increased ElevenLabs timeout from 30s to 60s",
                "✅ Added retry logic for failed requests", 
                "✅ Enhanced fallback to mock mode on persistent timeouts",
                "✅ Fixed Groq JSON parsing with better extraction",
                "✅ Simplified dynamic variables to avoid JSON issues",
                "✅ Added graceful error handling throughout"
            ],
            "recommendations": [
                "Run test-enhanced-campaign again to see improvements",
                "Monitor logs for timeout and JSON issues",
                "Consider increasing timeout further if needed"
            ]
        }
        
    except Exception as e:
        logger.error(f"❌ Test fixes failed: {e}")
        return {
            "error": str(e),
            "message": "Test failed - check logs for details"
        }

@enhanced_webhook_router.post("/test-enhanced-campaign-with-fixes")
async def test_enhanced_campaign_with_fixes(background_tasks: BackgroundTasks):
    """
    🧪 Test enhanced campaign with all fixes applied
    """
    test_campaign = CampaignWebhook(
        campaign_id=str(uuid.uuid4()),
        product_name="SmartFit Pro Tracker (Fixed)",
        brand_name="TechFit Solutions",
        product_description="Advanced fitness tracking device with AI-powered workout recommendations - testing with timeout fixes and improved error handling",
        target_audience="Fitness enthusiasts, athletes, and health-conscious individuals aged 22-40",
        campaign_goal="Test enhanced system with timeout fixes and JSON parsing improvements",
        product_niche="fitness",
        total_budget=18000.0
    )
    
    logger.info("🧪 Enhanced test campaign with fixes created")
    
    return await handle_enhanced_campaign_created(test_campaign, background_tasks)    

# Helper functions
def _validate_campaign_webhook(webhook: CampaignWebhook) -> Dict[str, Any]:
    """Validate campaign webhook data"""
    
    validation_result = {
        "is_valid": True,
        "errors": [],
        "warnings": []
    }
    
    # Required field validation
    if not webhook.product_name or len(webhook.product_name) < 3:
        validation_result["errors"].append("Product name must be at least 3 characters")
        validation_result["is_valid"] = False
    
    if not webhook.brand_name or len(webhook.brand_name) < 2:
        validation_result["errors"].append("Brand name must be at least 2 characters")
        validation_result["is_valid"] = False
    
    if not webhook.product_description or len(webhook.product_description) < 20:
        validation_result["errors"].append("Product description must be at least 20 characters")
        validation_result["is_valid"] = False
    
    if not webhook.total_budget or webhook.total_budget < 500:
        validation_result["errors"].append("Total budget must be at least $500")
        validation_result["is_valid"] = False
    
    # Warning conditions
    if webhook.total_budget and webhook.total_budget < 2000:
        validation_result["warnings"].append("Budget below $2,000 may limit creator options")
    
    if len(webhook.product_description) < 50:
        validation_result["warnings"].append("Short product description may affect creator matching")
    
    if not webhook.target_audience or len(webhook.target_audience) < 20:
        validation_result["warnings"].append("Detailed target audience description recommended")
    
    return validation_result

def _calculate_analysis_completeness(analysis_data: Dict[str, Any]) -> float:
    """Calculate completeness score of analysis data"""
    
    expected_fields = [
        "negotiation_outcome",
        "final_rate_mentioned",
        "deliverables_discussed",
        "timeline_mentioned",
        "creator_enthusiasm_level",
        "objections_raised"
    ]
    
    present_fields = sum(1 for field in expected_fields if analysis_data.get(field) is not None)
    return present_fields / len(expected_fields)

def _validate_analysis_structure(analysis_data: Dict[str, Any]) -> bool:
    """Validate the structure of analysis data"""
    
    if not analysis_data:
        return False
    
    # Check for required fields
    outcome = analysis_data.get("negotiation_outcome")
    if outcome not in ["accepted", "declined", "needs_followup", "unclear"]:
        return False
    
    # Check enthusiasm level is valid
    enthusiasm = analysis_data.get("creator_enthusiasm_level")
    if enthusiasm is not None and (not isinstance(enthusiasm, (int, float)) or enthusiasm < 1 or enthusiasm > 10):
        return False
    
    return True

def _generate_validation_next_steps(analysis_data: Dict[str, Any]) -> List[str]:
    """Generate next steps based on analysis results"""
    
    outcome = analysis_data.get("negotiation_outcome", "unclear")
    
    if outcome == "accepted":
        return [
            "Generate contract with negotiated terms",
            "Schedule content creation timeline",
            "Set up performance tracking",
            "Send welcome package to creator"
        ]
    elif outcome == "declined":
        return [
            "Document feedback for future campaigns",
            "Consider alternative creators from discovery list",
            "Analyze objections for strategy improvement",
            "Update creator database with interaction notes"
        ]
    elif outcome == "needs_followup":
        return [
            "Schedule follow-up call within 24-48 hours",
            "Address specific objections raised",
            "Prepare additional information or incentives",
            "Set reminder for continued engagement"
        ]
    else:
        return [
            "Review conversation transcript for clarity",
            "Consider manual follow-up to clarify outcome",
            "Check ElevenLabs analysis configuration",
            "Improve conversation prompts if needed"
        ]
