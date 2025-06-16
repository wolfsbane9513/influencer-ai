# agents/enhanced_orchestrator.py - ENHANCED WITH MINIMAL DATABASE INTEGRATION
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
from services.database import DatabaseService  # ← ADD DATABASE IMPORT
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
    🧠 ENHANCED CAMPAIGN ORCHESTRATOR WITH DATABASE
    
    ✅ Clean OOP design with proper encapsulation
    ✅ Minimal database integration 
    ✅ No unnecessary helper functions
    ✅ Uses only fields that exist in the model
    ✅ Maintainable modular structure
    ✅ No legacy code retention
    """
    
    def __init__(self):
        """Initialize orchestrator with minimal required components"""
        self.discovery_agent = InfluencerDiscoveryAgent()
        self.groq_client = self._initialize_groq_client()
        self.database_service = None  # ← ADD: Will be injected from main.py
        
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
        🎯 MAIN ORCHESTRATION WORKFLOW - CLEAN & CORRECT WITH DATABASE
        
        Uses only actual model fields, no over-engineering
        """
        
        logger.info(f"🎯 Starting enhanced campaign orchestration: {task_id}")
        
        # Initialize state with ONLY fields that exist in the model
        state = CampaignOrchestrationState(
            campaign_id=campaign_data.id,
            campaign_data=campaign_data
        )
        
        try:
            # *** ADD: Database initialization if available ***
            await self._initialize_database_if_available(state)
            
            # Phase 1: Discovery (with database storage)
            logger.info("🔍 Phase 1: Discovery")
            await self._run_discovery_phase(state)
            
            # Phase 2: AI Strategy Generation (with database storage)
            logger.info("🧠 Phase 2: AI Strategy")
            await self._run_strategy_phase(state)
            
            # Phase 3: Negotiations (with database storage)
            logger.info("📞 Phase 3: Negotiations")
            await self._run_negotiations_phase(state)
            
            # Phase 4: Contracts (with database storage)
            logger.info("📝 Phase 4: Contracts")
            await self._run_contracts_phase(state)
            
            # Phase 5: Completion (with database storage)
            logger.info("🏁 Phase 5: Completion")
            await self._run_completion_phase(state)
            
            logger.info(f"✅ Campaign orchestration completed: {task_id}")
            return state
            
        except Exception as e:
            logger.error(f"❌ Campaign orchestration failed: {e}")
            state.current_stage = "failed"
            state.completed_at = datetime.now()
            
            # *** ADD: Mark as failed in database ***
            await self._mark_campaign_failed_in_db(state, str(e))
            
            return state
    
    # *** ADD: Minimal database integration methods ***
    async def _initialize_database_if_available(self, state: CampaignOrchestrationState):
        """Initialize database if available - simple and clean"""
        if self.database_service:
            try:
                await self.database_service.initialize()
                db_campaign = await self.database_service.create_campaign(state.campaign_data)
                state.database_enabled = True
                logger.info(f"✅ Campaign created in database: {db_campaign.id}")
            except Exception as e:
                logger.error(f"❌ Database initialization failed: {e}")
                state.database_enabled = False
        else:
            state.database_enabled = False
    
    async def _store_creators_in_db(self, state: CampaignOrchestrationState):
        """Store discovered creators - simple implementation"""
        if state.database_enabled and self.database_service:
            for influencer_match in state.discovered_influencers:
                try:
                    await self.database_service.create_or_update_creator(influencer_match.creator)
                    logger.info(f"✅ Creator stored: {influencer_match.creator.name}")
                except Exception as e:
                    logger.error(f"❌ Failed to store creator: {e}")
    
    async def _store_negotiation_in_db(self, state: CampaignOrchestrationState, negotiation: NegotiationState):
        """Store negotiation result - simple implementation"""
        if state.database_enabled and self.database_service:
            try:
                negotiation_data = {
                    "status": negotiation.status,
                    "initial_rate": getattr(negotiation, 'initial_rate', None),
                    "final_rate": negotiation.final_rate,
                    "negotiated_terms": negotiation.negotiated_terms,
                    "call_status": getattr(negotiation, 'call_status', 'completed'),
                    "email_status": getattr(negotiation, 'email_status', 'sent'),
                    "last_contact_date": negotiation.completed_at or datetime.now()
                }
                
                db_negotiation = await self.database_service.create_negotiation(
                    state.campaign_id,
                    negotiation.creator_id,
                    negotiation_data
                )
                logger.info(f"✅ Negotiation stored: {db_negotiation.id}")
                
            except Exception as e:
                logger.error(f"❌ Failed to store negotiation: {e}")
    
    async def _store_contract_in_db(self, state: CampaignOrchestrationState, contract: Dict[str, Any]):
        """Store contract - simple implementation"""
        if state.database_enabled and self.database_service:
            try:
                db_contract = await self.database_service.create_contract({
                    "id": contract["contract_id"],
                    "campaign_id": contract["campaign_id"],
                    "creator_id": contract["creator_id"],
                    "compensation_amount": contract["compensation"],
                    "deliverables": contract["terms"].get("deliverables", []),
                    "timeline": {"duration": contract["terms"].get("timeline", "")},
                    "usage_rights": {"period": contract["terms"].get("usage_rights", "")},
                    "status": contract["status"],
                    "contract_text": f"Contract for {contract['creator_id']}"
                })
                logger.info(f"✅ Contract stored: {db_contract.id}")
                
            except Exception as e:
                logger.error(f"❌ Failed to store contract: {e}")
    
    async def _update_campaign_totals_in_db(self, state: CampaignOrchestrationState):
        """Update campaign totals - simple implementation"""
        if state.database_enabled and self.database_service:
            try:
                await self.database_service.update_campaign(
                    state.campaign_id,
                    {
                        "influencer_count": state.successful_negotiations,
                        "total_cost": state.total_cost
                    }
                )
                logger.info(f"✅ Campaign totals updated: {state.successful_negotiations} influencers, ${state.total_cost}")
                
            except Exception as e:
                logger.error(f"❌ Failed to update campaign totals: {e}")
    
    async def _mark_campaign_completed_in_db(self, state: CampaignOrchestrationState):
        """Mark campaign as completed - simple implementation"""
        if state.database_enabled and self.database_service:
            try:
                await self.database_service.update_campaign(
                    state.campaign_id,
                    {
                        "status": "completed",
                        "completed_at": state.completed_at
                    }
                )
                logger.info("✅ Campaign marked as completed in database")
                
            except Exception as e:
                logger.error(f"❌ Failed to mark campaign completed: {e}")
    
    async def _mark_campaign_failed_in_db(self, state: CampaignOrchestrationState, error_message: str):
        """Mark campaign as failed - simple implementation"""
        if state.database_enabled and self.database_service:
            try:
                await self.database_service.update_campaign(
                    state.campaign_id,
                    {
                        "status": "failed",
                        "ai_strategy": {"error": error_message}
                    }
                )
                logger.info("⚠️ Campaign marked as failed in database")
                
            except Exception as e:
                logger.error(f"❌ Failed to mark campaign failed: {e}")
    
    # *** UPDATED: Existing methods with database integration ***
    async def _run_discovery_phase(self, state: CampaignOrchestrationState):
        """🔍 Run discovery phase - simple and clean WITH DATABASE"""
        state.current_stage = "discovery"
        
        # Use discovery agent to find influencers
        discovered = await self.discovery_agent.discover_influencers(
            niche=state.campaign_data.product_niche,
            budget=state.campaign_data.total_budget
        )
        
        state.discovered_influencers = discovered
        logger.info(f"🔍 Discovered {len(discovered)} influencers")
        
        # *** ADD: Store creators in database ***
        await self._store_creators_in_db(state)
    
    async def _run_strategy_phase(self, state: CampaignOrchestrationState):
        """🧠 Generate AI strategy - clean implementation WITH DATABASE"""
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
        
        # *** ADD: Store strategy in database ***
        if state.database_enabled and self.database_service:
            try:
                await self.database_service.update_campaign(
                    state.campaign_id,
                    {"ai_strategy": state.ai_strategy}
                )
                logger.info("✅ AI strategy stored in database")
            except Exception as e:
                logger.error(f"❌ Failed to store strategy: {e}")
    
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
        """📞 Run negotiations phase - clean and simple WITH DATABASE"""
        state.current_stage = "negotiations"
        
        if not state.discovered_influencers:
            logger.warning("⚠️ No influencers discovered for negotiations")
            return
        
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
                # Simple negotiation simulation
                success = await self._simulate_negotiation(creator, state.campaign_data)
                
                if success:
                    negotiation.status = NegotiationStatus.SUCCESS
                    negotiation.final_rate = influencer_match.estimated_rate
                    negotiation.negotiated_terms = {
                        "deliverables": ["1 Instagram post", "3 Stories"],
                        "timeline": "2 weeks",
                        "usage_rights": "1 year"
                    }
                    state.successful_negotiations += 1
                    state.total_cost += negotiation.final_rate
                    logger.info(f"✅ Successful negotiation: {creator.name} - ${negotiation.final_rate}")
                else:
                    negotiation.status = NegotiationStatus.FAILED
                    negotiation.failure_reason = "Rate disagreement"
                    state.failed_negotiations += 1
                    logger.info(f"❌ Failed negotiation: {creator.name}")
                
                negotiation.completed_at = datetime.now()
                state.negotiations.append(negotiation)
                
                # *** ADD: Store negotiation in database ***
                await self._store_negotiation_in_db(state, negotiation)
                
                # *** ADD: Update campaign totals ***
                await self._update_campaign_totals_in_db(state)
                
            except Exception as e:
                logger.error(f"❌ Negotiation error for {creator.name}: {e}")
                negotiation.status = NegotiationStatus.FAILED
                negotiation.failure_reason = str(e)
                negotiation.completed_at = datetime.now()
                state.negotiations.append(negotiation)
                
                # Store failed negotiation too
                await self._store_negotiation_in_db(state, negotiation)
    
    async def _simulate_negotiation(self, creator, campaign_data) -> bool:
        """Simple negotiation simulation - clean logic"""
        # Simple success criteria based on creator availability
        if creator.availability.value in ["excellent", "good"]:
            return True
        return False
    
    async def _run_contracts_phase(self, state: CampaignOrchestrationState):
        """📝 Generate contracts - simple and clean WITH DATABASE"""
        state.current_stage = "contracts"
        
        successful_negotiations = [
            neg for neg in state.negotiations 
            if neg.status == NegotiationStatus.SUCCESS
        ]
        
        if not successful_negotiations:
            logger.warning("⚠️ No successful negotiations - skipping contracts")
            return
        
        # Generate simple contracts
        for negotiation in successful_negotiations:
            try:
                contract = self._create_contract(negotiation, state.campaign_data)
                state.contracts.append(contract)
                
                # Update negotiation with contract info
                negotiation.negotiated_terms["contract_generated"] = True
                negotiation.negotiated_terms["contract_id"] = contract["contract_id"]
                
                logger.info(f"📝 Contract generated: {contract['contract_id']}")
                
                # *** ADD: Store contract in database ***
                await self._store_contract_in_db(state, contract)
                
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
    
    async def _run_completion_phase(self, state: CampaignOrchestrationState):
        """🏁 Complete campaign - simple and clean WITH DATABASE"""
        state.current_stage = "completed"
        state.completed_at = datetime.now()
        
        # Calculate duration using actual model fields
        duration = (state.completed_at - state.started_at).total_seconds()
        
        logger.info(f"🏁 Campaign completed in {duration:.1f} seconds")
        logger.info(f"📊 Results: {state.successful_negotiations} successful, {len(state.contracts)} contracts")
        
        # *** ADD: Mark campaign as completed in database ***
        await self._mark_campaign_completed_in_db(state)
        
        # *** ADD: Final database sync ***
        if state.database_enabled and self.database_service:
            try:
                await self.database_service.sync_campaign_results(state)
                logger.info("✅ Final database sync completed")
            except Exception as e:
                logger.error(f"❌ Final database sync failed: {e}")


# Simple supporting classes - no over-engineering (keep existing)
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