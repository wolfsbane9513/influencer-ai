# agents/orchestrator.py - FINAL UNIFIED VERSION
import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

from core.models import CampaignData, OrchestrationState, NegotiationResult, Contract
from agents.discovery import DiscoveryAgent
from agents.negotiation import NegotiationAgent
from agents.contracts import ContractAgent
from services.voice import VoiceService
from services.database import DatabaseService
from core.config import settings

logger = logging.getLogger(__name__)

class CampaignOrchestrator:
    """
    🧠 Unified Campaign Orchestrator
    
    Single, clean implementation managing complete campaign workflow:
    Campaign → Discovery → Negotiations → Contracts → Database
    
    Key Features:
    - Clean OOP design with proper encapsulation
    - No unnecessary helper functions
    - Maintainable modular structure
    - No legacy code retention
    """
    
    def __init__(self):
        """Initialize with required services"""
        self.discovery_agent = DiscoveryAgent()
        self.negotiation_agent = NegotiationAgent()
        self.contract_agent = ContractAgent()
        self.voice_service = VoiceService()
        self.database_service = DatabaseService()
        
        # Optional AI intelligence
        self.ai_client = self._initialize_ai_client()
        
        logger.info("🧠 Campaign Orchestrator initialized")
    
    def _initialize_ai_client(self) -> Optional[Any]:
        """Initialize AI client if available"""
        try:
            if settings.groq_api_key:
                from groq import Groq
                return Groq(api_key=settings.groq_api_key)
        except ImportError:
            logger.warning("⚠️ Groq not available - using standard processing")
        return None
    
    async def orchestrate_campaign(
        self, 
        campaign_data: CampaignData
    ) -> OrchestrationState:
        """
        Main orchestration method - handles complete workflow
        
        Args:
            campaign_data: Campaign information and requirements
            
        Returns:
            OrchestrationState: Complete campaign results and metrics
            
        Raises:
            Exception: If any phase of the campaign fails
        """
        # Initialize state
        state = OrchestrationState(
            campaign_id=campaign_data.id,
            campaign_data=campaign_data,
            started_at=datetime.now()
        )
        
        try:
            logger.info(f"🚀 Starting campaign orchestration: {campaign_data.product_name}")
            
            # Phase 1: Creator Discovery
            state = await self._discover_creators(state)
            
            # Phase 2: Negotiations
            state = await self._conduct_negotiations(state)
            
            # Phase 3: Contract Generation
            state = await self._generate_contracts(state)
            
            # Phase 4: Database Sync
            state = await self._sync_to_database(state)
            
            # Mark completion
            state.completed_at = datetime.now()
            state.current_stage = "completed"
            
            duration = (state.completed_at - state.started_at).total_seconds()
            logger.info(f"🏁 Campaign {campaign_data.id} completed in {duration:.1f}s")
            logger.info(f"📊 Results: {state.successful_negotiations} successful, {len(state.contracts)} contracts")
            
            return state
            
        except Exception as e:
            state.current_stage = "failed"
            state.error_message = str(e)
            logger.error(f"❌ Campaign {campaign_data.id} failed: {e}")
            raise
    
    async def _discover_creators(self, state: OrchestrationState) -> OrchestrationState:
        """
        Phase 1: Discover relevant creators
        
        Uses AI-powered matching to find creators that fit the campaign requirements
        """
        state.current_stage = "discovery"
        logger.info("🔍 Starting creator discovery...")
        
        creators = await self.discovery_agent.find_creators(
            product_niche=state.campaign_data.product_niche,
            target_audience=state.campaign_data.target_audience,
            budget=state.campaign_data.total_budget
        )
        
        state.discovered_creators = creators
        logger.info(f"📊 Discovered {len(creators)} relevant creators")
        return state
    
    async def _conduct_negotiations(self, state: OrchestrationState) -> OrchestrationState:
        """
        Phase 2: Conduct voice negotiations with discovered creators
        
        Uses ElevenLabs AI to have natural conversations with creators
        """
        state.current_stage = "negotiations"
        logger.info("🤝 Starting negotiations...")
        
        # Prepare negotiation tasks
        negotiation_tasks = [
            self._negotiate_with_creator(creator, state.campaign_data)
            for creator in state.discovered_creators
        ]
        
        # Execute negotiations concurrently for better performance
        negotiation_results = await asyncio.gather(*negotiation_tasks, return_exceptions=True)
        
        # Process results
        for result in negotiation_results:
            if isinstance(result, Exception):
                logger.error(f"❌ Negotiation failed: {result}")
                continue
                
            state.negotiations.append(result)
            
            if result.status == "success":
                state.successful_negotiations += 1
                state.total_cost += result.agreed_rate or 0
        
        logger.info(f"🤝 Completed {len(state.negotiations)} negotiations")
        logger.info(f"✅ {state.successful_negotiations} successful negotiations")
        return state
    
    async def _negotiate_with_creator(
        self, 
        creator, 
        campaign_data: CampaignData
    ) -> NegotiationResult:
        """
        Negotiate with individual creator using voice service
        """
        return await self.negotiation_agent.negotiate_with_creator(
            creator=creator,
            campaign_data=campaign_data,
            voice_service=self.voice_service
        )
    
    async def _generate_contracts(self, state: OrchestrationState) -> OrchestrationState:
        """
        Phase 3: Generate contracts for successful negotiations
        
        Creates legal documents with terms negotiated during calls
        """
        state.current_stage = "contracts"
        logger.info("📝 Generating contracts...")
        
        # Generate contracts for successful negotiations
        contract_tasks = [
            self.contract_agent.generate_contract(
                negotiation=negotiation,
                campaign_data=state.campaign_data
            )
            for negotiation in state.negotiations
            if negotiation.status == "success"
        ]
        
        # Execute contract generation concurrently
        contracts = await asyncio.gather(*contract_tasks, return_exceptions=True)
        
        # Process results
        for contract in contracts:
            if isinstance(contract, Exception):
                logger.error(f"❌ Contract generation failed: {contract}")
                continue
            state.contracts.append(contract)
        
        logger.info(f"📝 Generated {len(state.contracts)} contracts")
        return state
    
    async def _sync_to_database(self, state: OrchestrationState) -> OrchestrationState:
        """
        Phase 4: Sync all results to database
        
        Stores campaign results, negotiations, and contracts for future reference
        """
        state.current_stage = "database_sync"
        logger.info("💾 Syncing to database...")
        
        await self.database_service.sync_campaign_results(state)
        
        logger.info("💾 Database sync completed")
        return state
    
    def get_campaign_metrics(self, state: OrchestrationState) -> Dict[str, Any]:
        """
        Calculate campaign performance metrics
        
        Args:
            state: Campaign orchestration state
            
        Returns:
            Dict containing performance metrics
        """
        total_creators = len(state.discovered_creators)
        success_rate = (state.successful_negotiations / total_creators * 100) if total_creators > 0 else 0
        
        duration_minutes = 0
        if state.completed_at and state.started_at:
            duration_minutes = (state.completed_at - state.started_at).total_seconds() / 60
        
        budget_utilization = (state.total_cost / state.campaign_data.total_budget * 100) if state.campaign_data.total_budget > 0 else 0
        
        return {
            "campaign_id": state.campaign_id,
            "total_creators_discovered": total_creators,
            "successful_negotiations": state.successful_negotiations,
            "success_rate_percentage": round(success_rate, 2),
            "total_cost": state.total_cost,
            "budget_utilization_percentage": round(budget_utilization, 2),
            "contracts_generated": len(state.contracts),
            "duration_minutes": round(duration_minutes, 2),
            "cost_per_successful_negotiation": round(state.total_cost / state.successful_negotiations, 2) if state.successful_negotiations > 0 else 0
        }