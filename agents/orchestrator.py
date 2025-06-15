# agents/orchestrator.py - FIXED UNIFIED ORCHESTRATOR
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

logger = logging.getLogger(__name__)

class CampaignOrchestrator:
    """
    🧠 Fixed Campaign Orchestrator
    
    Clean, maintainable implementation that:
    - Uses unified NegotiationResult model with consistent attributes
    - Properly handles database sync with correct attribute names
    - No legacy code or unnecessary helper functions
    - Proper OOP design with clear module boundaries
    """
    
    def __init__(self):
        """Initialize with required services"""
        self.discovery_agent = DiscoveryAgent()
        self.negotiation_agent = NegotiationAgent()
        self.contract_agent = ContractAgent()
        self.voice_service = VoiceService()
        self.database_service = DatabaseService()
        
        logger.info("🧠 Campaign Orchestrator initialized")
    
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
        """
        # Initialize orchestration state
        state = OrchestrationState(
            campaign_id=campaign_data.id,
            campaign_data=campaign_data,
            started_at=datetime.now()
        )
        
        try:
            logger.info(f"🚀 Starting campaign orchestration: {campaign_data.name}")
            
            # Phase 1: Creator Discovery
            state = await self._discover_creators(state)
            
            # Phase 2: Negotiations with unified result handling
            state = await self._conduct_negotiations(state)
            
            # Phase 3: Contract Generation
            state = await self._generate_contracts(state)
            
            # Phase 4: Database Sync with fixed attribute handling
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
            logger.error(f"❌ Campaign {campaign_data.id} failed: {e}")
            raise
    
    async def _discover_creators(self, state: OrchestrationState) -> OrchestrationState:
        """
        Phase 1: Discover relevant creators for the campaign
        """
        state.current_stage = "discovery"
        logger.info("🔍 Starting creator discovery...")
        
        try:
            # Use discovery agent to find creators
            creators = await self.discovery_agent.discover_creators(
                campaign_data=state.campaign_data,
                max_creators=state.campaign_data.max_creators
            )
            
            state.discovered_creators = creators
            logger.info(f"📊 Discovered {len(creators)} relevant creators")
            
            return state
            
        except Exception as e:
            logger.error(f"❌ Creator discovery failed: {e}")
            raise
    
    async def _conduct_negotiations(self, state: OrchestrationState) -> OrchestrationState:
        """
        Phase 2: Conduct negotiations with discovered creators
        
        Returns NegotiationResult objects with consistent attributes for database sync
        """
        state.current_stage = "negotiations"
        logger.info("🤝 Starting negotiations...")
        
        # Create negotiation tasks for all discovered creators
        negotiation_tasks = [
            self.negotiation_agent.negotiate_with_creator(
                creator=creator,
                campaign_data=state.campaign_data,
                voice_service=self.voice_service
            )
            for creator in state.discovered_creators
        ]
        
        # Execute negotiations concurrently
        negotiation_results = await asyncio.gather(*negotiation_tasks, return_exceptions=True)
        
        # Process results and update state
        for result in negotiation_results:
            if isinstance(result, Exception):
                logger.error(f"❌ Negotiation task failed: {result}")
                continue
            
            # Add negotiation result (automatically updates counters and totals)
            state.add_negotiation_result(result)
            
            # Log individual result
            status_emoji = "✅" if result.is_successful() else "❌"
            rate_info = f"${result.rate:.2f}" if result.rate else "No rate"
            logger.info(f"{status_emoji} Negotiation with {result.creator_name}: {result.status.value} - {rate_info}")
        
        logger.info(f"🤝 Completed {len(state.negotiations)} negotiations")
        logger.info(f"✅ {state.successful_negotiations} successful negotiations")
        
        return state
    
    async def _generate_contracts(self, state: OrchestrationState) -> OrchestrationState:
        """
        Phase 3: Generate contracts for successful negotiations
        """
        state.current_stage = "contracts"
        logger.info("📝 Generating contracts...")
        
        # Get successful negotiations
        successful_negotiations = [
            negotiation for negotiation in state.negotiations
            if negotiation.is_successful()
        ]
        
        if not successful_negotiations:
            logger.warning("⚠️ No successful negotiations - skipping contract generation")
            return state
        
        # Generate contracts for successful negotiations
        contract_tasks = [
            self.contract_agent.generate_contract(
                negotiation_result=negotiation,
                campaign_data=state.campaign_data
            )
            for negotiation in successful_negotiations
        ]
        
        # Execute contract generation concurrently
        contracts = await asyncio.gather(*contract_tasks, return_exceptions=True)
        
        # Process contract results
        for contract in contracts:
            if isinstance(contract, Exception):
                logger.error(f"❌ Contract generation failed: {contract}")
                continue
            
            state.contracts.append(contract)
            logger.info(f"📝 Contract generated: {contract.id}")
        
        logger.info(f"📝 Generated {len(state.contracts)} contracts")
        return state
    
    async def _sync_to_database(self, state: OrchestrationState) -> OrchestrationState:
        """
        Phase 4: Sync all results to database
        
        Uses the fixed database service that handles both agreed_rate and final_rate attributes
        """
        state.current_stage = "database_sync"
        logger.info("💾 Syncing to database...")
        
        try:
            # Use fixed database service that handles attribute compatibility
            await self.database_service.sync_campaign_results(state)
            
            logger.info("💾 Database sync completed successfully")
            return state
            
        except Exception as e:
            logger.error(f"❌ Database sync failed: {e}")
            raise
    
    def get_campaign_metrics(self, state: OrchestrationState) -> Dict[str, Any]:
        """
        Calculate comprehensive campaign performance metrics
        """
        total_creators = len(state.discovered_creators)
        success_rate = (state.successful_negotiations / total_creators * 100) if total_creators > 0 else 0
        
        duration_minutes = 0
        if state.completed_at and state.started_at:
            duration_minutes = (state.completed_at - state.started_at).total_seconds() / 60
        
        budget_utilization = (state.total_cost / state.campaign_data.total_budget * 100) if state.campaign_data.total_budget > 0 else 0
        
        return {
            "campaign_id": state.campaign_id,
            "campaign_name": state.campaign_data.name,
            "total_creators_discovered": total_creators,
            "successful_negotiations": state.successful_negotiations,
            "failed_negotiations": state.failed_negotiations,
            "success_rate_percentage": round(success_rate, 2),
            "total_cost": state.total_cost,
            "budget_utilization_percentage": round(budget_utilization, 2),
            "contracts_generated": len(state.contracts),
            "duration_minutes": round(duration_minutes, 2),
            "cost_per_successful_negotiation": round(state.total_cost / state.successful_negotiations, 2) if state.successful_negotiations > 0 else 0,
            "average_negotiation_rate": round(state.total_cost / state.successful_negotiations, 2) if state.successful_negotiations > 0 else 0
        }
    
    async def get_campaign_status(self, campaign_id: str) -> Dict[str, Any]:
        """
        Get real-time campaign status for monitoring
        """
        # In a real implementation, this would query the database
        # For now, return a mock status
        return {
            "campaign_id": campaign_id,
            "status": "active",
            "current_stage": "negotiations",
            "progress_percentage": 60,
            "estimated_completion_minutes": 3,
            "creators_contacted": 8,
            "successful_negotiations": 5,
            "contracts_generated": 3
        }