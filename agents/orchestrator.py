# agents/orchestrator.py
import asyncio
import logging
from datetime import datetime
from typing import Optional

from models.campaign import CampaignOrchestrationState, NegotiationState
from agents.discovery import InfluencerDiscoveryAgent
from agents.negotiation import NegotiationAgent
from agents.contracts import ContractAgent
from services.database import DatabaseService

# Import settings with fallback
try:
    from config.settings import settings
except ImportError:
    from config.simple_settings import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CampaignOrchestrator:
    """
    Master orchestrator that coordinates the entire campaign workflow:
    Campaign → Discovery → Negotiation → Contracts → Database Sync
    """
    
    def __init__(self):
        self.discovery_agent = InfluencerDiscoveryAgent()
        self.negotiation_agent = NegotiationAgent()
        self.contract_agent = ContractAgent()
        self.database_service = DatabaseService()
    
    async def orchestrate_campaign(
        self,
        orchestration_state: CampaignOrchestrationState,
        task_id: str
    ) -> CampaignOrchestrationState:
        """
        Main orchestration workflow
        """
        try:
            logger.info(f"🚀 Starting campaign orchestration for {orchestration_state.campaign_id}")
            
            # Update state
            orchestration_state.current_stage = "discovery"
            await self._update_active_campaign_state(task_id, orchestration_state)
            
            # Step 1: Discover top influencers
            await self._run_discovery_phase(orchestration_state)
            
            # Step 2: Sequential negotiations (for demo clarity)
            await self._run_negotiation_phase(orchestration_state, task_id)
            
            # Step 3: Generate contracts for successful negotiations
            await self._run_contract_phase(orchestration_state)
            
            # Step 4: Sync results to database
            await self._sync_to_database(orchestration_state)
            
            # Mark as completed
            orchestration_state.current_stage = "completed"
            orchestration_state.completed_at = datetime.now()
            await self._update_active_campaign_state(task_id, orchestration_state)
            
            logger.info(f"✅ Campaign orchestration completed for {orchestration_state.campaign_id}")
            logger.info(f"📊 Results: {orchestration_state.get_summary()}")
            
            return orchestration_state
            
        except Exception as e:
            logger.error(f"❌ Campaign orchestration failed: {str(e)}")
            orchestration_state.current_stage = "failed"
            orchestration_state.completed_at = datetime.now()
            await self._update_active_campaign_state(task_id, orchestration_state)
            raise
    
    async def _run_discovery_phase(self, state: CampaignOrchestrationState):
        """Run the influencer discovery phase"""
        logger.info("🔍 Starting influencer discovery phase...")
        
        state.current_stage = "discovery"
        
        # Find top matching influencers
        discovered_influencers = await self.discovery_agent.find_matches(
            state.campaign_data
        )
        
        state.discovered_influencers = discovered_influencers
        
        logger.info(f"✅ Discovery complete: Found {len(discovered_influencers)} matching influencers")
        for i, match in enumerate(discovered_influencers):
            logger.info(f"  {i+1}. {match.creator.name} - {match.similarity_score:.2f} similarity")
    
    async def _run_negotiation_phase(
        self,
        state: CampaignOrchestrationState,
        task_id: str
    ):
        """Run sequential negotiations with discovered influencers"""
        logger.info("📞 Starting negotiation phase...")
        
        state.current_stage = "negotiations"
        
        # Negotiate with top 3 influencers sequentially
        top_influencers = state.discovered_influencers[:3]
        
        for i, influencer_match in enumerate(top_influencers):
            logger.info(f"📞 Negotiating with {influencer_match.creator.name} ({i+1}/3)")
            
            # Update current influencer in state
            state.current_influencer = influencer_match.creator.name
            state.estimated_completion_minutes = (3 - i) * 1.5  # Rough estimate
            await self._update_active_campaign_state(task_id, state)
            
            # Run negotiation
            negotiation_result = await self.negotiation_agent.negotiate(
                influencer_match,
                state.campaign_data
            )
            
            # Add result to state
            state.add_negotiation_result(negotiation_result)
            
            # Log result
            if negotiation_result.status.value == "success":
                logger.info(f"✅ Successful negotiation: ${negotiation_result.final_rate}")
            else:
                logger.info(f"❌ Failed negotiation: {negotiation_result.failure_reason}")
            
            # Brief pause between calls for demo effect
            if i < len(top_influencers) - 1:
                await asyncio.sleep(2)
        
        logger.info(f"📞 Negotiation phase complete: {state.successful_negotiations}/{len(top_influencers)} successful")
    
    async def _run_contract_phase(self, state: CampaignOrchestrationState):
        """Generate contracts for successful negotiations"""
        logger.info("📝 Starting contract generation phase...")
        
        state.current_stage = "contracts"
        
        successful_negotiations = [
            neg for neg in state.negotiations 
            if neg.status.value == "success"
        ]
        
        for negotiation in successful_negotiations:
            try:
                contract = await self.contract_agent.generate_contract(
                    negotiation,
                    state.campaign_data
                )
                
                # Store contract reference in negotiation
                negotiation.negotiated_terms["contract_generated"] = True
                negotiation.negotiated_terms["contract_id"] = contract.get("contract_id")
                
                logger.info(f"📝 Contract generated for {negotiation.creator_id}")
                
            except Exception as e:
                logger.error(f"❌ Contract generation failed for {negotiation.creator_id}: {str(e)}")
        
        logger.info(f"📝 Contract phase complete: {len(successful_negotiations)} contracts generated")
    
    async def _sync_to_database(self, state: CampaignOrchestrationState):
        """Sync all results to database"""
        logger.info("💾 Syncing results to database...")
        
        state.current_stage = "database_sync"
        
        try:
            # Sync campaign results
            await self.database_service.sync_campaign_results(state)
            logger.info("✅ Database sync completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Database sync failed: {str(e)}")
            # Don't fail the entire orchestration for DB sync issues
    
    async def _update_active_campaign_state(
        self,
        task_id: str,
        state: CampaignOrchestrationState
    ):
        """Update the active campaign state for monitoring"""
        try:
            from main import active_campaigns
            active_campaigns[task_id] = state
        except Exception as e:
            logger.error(f"Failed to update active campaign state: {str(e)}")

# agents/__init__.py
"""
InfluencerFlow AI Agents

This package contains all the AI agents that power the automated
influencer marketing campaign workflow:

- CampaignOrchestrator: Master coordinator
- InfluencerDiscoveryAgent: Vector similarity matching
- NegotiationAgent: AI-powered phone negotiations
- ContractAgent: Automated contract generation
"""

from .orchestrator import CampaignOrchestrator
from .discovery import InfluencerDiscoveryAgent
from .negotiation import NegotiationAgent
from .contracts import ContractAgent

__all__ = [
    "CampaignOrchestrator",
    "InfluencerDiscoveryAgent", 
    "NegotiationAgent",
    "ContractAgent"
]