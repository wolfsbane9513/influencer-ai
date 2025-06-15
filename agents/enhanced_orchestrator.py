# agents/enhanced_orchestrator.py - CORRECTED VERSION
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
from agents.enhanced_negotiation import EnhancedNegotiationAgent, NegotiationResultValidator
from agents.enhanced_contracts import EnhancedContractAgent, ContractStatusManager
from services.database import DatabaseService
from services.enhanced_voice import EnhancedVoiceService
from services.conversation_monitor import ConversationMonitor, ConversationEventHandler

from config.settings import settings

logger = logging.getLogger(__name__)

# Import Groq for AI intelligence
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    logger.warning("⚠️ Groq not available - using enhanced default orchestration")

class EnhancedCampaignOrchestrator:
    """
    🧠 CORRECTED CAMPAIGN ORCHESTRATOR
    
    Key Fixes:
    1. Proper contract generation after successful calls
    2. Better error handling for failed/ended calls
    3. Improved state management throughout workflow
    4. Correct integration with conversation monitoring
    """
    
    def __init__(self):
        # Initialize enhanced agents
        self.discovery_agent = InfluencerDiscoveryAgent()
        self.negotiation_agent = EnhancedNegotiationAgent()
        self.contract_agent = EnhancedContractAgent()
        self.database_service = DatabaseService()
        
        # Initialize voice service and monitoring
        self.voice_service = EnhancedVoiceService()
        self.conversation_monitor = ConversationMonitor(self.voice_service)
        self.event_handler = ConversationEventHandler(self)
        
        # Initialize validators and managers
        self.negotiation_validator = NegotiationResultValidator()
        self.contract_manager = ContractStatusManager()
        
        # Initialize Groq AI client with proper error handling
        self.groq_client = None
        self._initialize_groq_client()
        
        # Track active conversations for proper state management
        self.active_conversations = {}
        
        logger.info("🧠 Enhanced Campaign Orchestrator initialized with fixes")
    
    def _initialize_groq_client(self):
        """Initialize Groq client with proper error handling"""
        if GROQ_AVAILABLE and settings.groq_api_key:
            try:
                self.groq_client = Groq(api_key=settings.groq_api_key)
                logger.info("✅ Groq AI client initialized")
            except Exception as e:
                logger.warning(f"⚠️ Groq initialization failed: {e}")
                self.groq_client = None
        else:
            logger.info("ℹ️ Groq not configured - using default strategies")
    
    async def orchestrate_enhanced_campaign(
        self,
        campaign_data: CampaignData,
        task_id: str
    ) -> CampaignOrchestrationState:
        """
        🎯 CORRECTED MAIN ORCHESTRATION WORKFLOW
        
        Fixes applied to handle contract generation and call state properly
        """
        
        logger.info(f"🎯 Starting enhanced campaign orchestration: {task_id}")
        
        # Initialize state
        state = CampaignOrchestrationState(
            task_id=task_id,
            campaign_data=campaign_data,
            current_stage="discovery",
            start_time=datetime.now()
        )
        
        try:
            # Phase 1: Discovery
            await self._run_discovery_phase(state)
            
            # Phase 2: AI Strategy Generation
            await self._run_strategy_generation_phase(state)
            
            # Phase 3: Enhanced Negotiations with proper monitoring
            await self._run_enhanced_negotiations_phase(state)
            
            # Phase 4: Contract Generation (only for successful negotiations)
            await self._run_enhanced_contracts_phase(state)
            
            # Phase 5: Final validation and completion
            await self._run_completion_phase(state)
            
            logger.info(f"✅ Campaign orchestration completed: {task_id}")
            return state
            
        except Exception as e:
            logger.error(f"❌ Campaign orchestration failed: {e}")
            state.error_message = str(e)
            state.current_stage = "failed"
            return state
    
    async def _run_enhanced_negotiations_phase(self, state: CampaignOrchestrationState):
        """
        📞 CORRECTED NEGOTIATIONS PHASE
        
        Key fixes:
        - Proper conversation monitoring setup
        - Better error handling for failed calls
        - Correct state tracking for contract generation
        """
        
        logger.info("📞 Starting enhanced negotiations phase...")
        state.current_stage = "negotiations"
        
        if not state.discovered_influencers:
            raise Exception("No influencers discovered for negotiations")
        
        # Process each influencer with proper monitoring
        for i, influencer in enumerate(state.discovered_influencers):
            try:
                logger.info(f"📞 Negotiating with influencer {i+1}/{len(state.discovered_influencers)}: {influencer.get('name', 'Unknown')}")
                
                # Update current influencer in state
                state.current_influencer = influencer.get('name', f'Creator_{i+1}')
                
                # Generate pricing strategy
                pricing_strategy = await self._generate_pricing_strategy(
                    influencer, state.campaign_data
                )
                
                # Start conversation with monitoring
                negotiation_result = await self._conduct_monitored_negotiation(
                    influencer,
                    state.campaign_data,
                    pricing_strategy,
                    state
                )
                
                # Process negotiation result
                await self._process_negotiation_result(
                    negotiation_result,
                    influencer,
                    state
                )
                
                # Check if we have enough successful negotiations
                if state.successful_negotiations >= 2:
                    logger.info("✅ Sufficient successful negotiations achieved")
                    break
                    
            except Exception as e:
                logger.error(f"❌ Error negotiating with {influencer.get('name', 'Unknown')}: {e}")
                
                # Record failed negotiation
                failed_negotiation = NegotiationState(
                    creator_id=influencer.get('name', f'Creator_{i+1}'),
                    status=NegotiationStatus.FAILED,
                    failure_reason=str(e)
                )
                state.negotiations.append(failed_negotiation)
                continue
        
        state.current_influencer = None
        logger.info(f"📞 Negotiations phase completed. Successful: {state.successful_negotiations}")
    
    async def _conduct_monitored_negotiation(
        self,
        influencer: Dict[str, Any],
        campaign_data: CampaignData,
        pricing_strategy: Dict[str, Any],
        state: CampaignOrchestrationState
    ) -> Dict[str, Any]:
        """
        🎯 CONDUCT NEGOTIATION WITH PROPER MONITORING
        
        This method ensures proper call state handling and contract generation
        """
        
        creator_phone = influencer.get('phone', '+1234567890')  # Use mock phone if not available
        creator_name = influencer.get('name', 'Creator')
        
        logger.info(f"📱 Starting monitored negotiation with {creator_name}")
        
        try:
            # Initiate the call with proper error checking
            call_result = await self.voice_service.initiate_negotiation_call(
                creator_phone,
                influencer,
                campaign_data.dict(),
                pricing_strategy
            )
            
            # CRITICAL FIX: Validate call initiation before proceeding
            if call_result.get("status") != "success":
                logger.error(f"❌ Call initiation failed for {creator_name}: {call_result}")
                return {
                    "status": "failed",
                    "error": call_result.get("error", "Call initiation failed"),
                    "creator_name": creator_name
                }
            
            conversation_id = call_result.get("conversation_id")
            if not conversation_id:
                logger.error(f"❌ No conversation_id returned for {creator_name}")
                return {
                    "status": "failed",
                    "error": "Missing conversation_id in call result",
                    "creator_name": creator_name
                }
            
            # Store conversation info for state tracking
            self.active_conversations[conversation_id] = {
                "creator_name": creator_name,
                "creator_profile": influencer,
                "campaign_data": campaign_data,
                "pricing_strategy": pricing_strategy,
                "state": state,
                "start_time": datetime.now()
            }
            
            logger.info(f"✅ Call initiated successfully for {creator_name}: {conversation_id}")
            
            # Wait for conversation completion with analysis
            completion_result = await self.voice_service.wait_for_conversation_completion_with_analysis(
                conversation_id,
                max_wait_seconds=480  # 8 minutes max
            )
            
            # Process completion result
            if completion_result.get("status") == "completed":
                logger.info(f"✅ Conversation completed successfully: {creator_name}")
                
                # Extract analysis data for contract generation
                analysis_data = completion_result.get("analysis_data", {})
                
                return {
                    "status": "success",
                    "conversation_id": conversation_id,
                    "creator_name": creator_name,
                    "analysis_data": analysis_data,
                    "conversation_data": completion_result.get("conversation_data", {})
                }
            
            elif completion_result.get("status") == "timeout":
                logger.warning(f"⏰ Conversation timeout for {creator_name}")
                return {
                    "status": "timeout",
                    "error": "Conversation timeout",
                    "creator_name": creator_name,
                    "conversation_id": conversation_id
                }
            
            else:
                logger.error(f"❌ Conversation failed for {creator_name}: {completion_result}")
                return {
                    "status": "failed",
                    "error": completion_result.get("error", "Conversation failed"),
                    "creator_name": creator_name,
                    "conversation_id": conversation_id
                }
            
        except Exception as e:
            logger.error(f"❌ Exception during monitored negotiation with {creator_name}: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "creator_name": creator_name
            }
        
        finally:
            # Cleanup conversation tracking
            if conversation_id and conversation_id in self.active_conversations:
                del self.active_conversations[conversation_id]
    
    async def _process_negotiation_result(
        self,
        result: Dict[str, Any],
        influencer: Dict[str, Any],
        state: CampaignOrchestrationState
    ):
        """
        📊 PROCESS NEGOTIATION RESULT WITH PROPER STATE UPDATES
        
        Fixes to ensure contract generation gets correct data
        """
        
        creator_name = result.get("creator_name", influencer.get("name", "Unknown"))
        
        if result.get("status") == "success":
            logger.info(f"✅ Processing successful negotiation: {creator_name}")
            
            # Extract negotiation details from analysis
            analysis_data = result.get("analysis_data", {})
            
            # Determine negotiation outcome and pricing
            outcome = analysis_data.get("negotiation_outcome", "unknown")
            agreed_rate = analysis_data.get("agreed_rate")
            
            # Set default rate if not extracted from conversation
            if not agreed_rate:
                pricing_strategy = await self._generate_pricing_strategy(influencer, state.campaign_data)
                agreed_rate = pricing_strategy.get("initial_offer", 1000)
                logger.info(f"ℹ️ Using fallback rate for {creator_name}: ${agreed_rate}")
            
            # Create successful negotiation state
            negotiation = NegotiationState(
                creator_id=creator_name,
                status=NegotiationStatus.SUCCESS,
                final_rate=float(agreed_rate),
                conversation_id=result.get("conversation_id"),
                negotiation_data=analysis_data
            )
            
            state.negotiations.append(negotiation)
            state.successful_negotiations += 1
            state.total_cost += float(agreed_rate)
            
            logger.info(f"✅ Recorded successful negotiation: {creator_name} - ${agreed_rate}")
            
        else:
            logger.error(f"❌ Processing failed negotiation: {creator_name}")
            
            # Create failed negotiation state
            negotiation = NegotiationState(
                creator_id=creator_name,
                status=NegotiationStatus.FAILED,
                failure_reason=result.get("error", "Unknown failure"),
                conversation_id=result.get("conversation_id")
            )
            
            state.negotiations.append(negotiation)
            logger.info(f"❌ Recorded failed negotiation: {creator_name}")
    
    async def _run_enhanced_contracts_phase(self, state: CampaignOrchestrationState):
        """
        📋 CORRECTED CONTRACTS PHASE
        
        Only generates contracts for successful negotiations with proper data
        """
        
        logger.info("📋 Starting enhanced contracts phase...")
        state.current_stage = "contracts"
        
        successful_negotiations = [
            n for n in state.negotiations 
            if n.status == NegotiationStatus.SUCCESS
        ]
        
        if not successful_negotiations:
            logger.warning("⚠️ No successful negotiations found - skipping contract generation")
            return
        
        logger.info(f"📋 Generating contracts for {len(successful_negotiations)} successful negotiations")
        
        for negotiation in successful_negotiations:
            try:
                logger.info(f"📄 Generating contract for {negotiation.creator_id}")
                
                # Prepare contract data
                contract_data = {
                    "creator_name": negotiation.creator_id,
                    "agreed_rate": negotiation.final_rate,
                    "campaign_details": state.campaign_data.dict(),
                    "negotiation_data": negotiation.negotiation_data or {},
                    "conversation_id": negotiation.conversation_id
                }
                
                # Generate contract
                contract = await self.contract_agent.generate_enhanced_contract(contract_data)
                
                if contract.get("status") == "success":
                    state.contracts.append({
                        "creator_id": negotiation.creator_id,
                        "contract": contract,
                        "rate": negotiation.final_rate
                    })
                    logger.info(f"✅ Contract generated successfully for {negotiation.creator_id}")
                else:
                    logger.error(f"❌ Contract generation failed for {negotiation.creator_id}: {contract}")
                
            except Exception as e:
                logger.error(f"❌ Exception generating contract for {negotiation.creator_id}: {e}")
                continue
        
        logger.info(f"📋 Contracts phase completed. Generated: {len(state.contracts)}")
    
    async def _generate_pricing_strategy(
        self,
        influencer: Dict[str, Any],
        campaign_data: CampaignData
    ) -> Dict[str, Any]:
        """Generate pricing strategy for influencer"""
        
        # Base pricing calculation
        followers = influencer.get('followers', 10000)
        engagement_rate = influencer.get('engagement_rate', 0.03)
        
        # Calculate base rate (simplified)
        base_rate = min(followers * engagement_rate * 0.1, 5000)
        
        return {
            "initial_offer": max(int(base_rate * 0.8), 500),
            "max_offer": max(int(base_rate * 1.2), 1000),
            "style": "collaborative"
        }
    
    # Event handlers for conversation monitoring
    async def handle_conversation_completed(
        self,
        conversation_id: str,
        conversation_data: Dict[str, Any],
        analysis_data: Dict[str, Any]
    ):
        """Handle conversation completion from monitoring"""
        
        logger.info(f"🎯 Handling conversation completion: {conversation_id}")
        
        if conversation_id in self.active_conversations:
            conv_info = self.active_conversations[conversation_id]
            logger.info(f"✅ Conversation completed for {conv_info['creator_name']}")
            
            # The main orchestration loop will handle the result
            # This is just for logging and state tracking
            
        else:
            logger.warning(f"⚠️ Completed conversation not found in active tracking: {conversation_id}")
    
    async def handle_conversation_error(
        self,
        conversation_id: str,
        error_message: str
    ):
        """Handle conversation errors from monitoring"""
        
        logger.error(f"❌ Handling conversation error: {conversation_id} - {error_message}")
        
        if conversation_id in self.active_conversations:
            conv_info = self.active_conversations[conversation_id]
            logger.error(f"❌ Conversation failed for {conv_info['creator_name']}: {error_message}")
            
            # The main orchestration loop will handle the error
            # This is just for logging and state tracking
            
        else:
            logger.warning(f"⚠️ Failed conversation not found in active tracking: {conversation_id}")
    
    # Existing methods (discovery, strategy, completion phases)
    async def _run_discovery_phase(self, state: CampaignOrchestrationState):
        """Run influencer discovery phase"""
        logger.info("🔍 Starting discovery phase...")
        state.current_stage = "discovery"
        
        discovered = await self.discovery_agent.discover_influencers(
            state.campaign_data.product_niche,
            state.campaign_data.total_budget
        )
        
        state.discovered_influencers = discovered
        logger.info(f"🔍 Discovered {len(discovered)} influencers")
    
    async def _run_strategy_generation_phase(self, state: CampaignOrchestrationState):
        """Generate AI-powered strategy"""
        logger.info("🧠 Starting strategy generation phase...")
        state.current_stage = "strategy"
        
        if self.groq_client:
            try:
                strategy = await self._generate_ai_strategy(state)
                state.ai_strategy = strategy
                logger.info("🧠 AI strategy generated successfully")
            except Exception as e:
                logger.warning(f"⚠️ AI strategy generation failed: {e}")
                state.ai_strategy = "Using default strategy due to AI error"
        else:
            state.ai_strategy = "Default strategy - Groq not available"
    
    async def _generate_ai_strategy(self, state: CampaignOrchestrationState) -> str:
        """Generate AI strategy using Groq"""
        
        prompt = f"""
        Generate a negotiation strategy for this influencer marketing campaign:
        
        Product: {state.campaign_data.product_name}
        Niche: {state.campaign_data.product_niche}
        Budget: ${state.campaign_data.total_budget}
        Target Audience: {state.campaign_data.target_audience}
        
        Provide a concise strategy focusing on:
        1. Key talking points
        2. Pricing approach
        3. Value proposition
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"❌ Groq API error: {e}")
            raise
    
    async def _run_completion_phase(self, state: CampaignOrchestrationState):
        """Complete the campaign orchestration"""
        logger.info("🏁 Starting completion phase...")
        state.current_stage = "completed"
        state.end_time = datetime.now()
        
        # Calculate final metrics
        duration = (state.end_time - state.start_time).total_seconds()
        state.total_duration_seconds = duration
        
        logger.info(f"🏁 Campaign completed in {duration:.1f} seconds")
        logger.info(f"📊 Final stats: {state.successful_negotiations} successful, {len(state.contracts)} contracts")