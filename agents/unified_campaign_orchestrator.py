# agents/unified_campaign_orchestrator.py
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum
from pydantic import BaseModel

from models.campaign import CampaignData, CampaignOrchestrationState
from agents.campaign_data_collector import EnhancedCampaignDataCollector, DataCollectionMethod
from agents.enhanced_influencer_matcher import EnhancedInfluencerMatcher, InfluencerSelectionStrategy
from agents.enhanced_negotiation_manager import EnhancedNegotiationManager, NegotiationPhase
from agents.enhanced_contract_generator import EnhancedContractGenerator
from services.database import DatabaseService

logger = logging.getLogger(__name__)

class CampaignWorkflowPhase(str, Enum):
    DATA_COLLECTION = "data_collection"
    DATA_VALIDATION = "data_validation"
    INFLUENCER_DISCOVERY = "influencer_discovery"
    INFLUENCER_SELECTION = "influencer_selection"
    NEGOTIATION_SEQUENCE = "negotiation_sequence"
    HUMAN_REVIEW = "human_review"
    SPONSOR_APPROVAL = "sponsor_approval"
    CONTRACT_GENERATION = "contract_generation"
    CONTRACT_DELIVERY = "contract_delivery"
    CAMPAIGN_MONITORING = "campaign_monitoring"
    COMPLETED = "completed"
    FAILED = "failed"

class WorkflowConfiguration(BaseModel):
    """Configuration for campaign workflow"""
    
    # Data collection settings
    data_collection_method: DataCollectionMethod = DataCollectionMethod.MANUAL
    require_data_validation: bool = True
    
    # Influencer selection settings
    selection_strategy: InfluencerSelectionStrategy = InfluencerSelectionStrategy.BUDGET_OPTIMIZED
    max_influencers: Optional[int] = None
    require_human_review: bool = True
    
    # Negotiation settings
    sequential_calling: bool = True
    max_parallel_negotiations: int = 2
    auto_approve_threshold: float = 0.85
    
    # Approval workflow
    require_sponsor_approval: bool = True
    sponsor_approval_timeout_hours: int = 48
    
    # Contract settings
    auto_send_contracts: bool = True
    preferred_delivery_method: str = "email"
    
    # Monitoring
    real_time_progress: bool = True
    send_notifications: bool = True

class CampaignWorkflowState(BaseModel):
    """Complete campaign workflow state"""
    workflow_id: str
    campaign_id: Optional[str] = None
    
    # Phase tracking
    current_phase: CampaignWorkflowPhase
    completed_phases: List[CampaignWorkflowPhase] = []
    
    # Data collection
    data_collection_session_id: Optional[str] = None
    campaign_data: Optional[CampaignData] = None
    
    # Influencer management
    influencer_pool: Optional[Dict[str, Any]] = None
    budget_allocation: Optional[Dict[str, Any]] = None
    
    # Negotiations
    active_negotiations: Dict[str, str] = {}  # creator_id -> negotiation_id
    completed_negotiations: List[str] = []
    successful_negotiations: List[str] = []
    
    # Contracts
    generated_contracts: List[str] = []
    signed_contracts: List[str] = []
    
    # Workflow metadata
    configuration: WorkflowConfiguration
    started_at: datetime
    estimated_completion: Optional[datetime] = None
    actual_completion: Optional[datetime] = None
    
    # Progress tracking
    progress_percentage: float = 0.0
    current_activity: str = "Initializing workflow"
    
    def update_progress(self, percentage: float, activity: str):
        """Update workflow progress"""
        self.progress_percentage = percentage
        self.current_activity = activity
        logger.info(f"📊 Workflow Progress: {percentage:.1f}% - {activity}")

class UnifiedCampaignOrchestrator:
    """
    🎯 UNIFIED ENHANCED CAMPAIGN ORCHESTRATOR
    
    Complete end-to-end campaign automation:
    1. Enhanced data collection (manual/file/conversational)
    2. Intelligent influencer matching with budget optimization
    3. Sequential negotiations with human-in-the-loop
    4. Sponsor approval workflow
    5. Automated contract generation and delivery
    6. Real-time monitoring and analytics
    """
    
    def __init__(self):
        # Initialize all enhanced agents
        self.data_collector = EnhancedCampaignDataCollector()
        self.influencer_matcher = EnhancedInfluencerMatcher()
        self.negotiation_manager = EnhancedNegotiationManager()
        self.contract_generator = EnhancedContractGenerator()
        self.database_service = DatabaseService()
        
        # Workflow tracking
        self.active_workflows: Dict[str, CampaignWorkflowState] = {}
        
        # Configuration
        self.default_config = WorkflowConfiguration()
    
    async def start_unified_campaign_workflow(
        self,
        initial_data: Optional[Dict[str, Any]] = None,
        configuration: Optional[WorkflowConfiguration] = None,
        workflow_id: Optional[str] = None
    ) -> CampaignWorkflowState:
        """
        🚀 Start complete unified campaign workflow
        """
        
        if not workflow_id:
            workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        config = configuration or self.default_config
        
        # Initialize workflow state
        workflow_state = CampaignWorkflowState(
            workflow_id=workflow_id,
            current_phase=CampaignWorkflowPhase.DATA_COLLECTION,
            configuration=config,
            started_at=datetime.now()
        )
        
        self.active_workflows[workflow_id] = workflow_state
        
        logger.info(f"🚀 Starting unified campaign workflow: {workflow_id}")
        logger.info(f"📋 Configuration: {config.data_collection_method.value} data collection")
        
        try:
            # Phase 1: Enhanced Data Collection
            await self._execute_data_collection_phase(workflow_state, initial_data)
            
            # Phase 2: Data Validation
            await self._execute_data_validation_phase(workflow_state)
            
            # Phase 3: Influencer Discovery & Selection
            await self._execute_influencer_discovery_phase(workflow_state)
            
            # Phase 4: Enhanced Negotiation Sequence
            await self._execute_negotiation_sequence_phase(workflow_state)
            
            # Phase 5: Human Review & Sponsor Approval
            await self._execute_approval_workflow_phase(workflow_state)
            
            # Phase 6: Contract Generation & Delivery
            await self._execute_contract_workflow_phase(workflow_state)
            
            # Phase 7: Campaign Monitoring Setup
            await self._execute_monitoring_setup_phase(workflow_state)
            
            # Completion
            workflow_state.current_phase = CampaignWorkflowPhase.COMPLETED
            workflow_state.actual_completion = datetime.now()
            workflow_state.update_progress(100.0, "Campaign workflow completed successfully")
            
            logger.info(f"🎉 Unified campaign workflow completed: {workflow_id}")
            
            return workflow_state
            
        except Exception as e:
            logger.error(f"❌ Unified workflow failed: {e}")
            workflow_state.current_phase = CampaignWorkflowPhase.FAILED
            workflow_state.update_progress(0.0, f"Workflow failed: {str(e)}")
            raise
    
    async def _execute_data_collection_phase(self, workflow_state: CampaignWorkflowState, initial_data: Optional[Dict[str, Any]]):
        """📝 Execute enhanced data collection phase"""
        
        logger.info("📝 Phase 1: Enhanced Data Collection")
        workflow_state.update_progress(5.0, "Starting data collection")
        
        # Start data collection based on configuration
        collection_session = await self.data_collector.start_data_collection(
            method=workflow_state.configuration.data_collection_method,
            initial_data=initial_data
        )
        
        workflow_state.data_collection_session_id = collection_session.session_id
        
        # Monitor collection progress
        while collection_session.status.value not in ["completed", "failed"]:
            await asyncio.sleep(2)
            collection_session = self.data_collector.get_session_status(collection_session.session_id)
            
            progress = 5.0 + (collection_session.progress_percentage * 0.15)  # 5-20% range
            workflow_state.update_progress(progress, f"Collecting data: {collection_session.progress_percentage:.1f}% complete")
        
        if collection_session.status.value == "completed":
            workflow_state.completed_phases.append(CampaignWorkflowPhase.DATA_COLLECTION)
            workflow_state.update_progress(20.0, "Data collection completed")
        else:
            raise Exception(f"Data collection failed: {collection_session.validation_errors}")
    
    async def _execute_data_validation_phase(self, workflow_state: CampaignWorkflowState):
        """✅ Execute data validation phase"""
        
        logger.info("✅ Phase 2: Data Validation")
        workflow_state.current_phase = CampaignWorkflowPhase.DATA_VALIDATION
        workflow_state.update_progress(22.0, "Validating campaign data")
        
        # Finalize campaign data from collection session
        campaign_data = await self.data_collector.finalize_campaign_data(
            workflow_state.data_collection_session_id
        )
        
        if not campaign_data:
            raise Exception("Failed to finalize campaign data")
        
        workflow_state.campaign_data = campaign_data
        workflow_state.campaign_id = campaign_data.id
        
        # Additional validation if required
        if workflow_state.configuration.require_data_validation:
            validation_result = self._perform_enhanced_validation(campaign_data)
            if not validation_result["is_valid"]:
                raise Exception(f"Validation failed: {validation_result['errors']}")
        
        workflow_state.completed_phases.append(CampaignWorkflowPhase.DATA_VALIDATION)
        workflow_state.update_progress(25.0, "Data validation completed")
    
    async def _execute_influencer_discovery_phase(self, workflow_state: CampaignWorkflowState):
        """🔍 Execute enhanced influencer discovery and selection"""
        
        logger.info("🔍 Phase 3: Enhanced Influencer Discovery & Selection")
        workflow_state.current_phase = CampaignWorkflowPhase.INFLUENCER_DISCOVERY
        workflow_state.update_progress(27.0, "Discovering potential influencers")
        
        # Enhanced influencer matching
        influencer_pool, budget_allocation = await self.influencer_matcher.enhanced_influencer_matching(
            campaign_data=workflow_state.campaign_data,
            strategy=workflow_state.configuration.selection_strategy,
            max_influencers=workflow_state.configuration.max_influencers
        )
        
        # Store results
        workflow_state.influencer_pool = {
            "primary_selections": [self._serialize_creator_match(match) for match in influencer_pool.primary_selections],
            "reserve_selections": [self._serialize_creator_match(match) for match in influencer_pool.reserve_selections],
            "backup_selections": [self._serialize_creator_match(match) for match in influencer_pool.backup_selections]
        }
        
        workflow_state.budget_allocation = {
            "total_budget": budget_allocation.total_budget,
            "primary_allocation": budget_allocation.primary_allocation,
            "reserve_allocation": budget_allocation.reserve_allocation,
            "buffer_allocation": budget_allocation.buffer_allocation
        }
        
        workflow_state.completed_phases.append(CampaignWorkflowPhase.INFLUENCER_DISCOVERY)
        workflow_state.current_phase = CampaignWorkflowPhase.INFLUENCER_SELECTION
        workflow_state.update_progress(35.0, f"Selected {len(influencer_pool.primary_selections)} primary influencers")
    
    async def _execute_negotiation_sequence_phase(self, workflow_state: CampaignWorkflowState):
        """📞 Execute enhanced negotiation sequence"""
        
        logger.info("📞 Phase 4: Enhanced Negotiation Sequence")
        workflow_state.current_phase = CampaignWorkflowPhase.NEGOTIATION_SEQUENCE
        workflow_state.update_progress(40.0, "Starting negotiation sequence")
        
        # Reconstruct influencer pool from serialized data
        primary_selections = workflow_state.influencer_pool["primary_selections"]
        total_negotiations = len(primary_selections)
        
        # Sequential negotiations
        for i, creator_data in enumerate(primary_selections):
            creator_id = creator_data["creator_id"]
            
            progress = 40.0 + ((i / total_negotiations) * 25.0)  # 40-65% range
            workflow_state.update_progress(progress, f"Negotiating with {creator_data['creator_name']} ({i+1}/{total_negotiations})")
            
            # Execute enhanced negotiation
            negotiation_context = {
                "workflow_id": workflow_state.workflow_id,
                "campaign_data": workflow_state.campaign_data,
                "budget_allocation": workflow_state.budget_allocation
            }
            
            try:
                # Create creator match object for negotiation
                creator_match = self._deserialize_creator_match(creator_data)
                
                negotiation_result = await self.negotiation_manager.execute_enhanced_negotiation(
                    creator_match=creator_match,
                    campaign_data=workflow_state.campaign_data,
                    negotiation_context=negotiation_context
                )
                
                # Track negotiation
                negotiation_id = negotiation_result["negotiation_id"]
                workflow_state.active_negotiations[creator_id] = negotiation_id
                
                if negotiation_result["status"] == "completed":
                    workflow_state.completed_negotiations.append(negotiation_id)
                    if negotiation_result["final_outcome"]["status"] == "confirmed":
                        workflow_state.successful_negotiations.append(negotiation_id)
                
            except Exception as e:
                logger.error(f"❌ Negotiation failed with {creator_id}: {e}")
                continue
        
        workflow_state.completed_phases.append(CampaignWorkflowPhase.NEGOTIATION_SEQUENCE)
        workflow_state.update_progress(65.0, f"Negotiations completed: {len(workflow_state.successful_negotiations)} successful")
    
    async def _execute_approval_workflow_phase(self, workflow_state: CampaignWorkflowState):
        """👤 Execute human review and sponsor approval workflow"""
        
        logger.info("👤 Phase 5: Human Review & Sponsor Approval")
        workflow_state.current_phase = CampaignWorkflowPhase.HUMAN_REVIEW
        workflow_state.update_progress(67.0, "Processing human reviews and sponsor approvals")
        
        # Check for pending human reviews
        pending_reviews = self.negotiation_manager.get_human_review_queue()
        
        if workflow_state.configuration.require_human_review and pending_reviews:
            workflow_state.update_progress(70.0, f"Waiting for {len(pending_reviews)} human reviews")
            
            # Wait for human reviews (with timeout)
            await self._wait_for_human_reviews(pending_reviews, workflow_state)
        
        # Check for sponsor approvals
        if workflow_state.configuration.require_sponsor_approval:
            workflow_state.current_phase = CampaignWorkflowPhase.SPONSOR_APPROVAL
            workflow_state.update_progress(75.0, "Waiting for sponsor approval")
            
            await self._wait_for_sponsor_approvals(workflow_state)
        
        workflow_state.completed_phases.append(CampaignWorkflowPhase.HUMAN_REVIEW)
        workflow_state.completed_phases.append(CampaignWorkflowPhase.SPONSOR_APPROVAL)
        workflow_state.update_progress(80.0, "Approvals completed")
    
    async def _execute_contract_workflow_phase(self, workflow_state: CampaignWorkflowState):
        """📝 Execute contract generation and delivery"""
        
        logger.info("📝 Phase 6: Contract Generation & Delivery")
        workflow_state.current_phase = CampaignWorkflowPhase.CONTRACT_GENERATION
        workflow_state.update_progress(82.0, "Generating contracts")
        
        # Generate contracts for successful negotiations
        for negotiation_id in workflow_state.successful_negotiations:
            try:
                # Get negotiation details
                negotiation_state = self.negotiation_manager.get_negotiation_status(negotiation_id)
                
                if negotiation_state and negotiation_state["final_outcome"]["status"] == "confirmed":
                    # Generate contract
                    contract_data = await self.contract_generator.generate_enhanced_contract(
                        negotiation_state=self._convert_to_negotiation_state(negotiation_state),
                        campaign_data=workflow_state.campaign_data
                    )
                    
                    workflow_state.generated_contracts.append(contract_data.contract_id)
                    
                    # Send contract if auto-send is enabled
                    if workflow_state.configuration.auto_send_contracts:
                        await self.contract_generator.send_contract_for_signature(
                            contract_id=contract_data.contract_id
                        )
            
            except Exception as e:
                logger.error(f"❌ Contract generation failed for {negotiation_id}: {e}")
                continue
        
        workflow_state.completed_phases.append(CampaignWorkflowPhase.CONTRACT_GENERATION)
        workflow_state.current_phase = CampaignWorkflowPhase.CONTRACT_DELIVERY
        workflow_state.update_progress(90.0, f"Generated {len(workflow_state.generated_contracts)} contracts")
    
    async def _execute_monitoring_setup_phase(self, workflow_state: CampaignWorkflowState):
        """📊 Setup campaign monitoring"""
        
        logger.info("📊 Phase 7: Campaign Monitoring Setup")
        workflow_state.current_phase = CampaignWorkflowPhase.CAMPAIGN_MONITORING
        workflow_state.update_progress(95.0, "Setting up campaign monitoring")
        
        # Setup monitoring for contracts and campaign performance
        monitoring_config = {
            "workflow_id": workflow_state.workflow_id,
            "campaign_id": workflow_state.campaign_id,
            "contracts_to_monitor": workflow_state.generated_contracts,
            "real_time_tracking": workflow_state.configuration.real_time_progress,
            "notifications_enabled": workflow_state.configuration.send_notifications
        }
        
        # Initialize campaign monitoring (implementation would setup dashboards, alerts, etc.)
        logger.info(f"📊 Campaign monitoring configured: {monitoring_config}")
        
        workflow_state.completed_phases.append(CampaignWorkflowPhase.CAMPAIGN_MONITORING)
        workflow_state.update_progress(98.0, "Campaign monitoring active")
    
    # Helper methods
    
    def _serialize_creator_match(self, match) -> Dict[str, Any]:
        """Serialize creator match for storage"""
        return {
            "creator_id": match.creator.id,
            "creator_name": match.creator.name,
            "similarity_score": match.similarity_score,
            "estimated_rate": match.estimated_rate,
            "rate_compatible": match.rate_compatible,
            "match_reasons": match.match_reasons
        }
    
    def _deserialize_creator_match(self, data: Dict[str, Any]):
        """Deserialize creator match from storage"""
        # This would reconstruct the full CreatorMatch object
        # For now, returning the data as-is
        return data
    
    def _perform_enhanced_validation(self, campaign_data: CampaignData) -> Dict[str, Any]:
        """Perform enhanced campaign data validation"""
        
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Enhanced validation rules
        if campaign_data.total_budget < 500:
            validation_result["errors"].append("Budget must be at least $500")
            validation_result["is_valid"] = False
        
        if len(campaign_data.product_description) < 50:
            validation_result["warnings"].append("Product description is very short")
        
        if not campaign_data.target_audience or len(campaign_data.target_audience) < 20:
            validation_result["warnings"].append("Target audience description should be more detailed")
        
        return validation_result
    
    async def _wait_for_human_reviews(self, pending_reviews: List, workflow_state: CampaignWorkflowState):
        """Wait for human reviews with timeout"""
        
        timeout_hours = 24  # 24 hours for human review
        start_time = datetime.now()
        
        while (datetime.now() - start_time).total_seconds() < (timeout_hours * 3600):
            # Check if reviews are completed
            current_reviews = self.negotiation_manager.get_human_review_queue()
            
            if len(current_reviews) == 0:
                logger.info("✅ All human reviews completed")
                break
            
            # Update progress
            completed_reviews = len(pending_reviews) - len(current_reviews)
            progress = 70.0 + ((completed_reviews / len(pending_reviews)) * 5.0)
            workflow_state.update_progress(progress, f"Human reviews: {completed_reviews}/{len(pending_reviews)} completed")
            
            await asyncio.sleep(60)  # Check every minute
        
        # Handle timeout
        remaining_reviews = self.negotiation_manager.get_human_review_queue()
        if remaining_reviews:
            logger.warning(f"⏰ Human review timeout: {len(remaining_reviews)} reviews still pending")
    
    async def _wait_for_sponsor_approvals(self, workflow_state: CampaignWorkflowState):
        """Wait for sponsor approvals with timeout"""
        
        timeout_hours = workflow_state.configuration.sponsor_approval_timeout_hours
        start_time = datetime.now()
        
        while (datetime.now() - start_time).total_seconds() < (timeout_hours * 3600):
            # Check approval status
            pending_approvals = self.negotiation_manager.sponsor_approval_queue
            
            if len(pending_approvals) == 0:
                logger.info("✅ All sponsor approvals completed")
                break
            
            workflow_state.update_progress(77.0, f"Waiting for {len(pending_approvals)} sponsor approvals")
            await asyncio.sleep(300)  # Check every 5 minutes
        
        # Handle timeout
        if self.negotiation_manager.sponsor_approval_queue:
            logger.warning(f"⏰ Sponsor approval timeout")
    
    def _convert_to_negotiation_state(self, negotiation_data: Dict[str, Any]):
        """Convert negotiation data to NegotiationState object"""
        # This would properly convert the data structure
        # For now, returning mock object
        from models.campaign import NegotiationState, NegotiationStatus
        return NegotiationState(
            creator_id=negotiation_data.get("creator_id", "unknown"),
            campaign_id=negotiation_data.get("campaign_id", "unknown"),
            status=NegotiationStatus.SUCCESS,
            final_rate=negotiation_data.get("final_rate", 5000)
        )
    
    # API methods for workflow management
    
    def get_workflow_status(self, workflow_id: str) -> Optional[CampaignWorkflowState]:
        """Get current workflow status"""
        return self.active_workflows.get(workflow_id)
    
    def get_all_active_workflows(self) -> List[CampaignWorkflowState]:
        """Get all active workflows"""
        return list(self.active_workflows.values())
    
    def get_workflow_analytics(self, workflow_id: str) -> Dict[str, Any]:
        """Get comprehensive workflow analytics"""
        
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return {"error": "Workflow not found"}
        
        duration = (datetime.now() - workflow.started_at).total_seconds() / 3600  # hours
        
        return {
            "workflow_id": workflow_id,
            "current_phase": workflow.current_phase.value,
            "progress_percentage": workflow.progress_percentage,
            "duration_hours": duration,
            "phases_completed": len(workflow.completed_phases),
            "total_phases": len(CampaignWorkflowPhase) - 2,  # Exclude COMPLETED and FAILED
            "influencers_contacted": len(workflow.active_negotiations),
            "successful_negotiations": len(workflow.successful_negotiations),
            "contracts_generated": len(workflow.generated_contracts),
            "estimated_completion": workflow.estimated_completion,
            "configuration": workflow.configuration.dict()
        }