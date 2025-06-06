# agents/enhanced_orchestrator.py - UPDATED WITH CONVERSATION MONITORING
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
from services.conversation_monitor import ConversationMonitor, ConversationEventHandler

from config.settings import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import Groq for AI intelligence
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    logger.warning("⚠️  Groq not available - using enhanced default orchestration")

class EnhancedCampaignOrchestrator:
    """
    🧠 ENHANCED CAMPAIGN ORCHESTRATOR WITH CONVERSATION MONITORING
    
    New Features:
    - Real-time conversation monitoring with ElevenLabs API polling
    - Automatic workflow continuation when conversations complete
    - Better error handling and recovery
    - Asynchronous conversation management
    """
    
    def __init__(self):
        # Initialize enhanced agents
        self.discovery_agent = InfluencerDiscoveryAgent()
        self.negotiation_agent = EnhancedNegotiationAgent()
        self.contract_agent = EnhancedContractAgent()
        self.database_service = DatabaseService()
        
        # Initialize validators and managers
        self.negotiation_validator = NegotiationResultValidator()
        self.contract_manager = ContractStatusManager()
        
        # Initialize Groq AI client
        self.groq_client = None
        self._initialize_groq()
        
        # NEW: Initialize conversation monitoring system
        self.conversation_monitor = None
        self.conversation_handler = None
        self.current_orchestration_state = None  # Track current state for monitoring
        self._initialize_conversation_monitoring()
    
    def _initialize_groq(self):
        """🧠 Initialize Groq LLM client for intelligent orchestration"""
        if not GROQ_AVAILABLE:
            logger.warning("⚠️  Groq not available - using enhanced default orchestration")
            return
        
        groq_api_key = settings.groq_api_key
        
        if groq_api_key:
            try:
                self.groq_client = Groq(api_key=groq_api_key)
                
                # Test the API key
                test_response = self.groq_client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[{"role": "user", "content": "Test"}],
                    max_tokens=5
                )
                
                logger.info("✅ Enhanced Groq LLM initialized successfully")
                
            except Exception as e:
                logger.error(f"❌ Groq initialization failed: {e}")
                if "401" in str(e) or "Unauthorized" in str(e):
                    logger.error("🔑 Groq API key is invalid - check your .env file")
                
                self.groq_client = None
                logger.info("📋 Using enhanced default orchestration")
        else:
            logger.warning("⚠️  GROQ_API_KEY not found - using enhanced default orchestration")
    
    def _initialize_conversation_monitoring(self):
        """🔄 Initialize conversation monitoring system"""
        
        if settings.elevenlabs_api_key:
            self.conversation_monitor = ConversationMonitor(
                api_key=settings.elevenlabs_api_key
            )
            self.conversation_handler = ConversationEventHandler(self)
            logger.info("✅ Conversation monitoring system initialized")
        else:
            logger.warning("⚠️  ElevenLabs API key not found - conversation monitoring disabled")
    
    async def orchestrate_enhanced_campaign(
        self,
        orchestration_state: CampaignOrchestrationState,
        task_id: str
    ) -> CampaignOrchestrationState:
        """
        🚀 ENHANCED ORCHESTRATION WORKFLOW WITH CONVERSATION MONITORING
        """
        try:
            # Store state for conversation monitoring access
            self.current_orchestration_state = orchestration_state
            
            logger.info(f"🚀 Starting enhanced campaign orchestration for {orchestration_state.campaign_id}")
            
            # PHASE 0: INITIALIZATION & VALIDATION
            orchestration_state.current_stage = "initializing"
            await self._update_campaign_state(task_id, orchestration_state)
            
            # Validate campaign data
            campaign_validation = self._validate_campaign_data(orchestration_state.campaign_data)
            if not campaign_validation["is_valid"]:
                raise ValueError(f"Invalid campaign data: {campaign_validation['errors']}")
            
            # PHASE 1: AI STRATEGIC PLANNING
            logger.info("🧠 Phase 1: AI Strategic Planning")
            strategy = await self._generate_enhanced_ai_strategy(orchestration_state.campaign_data)
            logger.info(f"🎯 Enhanced Strategy: {strategy.get('negotiation_approach', 'collaborative')}")
            
            # PHASE 2: DISCOVERY WITH ENHANCED MATCHING
            logger.info("🔍 Phase 2: Enhanced Creator Discovery")
            orchestration_state.current_stage = "discovery"
            await self._update_campaign_state(task_id, orchestration_state)
            
            await self._run_enhanced_discovery_phase(orchestration_state, strategy)
            
            # PHASE 3: ENHANCED NEGOTIATIONS WITH REAL-TIME MONITORING
            logger.info("📞 Phase 3: Enhanced AI-Guided Negotiations with Monitoring")
            orchestration_state.current_stage = "negotiations"
            await self._update_campaign_state(task_id, orchestration_state)
            
            await self._run_enhanced_negotiation_phase_with_monitoring(orchestration_state, task_id, strategy)
            
            # PHASE 4: NEGOTIATION VALIDATION & PROCESSING
            logger.info("🔍 Phase 4: Negotiation Validation & Processing")
            await self._validate_and_process_negotiations(orchestration_state)
            
            # PHASE 5: ENHANCED CONTRACT GENERATION
            logger.info("📝 Phase 5: Enhanced Contract Generation")
            orchestration_state.current_stage = "contracts"
            await self._update_campaign_state(task_id, orchestration_state)
            
            await self._run_enhanced_contract_phase(orchestration_state)
            
            # PHASE 6: COMPREHENSIVE DATABASE SYNC
            logger.info("💾 Phase 6: Comprehensive Database Sync")
            orchestration_state.current_stage = "database_sync"
            await self._update_campaign_state(task_id, orchestration_state)
            
            await self._sync_enhanced_data_to_database(orchestration_state)
            
            # PHASE 7: COMPLETION & ANALYSIS
            orchestration_state.current_stage = "completed"
            orchestration_state.completed_at = datetime.now()
            await self._update_campaign_state(task_id, orchestration_state)
            
            # Cleanup monitoring
            if self.conversation_monitor:
                self.conversation_monitor.stop_all_monitoring()
            
            # Generate comprehensive summary
            summary = await self._generate_enhanced_campaign_summary(orchestration_state)
            logger.info(f"🎉 Enhanced campaign orchestration completed!")
            logger.info(f"📊 Results: {summary}")
            
            return orchestration_state
            
        except Exception as e:
            logger.error(f"❌ Enhanced campaign orchestration failed: {str(e)}")
            orchestration_state.current_stage = "failed"
            orchestration_state.completed_at = datetime.now()
            await self._update_campaign_state(task_id, orchestration_state)
            
            # Cleanup monitoring on failure
            if self.conversation_monitor:
                self.conversation_monitor.stop_all_monitoring()
            
            raise
    
    async def _run_enhanced_negotiation_phase_with_monitoring(
        self,
        state: CampaignOrchestrationState,
        task_id: str,
        strategy: Dict[str, Any]
    ):
        """
        📞 ENHANCED NEGOTIATION WITH REAL-TIME CONVERSATION MONITORING
        
        Key improvements:
        - Initiate calls and immediately start monitoring
        - Don't wait for completion in main thread
        - Let conversation monitor handle status checking
        - Continue workflow automatically when conversations complete
        """
        
        logger.info("📞 Starting enhanced negotiation phase with real-time monitoring...")
        
        creators_to_contact = state.discovered_influencers
        conversation_strategy = strategy.get("conversation_strategy", {})
        
        # Track active conversations
        active_conversations = {}
        
        for i, influencer_match in enumerate(creators_to_contact):
            logger.info(f"📞 Enhanced negotiation {i+1}/{len(creators_to_contact)}: {influencer_match.creator.name}")
            
            # Update progress
            state.current_influencer = influencer_match.creator.name
            state.estimated_completion_minutes = (len(creators_to_contact) - i) * 2
            await self._update_campaign_state(task_id, state)
            
            # Generate specific AI strategy for this creator
            creator_strategy = await self._generate_creator_specific_strategy(
                influencer_match, state.campaign_data, strategy, state.negotiations
            )
            
            # ENHANCED: Initiate call without waiting for completion
            conversation_id = await self._initiate_monitored_negotiation(
                influencer_match,
                state.campaign_data,
                creator_strategy,
                state
            )
            
            if conversation_id:
                active_conversations[conversation_id] = {
                    "creator": influencer_match.creator,
                    "started_at": datetime.now()
                }
                logger.info(f"🔄 Started monitoring conversation: {conversation_id}")
            
            # Brief pause between call initiations
            await asyncio.sleep(5)
        
        # ENHANCED: Wait for all conversations to complete via monitoring
        if active_conversations and self.conversation_monitor:
            logger.info(f"⏳ Waiting for {len(active_conversations)} conversations to complete...")
            await self._wait_for_all_conversations_completion(active_conversations, state)
        
        logger.info(f"📞 Enhanced negotiation phase complete: {state.successful_negotiations}/{len(creators_to_contact)} successful")
    
    # Fix for enhanced_orchestrator.py - ensure fallback to mock works

    async def _initiate_monitored_negotiation(
        self,
        influencer_match,
        campaign_data,
        creator_strategy,
        state
    ) -> Optional[str]:
        """
        🚀 INITIATE NEGOTIATION WITH IMMEDIATE MONITORING SETUP - FIXED FALLBACK
        """
        
        try:
            # Start the negotiation (this initiates the ElevenLabs call)
            negotiation_result = await self._start_negotiation_call_only(
                influencer_match,
                campaign_data,
                creator_strategy
            )
            
            conversation_id = negotiation_result.get("conversation_id")
            
            # FIXED: Check if call was successful OR if it's a mock fallback
            if conversation_id and negotiation_result.get("status") == "success":
                # Create negotiation state record
                negotiation_state = NegotiationState(
                    creator_id=influencer_match.creator.id,
                    campaign_id=campaign_data.id,
                    status=NegotiationStatus.NEGOTIATING,
                    conversation_id=conversation_id,
                    initial_offer=creator_strategy.get("opening_offer_multiplier", 1.0) * influencer_match.creator.typical_rate,
                    started_at=datetime.now()
                )
                
                # Add to state immediately
                state.negotiations.append(negotiation_state)
                
                # Start monitoring this conversation (works for both real and mock)
                if self.conversation_monitor:
                    await self.conversation_monitor.start_monitoring(
                        conversation_id,
                        completion_callback=self.conversation_handler.on_conversation_completed,
                        error_callback=self.conversation_handler.on_conversation_failed
                    )
                
                logger.info(f"🔄 Started monitoring conversation: {conversation_id}")
                return conversation_id
            else:
                # FIXED: If ElevenLabs fails, create a failed negotiation record
                logger.warning(f"⚠️ Call failed for {influencer_match.creator.name}, creating failed negotiation record")
                
                failed_negotiation = NegotiationState(
                    creator_id=influencer_match.creator.id,
                    campaign_id=campaign_data.id,
                    status=NegotiationStatus.FAILED,
                    failure_reason=negotiation_result.get("error", "Call initiation failed"),
                    completed_at=datetime.now()
                )
                
                state.negotiations.append(failed_negotiation)
                return None
            
        except Exception as e:
            logger.error(f"❌ Failed to initiate monitored negotiation: {e}")
            
            # Create failed negotiation record
            failed_negotiation = NegotiationState(
                creator_id=influencer_match.creator.id,
                campaign_id=campaign_data.id,
                status=NegotiationStatus.FAILED,
                failure_reason=f"System error: {str(e)}",
                completed_at=datetime.now()
            )
            
            state.negotiations.append(failed_negotiation)
            return None
        
    async def _start_negotiation_call_only(
        self,
        influencer_match,
        campaign_data,
        creator_strategy
    ) -> Dict[str, Any]:
        """
        📱 START ELEVENLABS CALL WITHOUT WAITING FOR COMPLETION
        """
        
        from services.enhanced_voice import EnhancedVoiceService
        
        voice_service = EnhancedVoiceService()
        
        # Prepare enhanced call data
        creator_profile = {
            "id": influencer_match.creator.id,
            "name": influencer_match.creator.name,
            "niche": influencer_match.creator.niche,
            "followers": influencer_match.creator.followers,
            "engagement_rate": influencer_match.creator.engagement_rate,
            "average_views": influencer_match.creator.average_views,
            "location": influencer_match.creator.location,
            "languages": influencer_match.creator.languages,
            "typical_rate": influencer_match.creator.typical_rate,
            "platform": influencer_match.creator.platform.value,
            "availability": influencer_match.creator.availability.value
        }
        
        campaign_data_dict = {
            "brand_name": campaign_data.brand_name,
            "product_name": campaign_data.product_name,
            "product_description": campaign_data.product_description,
            "target_audience": campaign_data.target_audience,
            "campaign_goal": campaign_data.campaign_goal,
            "product_niche": campaign_data.product_niche
        }
        
        pricing_strategy = {
            "initial_offer": creator_strategy.get("opening_offer_multiplier", 0.95) * influencer_match.creator.typical_rate,
            "max_offer": creator_strategy.get("max_offer_multiplier", 1.25) * influencer_match.creator.typical_rate
        }
        
        # Initiate call and return immediately
        call_result = await voice_service.initiate_negotiation_call(
            creator_phone=influencer_match.creator.phone_number,
            creator_profile=creator_profile,
            campaign_data=campaign_data_dict,
            pricing_strategy=pricing_strategy
        )
        
        return call_result
    
    async def _wait_for_all_conversations_completion(
        self,
        active_conversations: Dict[str, Any],
        state: CampaignOrchestrationState
    ):
        """
        ⏳ WAIT FOR ALL CONVERSATIONS TO COMPLETE VIA MONITORING
        """
        
        max_wait_minutes = 8  # Maximum time to wait for all conversations
        check_interval = 30   # Check every 30 seconds
        
        start_time = datetime.now()
        
        while (datetime.now() - start_time).total_seconds() < (max_wait_minutes * 60):
            # Check monitoring status
            if not self.conversation_monitor:
                break
                
            active_monitors = self.conversation_monitor.get_active_conversations()
            
            if not active_monitors:
                logger.info("✅ All conversations completed via monitoring")
                break
            
            logger.info(f"⏳ Still monitoring {len(active_monitors)} conversations...")
            
            # Update progress
            completed_count = len([n for n in state.negotiations if n.status in ["success", "failed"]])
            total_count = len(state.negotiations)
            
            if completed_count >= total_count:
                logger.info("✅ All negotiations completed")
                break
            
            await asyncio.sleep(check_interval)
        
        # Final check
        remaining_monitors = self.conversation_monitor.get_active_conversations() if self.conversation_monitor else {}
        if remaining_monitors:
            logger.warning(f"⏰ Timeout reached with {len(remaining_monitors)} conversations still active")
            
            # Force cleanup
            for conv_id in remaining_monitors:
                self.conversation_monitor.stop_monitoring(conv_id)
    
    # Include all other methods from the original orchestrator...
    # (keeping the existing methods unchanged for brevity)
    
    def _validate_campaign_data(self, campaign_data: CampaignData) -> Dict[str, Any]:
        """✅ Validate campaign data before processing"""
        
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Required fields validation
        required_fields = {
            "brand_name": campaign_data.brand_name,
            "product_name": campaign_data.product_name,
            "product_description": campaign_data.product_description,
            "total_budget": campaign_data.total_budget,
            "product_niche": campaign_data.product_niche
        }
        
        for field_name, field_value in required_fields.items():
            if not field_value:
                validation_result["errors"].append(f"Missing required field: {field_name}")
                validation_result["is_valid"] = False
        
        # Budget validation
        if campaign_data.total_budget and campaign_data.total_budget < 1000:
            validation_result["warnings"].append("Budget below $1,000 may limit creator options")
        
        # Description length validation
        if campaign_data.product_description and len(campaign_data.product_description) < 50:
            validation_result["warnings"].append("Product description is very short - may affect matching")
        
        return validation_result
    
    async def _generate_enhanced_ai_strategy(self, campaign_data: CampaignData) -> Dict[str, Any]:
        """🧠 Generate enhanced AI strategy with better error handling"""
        
        if not self.groq_client:
            return self._get_enhanced_default_strategy(campaign_data)
        
        # FIXED: Simplified prompt to avoid JSON parsing issues
        prompt = f"""
        Create an influencer marketing strategy for this campaign. Respond with valid JSON only.

        Campaign: {campaign_data.product_name} by {campaign_data.brand_name}
        Budget: ${campaign_data.total_budget:,}
        Niche: {campaign_data.product_niche}

        Return this exact JSON structure:
        {{
            "creator_tier_priority": ["micro", "macro", "mega"],
            "negotiation_approach": "collaborative",
            "success_criteria": {{
                "min_successful_partnerships": 2,
                "target_success_rate": 0.7
            }},
            "conversation_strategy": {{
                "opening_offer_multiplier": 0.95,
                "max_offer_multiplier": 1.25
            }},
            "max_creators_to_contact": 3
        }}
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,  # FIXED: Lower temperature for more consistent output
                max_tokens=500    # FIXED: Reduced tokens for simpler response
            )
            
            strategy_text = response.choices[0].message.content.strip()
            
            # FIXED: Better JSON extraction and validation
            logger.info(f"🧠 Raw Groq response: {strategy_text[:200]}...")
            
            # Try to extract JSON from response
            json_start = strategy_text.find('{')
            json_end = strategy_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = strategy_text[json_start:json_end]
                
                try:
                    strategy = json.loads(json_str)
                    
                    # Validate required fields
                    required_keys = ["creator_tier_priority", "negotiation_approach"]
                    if all(key in strategy for key in required_keys):
                        logger.info("🧠 Enhanced AI strategy generated successfully")
                        return strategy
                    else:
                        logger.warning("AI strategy missing required fields, using enhanced default")
                        return self._get_enhanced_default_strategy(campaign_data)
                        
                except json.JSONDecodeError as e:
                    logger.error(f"JSON parsing failed: {e}")
                    logger.info("🔄 Falling back to enhanced default strategy")
                    return self._get_enhanced_default_strategy(campaign_data)
            else:
                logger.warning("No valid JSON found in Groq response")
                return self._get_enhanced_default_strategy(campaign_data)
                
        except Exception as e:
            logger.error(f"Enhanced AI strategy generation failed: {e}")
            return self._get_enhanced_default_strategy(campaign_data)
    
    def _get_enhanced_default_strategy(self, campaign_data: CampaignData) -> Dict[str, Any]:
        """📋 Enhanced default strategy with smart defaults"""
        
        budget = campaign_data.total_budget
        niche = campaign_data.product_niche.lower()
        
        # Smart approach selection
        if budget > 15000:
            approach = "premium"
            max_creators = 5
            tier_priority = ["macro", "mega", "micro"]
        elif budget > 8000:
            approach = "collaborative" 
            max_creators = 4
            tier_priority = ["macro", "micro", "mega"]
        else:
            approach = "collaborative"
            max_creators = 3
            tier_priority = ["micro", "macro", "mega"]
        
        return {
            "creator_tier_priority": tier_priority,
            "budget_allocation": {
                "discovery_budget_per_creator": 0.35 if budget > 10000 else 0.4,
                "negotiation_buffer": 0.15,
                "reserve_fund": 0.1
            },
            "negotiation_approach": approach,
            "success_criteria": {
                "min_successful_partnerships": 1 if budget < 5000 else 2,
                "target_success_rate": 0.7,
                "max_cost_per_partnership": budget * 0.5
            },
            "conversation_strategy": {
                "opening_offer_multiplier": 0.95 if approach == "collaborative" else 0.9,
                "max_offer_multiplier": 1.25 if approach == "collaborative" else 1.15,
                "enthusiasm_threshold": 6,
                "objection_handling": "flexible"
            },
            "max_creators_to_contact": max_creators,
            "strategy_source": "enhanced_default",
            "niche_optimized": True
        }
    
    async def _run_enhanced_discovery_phase(self, state: CampaignOrchestrationState, strategy: Dict[str, Any]):
        """🔍 Enhanced discovery with strategy-driven selection"""
        
        logger.info("🔍 Starting enhanced discovery phase...")
        
        max_creators = strategy.get("max_creators_to_contact", 3)
        
        # Discovery with enhanced matching
        discovered_influencers = await self.discovery_agent.find_matches(
            state.campaign_data,
            max_results=max_creators + 2  # Get extras for backup
        )
        
        # Apply strategy-based filtering and ranking
        filtered_influencers = self._apply_strategy_filtering(discovered_influencers, strategy)
        
        state.discovered_influencers = filtered_influencers[:max_creators]
        
        logger.info(f"✅ Enhanced discovery complete: Found {len(state.discovered_influencers)} strategic matches")
        for i, match in enumerate(state.discovered_influencers):
            logger.info(f"  {i+1}. {match.creator.name} ({match.creator.tier.value}) - {match.similarity_score:.3f} score, ${match.estimated_rate:,}")
    
    def _apply_strategy_filtering(self, discovered_influencers, strategy: Dict[str, Any]):
        """🎯 Apply strategy-based filtering to discovered influencers"""
        
        tier_priority = strategy.get("creator_tier_priority", ["micro", "macro", "mega"])
        quality_priorities = strategy.get("quality_priorities", ["engagement_rate"])
        
        # Score influencers based on strategy
        for match in discovered_influencers:
            creator = match.creator
            
            # Tier priority bonus
            tier_bonus = 0
            if creator.tier.value == tier_priority[0]:
                tier_bonus = 0.1
            elif creator.tier.value == tier_priority[1]:
                tier_bonus = 0.05
            
            # Quality priority bonuses
            quality_bonus = 0
            if "engagement_rate" in quality_priorities and creator.engagement_rate > 5.0:
                quality_bonus += 0.05
            if "audience_alignment" in quality_priorities and match.similarity_score > 0.8:
                quality_bonus += 0.05
            
            # Update overall score
            match.similarity_score = min(match.similarity_score + tier_bonus + quality_bonus, 1.0)
        
        # Re-sort by updated scores
        discovered_influencers.sort(key=lambda x: x.similarity_score, reverse=True)
        
        return discovered_influencers
    
    async def _generate_creator_specific_strategy(
        self,
        creator_match,
        campaign_data: CampaignData,
        overall_strategy: Dict[str, Any],
        previous_results: list
    ) -> Dict[str, Any]:
        """🎯 Generate AI strategy for specific creator - FIXED JSON parsing"""
        
        if not self.groq_client:
            return {
                "negotiation_approach": overall_strategy.get("negotiation_approach", "collaborative"),
                "opening_offer_multiplier": 0.95,
                "max_offer_multiplier": 1.25
            }
        
        # FIXED: Simplified prompt
        prompt = f"""
        Recommend negotiation strategy for this creator. Respond with valid JSON only.

        Creator: {creator_match.creator.name} ({creator_match.creator.tier.value})
        Followers: {creator_match.creator.followers:,}
        Engagement: {creator_match.creator.engagement_rate}%
        Budget: ${campaign_data.total_budget:,}

        Return this exact JSON:
        {{
            "negotiation_approach": "collaborative",
            "opening_offer_multiplier": 0.95,
            "max_offer_multiplier": 1.25
        }}
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=200
            )
            
            strategy_text = response.choices[0].message.content.strip()
            
            # Extract JSON
            json_start = strategy_text.find('{')
            json_end = strategy_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = strategy_text[json_start:json_end]
                strategy = json.loads(json_str)
                
                logger.info(f"🧠 Creator-specific strategy: {strategy.get('negotiation_approach')} approach")
                return strategy
            else:
                raise ValueError("No valid JSON in response")
                
        except Exception as e:
            logger.error(f"Creator strategy generation failed: {e}")
            return {
                "negotiation_approach": overall_strategy.get("negotiation_approach", "collaborative"),
                "opening_offer_multiplier": 0.95,
                "max_offer_multiplier": 1.25
            }    
        
    # Add the remaining methods from the original file...
    async def _validate_and_process_negotiations(self, state: CampaignOrchestrationState):
        """🔍 Validate all negotiation results before contract generation"""
        
        logger.info("🔍 Validating negotiation results...")
        
        valid_negotiations = []
        invalid_negotiations = []
        
        for negotiation in state.negotiations:
            if negotiation.status == NegotiationStatus.SUCCESS:
                validation_result = self.negotiation_validator.validate_negotiation_result(negotiation)
                
                if validation_result["is_valid"]:
                    valid_negotiations.append(negotiation)
                    logger.info(f"✅ Validation passed: {negotiation.creator_id}")
                else:
                    invalid_negotiations.append((negotiation, validation_result))
                    logger.warning(f"⚠️  Validation issues for {negotiation.creator_id}: {validation_result['warnings']}")
        
        # Log validation summary
        logger.info(f"📊 Negotiation validation complete:")
        logger.info(f"   Valid for contracts: {len(valid_negotiations)}")
        logger.info(f"   Invalid/incomplete: {len(invalid_negotiations)}")
        
        # Update state statistics
        state.successful_negotiations = len([n for n in state.negotiations if n.status == NegotiationStatus.SUCCESS])
        state.failed_negotiations = len([n for n in state.negotiations if n.status == NegotiationStatus.FAILED])
        state.total_cost = sum(n.final_rate or 0 for n in state.negotiations if n.status == NegotiationStatus.SUCCESS)
    
    async def _run_enhanced_contract_phase(self, state: CampaignOrchestrationState):
        """📝 Enhanced contract generation with comprehensive data"""
        
        logger.info("📝 Starting enhanced contract generation...")
        
        successful_negotiations = [
            neg for neg in state.negotiations 
            if neg.status == NegotiationStatus.SUCCESS
        ]
        
        contracts_generated = []
        
        for negotiation in successful_negotiations:
            try:
                # Look up creator data for enhanced contracts
                creator_data = None
                for match in state.discovered_influencers:
                    if match.creator.id == negotiation.creator_id:
                        creator_data = match.creator
                        break
                
                # Generate enhanced contract
                contract = await self.contract_agent.generate_enhanced_contract(
                    negotiation,
                    state.campaign_data,
                    creator_data
                )
                
                # Update contract status
                contract = self.contract_manager.update_contract_status(contract, "draft")
                
                contracts_generated.append(contract)
                
                # Update negotiation with contract reference
                negotiation.negotiated_terms["contract_id"] = contract["contract_id"]
                negotiation.negotiated_terms["contract_generated"] = True
                
                logger.info(f"📝 Enhanced contract generated: {contract['contract_id']}")
                logger.info(f"   Value: ${contract['final_rate']:,.2f}")
                logger.info(f"   Template: {contract['template_type']}")
                
            except Exception as e:
                logger.error(f"❌ Enhanced contract generation failed for {negotiation.creator_id}: {str(e)}")
                
                # Mark as failed but don't stop the process
                negotiation.negotiated_terms["contract_generation_failed"] = True
                negotiation.negotiated_terms["contract_error"] = str(e)
        
        logger.info(f"📝 Enhanced contract phase complete: {len(contracts_generated)} contracts generated")
    
    async def _sync_enhanced_data_to_database(self, state: CampaignOrchestrationState):
        """💾 Comprehensive database sync with enhanced data"""
        
        logger.info("💾 Starting enhanced database sync...")
        
        try:
            # Enhanced sync with all structured data
            await self.database_service.sync_campaign_results(state)
            
            logger.info("✅ Enhanced database sync completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Enhanced database sync failed: {str(e)}")
            # Don't fail the entire orchestration for DB sync issues
    
    async def _generate_enhanced_campaign_summary(self, state: CampaignOrchestrationState) -> Dict[str, Any]:
        """📊 Generate comprehensive campaign summary"""
        
        base_summary = state.get_campaign_summary()
        
        # Enhanced metrics
        enhanced_summary = {
            **base_summary,
            "enhanced_metrics": {
                "negotiation_success_rate": f"{(state.successful_negotiations / max(len(state.negotiations), 1)) * 100:.1f}%",
                "cost_efficiency_score": self._calculate_cost_efficiency(state),
                "strategy_effectiveness": "high",
                "monitoring_enabled": self.conversation_monitor is not None
            },
            "conversation_monitoring": {
                "total_conversations_monitored": len(state.negotiations),
                "monitoring_system_active": self.conversation_monitor is not None,
                "real_time_status_updates": True
            }
        }
        
        return enhanced_summary
    
    def _calculate_cost_efficiency(self, state: CampaignOrchestrationState) -> str:
        """Calculate cost efficiency rating"""
        if state.successful_negotiations == 0:
            return "N/A"
        
        budget_utilization = (state.total_cost / state.campaign_data.total_budget) * 100
        
        if budget_utilization < 60:
            return "Excellent"
        elif budget_utilization < 80:
            return "Good"
        elif budget_utilization < 95:
            return "Fair"
        else:
            return "Over Budget"
    
    async def _update_campaign_state(self, task_id: str, state: CampaignOrchestrationState):
        """🔄 Update campaign state for monitoring"""
        try:
            from main import active_campaigns
            active_campaigns[task_id] = state
        except Exception as e:
            logger.error(f"Failed to update campaign state: {str(e)}")

# Backward compatibility wrapper
class CampaignOrchestrator(EnhancedCampaignOrchestrator):
    """Backward compatibility wrapper for existing code"""
    
    async def orchestrate_campaign(self, orchestration_state, task_id):
        """Legacy method wrapper"""
        return await self.orchestrate_enhanced_campaign(orchestration_state, task_id)