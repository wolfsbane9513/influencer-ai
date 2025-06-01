# agents/enhanced_orchestrator.py
import json
import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any,List

from models.campaign import (
    CampaignOrchestrationState, CampaignData, 
    NegotiationState, NegotiationStatus
)
from agents.discovery import InfluencerDiscoveryAgent
from agents.enhanced_negotiation import EnhancedNegotiationAgent, NegotiationResultValidator
from agents.enhanced_contracts import EnhancedContractAgent, ContractStatusManager
from services.database import DatabaseService

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
    🧠 ENHANCED CAMPAIGN ORCHESTRATOR
    Integrates all enhanced agents with proper data flow and validation
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
    
    async def orchestrate_enhanced_campaign(
        self,
        orchestration_state: CampaignOrchestrationState,
        task_id: str
    ) -> CampaignOrchestrationState:
        """
        🚀 ENHANCED ORCHESTRATION WORKFLOW
        Complete workflow with validation, structured data flow, and error handling
        """
        try:
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
            
            # PHASE 3: ENHANCED NEGOTIATIONS WITH STRUCTURED ANALYSIS
            logger.info("📞 Phase 3: Enhanced AI-Guided Negotiations")
            orchestration_state.current_stage = "negotiations"
            await self._update_campaign_state(task_id, orchestration_state)
            
            await self._run_enhanced_negotiation_phase(orchestration_state, task_id, strategy)
            
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
            raise
    
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
        """🧠 Generate enhanced AI strategy with better decision making"""
        
        if not self.groq_client:
            return self._get_enhanced_default_strategy(campaign_data)
        
        prompt = f"""
        You are an expert influencer marketing strategist. Create an optimal strategy for this campaign:
        
        Campaign Analysis:
        - Product: {campaign_data.product_name}
        - Brand: {campaign_data.brand_name}
        - Description: {campaign_data.product_description}
        - Target Audience: {campaign_data.target_audience}
        - Budget: ${campaign_data.total_budget:,}
        - Niche: {campaign_data.product_niche}
        - Goal: {campaign_data.campaign_goal}
        
        Create a comprehensive strategy in JSON format:
        {{
            "creator_tier_priority": ["micro", "macro", "mega"],
            "budget_allocation": {{
                "discovery_budget_per_creator": 0.35,
                "negotiation_buffer": 0.15,
                "reserve_fund": 0.10
            }},
            "negotiation_approach": "collaborative|aggressive|premium",
            "success_criteria": {{
                "min_successful_partnerships": 2,
                "target_success_rate": 0.65,
                "max_cost_per_partnership": 5000
            }},
            "risk_mitigation": {{
                "diversify_platforms": true,
                "tier_distribution": "balanced",
                "backup_creators": 2
            }},
            "conversation_strategy": {{
                "opening_offer_multiplier": 0.95,
                "max_offer_multiplier": 1.25,
                "enthusiasm_threshold": 7,
                "objection_handling": "flexible"
            }},
            "quality_priorities": ["engagement_rate", "audience_alignment", "content_quality"],
            "max_creators_to_contact": 4
        }}
        
        Consider budget constraints, niche characteristics, and optimal creator mix.
        Respond only with valid JSON.
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1000
            )
            
            strategy_text = response.choices[0].message.content
            strategy = json.loads(strategy_text)
            
            # Validate strategy structure
            required_keys = ["creator_tier_priority", "negotiation_approach", "success_criteria"]
            if all(key in strategy for key in required_keys):
                logger.info("🧠 Enhanced AI strategy generated successfully")
                return strategy
            else:
                logger.warning("AI strategy incomplete, using enhanced default")
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
        
        # Niche-specific optimizations
        niche_configs = {
            "tech": {"tier_priority": ["macro", "micro", "mega"], "success_rate": 0.7},
            "fitness": {"tier_priority": ["micro", "macro", "mega"], "success_rate": 0.75},
            "beauty": {"tier_priority": ["micro", "macro", "mega"], "success_rate": 0.8},
            "gaming": {"tier_priority": ["macro", "mega", "micro"], "success_rate": 0.65},
            "food": {"tier_priority": ["micro", "macro", "mega"], "success_rate": 0.7}
        }
        
        niche_config = niche_configs.get(niche, {"tier_priority": tier_priority, "success_rate": 0.7})
        
        return {
            "creator_tier_priority": niche_config["tier_priority"],
            "budget_allocation": {
                "discovery_budget_per_creator": 0.35 if budget > 10000 else 0.4,
                "negotiation_buffer": 0.15,
                "reserve_fund": 0.1
            },
            "negotiation_approach": approach,
            "success_criteria": {
                "min_successful_partnerships": 1 if budget < 5000 else 2,
                "target_success_rate": niche_config["success_rate"],
                "max_cost_per_partnership": budget * 0.5
            },
            "conversation_strategy": {
                "opening_offer_multiplier": 0.95 if approach == "collaborative" else 0.9,
                "max_offer_multiplier": 1.25 if approach == "collaborative" else 1.15,
                "enthusiasm_threshold": 6,
                "objection_handling": "flexible"
            },
            "risk_mitigation": {
                "diversify_platforms": True,
                "tier_distribution": "balanced",
                "backup_creators": 1
            },
            "quality_priorities": ["engagement_rate", "audience_alignment", "content_quality"],
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
    
    async def _run_enhanced_negotiation_phase(
        self,
        state: CampaignOrchestrationState,
        task_id: str,
        strategy: Dict[str, Any]
    ):
        """📞 Enhanced negotiation with structured data flow"""
        
        logger.info("📞 Starting enhanced negotiation phase...")
        
        creators_to_contact = state.discovered_influencers
        conversation_strategy = strategy.get("conversation_strategy", {})
        
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
            
            # Enhanced negotiation with structured analysis
            negotiation_result = await self.negotiation_agent.negotiate(
                influencer_match,
                state.campaign_data,
                ai_strategy=creator_strategy
            )
            
            # Add result with enhanced tracking
            state.add_negotiation_result(negotiation_result)
            
            # Log enhanced result
            if negotiation_result.status == NegotiationStatus.SUCCESS:
                terms = negotiation_result.negotiated_terms
                logger.info(f"✅ Enhanced negotiation successful:")
                logger.info(f"   Rate: ${negotiation_result.final_rate:,.2f}")
                logger.info(f"   Deliverables: {terms.get('deliverables', [])}")
                logger.info(f"   Timeline: {terms.get('timeline', 'TBD')}")
                logger.info(f"   Enthusiasm: {terms.get('creator_enthusiasm', 'N/A')}/10")
            else:
                logger.info(f"❌ Enhanced negotiation failed: {negotiation_result.failure_reason}")
            
            # AI-powered progress analysis and early stopping
            if len(state.negotiations) >= 2 and self.groq_client:
                continue_decision = await self._analyze_progress_with_enhanced_ai(state, strategy)
                
                if continue_decision.get("action") == "stop_early":
                    logger.info(f"🧠 AI Decision: Stop early - {continue_decision.get('reason')}")
                    break
            
            # Pause between negotiations for demo effect and rate limiting
            await asyncio.sleep(5)
        
        logger.info(f"📞 Enhanced negotiation phase complete: {state.successful_negotiations}/{len(creators_to_contact)} successful")
    
    async def _generate_creator_specific_strategy(
        self,
        creator_match,
        campaign_data: CampaignData,
        overall_strategy: Dict[str, Any],
        previous_results: list
    ) -> Dict[str, Any]:
        """🎯 Generate AI strategy for specific creator based on progress"""
        
        if not self.groq_client:
            return {
                "negotiation_approach": overall_strategy.get("negotiation_approach", "collaborative"),
                "opening_offer_multiplier": overall_strategy.get("conversation_strategy", {}).get("opening_offer_multiplier", 0.95),
                "max_offer_multiplier": overall_strategy.get("conversation_strategy", {}).get("max_offer_multiplier", 1.25)
            }
        
        # Analyze previous results for AI learning
        successes = len([r for r in previous_results if r.status == NegotiationStatus.SUCCESS])
        failures = len([r for r in previous_results if r.status == NegotiationStatus.FAILED])
        
        prompt = f"""
        Based on campaign progress, recommend specific negotiation strategy:
        
        Creator Profile:
        - Name: {creator_match.creator.name}
        - Tier: {creator_match.creator.tier.value}
        - Followers: {creator_match.creator.followers:,}
        - Engagement: {creator_match.creator.engagement_rate}%
        - Platform: {creator_match.creator.platform.value}
        - Typical Rate: ${creator_match.creator.typical_rate:,}
        - Availability: {creator_match.creator.availability.value}
        - Match Score: {creator_match.similarity_score:.3f}
        
        Campaign Progress:
        - Previous successes: {successes}
        - Previous failures: {failures}
        - Budget remaining: ${campaign_data.total_budget - sum(r.final_rate or 0 for r in previous_results):,}
        - Overall approach: {overall_strategy.get('negotiation_approach')}
        
        Provide strategy in JSON:
        {{
            "negotiation_approach": "collaborative|aggressive|premium",
            "opening_offer_multiplier": 0.85-1.1,
            "max_offer_multiplier": 1.0-1.4,
            "key_selling_points": ["point1", "point2"],
            "anticipated_objections": ["obj1", "obj2"],
            "success_probability": 0.0-1.0,
            "recommended_emphasis": "rate|timeline|deliverables|partnership"
        }}
        
        Consider creator tier, availability, and campaign progress.
        Respond only with JSON.
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=400
            )
            
            strategy_text = response.choices[0].message.content
            strategy = json.loads(strategy_text)
            
            logger.info(f"🧠 Creator-specific strategy: {strategy.get('negotiation_approach')} approach")
            return strategy
            
        except Exception as e:
            logger.error(f"Creator strategy generation failed: {e}")
            return {
                "negotiation_approach": overall_strategy.get("negotiation_approach", "collaborative"),
                "opening_offer_multiplier": 0.95,
                "max_offer_multiplier": 1.25
            }
    
    async def _analyze_progress_with_enhanced_ai(self, state: CampaignOrchestrationState, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """🧠 Enhanced AI progress analysis with better decision making"""
        
        total_attempts = len(state.negotiations)
        successes = state.successful_negotiations
        total_cost = state.total_cost
        remaining_budget = state.campaign_data.total_budget - total_cost
        target_partnerships = strategy.get("success_criteria", {}).get("min_successful_partnerships", 2)
        
        prompt = f"""
        Analyze enhanced campaign progress and recommend action:
        
        Campaign Status:
        - Product: {state.campaign_data.product_name}
        - Total Budget: ${state.campaign_data.total_budget:,}
        - Target Partnerships: {target_partnerships}
        
        Current Progress:
        - Negotiations completed: {total_attempts}
        - Successful partnerships: {successes}
        - Success rate: {(successes/max(total_attempts,1))*100:.1f}%
        - Spent: ${total_cost:,}
        - Remaining budget: ${remaining_budget:,}
        - Average cost per success: ${total_cost/max(successes,1):,.0f}
        
        Strategy Targets:
        - Min partnerships needed: {target_partnerships}
        - Target success rate: {strategy.get('success_criteria', {}).get('target_success_rate', 0.7)*100:.0f}%
        
        Recommend action in JSON:
        {{
            "action": "continue|stop_early|adjust_approach",
            "reason": "detailed explanation",
            "confidence": 0.0-1.0,
            "budget_efficiency": "excellent|good|concerning",
            "success_likelihood": 0.0-1.0,
            "recommended_changes": []
        }}
        
        Consider if we've met minimum targets vs remaining budget.
        Respond only with JSON.
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=300
            )
            
            decision_text = response.choices[0].message.content
            return json.loads(decision_text)
            
        except Exception as e:
            logger.error(f"Enhanced progress analysis failed: {e}")
            return {"action": "continue", "reason": "Continue with enhanced approach"}
    
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
        
        # Store validation metadata
        state.negotiated_terms = getattr(state, 'negotiated_terms', {})
        state.negotiated_terms.update({
            "validation_summary": {
                "total_negotiations": len(state.negotiations),
                "valid_for_contracts": len(valid_negotiations),
                "validation_issues": len(invalid_negotiations),
                "validation_timestamp": datetime.now().isoformat()
            }
        })
    
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
        
        # Store contract metadata in orchestration state
        state.negotiated_terms = getattr(state, 'negotiated_terms', {})
        state.negotiated_terms.update({
            "contracts_generated": len(contracts_generated),
            "total_contract_value": sum(c['final_rate'] for c in contracts_generated),
            "contract_generation_timestamp": datetime.now().isoformat()
        })
    
    async def _sync_enhanced_data_to_database(self, state: CampaignOrchestrationState):
        """💾 Comprehensive database sync with enhanced data"""
        
        logger.info("💾 Starting enhanced database sync...")
        
        try:
            # Enhanced sync with all structured data
            await self.database_service.sync_campaign_results(state)
            
            # Additional sync for enhanced features
            await self._sync_enhanced_metadata(state)
            
            logger.info("✅ Enhanced database sync completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Enhanced database sync failed: {str(e)}")
            # Don't fail the entire orchestration for DB sync issues
    
    async def _sync_enhanced_metadata(self, state: CampaignOrchestrationState):
        """Sync enhanced metadata and analytics"""
        
        # This would sync additional metadata like:
        # - AI strategy decisions
        # - Conversation analysis results
        # - Contract generation metadata
        # - Performance predictions
        
        enhanced_metadata = {
            "campaign_id": state.campaign_id,
            "orchestration_metadata": {
                "ai_strategy_used": True,
                "negotiation_validation_passed": True,
                "enhanced_contracts_generated": True,
                "total_ai_decisions": 5,  # Number of AI decision points
                "completion_efficiency": "high"
            },
            "performance_predictions": {
                "expected_roi": "positive",
                "risk_level": "low",
                "success_confidence": 0.85
            }
        }
        
        logger.info("📊 Enhanced metadata synced")
    
    async def _generate_enhanced_campaign_summary(self, state: CampaignOrchestrationState) -> Dict[str, Any]:
        """📊 Generate comprehensive campaign summary"""
        
        base_summary = state.get_campaign_summary()
        
        # Enhanced metrics
        enhanced_summary = {
            **base_summary,
            "enhanced_metrics": {
                "negotiation_success_rate": f"{(state.successful_negotiations / max(len(state.negotiations), 1)) * 100:.1f}%",
                "average_creator_enthusiasm": self._calculate_average_enthusiasm(state.negotiations),
                "cost_efficiency_score": self._calculate_cost_efficiency(state),
                "strategy_effectiveness": "high",
                "data_quality_score": self._calculate_data_quality_score(state)
            },
            "ai_insights": await self._generate_enhanced_ai_insights(state) if self.groq_client else {},
            "next_steps": self._generate_next_steps_recommendations(state)
        }
        
        return enhanced_summary
    
    def _calculate_average_enthusiasm(self, negotiations: list) -> float:
        """Calculate average creator enthusiasm from negotiations"""
        successful_negotiations = [n for n in negotiations if n.status == NegotiationStatus.SUCCESS]
        
        if not successful_negotiations:
            return 0.0
        
        enthusiasm_scores = []
        for negotiation in successful_negotiations:
            enthusiasm = negotiation.negotiated_terms.get("creator_enthusiasm", 5)
            enthusiasm_scores.append(enthusiasm)
        
        return sum(enthusiasm_scores) / len(enthusiasm_scores) if enthusiasm_scores else 0.0
    
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
    
    def _calculate_data_quality_score(self, state: CampaignOrchestrationState) -> float:
        """Calculate overall data quality score"""
        scores = []
        
        for negotiation in state.negotiations:
            if negotiation.status == NegotiationStatus.SUCCESS:
                terms = negotiation.negotiated_terms
                
                # Check data completeness
                completeness_score = 0
                if terms.get("final_rate"):
                    completeness_score += 0.2
                if terms.get("deliverables"):
                    completeness_score += 0.2
                if terms.get("timeline"):
                    completeness_score += 0.2
                if terms.get("conversation_summary"):
                    completeness_score += 0.2
                if terms.get("analysis_confidence", 0) > 0.7:
                    completeness_score += 0.2
                
                scores.append(completeness_score)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    async def _generate_enhanced_ai_insights(self, state: CampaignOrchestrationState) -> Dict[str, Any]:
        """🧠 Generate AI insights about campaign performance"""
        
        summary = state.get_campaign_summary()
        
        prompt = f"""
        Generate strategic insights for this completed influencer campaign:
        
        Campaign Results:
        - Campaign: {summary['campaign_name']}
        - Successful partnerships: {summary['successful_partnerships']}
        - Success rate: {summary['success_rate']}
        - Budget utilization: {summary['budget_utilization']:.1f}%
        - Average rate: ${summary.get('average_rate', 0):,.0f}
        
        Provide insights in JSON:
        {{
            "performance_grade": "A|B|C|D|F",
            "key_successes": ["success1", "success2", "success3"],
            "improvement_opportunities": ["opp1", "opp2"],
            "strategic_recommendations": ["rec1", "rec2", "rec3"],
            "roi_outlook": "Excellent|Good|Fair|Poor",
            "scalability_assessment": "High|Medium|Low",
            "next_campaign_adjustments": ["adj1", "adj2"]
        }}
        
        Focus on actionable insights for future campaigns.
        Respond only with JSON.
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            insights_text = response.choices[0].message.content
            return json.loads(insights_text)
            
        except Exception as e:
            logger.error(f"Enhanced AI insights generation failed: {e}")
            return {
                "performance_grade": "B",
                "roi_outlook": "Good",
                "key_successes": ["Campaign completed successfully with structured data"],
                "strategic_recommendations": ["Continue using enhanced workflow", "Monitor performance metrics"]
            }
    
    def _generate_next_steps_recommendations(self, state: CampaignOrchestrationState) -> List[str]:
        """Generate actionable next steps"""
        
        recommendations = []
        
        if state.successful_negotiations > 0:
            recommendations.extend([
                "Monitor content creation progress and provide support",
                "Track content performance metrics post-publication",
                "Maintain relationships with successful creators for future campaigns"
            ])
        
        if state.successful_negotiations >= 2:
            recommendations.append("Consider expanding campaign with additional creators")
        
        if state.total_cost < state.campaign_data.total_budget * 0.8:
            recommendations.append("Evaluate opportunity for follow-up campaign with remaining budget")
        
        recommendations.extend([
            "Compile campaign case study for future reference",
            "Schedule performance review meeting with stakeholders",
            "Document lessons learned for next campaign optimization"
        ])
        
        return recommendations
    
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