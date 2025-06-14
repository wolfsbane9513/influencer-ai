# agents/campaign_orchestrator.py
"""
Unified Campaign Orchestrator with clean architecture and strategy pattern.
Consolidates all orchestration functionality into a single, maintainable class.
"""

import asyncio
import json
import logging
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional, Protocol

from models.campaign import (
    CampaignOrchestrationState, CampaignData, 
    NegotiationState, NegotiationStatus
)
from agents.discovery import InfluencerDiscoveryAgent
from agents.contracts import ContractAgent
from services.database import DatabaseService
from services.elevenlabs_voice_service import VoiceServiceFactory, ConversationResult, CallResult
from core.exceptions import (
    InfluencerFlowException,
    BusinessLogicError,
    CampaignValidationError,
    create_error_context,
)

logger = logging.getLogger(__name__)

# Import Groq with fallback
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    logger.warning("⚠️  Groq not available - using rule-based strategy")


class WorkflowStage(str, Enum):
    """Campaign workflow stages"""
    INITIALIZING = "initializing"
    STRATEGY_PLANNING = "strategy_planning"
    DISCOVERY = "discovery"
    NEGOTIATIONS = "negotiations"
    VALIDATION = "validation"
    CONTRACTS = "contracts"
    DATABASE_SYNC = "database_sync"
    COMPLETED = "completed"
    FAILED = "failed"


class OrchestrationStrategy(str, Enum):
    """Orchestration strategy types"""
    BASIC = "basic"           # Simple linear workflow
    AI_ENHANCED = "ai_enhanced"  # AI-driven decision making
    ADAPTIVE = "adaptive"     # Adapts based on results


class OrchestrationError(BusinessLogicError):
    """General orchestration failure"""
    pass


# Strategy Pattern Interfaces
class IStrategyGenerator(Protocol):
    """Interface for strategy generation"""
    async def generate_strategy(self, campaign_data: CampaignData) -> Dict[str, Any]:
        ...


class INegotiationHandler(Protocol):
    """Interface for negotiation handling"""
    async def handle_negotiations(
        self, 
        state: CampaignOrchestrationState,
        strategy: Dict[str, Any]
    ) -> List[NegotiationState]:
        ...


class IProgressTracker(Protocol):
    """Interface for progress tracking"""
    def update_progress(self, state: CampaignOrchestrationState, stage: WorkflowStage) -> None:
        ...


# Strategy Implementations
class AIStrategyGenerator:
    """AI-powered strategy generation using Groq"""
    
    def __init__(self, groq_client: Optional[Any] = None):
        self.groq_client = groq_client
    
    async def generate_strategy(self, campaign_data: CampaignData) -> Dict[str, Any]:
        """Generate AI-powered campaign strategy"""
        if not self.groq_client:
            return self._get_rule_based_strategy(campaign_data)
        
        prompt = self._create_strategy_prompt(campaign_data)
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=500
            )
            
            strategy_text = response.choices[0].message.content.strip()
            strategy = self._extract_json_from_response(strategy_text)
            
            if self._validate_strategy(strategy):
                logger.info("🧠 AI strategy generated successfully")
                return strategy
            else:
                logger.warning("AI strategy validation failed, using rule-based fallback")
                return self._get_rule_based_strategy(campaign_data)
                
        except Exception as e:
            logger.error(f"AI strategy generation failed: {e}")
            return self._get_rule_based_strategy(campaign_data)
    
    def _create_strategy_prompt(self, campaign_data: CampaignData) -> str:
        """Create strategy generation prompt"""
        return f"""
        Generate an influencer marketing strategy for this campaign. Return valid JSON only.

        Campaign: {campaign_data.product_name} by {campaign_data.brand_name}
        Budget: ${campaign_data.total_budget:,}
        Niche: {campaign_data.product_niche}
        Goal: {campaign_data.campaign_goal}

        Return this JSON structure:
        {{
            "approach": "collaborative|premium|cost_effective",
            "creator_tier_priority": ["micro", "macro", "mega"],
            "max_creators_to_contact": 3,
            "negotiation_style": "flexible|firm|value_focused",
            "success_criteria": {{
                "min_partnerships": 1,
                "target_success_rate": 0.7
            }},
            "budget_allocation": {{
                "max_per_creator_pct": 0.4,
                "reserve_pct": 0.2
            }}
        }}
        """
    
    def _extract_json_from_response(self, response_text: str) -> Dict[str, Any]:
        """Extract JSON from AI response"""
        try:
            # Find JSON boundaries
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            else:
                raise ValueError("No valid JSON found in response")
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            raise
    
    def _validate_strategy(self, strategy: Dict[str, Any]) -> bool:
        """Validate strategy structure"""
        required_fields = [
            "approach", "creator_tier_priority", "max_creators_to_contact",
            "negotiation_style", "success_criteria", "budget_allocation"
        ]
        return all(field in strategy for field in required_fields)
    
    def _get_rule_based_strategy(self, campaign_data: CampaignData) -> Dict[str, Any]:
        """Generate rule-based strategy as fallback"""
        budget = campaign_data.total_budget
        niche = campaign_data.product_niche.lower()
        
        # Determine approach based on budget and niche
        if budget > 15000:
            approach = "premium"
            max_creators = 4
            tier_priority = ["macro", "mega", "micro"]
        elif budget > 8000:
            approach = "collaborative"
            max_creators = 3
            tier_priority = ["macro", "micro", "mega"]
        else:
            approach = "cost_effective"
            max_creators = 2
            tier_priority = ["micro", "macro", "mega"]
        
        # Niche-specific adjustments
        niche_adjustments = {
            "tech": {"tier_priority": ["macro", "micro", "mega"]},
            "beauty": {"tier_priority": ["micro", "macro", "mega"]},
            "gaming": {"max_creators": max_creators + 1}
        }
        
        if niche in niche_adjustments:
            adjustments = niche_adjustments[niche]
            tier_priority = adjustments.get("tier_priority", tier_priority)
            max_creators = adjustments.get("max_creators", max_creators)
        
        return {
            "approach": approach,
            "creator_tier_priority": tier_priority,
            "max_creators_to_contact": max_creators,
            "negotiation_style": "flexible" if approach == "collaborative" else "firm",
            "success_criteria": {
                "min_partnerships": 1 if budget < 5000 else 2,
                "target_success_rate": 0.7
            },
            "budget_allocation": {
                "max_per_creator_pct": 0.4 if budget > 10000 else 0.5,
                "reserve_pct": 0.2
            },
            "strategy_source": "rule_based"
        }


class BasicNegotiationHandler:
    """Basic negotiation handling without advanced features"""
    
    def __init__(self, voice_service_factory: Any):
        self.voice_service_factory = voice_service_factory
    
    async def handle_negotiations(
        self, 
        state: CampaignOrchestrationState,
        strategy: Dict[str, Any]
    ) -> List[NegotiationState]:
        """Handle negotiations with basic approach"""
        negotiations = []
        creators_to_contact = state.discovered_influencers[:strategy.get("max_creators_to_contact", 3)]
        
        # Create voice service
        voice_service = self.voice_service_factory.create_voice_service()
        
        for i, creator_match in enumerate(creators_to_contact):
            logger.info(f"📞 Negotiating with {creator_match.creator.name} ({i+1}/{len(creators_to_contact)})")
            
            # Update progress
            state.current_influencer = creator_match.creator.name
            
            # Create negotiation state
            negotiation = NegotiationState(
                creator_id=creator_match.creator.id,
                campaign_id=state.campaign_data.id,
                initial_offer=self._calculate_initial_offer(creator_match, strategy),
                started_at=datetime.now()
            )
            
            try:
                # Prepare conversation context
                conversation_context = self._prepare_conversation_context(
                    creator_match, state.campaign_data, strategy
                )
                
                # Initiate call
                conversation_id = await voice_service.initiate_call(
                    creator_match.creator.phone_number,
                    conversation_context
                )
                
                negotiation.conversation_id = conversation_id
                negotiation.status = NegotiationStatus.NEGOTIATING
                
                # Monitor conversation
                result = await voice_service.monitor_conversation(conversation_id)
                
                # Process result
                self._process_negotiation_result(negotiation, result)
                
            except Exception as e:
                logger.error(f"Negotiation failed for {creator_match.creator.name}: {e}")
                negotiation.status = NegotiationStatus.FAILED
                negotiation.failure_reason = str(e)
                negotiation.completed_at = datetime.now()
            
            negotiations.append(negotiation)
            
            # Brief pause between calls
            if i < len(creators_to_contact) - 1:
                await asyncio.sleep(5)
        
        return negotiations
    
    def _calculate_initial_offer(self, creator_match, strategy: Dict[str, Any]) -> float:
        """Calculate initial offer based on strategy"""
        base_rate = creator_match.estimated_rate
        
        approach = strategy.get("approach", "collaborative")
        if approach == "premium":
            multiplier = 1.05
        elif approach == "cost_effective":
            multiplier = 0.9
        else:
            multiplier = 0.95
        
        return round(base_rate * multiplier, 2)
    
    def _prepare_conversation_context(
        self, 
        creator_match, 
        campaign_data: CampaignData, 
        strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare conversation context"""
        creator = creator_match.creator
        
        creator_profile = {
            "id": creator.id,
            "name": creator.name,
            "niche": creator.niche,
            "followers": creator.followers,
            "engagement_rate": creator.engagement_rate,
            "platform": creator.platform.value,
            "typical_rate": creator.typical_rate
        }
        
        campaign_context = {
            "brand_name": campaign_data.brand_name,
            "product_name": campaign_data.product_name,
            "product_description": campaign_data.product_description,
            "target_audience": campaign_data.target_audience,
            "campaign_goal": campaign_data.campaign_goal
        }
        
        initial_offer = self._calculate_initial_offer(creator_match, strategy)
        max_offer = initial_offer * 1.25
        
        pricing_strategy = {
            "initial_offer": initial_offer,
            "max_offer": max_offer,
            "approach": strategy.get("negotiation_style", "flexible")
        }
        
        return {
            "creator_profile": creator_profile,
            "campaign_data": campaign_context,
            "pricing_strategy": pricing_strategy
        }
    
    def _process_negotiation_result(
        self, 
        negotiation: NegotiationState, 
        result: ConversationResult
    ) -> None:
        """Process conversation result into negotiation state"""
        negotiation.completed_at = datetime.now()
        negotiation.call_duration_seconds = result.duration_seconds or 0
        negotiation.call_transcript = result.transcript
        negotiation.call_recording_url = result.recording_url
        
        if result.call_result == CallResult.SUCCESS:
            negotiation.status = NegotiationStatus.SUCCESS
            
            # Extract final rate from analysis
            if result.analysis_data:
                final_rate = result.analysis_data.get("final_rate_mentioned")
                if final_rate:
                    negotiation.final_rate = final_rate
                else:
                    # Estimate based on initial offer
                    negotiation.final_rate = negotiation.initial_offer * 1.1
                
                # Extract negotiated terms
                negotiation.negotiated_terms = {
                    "deliverables": result.analysis_data.get("deliverables_discussed", ["video_review"]),
                    "timeline": result.analysis_data.get("timeline_mentioned", "7 days"),
                    "usage_rights": "organic_only",
                    "payment_schedule": "50% upfront, 50% on delivery",
                    "enthusiasm_level": result.analysis_data.get("creator_enthusiasm_level", 5)
                }
            else:
                # Default terms
                negotiation.final_rate = negotiation.initial_offer * 1.1
                negotiation.negotiated_terms = {
                    "deliverables": ["video_review"],
                    "timeline": "7 days",
                    "usage_rights": "organic_only",
                    "payment_schedule": "50% upfront, 50% on delivery"
                }
        else:
            negotiation.status = NegotiationStatus.FAILED
            negotiation.failure_reason = result.error_message or f"Call failed: {result.call_result.value}"


class ProgressTracker:
    """Tracks and updates orchestration progress"""
    
    def __init__(self, state_updater: Optional[Any] = None):
        self.state_updater = state_updater
    
    def update_progress(self, state: CampaignOrchestrationState, stage: WorkflowStage) -> None:
        """Update orchestration progress"""
        state.current_stage = stage.value
        
        # Update estimated completion time
        stage_durations = {
            WorkflowStage.INITIALIZING: 0.5,
            WorkflowStage.STRATEGY_PLANNING: 1.0,
            WorkflowStage.DISCOVERY: 1.5,
            WorkflowStage.NEGOTIATIONS: len(state.discovered_influencers) * 2.0,
            WorkflowStage.VALIDATION: 0.5,
            WorkflowStage.CONTRACTS: 1.0,
            WorkflowStage.DATABASE_SYNC: 0.5
        }
        
        remaining_stages = [s for s in WorkflowStage if s.value > stage.value]
        estimated_remaining = sum(stage_durations.get(s, 0) for s in remaining_stages)
        state.estimated_completion_minutes = estimated_remaining
        
        # Update external state if updater provided
        if self.state_updater:
            self.state_updater(state)
        
        logger.info(f"📊 Progress: {stage.value} - Est. {estimated_remaining:.1f}min remaining")


class CampaignOrchestrator:
    """
    Unified campaign orchestrator with strategy pattern and clean architecture
    """
    
    def __init__(self):
        # Initialize dependencies
        self.discovery_agent = InfluencerDiscoveryAgent()
        self.contract_agent = ContractAgent()
        self.database_service = DatabaseService()
        self.voice_service_factory = VoiceServiceFactory()
        
        # Initialize strategy components
        self.groq_client = self._initialize_groq()
        self.strategy_generator = AIStrategyGenerator(self.groq_client)
        self.negotiation_handler = BasicNegotiationHandler(self.voice_service_factory)
        self.progress_tracker = ProgressTracker()
        
        # Configuration
        self.default_strategy = OrchestrationStrategy.AI_ENHANCED if self.groq_client else OrchestrationStrategy.BASIC
    
    def _initialize_groq(self) -> Optional[Any]:
        """Initialize Groq client with proper error handling"""
        if not GROQ_AVAILABLE:
            return None
        
        try:
            from config.settings import settings
            
            if not settings.groq_api_key:
                logger.warning("No Groq API key found")
                return None
            
            groq_client = Groq(api_key=settings.groq_api_key)
            
            # Test connection
            groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            
            logger.info("✅ Groq client initialized successfully")
            return groq_client
            
        except Exception as e:
            logger.error(f"Groq initialization failed: {e}")
            return None
    
    async def orchestrate_campaign(
        self,
        orchestration_state: CampaignOrchestrationState,
        task_id: str,
        strategy_type: OrchestrationStrategy = None
    ) -> CampaignOrchestrationState:
        """
        Main orchestration method - unified entry point for all campaign types
        """
        strategy_type = strategy_type or self.default_strategy
        logger.info(f"🚀 Starting {strategy_type.value} campaign orchestration")

        context = create_error_context(
            operation="orchestrate_campaign",
            component="CampaignOrchestrator",
            campaign_id=orchestration_state.campaign_id,
        )

        try:
            
            # Set up progress tracking
            self.progress_tracker.state_updater = lambda state: self._update_external_state(task_id, state)
            
            # Phase 1: Initialization and Validation
            await self._phase_initialization(orchestration_state)
            
            # Phase 2: Strategy Planning
            await self._phase_strategy_planning(orchestration_state, strategy_type)
            
            # Phase 3: Discovery
            await self._phase_discovery(orchestration_state)
            
            # Phase 4: Negotiations
            await self._phase_negotiations(orchestration_state)
            
            # Phase 5: Validation
            await self._phase_validation(orchestration_state)
            
            # Phase 6: Contracts
            await self._phase_contracts(orchestration_state)
            
            # Phase 7: Database Sync
            await self._phase_database_sync(orchestration_state)
            
            # Phase 8: Completion
            await self._phase_completion(orchestration_state)
            
            logger.info("🎉 Campaign orchestration completed successfully")
            return orchestration_state

        except InfluencerFlowException as e:
            logger.error(f"❌ Campaign orchestration failed: {e.message}")
            await self._handle_orchestration_failure(orchestration_state, e.message)
            raise
        except Exception as e:
            logger.error(f"❌ Campaign orchestration failed: {e}")
            await self._handle_orchestration_failure(orchestration_state, str(e))
            raise OrchestrationError(
                message=f"Campaign orchestration failed: {e}",
                context=context,
            )
    
    async def _phase_initialization(self, state: CampaignOrchestrationState) -> None:
        """Phase 1: Initialize and validate campaign"""
        self.progress_tracker.update_progress(state, WorkflowStage.INITIALIZING)
        
        # Validate campaign data
        validation_result = self._validate_campaign_data(state.campaign_data)
        if not validation_result["is_valid"]:
            raise CampaignValidationError(
                message="Campaign validation failed",
                validation_errors=validation_result["errors"],
                context=create_error_context(
                    operation="_phase_initialization",
                    component="CampaignOrchestrator",
                    campaign_id=state.campaign_id,
                ),
            )
        
        logger.info("✅ Campaign validation passed")
    
    async def _phase_strategy_planning(
        self, 
        state: CampaignOrchestrationState, 
        strategy_type: OrchestrationStrategy
    ) -> None:
        """Phase 2: Generate campaign strategy"""
        self.progress_tracker.update_progress(state, WorkflowStage.STRATEGY_PLANNING)
        
        # Generate strategy based on type
        if strategy_type == OrchestrationStrategy.AI_ENHANCED:
            strategy = await self.strategy_generator.generate_strategy(state.campaign_data)
        else:
            # Use rule-based strategy for basic mode
            ai_generator = AIStrategyGenerator(None)
            strategy = ai_generator._get_rule_based_strategy(state.campaign_data)
        
        # Store strategy in state
        state.negotiated_terms["campaign_strategy"] = strategy
        
        logger.info(f"🎯 Strategy: {strategy.get('approach', 'unknown')} approach")
    
    async def _phase_discovery(self, state: CampaignOrchestrationState) -> None:
        """Phase 3: Discover matching creators"""
        self.progress_tracker.update_progress(state, WorkflowStage.DISCOVERY)
        
        strategy = state.negotiated_terms.get("campaign_strategy", {})
        max_creators = strategy.get("max_creators_to_contact", 3)
        
        # Run discovery
        discovered_creators = await self.discovery_agent.find_matches(
            state.campaign_data,
            max_results=max_creators
        )
        
        state.discovered_influencers = discovered_creators
        
        logger.info(f"🔍 Discovered {len(discovered_creators)} matching creators")
    
    async def _phase_negotiations(self, state: CampaignOrchestrationState) -> None:
        """Phase 4: Conduct negotiations"""
        self.progress_tracker.update_progress(state, WorkflowStage.NEGOTIATIONS)

        strategy = state.negotiated_terms.get("campaign_strategy", {})

        # Handle negotiations
        try:
            negotiations = await self.negotiation_handler.handle_negotiations(state, strategy)
        except InfluencerFlowException as e:
            logger.error(f"Negotiation handler failed: {e.message}")
            raise

        # Update state
        state.negotiations = negotiations
        state.successful_negotiations = len([n for n in negotiations if n.status == NegotiationStatus.SUCCESS])
        state.failed_negotiations = len([n for n in negotiations if n.status == NegotiationStatus.FAILED])
        state.total_cost = sum(n.final_rate or 0 for n in negotiations if n.final_rate)
        
        logger.info(f"📞 Negotiations complete: {state.successful_negotiations}/{len(negotiations)} successful")
    
    async def _phase_validation(self, state: CampaignOrchestrationState) -> None:
        """Phase 5: Validate results"""
        self.progress_tracker.update_progress(state, WorkflowStage.VALIDATION)
        
        # Validate negotiation results
        valid_negotiations = []
        for negotiation in state.negotiations:
            if negotiation.status == NegotiationStatus.SUCCESS:
                if negotiation.final_rate and negotiation.final_rate > 0:
                    valid_negotiations.append(negotiation)
                else:
                    logger.warning(f"Invalid negotiation result for {negotiation.creator_id}")
        
        logger.info(f"✅ Validation complete: {len(valid_negotiations)} valid negotiations")
    
    async def _phase_contracts(self, state: CampaignOrchestrationState) -> None:
        """Phase 6: Generate contracts"""
        self.progress_tracker.update_progress(state, WorkflowStage.CONTRACTS)
        
        successful_negotiations = [
            n for n in state.negotiations 
            if n.status == NegotiationStatus.SUCCESS
        ]
        
        contracts_generated = 0
        for negotiation in successful_negotiations:
            try:
                contract = await self.contract_agent.generate_contract(
                    negotiation,
                    state.campaign_data
                )
                
                # Update negotiation with contract reference
                negotiation.negotiated_terms = negotiation.negotiated_terms or {}
                negotiation.negotiated_terms["contract_id"] = contract["contract_id"]
                contracts_generated += 1
                
            except InfluencerFlowException as e:
                logger.error(
                    f"Contract generation failed for {negotiation.creator_id}: {e.message}"
                )
            except Exception as e:
                logger.error(
                    f"Contract generation failed for {negotiation.creator_id}: {e}"
                )
        
        logger.info(f"📝 Generated {contracts_generated} contracts")
    
    async def _phase_database_sync(self, state: CampaignOrchestrationState) -> None:
        """Phase 7: Sync to database"""
        self.progress_tracker.update_progress(state, WorkflowStage.DATABASE_SYNC)
        
        try:
            await self.database_service.sync_campaign_results(state)
            logger.info("💾 Database sync completed")
        except InfluencerFlowException as e:
            logger.error(f"Database sync failed: {e.message}")
        except Exception as e:
            logger.error(f"Database sync failed: {e}")
            # Don't fail the entire orchestration for DB issues
    
    async def _phase_completion(self, state: CampaignOrchestrationState) -> None:
        """Phase 8: Complete orchestration"""
        self.progress_tracker.update_progress(state, WorkflowStage.COMPLETED)
        
        state.completed_at = datetime.now()
        
        # Generate summary
        summary = state.get_campaign_summary()
        logger.info(f"🎉 Campaign completed: {summary}")
    
    def _validate_campaign_data(self, campaign_data: CampaignData) -> Dict[str, Any]:
        """Validate campaign data"""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Required field validation
        required_fields = {
            "brand_name": campaign_data.brand_name,
            "product_name": campaign_data.product_name,
            "total_budget": campaign_data.total_budget,
            "product_niche": campaign_data.product_niche
        }
        
        for field_name, field_value in required_fields.items():
            if not field_value:
                validation_result["errors"].append(f"Missing required field: {field_name}")
                validation_result["is_valid"] = False
        
        # Budget validation
        if campaign_data.total_budget and campaign_data.total_budget < 1000:
            validation_result["warnings"].append("Budget below $1,000 may limit options")
        
        return validation_result
    
    async def _handle_orchestration_failure(
        self, 
        state: CampaignOrchestrationState, 
        error_message: str
    ) -> None:
        """Handle orchestration failure"""
        self.progress_tracker.update_progress(state, WorkflowStage.FAILED)
        state.completed_at = datetime.now()
        state.negotiated_terms["error_message"] = error_message
        
        logger.error(f"Orchestration failed: {error_message}")
    
    def _update_external_state(self, task_id: str, state: CampaignOrchestrationState) -> None:
        """Update external state tracking"""
        try:
            from main import active_campaigns
            active_campaigns[task_id] = state
        except Exception as e:
            logger.error(f"Failed to update external state: {e}")
    
    # Backward compatibility methods
    async def orchestrate_enhanced_campaign(self, state, task_id):
        """Legacy enhanced orchestration"""
        return await self.orchestrate_campaign(state, task_id, OrchestrationStrategy.AI_ENHANCED)
    
    async def run_campaign(self, campaign_data, task_id):
        """Legacy basic orchestration"""
        state = CampaignOrchestrationState(
            campaign_id=campaign_data.id,
            campaign_data=campaign_data
        )
        return await self.orchestrate_campaign(state, task_id, OrchestrationStrategy.BASIC)


# Factory for creating orchestrators with different configurations
class OrchestratorFactory:
    """Factory for creating configured orchestrator instances"""
    
    @staticmethod
    def create_orchestrator() -> CampaignOrchestrator:
        """Create a standard orchestrator instance"""
        return CampaignOrchestrator()
    
    @staticmethod
    def create_testing_orchestrator() -> CampaignOrchestrator:
        """Create orchestrator for testing with mocked dependencies"""
        orchestrator = CampaignOrchestrator()
        # Could inject mock services here for testing
        return orchestrator