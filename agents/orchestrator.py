# agents/orchestrator.py - COMPLETELY FIXED CAMPAIGN ORCHESTRATOR
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field

from core.models import Creator, CampaignData, OrchestrationState
from agents.discovery import DiscoveryAgent
from agents.negotiation import NegotiationAgent, NegotiationResult
from agents.contracts import ContractAgent
from services.database import DatabaseService

logger = logging.getLogger(__name__)


@dataclass
class CampaignMetrics:
    """Campaign performance metrics"""
    total_creators_found: int = 0
    successful_negotiations: int = 0
    failed_negotiations: int = 0
    contracts_generated: int = 0
    total_budget_allocated: float = 0.0
    average_rate: float = 0.0


class CampaignOrchestrator:
    """
    🧠 Fixed Campaign Orchestrator
    
    Key Fixes:
    1. Sequential creator processing instead of mass calling
    2. Proper enum/string handling throughout
    3. Added missing error_message field support
    4. Proper resource cleanup with close() method
    5. Improved state management and error handling
    """
    
    def __init__(self):
        """Initialize orchestrator with all required agents"""
        self.discovery_agent = DiscoveryAgent()
        self.negotiation_agent = NegotiationAgent()
        self.contract_agent = ContractAgent()
        self.database = DatabaseService()
        
        # Configuration
        self.max_concurrent_negotiations = 3  # Reduced from mass calling
        self.negotiation_timeout_minutes = 10
        
        logger.info("🧠 Campaign Orchestrator initialized")
    
    async def orchestrate_campaign(self, campaign_data: CampaignData) -> OrchestrationState:
        """
        Orchestrate complete campaign workflow with proper error handling
        
        Args:
            campaign_data: Campaign requirements and configuration
            
        Returns:
            Final orchestration state with results or errors
        """
        
        state = OrchestrationState(
            stage="starting",
            campaign_id=campaign_data.campaign_id,
            company_name=campaign_data.company_name,
            product_name=campaign_data.product_name,
            start_time=datetime.now()
        )
        
        logger.info(f"🚀 Starting campaign orchestration: {campaign_data.company_name} - {campaign_data.product_name}")
        
        try:
            # Phase 1: Creator Discovery
            state = await self._discover_creators(state, campaign_data)
            if state.stage == "failed":
                return state
            
            # Phase 2: Sequential Negotiations (NOT mass calling)
            state = await self._conduct_sequential_negotiations(state, campaign_data)
            if state.stage == "failed":
                return state
            
            # Phase 3: Contract Generation
            state = await self._generate_contracts(state, campaign_data)
            
            # Final completion
            state.stage = "completed"
            state.is_complete = True
            state.end_time = datetime.now()
            
            logger.info(f"✅ Campaign orchestration completed: {state.campaign_id}")
            return state
            
        except Exception as e:
            logger.error(f"❌ Campaign {state.campaign_id} failed: {e}")
            state.stage = "failed"
            state.error_message = str(e)  # This field now exists
            state.end_time = datetime.now()
            return state
    
    async def _discover_creators(self, state: OrchestrationState, campaign_data: CampaignData) -> OrchestrationState:
        """Phase 1: Discover relevant creators"""
        
        logger.info("🔍 Starting creator discovery...")
        state.stage = "discovery"
        
        try:
            discovered_creators = await self.discovery_agent.find_creators(
                campaign_data.target_audience,
                campaign_data.budget_per_creator,
                campaign_data.max_creators
            )
            
            state.discovered_creators = discovered_creators
            state.creators_found = len(discovered_creators)
            
            logger.info(f"📊 Discovered {len(discovered_creators)} relevant creators")
            
            if not discovered_creators:
                state.stage = "failed"
                state.error_message = "No suitable creators found for campaign criteria"
                return state
            
            return state
            
        except Exception as e:
            logger.error(f"❌ Creator discovery failed: {e}")
            state.stage = "failed" 
            state.error_message = f"Creator discovery failed: {str(e)}"
            return state
    
    async def _conduct_sequential_negotiations(self, state: OrchestrationState, campaign_data: CampaignData) -> OrchestrationState:
        """
        Phase 2: Sequential creator negotiations (FIXED - no mass calling)
        
        Key Fix: Process creators one by one or in small batches to avoid overwhelming ElevenLabs API
        """
        
        logger.info("🤝 Starting sequential negotiations...")
        state.stage = "negotiations"
        
        try:
            successful_negotiations = []
            failed_negotiations = []
            
            # Process creators in small batches to avoid API limits
            batch_size = self.max_concurrent_negotiations
            creators = state.discovered_creators
            
            for i in range(0, len(creators), batch_size):
                batch = creators[i:i + batch_size]
                
                logger.info(f"🔄 Processing creator batch {i//batch_size + 1} ({len(batch)} creators)")
                
                # Process batch with limited concurrency
                batch_results = await self._process_creator_batch(batch, campaign_data)
                
                # Categorize results
                for result in batch_results:
                    if result.is_successful():
                        successful_negotiations.append(result)
                        logger.info(f"✅ Successful negotiation: {result.creator_id} - ${result.final_rate}")
                    else:
                        failed_negotiations.append(result)
                        logger.info(f"❌ Failed negotiation: {result.creator_id} - {result.error_message}")
                
                # Brief pause between batches to respect API limits
                if i + batch_size < len(creators):
                    await asyncio.sleep(2)
            
            # Update state with results
            state.negotiation_results = successful_negotiations + failed_negotiations
            state.successful_negotiations = len(successful_negotiations)
            state.failed_negotiations = len(failed_negotiations)
            
            logger.info(f"📊 Negotiations completed: {len(successful_negotiations)} successful, {len(failed_negotiations)} failed")
            
            if not successful_negotiations:
                state.stage = "failed"
                state.error_message = "No successful negotiations completed"
                return state
            
            return state
            
        except Exception as e:
            logger.error(f"❌ Negotiations failed: {e}")
            state.stage = "failed"
            state.error_message = f"Negotiations failed: {str(e)}"
            return state
    
    async def _process_creator_batch(self, creators: List[Creator], campaign_data: CampaignData) -> List[NegotiationResult]:
        """Process a small batch of creators concurrently"""
        
        tasks = []
        for creator in creators:
            task = asyncio.create_task(
                self.negotiation_agent.negotiate_with_creator(
                    creator=creator,
                    campaign_data=campaign_data
                )
            )
            tasks.append(task)
        
        # Wait for all negotiations in batch to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"❌ Negotiation exception for {creators[i].id}: {result}")
                processed_results.append(
                    NegotiationResult(
                        creator_id=creators[i].id,
                        status="failed",
                        error_message=str(result)
                    )
                )
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _generate_contracts(self, state: OrchestrationState, campaign_data: CampaignData) -> OrchestrationState:
        """Phase 3: Generate contracts for successful negotiations"""
        
        logger.info("📝 Starting contract generation...")
        state.stage = "contracts"
        
        try:
            successful_negotiations = [r for r in state.negotiation_results if r.is_successful()]
            contracts_generated = []
            
            for negotiation in successful_negotiations:
                try:
                    contract = await self.contract_agent.generate_contract(
                        negotiation_result=negotiation,
                        campaign_data=campaign_data
                    )
                    contracts_generated.append(contract)
                    logger.info(f"📄 Contract generated for {negotiation.creator_id}")
                    
                except Exception as e:
                    logger.error(f"❌ Contract generation failed for {negotiation.creator_id}: {e}")
            
            state.contracts_generated = contracts_generated
            state.contracts_count = len(contracts_generated)
            
            logger.info(f"📊 Generated {len(contracts_generated)} contracts")
            return state
            
        except Exception as e:
            logger.error(f"❌ Contract generation failed: {e}")
            state.stage = "failed"
            state.error_message = f"Contract generation failed: {str(e)}"
            return state
    
    async def get_campaign_status(self, campaign_id: str) -> Dict[str, Any]:
        """Get current campaign status and metrics"""
        
        try:
            # In a real implementation, this would query the database
            # For now, return basic status structure
            return {
                "campaign_id": campaign_id,
                "stage": "running",
                "is_complete": False,
                "creators_found": 0,
                "successful_negotiations": 0,
                "contracts_generated": 0,
                "error_message": None
            }
            
        except Exception as e:
            logger.error(f"❌ Status check failed for {campaign_id}: {e}")
            return {
                "campaign_id": campaign_id,
                "stage": "failed",
                "error_message": str(e)
            }
    
    async def close(self) -> None:
        """
        Clean up resources (FIXED - added missing close method)
        """
        try:
            await self.negotiation_agent.close()
            await self.contract_agent.close()
            await self.database.close()
            logger.info("✅ Campaign Orchestrator resources cleaned up")
        except Exception as e:
            logger.error(f"❌ Error during orchestrator cleanup: {e}")