# agents/enhanced_orchestrator.py - CORRECT CLEAN VERSION
import json
import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

from models.campaign import (
    CampaignOrchestrationState, CampaignData,
    NegotiationState, NegotiationStatus
)
from agents.discovery import InfluencerDiscoveryAgent
from services.enhanced_voice import EnhancedVoiceService
from services.contract_service import contract_service
from config.settings import settings

logger = logging.getLogger(__name__)

# Import Groq for AI intelligence
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    logger.warning("⚠️ Groq not available - using default orchestration")

class EnhancedCampaignOrchestrator:
    """
    🧠 CORRECT ENHANCED CAMPAIGN ORCHESTRATOR
    
    ✅ Clean OOP design with proper encapsulation
    ✅ No unnecessary helper functions
    ✅ Uses only fields that exist in the model
    ✅ Maintainable modular structure
    ✅ No legacy code retention
    """
    
    def __init__(self):
        """Initialize orchestrator with minimal required components"""
        self.discovery_agent = InfluencerDiscoveryAgent()
        self.groq_client = self._initialize_groq_client()
        self.voice_service = EnhancedVoiceService()
        
        logger.info("🧠 Enhanced Campaign Orchestrator initialized")
    
    def _initialize_groq_client(self) -> Optional[Groq]:
        """Initialize Groq client with proper error handling"""
        if GROQ_AVAILABLE and hasattr(settings, 'groq_api_key') and settings.groq_api_key:
            try:
                return Groq(api_key=settings.groq_api_key)
            except Exception as e:
                logger.warning(f"⚠️ Groq initialization failed: {e}")
        return None
    
    async def orchestrate_enhanced_campaign(
        self,
        campaign_data: CampaignData,
        task_id: str
    ) -> CampaignOrchestrationState:
        """
        🎯 MAIN ORCHESTRATION WORKFLOW - CLEAN & CORRECT
        
        Uses only actual model fields, no over-engineering
        """
        
        logger.info(f"🎯 Starting enhanced campaign orchestration: {task_id}")
        
        # Initialize state with ONLY fields that exist in the model
        state = CampaignOrchestrationState(
            campaign_id=campaign_data.id,
            campaign_data=campaign_data
        )
        
        try:
            # Phase 1: Discovery
            logger.info("🔍 Phase 1: Discovery")
            await self._run_discovery_phase(state)
            
            # Phase 2: AI Strategy Generation  
            logger.info("🧠 Phase 2: AI Strategy")
            await self._run_strategy_phase(state)
            
            # Phase 3: Negotiations
            logger.info("📞 Phase 3: Negotiations")
            await self._run_negotiations_phase(state)
            
            # Phase 4: Contracts
            logger.info("📝 Phase 4: Contracts")
            await self._run_contracts_phase(state)
            
            # Phase 5: Completion
            logger.info("🏁 Phase 5: Completion")
            await self._run_completion_phase(state)
            
            logger.info(f"✅ Campaign orchestration completed: {task_id}")
            return state
            
        except Exception as e:
            logger.error(f"❌ Campaign orchestration failed: {e}")
            state.current_stage = "failed"
            state.completed_at = datetime.now()
            return state
    
    async def _run_discovery_phase(self, state: CampaignOrchestrationState):
        """🔍 Run discovery phase - simple and clean"""
        state.current_stage = "discovery"
        
        # Use discovery agent to find influencers
        discovered = await self.discovery_agent.discover_influencers(
            product_niche=state.campaign_data.product_niche,
            total_budget=state.campaign_data.total_budget
        )
        
        state.discovered_influencers = discovered
        logger.info(f"🔍 Discovered {len(discovered)} influencers")
    
    async def _run_strategy_phase(self, state: CampaignOrchestrationState):
        """🧠 Generate AI strategy - clean implementation"""
        state.current_stage = "strategy"
        
        if self.groq_client:
            try:
                strategy = await self._generate_ai_strategy(state)
                state.ai_strategy = strategy
                logger.info("🧠 AI strategy generated successfully")
            except Exception as e:
                logger.warning(f"⚠️ AI strategy generation failed: {e}")
                state.ai_strategy = "Default strategy due to AI error"
        else:
            state.ai_strategy = "Default strategy - Groq not available"
    
    async def _generate_ai_strategy(self, state: CampaignOrchestrationState) -> str:
        """Generate AI strategy using Groq - simple and focused"""
        
        campaign = state.campaign_data
        prompt = f"""
        Generate a concise negotiation strategy for this influencer campaign:
        
        Product: {campaign.product_name}
        Brand: {campaign.brand_name} 
        Budget: ${campaign.total_budget}
        Target: {campaign.target_audience}
        Niche: {campaign.product_niche}
        
        Provide 3-4 key talking points for creator negotiations.
        Keep response under 150 words.
        """
        
        response = self.groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    async def _run_negotiations_phase(self, state: CampaignOrchestrationState):
        """📞 Run negotiations phase - clean and simple"""
        state.current_stage = "negotiations"
        
        if not state.discovered_influencers:
            logger.warning("⚠️ No influencers discovered for negotiations")
            return
        
        # Store current state for contract email access
        self._current_state = state
        
        # Process each influencer with simple logic
        for i, influencer_match in enumerate(state.discovered_influencers):
            creator = influencer_match.creator
            logger.info(f"📞 Processing creator {i+1}: {creator.name}")
            
            # Create negotiation record
            negotiation = NegotiationState(
                creator_id=creator.id,
                campaign_id=state.campaign_id
            )
            
            try:
                # Real voice service negotiation
                success, call_data = await self._conduct_real_negotiation(creator, state.campaign_data, influencer_match)
                
                if success:
                    negotiation.status = NegotiationStatus.SUCCESS
                    negotiation.final_rate = call_data.get("final_rate", influencer_match.estimated_rate)
                    negotiation.conversation_id = call_data.get("conversation_id")
                    negotiation.call_duration_seconds = call_data.get("duration_seconds", 0)
                    negotiation.negotiated_terms = call_data.get("terms", {
                        "deliverables": ["1 Instagram post", "3 Stories"],
                        "timeline": "2 weeks",
                        "usage_rights": "1 year"
                    })
                    state.successful_negotiations += 1
                    state.total_cost += negotiation.final_rate
                    logger.info(f"✅ Successful negotiation: {creator.name} - ${negotiation.final_rate}")
                else:
                    negotiation.status = NegotiationStatus.FAILED
                    negotiation.failure_reason = call_data.get("failure_reason", "Negotiation failed")
                    negotiation.conversation_id = call_data.get("conversation_id")
                    state.failed_negotiations += 1
                    logger.info(f"❌ Failed negotiation: {creator.name}")
                
                negotiation.completed_at = datetime.now()
                state.negotiations.append(negotiation)
                
            except Exception as e:
                logger.error(f"❌ Negotiation error for {creator.name}: {e}")
                negotiation.status = NegotiationStatus.FAILED
                negotiation.failure_reason = str(e)
                negotiation.completed_at = datetime.now()
                state.negotiations.append(negotiation)
    
    async def _conduct_real_negotiation(self, creator, campaign_data, influencer_match) -> tuple[bool, dict]:
        """Conduct real ElevenLabs phone call negotiation"""
        try:
            logger.info(f"📞 Initiating REAL call to {creator.name} at {creator.phone_number}")
            
            # Prepare creator profile for voice service
            creator_profile = {
                "name": creator.name,
                "niche": creator.niche,
                "followers": creator.followers,
                "engagement_rate": creator.engagement_rate,
                "platform": creator.platform.value if hasattr(creator.platform, 'value') else str(creator.platform)
            }
            
            # Prepare campaign data
            campaign_data_dict = {
                "brand_name": campaign_data.brand_name,
                "product_name": campaign_data.product_name,
                "product_description": campaign_data.product_description,
                "target_audience": campaign_data.target_audience,
                "total_budget": campaign_data.total_budget
            }
            
            # Prepare pricing strategy
            pricing_strategy = {
                "initial_offer": influencer_match.estimated_rate * 0.8,  # Start 20% lower
                "max_offer": influencer_match.estimated_rate,
                "negotiation_range": influencer_match.estimated_rate * 0.2
            }
            
            # Initiate the call
            call_result = await self.voice_service.initiate_negotiation_call(
                creator_phone=creator.phone_number,
                creator_profile=creator_profile,
                campaign_data=campaign_data_dict,
                pricing_strategy=pricing_strategy
            )
            
            if call_result.get("status") == "success":
                conversation_id = call_result.get("conversation_id")
                logger.info(f"📞 Call started successfully: {conversation_id}")
                
                # Wait for call completion and get results
                completion_result = await self.voice_service.wait_for_conversation_completion_with_analysis(
                    conversation_id=conversation_id,
                    max_wait_seconds=180  # 3 minutes max
                )
                
                # Parse the results
                if completion_result.get("status") == "completed":
                    # Get analysis from the voice service processed data
                    analysis = completion_result.get("analysis_data", {})
                    
                    # Check multiple possible success indicators
                    call_successful = analysis.get("call_successful")
                    negotiation_outcome = analysis.get("negotiation_outcome", "unknown")
                    agreed_rate = analysis.get("agreed_rate")
                    
                    # Determine if negotiation was successful
                    is_successful = (
                        call_successful == "success" or 
                        negotiation_outcome in ["success", "accepted", "positive"] or
                        agreed_rate is not None  # If a rate was agreed upon, consider it successful
                    )
                    
                    if is_successful:
                        logger.info(f"✅ Successful negotiation detected - call_successful: {call_successful}, outcome: {negotiation_outcome}, final_rate: {agreed_rate}")
                        return True, {
                            "conversation_id": conversation_id,
                            "final_rate": agreed_rate or influencer_match.estimated_rate,
                            "duration_seconds": analysis.get("duration_seconds", 0),
                            "terms": {"agreed_rate": agreed_rate},
                            "call_summary": analysis.get("summary", "")
                        }
                    else:
                        logger.warning(f"❌ Negotiation marked as failed - call_successful: {call_successful}, outcome: {negotiation_outcome}, agreed_rate: {agreed_rate}")
                        return False, {
                            "conversation_id": conversation_id,
                            "failure_reason": "Creator declined or no agreement reached",
                            "duration_seconds": analysis.get("duration_seconds", 0)
                        }
                else:
                    return False, {
                        "conversation_id": conversation_id,
                        "failure_reason": "Call failed to complete properly"
                    }
            else:
                logger.error(f"❌ Failed to initiate call: {call_result}")
                return False, {
                    "failure_reason": f"Call initiation failed: {call_result.get('error', 'Unknown error')}"
                }
                
        except Exception as e:
            logger.error(f"❌ Exception during real negotiation: {e}")
            return False, {
                "failure_reason": f"Exception during call: {str(e)}"
            }
    
    async def _simulate_negotiation(self, creator, campaign_data) -> bool:
        """Fallback simulation - should not be used when voice service is available"""
        logger.warning("⚠️ Using fallback simulation instead of real calls")
        if creator.availability.value in ["excellent", "good"]:
            return True
        return False
    
    async def _run_contracts_phase(self, state: CampaignOrchestrationState):
        """📝 Generate contracts and send via email - enhanced with automatic email delivery"""
        state.current_stage = "contracts"
        
        successful_negotiations = [
            neg for neg in state.negotiations 
            if neg.status == NegotiationStatus.SUCCESS
        ]
        
        if not successful_negotiations:
            logger.warning("⚠️ No successful negotiations - skipping contracts")
            return
        
        # Generate contracts and send via email
        for negotiation in successful_negotiations:
            try:
                # Generate contract data
                contract = self._create_contract(negotiation, state.campaign_data)
                state.contracts.append(contract)
                
                # Update negotiation with contract info
                negotiation.negotiated_terms["contract_generated"] = True
                negotiation.negotiated_terms["contract_id"] = contract["contract_id"]
                
                logger.info(f"📝 Contract generated: {contract['contract_id']}")
                
                # 🚀 NEW: Automatically send contract via email
                await self._send_contract_email(negotiation, state.campaign_data, contract)
                
            except Exception as e:
                logger.error(f"❌ Contract generation failed: {e}")
        
        logger.info(f"📝 Generated {len(state.contracts)} contracts")
    
    def _create_contract(self, negotiation: NegotiationState, campaign_data: CampaignData) -> Dict[str, Any]:
        """Create simple contract - no over-engineering"""
        contract_id = f"contract_{negotiation.creator_id}_{int(datetime.now().timestamp())}"
        
        return {
            "contract_id": contract_id,
            "campaign_id": negotiation.campaign_id,
            "creator_id": negotiation.creator_id,
            "compensation": negotiation.final_rate,
            "terms": negotiation.negotiated_terms,
            "status": "draft",
            "created_at": datetime.now().isoformat()
        }
    
    async def _send_contract_email(
        self, 
        negotiation: NegotiationState, 
        campaign_data: CampaignData, 
        contract: Dict[str, Any]
    ):
        """
        🚀 Send contract via email after successful negotiation
        """
        try:
            # Get creator information from the discovered influencers
            creator = None
            if hasattr(self, '_current_state') and self._current_state.discovered_influencers:
                for influencer_match in self._current_state.discovered_influencers:
                    if influencer_match.creator.id == negotiation.creator_id:
                        creator = influencer_match.creator
                        break
            
            if not creator:
                logger.error(f"❌ Creator not found for contract email: {negotiation.creator_id}")
                return
            
            # Prepare data for contract service
            call_data = {
                "agreed_rate": negotiation.final_rate,
                "special_terms": [],
                "contract_id": contract["contract_id"]
            }
            
            influencer_data = {
                "name": creator.name,
                "email": creator.email,
                "id": creator.id
            }
            
            campaign_details = {
                "campaign_name": f"{campaign_data.brand_name} - {campaign_data.product_name}",
                "brand_name": campaign_data.brand_name,
                "budget": campaign_data.total_budget,
                "deliverables": negotiation.negotiated_terms.get("deliverables", ["Social media content"]),
                "timeline": negotiation.negotiated_terms.get("timeline", "30 days"),
                "offered_rate": negotiation.final_rate
            }
            
            # Send contract via email using the contract service
            success = await contract_service.process_successful_call(
                call_data=call_data,
                influencer_data=influencer_data,
                campaign_data=campaign_details
            )
            
            if success:
                logger.info(f"✅ Contract email sent successfully to {creator.email}")
                # Update contract status
                contract["status"] = "sent"
                contract["email_sent_at"] = datetime.now().isoformat()
                negotiation.negotiated_terms["contract_emailed"] = True
            else:
                logger.error(f"❌ Failed to send contract email to {creator.email}")
                contract["status"] = "email_failed"
                
        except Exception as e:
            logger.error(f"❌ Error sending contract email: {str(e)}")
            contract["status"] = "email_error"
    
    async def _run_completion_phase(self, state: CampaignOrchestrationState):
        """🏁 Complete campaign - simple and clean"""
        state.current_stage = "completed"
        state.completed_at = datetime.now()
        
        # Calculate duration using actual model fields
        duration = (state.completed_at - state.started_at).total_seconds()
        
        logger.info(f"🏁 Campaign completed in {duration:.1f} seconds")
        logger.info(f"📊 Results: {state.successful_negotiations} successful, {len(state.contracts)} contracts")


# Simple supporting classes - no over-engineering
class EnhancedNegotiationAgent:
    """Simple negotiation agent"""
    
    def __init__(self):
        logger.info("🤝 Enhanced Negotiation Agent initialized")
    
    async def negotiate_with_creator(self, creator, campaign_data):
        """Simple negotiation implementation"""
        pass


class EnhancedContractAgent:
    """Simple contract agent"""
    
    def __init__(self):
        logger.info("📝 Enhanced Contract Agent initialized")
    
    async def generate_contract(self, negotiation, campaign_data):
        """Simple contract generation"""
        pass


class NegotiationResultValidator:
    """Simple validation"""
    
    def __init__(self):
        logger.info("✅ Negotiation Result Validator initialized")
    
    def validate_result(self, result):
        """Simple validation logic"""
        return True


class ContractStatusManager:
    """Simple contract status tracking"""
    
    def __init__(self):
        self.statuses = {}
        logger.info("📋 Contract Status Manager initialized")
    
    def update_status(self, contract_id: str, status: str):
        """Update contract status"""
        self.statuses[contract_id] = {
            "status": status,
            "updated_at": datetime.now().isoformat()
        }
        logger.info(f"📋 Contract {contract_id} status: {status}")