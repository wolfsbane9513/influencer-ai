import json
import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from models.campaign import CampaignOrchestrationState, CampaignData,NegotiationState, NegotiationStatus
from agents.discovery import InfluencerDiscoveryAgent
from agents.negotiation import NegotiationAgent
from agents.contracts import ContractAgent
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
    logger.warning("⚠️  Groq is not available - using simple orchestration")

class CampaignOrchestrator:
    """
    🧠 INTELLIGENT CAMPAIGN ORCHESTRATOR WITH FULL DATABASE INTEGRATION
    Master coordinator that manages the entire campaign workflow with AI decision making:
    Campaign → Discovery → Negotiation → Contracts → Database Sync (at every step)
    """
    
    def __init__(self):
        # Initialize all agents
        self.discovery_agent = InfluencerDiscoveryAgent()
        self.negotiation_agent = NegotiationAgent()
        self.contract_agent = ContractAgent()
        self.database_service = DatabaseService()
        
        # Initialize Groq AI client
        self.groq_client = None
        self._initialize_groq()
    
    def _initialize_groq(self):
        """🧠 Initialize Groq LLM client for intelligent orchestration"""
        if not GROQ_AVAILABLE:
            logger.warning("⚠️  Groq not available - using simple orchestration")
            return
        
        # ✅ FIX: Use settings object instead of os.getenv()
        groq_api_key = settings.groq_api_key
        
        if groq_api_key:
            try:
                self.groq_client = Groq(api_key=groq_api_key)
                
                # ✅ ENHANCED: Test the API key with a simple request
                test_response = self.groq_client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=10
                )
                
                logger.info("✅ Groq LLM initialized and tested successfully")
                
            except Exception as e:
                logger.error(f"❌ Groq initialization/test failed: {e}")
                
                # ✅ ENHANCED: Provide specific error guidance
                if "401" in str(e) or "Unauthorized" in str(e):
                    logger.error("🔑 Groq API key is invalid or expired")
                    logger.error("💡 Get a new key from: https://console.groq.com/keys")
                    logger.error("📝 Update your .env file: GROQ_API_KEY=gsk_your_new_key_here")
                elif "quota" in str(e).lower() or "limit" in str(e).lower():
                    logger.error("📊 Groq API quota exceeded or rate limited")
                else:
                    logger.error(f"🔧 Groq API error: {str(e)}")
                
                self.groq_client = None
                logger.info("📋 Continuing with simple orchestration (no AI strategy)")
        else:
            logger.warning("⚠️  GROQ_API_KEY not found in settings - using simple orchestration")
        
    async def orchestrate_campaign(
        self,
        orchestration_state: CampaignOrchestrationState,
        task_id: str
    ) -> CampaignOrchestrationState:
        """
        🚀 MAIN ORCHESTRATION WORKFLOW WITH DATABASE INTEGRATION
        Coordinates the entire campaign from start to finish with AI intelligence
        """
        try:
            logger.info(f"🚀 Starting campaign orchestration for {orchestration_state.campaign_id}")
            
            # *** STEP 0: Initialize database and create campaign record ***
            await self._initialize_database_and_create_campaign(orchestration_state)
            
            # Update state tracking
            orchestration_state.current_stage = "initializing"
            await self._update_active_campaign_state(task_id, orchestration_state)
            
            # 🧠 PHASE 0: AI STRATEGIC PLANNING (if Groq available)
            if self.groq_client:
                strategy = await self._generate_ai_strategy(orchestration_state.campaign_data)
                logger.info(f"🎯 AI Strategy Generated: {strategy.get('negotiation_approach', 'collaborative')}")
                
                # *** Store strategy in database ***
                await self._store_strategy_in_database(orchestration_state, strategy)
            else:
                strategy = self._get_default_strategy()
                logger.info("📋 Using default strategy (Groq not available)")
            
            # PHASE 1: DISCOVERY (with immediate database storage)
            logger.info("🔍 Phase 1: Creator Discovery")
            orchestration_state.current_stage = "discovery"
            await self._update_active_campaign_state(task_id, orchestration_state)
            
            await self._run_discovery_phase_with_db(orchestration_state, strategy)
            
            # PHASE 2: NEGOTIATIONS (with real-time database updates)
            logger.info("📞 Phase 2: AI-Guided Negotiations")
            orchestration_state.current_stage = "negotiations"
            await self._update_active_campaign_state(task_id, orchestration_state)
            
            await self._run_negotiation_phase_with_db(orchestration_state, task_id, strategy)
            
            # 🧠 PHASE 3: AI COMPLETION DECISION (if Groq available)
            if self.groq_client and orchestration_state.successful_negotiations > 0:
                completion_decision = await self._make_ai_completion_decision(orchestration_state)
                logger.info(f"🧠 AI Completion Decision: {completion_decision.get('action', 'complete')}")
                
                if completion_decision.get("action") == "continue" and completion_decision.get("find_more"):
                    await self._find_additional_creators(orchestration_state, completion_decision)
            
            # PHASE 4: CONTRACT GENERATION (with immediate database storage)
            logger.info("📝 Phase 4: Contract Generation")
            orchestration_state.current_stage = "contracts"
            await self._update_active_campaign_state(task_id, orchestration_state)
            
            await self._run_contract_phase_with_db(orchestration_state)
            
            # PHASE 5: FINAL DATABASE SYNC AND ANALYTICS
            logger.info("💾 Phase 5: Final Database Sync & Analytics")
            orchestration_state.current_stage = "database_sync"
            await self._update_active_campaign_state(task_id, orchestration_state)
            
            await self._final_database_sync_and_analytics(orchestration_state)
            
            # PHASE 6: COMPLETION
            orchestration_state.current_stage = "completed"
            orchestration_state.completed_at = datetime.now()
            await self._update_active_campaign_state(task_id, orchestration_state)
            
            # *** Update campaign completion in database ***
            await self._mark_campaign_completed_in_db(orchestration_state)
            
            # Generate final summary
            summary = {
                "successful_partnerships": orchestration_state.successful_negotiations,
                "total_cost": orchestration_state.total_cost,
                "creators_contacted": len(orchestration_state.negotiations)
            }
            logger.info(f"🎉 Campaign orchestration completed!")
            logger.info(f"📊 Final Results: {summary}")
            
            # AI-generated insights (if available)
            if self.groq_client:
                ai_insights = await self._generate_ai_campaign_summary(orchestration_state)
                logger.info(f"🧠 AI Insights: {ai_insights}")
            
            return orchestration_state
            
        except Exception as e:
            logger.error(f"❌ Campaign orchestration failed: {str(e)}")
            orchestration_state.current_stage = "failed"
            orchestration_state.completed_at = datetime.now()
            
            # *** Even if failed, update database ***
            try:
                await self._mark_campaign_failed_in_db(orchestration_state, str(e))
            except:
                pass  # Don't fail twice
                
            await self._update_active_campaign_state(task_id, orchestration_state)
            raise
    
    # ================================
    # NEW DATABASE INTEGRATION METHODS
    # ================================
    
    async def _initialize_database_and_create_campaign(self, state: CampaignOrchestrationState):
        """*** STEP 0: Initialize database and create campaign record ***"""
        try:
            logger.info("💾 Initializing database and creating campaign...")
            
            # Initialize database
            await self.database_service.initialize()
            
            # Create campaign in database
            campaign_record = await self.database_service.create_campaign(state.campaign_data)
            logger.info(f"✅ Campaign created in database: {campaign_record.id}")
            
            # Store database reference
            state.database_campaign_id = campaign_record.id
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize database or create campaign: {e}")
            # Continue without database - don't fail the entire workflow
            state.database_enabled = False
    
    async def _store_strategy_in_database(self, state: CampaignOrchestrationState, strategy: Dict[str, Any]):
        """Store AI strategy in database"""
        try:
            await self.database_service.update_campaign(
                state.campaign_id,
                {"ai_strategy": strategy}
            )
            logger.info("🧠 AI strategy stored in database")
            
        except Exception as e:
            logger.error(f"❌ Failed to store strategy: {e}")
    
    async def _run_discovery_phase_with_db(self, state: CampaignOrchestrationState, strategy: Dict[str, Any]):
        """🔍 Run discovery phase with immediate database storage"""
        logger.info("🔍 Starting influencer discovery phase...")
        
        # Use strategy to determine how many creators to find
        max_creators = strategy.get("max_creators_to_contact", 3)
        
        # Find top matching influencers
        discovered_influencers = await self.discovery_agent.find_matches(
            state.campaign_data,
            max_results=max_creators
        )
        
        state.discovered_influencers = discovered_influencers
        
        # *** IMMEDIATELY store discovered creators in database ***
        logger.info("💾 Storing discovered creators in database...")
        for i, match in enumerate(discovered_influencers):
            try:
                await self.database_service.create_or_update_creator(match.creator)
                logger.info(f"✅ Creator {i+1} stored: {match.creator.name}")
            except Exception as e:
                logger.error(f"❌ Failed to store creator {match.creator.name}: {e}")
        
        logger.info(f"✅ Discovery complete: Found {len(discovered_influencers)} matching influencers")
        for i, match in enumerate(discovered_influencers):
            logger.info(f"  {i+1}. {match.creator.name} - {match.similarity_score:.2f} similarity, ${match.estimated_rate:,}")
    
    async def _run_negotiation_phase_with_db(
        self,
        state: CampaignOrchestrationState,
        task_id: str,
        strategy: Dict[str, Any]
    ):
        """📞 Run negotiation phase with real-time database updates"""
        logger.info("📞 Starting negotiation phase...")
        
        # Get creators to negotiate with based on strategy
        creators_to_contact = state.discovered_influencers[:strategy.get("max_creators_to_contact", 3)]
        
        for i, influencer_match in enumerate(creators_to_contact):
            logger.info(f"📞 Negotiating with {influencer_match.creator.name} ({i+1}/{len(creators_to_contact)})")
            
            # Update current influencer in state
            state.current_influencer = influencer_match.creator.name
            state.estimated_completion_minutes = (len(creators_to_contact) - i) * 1.5
            await self._update_active_campaign_state(task_id, state)
            
            # 🧠 AI decides negotiation approach for this specific creator
            if self.groq_client and len(state.negotiations) > 0:
                negotiation_strategy = await self._get_ai_negotiation_strategy(
                    influencer_match, state.campaign_data, state.negotiations, strategy
                )
            else:
                negotiation_strategy = {"approach": strategy.get("negotiation_approach", "collaborative")}
            
            # Run negotiation with AI guidance
            negotiation_result = await self.negotiation_agent.negotiate(
                influencer_match,
                state.campaign_data,
                ai_strategy=negotiation_strategy
            )
            
            # Add result to state
            state.add_negotiation_result(negotiation_result)
            
            # *** IMMEDIATELY store negotiation in database ***
            await self._store_negotiation_in_db(state, negotiation_result)
            
            # *** Update campaign totals in database immediately ***
            await self._update_campaign_totals_in_db(state)
            
            # Log result
            if negotiation_result.status == NegotiationStatus.SUCCESS:
                logger.info(f"✅ Successful negotiation: ${negotiation_result.final_rate:,}")
            else:
                logger.info(f"❌ Failed negotiation: {negotiation_result.failure_reason}")
            
            # 🧠 AI analyzes progress and decides whether to continue
            if len(state.negotiations) >= 2 and self.groq_client:
                continue_decision = await self._analyze_progress_with_ai(state, strategy)
                
                if continue_decision.get("action") == "stop_early":
                    logger.info(f"🧠 AI Decision: Stop early - {continue_decision.get('reason')}")
                    break
                elif continue_decision.get("action") == "adjust_approach":
                    logger.info(f"🧠 AI Decision: Adjust approach - {continue_decision.get('reason')}")
                    # AI adjustments would be applied to remaining negotiations
            
            # Brief pause between calls for demo effect
            await asyncio.sleep(3)
        
        logger.info(f"📞 Negotiation phase complete: {state.successful_negotiations}/{len(creators_to_contact)} successful")
    
    async def _store_negotiation_in_db(self, state: CampaignOrchestrationState, negotiation_result):
        """Store individual negotiation in database immediately"""
        try:
            negotiation_data = {
                "status": negotiation_result.status,
                "initial_rate": negotiation_result.initial_rate,
                "final_rate": negotiation_result.final_rate,
                "call_status": negotiation_result.call_status,
                "email_status": negotiation_result.email_status,
                "call_duration_seconds": negotiation_result.call_duration_seconds,
                "negotiated_terms": negotiation_result.negotiated_terms,
                "last_contact_date": negotiation_result.last_contact_date,
                "call_recording_url": getattr(negotiation_result, 'call_recording_url', None),
                "call_transcript": getattr(negotiation_result, 'call_transcript', None)
            }
            
            negotiation_record = await self.database_service.create_negotiation(
                state.campaign_id,
                negotiation_result.creator_id,
                negotiation_data
            )
            
            logger.info(f"✅ Negotiation stored in database: ID {negotiation_record.id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to store negotiation for {negotiation_result.creator_id}: {e}")
    
    async def _update_campaign_totals_in_db(self, state: CampaignOrchestrationState):
        """Update campaign totals in database in real-time"""
        try:
            updates = {
                "influencer_count": state.successful_negotiations,
                "total_cost": state.total_cost,
                "updated_at": datetime.now()
            }
            
            await self.database_service.update_campaign(state.campaign_id, updates)
            logger.info(f"💾 Campaign totals updated: {state.successful_negotiations} influencers, ${state.total_cost:,}")
            
        except Exception as e:
            logger.error(f"❌ Failed to update campaign totals: {e}")
    
    async def _run_contract_phase_with_db(self, state: CampaignOrchestrationState):
        """📝 Generate contracts with immediate database storage"""
        logger.info("📝 Starting contract generation phase...")
        
        successful_negotiations = [
            neg for neg in state.negotiations 
            if neg.status == NegotiationStatus.SUCCESS
        ]
        
        for negotiation in successful_negotiations:
            try:
                # Generate contract
                contract_data = await self.contract_agent.generate_contract(
                    negotiation,
                    state.campaign_data
                )
                
                # *** IMMEDIATELY store contract in database ***
                contract_record = await self._store_contract_in_db(state, negotiation, contract_data)
                
                # Store contract reference in negotiation
                negotiation.negotiated_terms["contract_generated"] = True
                negotiation.negotiated_terms["contract_id"] = contract_record.id
                
                logger.info(f"📝 Contract generated and stored: {contract_record.id}")
                
            except Exception as e:
                logger.error(f"❌ Contract generation failed for {negotiation.creator_id}: {str(e)}")
        
        logger.info(f"📝 Contract phase complete: {len(successful_negotiations)} contracts generated")
    
    async def _store_contract_in_db(self, state: CampaignOrchestrationState, negotiation, contract_data):
        """Store contract in database"""
        try:
            contract_record = await self.database_service.create_contract({
                "id": f"contract_{negotiation.creator_id}_{state.campaign_id}",
                "campaign_id": state.campaign_id,
                "creator_id": negotiation.creator_id,
                "compensation_amount": negotiation.final_rate,
                "deliverables": contract_data.get("deliverables", []),
                "timeline": contract_data.get("timeline", {}),
                "usage_rights": contract_data.get("usage_rights", {}),
                "status": "draft",
                "contract_text": contract_data.get("contract_text", "")
            })
            
            # Also create payment record
            payment_record = await self.database_service.create_payment({
                "contract_id": contract_record.id,
                "amount": negotiation.final_rate,
                "status": "pending",
                "payment_method": "bank_transfer",
                "due_date": datetime.now()
            })
            
            logger.info(f"✅ Contract and payment record created: {contract_record.id}")
            return contract_record
            
        except Exception as e:
            logger.error(f"❌ Failed to store contract: {e}")
            raise
    
    async def _final_database_sync_and_analytics(self, state: CampaignOrchestrationState):
        """Final comprehensive database sync and analytics generation"""
        try:
            logger.info("💾 Running final comprehensive database sync...")
            
            # Run comprehensive sync (this ensures everything is stored)
            await self.database_service.sync_campaign_results(state)
            
            # Generate analytics from database
            analytics = await self.database_service.get_campaign_analytics(state.campaign_id)
            state.final_analytics = analytics
            
            logger.info("✅ Final database sync and analytics completed")
            logger.info(f"📊 Analytics: {analytics.get('success_rate', 0):.1f}% success rate, ${analytics.get('total_cost', 0):,} spent")
            
        except Exception as e:
            logger.error(f"❌ Final database sync failed: {e}")
    
    async def _mark_campaign_completed_in_db(self, state: CampaignOrchestrationState):
        """Mark campaign as completed in database"""
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
        """Mark campaign as failed in database"""
        try:
            await self.database_service.update_campaign(
                state.campaign_id,
                {
                    "status": "failed",
                    "completed_at": datetime.now(),
                    "ai_strategy": {"error": error_message}
                }
            )
            logger.info("⚠️ Campaign marked as failed in database")
            
        except Exception as e:
            logger.error(f"❌ Failed to mark campaign failed: {e}")
    
    # ================================
    # EXISTING METHODS (Keep all your existing AI methods)
    # ================================
    
    async def _generate_ai_strategy(self, campaign_data: CampaignData) -> Dict[str, Any]:
        """🧠 Generate AI-powered campaign strategy using Groq"""
        
        # ✅ ENHANCED: Graceful fallback if Groq is not available
        if not self.groq_client:
            logger.info("📋 Groq not available - using enhanced default strategy")
            return self._get_enhanced_default_strategy(campaign_data)
        
        prompt = f"""
        You are an expert influencer marketing strategist. Analyze this campaign and create an optimal strategy:
        
        Campaign Details:
        - Product: {campaign_data.product_name}
        - Brand: {campaign_data.brand_name}
        - Description: {campaign_data.product_description}
        - Target Audience: {campaign_data.target_audience}
        - Budget: ${campaign_data.total_budget:,}
        - Niche: {campaign_data.product_niche}
        - Goal: {campaign_data.campaign_goal}
        
        Create a strategic plan in JSON format with:
        1. creator_tier_priority: ["micro", "macro", "mega"] in order of preference
        2. budget_allocation: How to split budget (per_creator_max as decimal, reserve as decimal)
        3. success_criteria: min_creators and target_success_rate
        4. risk_mitigation: strategy approach
        5. negotiation_approach: "aggressive", "collaborative", or "premium"
        6. max_creators_to_contact: number (3-6)
        
        Consider the budget and niche to determine optimal approach.
        Respond only with valid JSON.
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=800
            )
            
            strategy_text = response.choices[0].message.content
            
            # Try to parse JSON
            try:
                strategy = json.loads(strategy_text)
                # Validate strategy has required fields
                required_fields = ["creator_tier_priority", "budget_allocation", "negotiation_approach"]
                if all(field in strategy for field in required_fields):
                    logger.info("🧠 AI strategy generated successfully")
                    return strategy
                else:
                    logger.warning("AI strategy missing required fields, using enhanced default")
                    return self._get_enhanced_default_strategy(campaign_data)
            except json.JSONDecodeError:
                logger.warning("AI strategy JSON parsing failed, using enhanced default")
                return self._get_enhanced_default_strategy(campaign_data)
            
        except Exception as e:
            logger.error(f"AI strategy generation failed: {e}")
            
            # ✅ ENHANCED: Handle specific API errors
            if "401" in str(e) or "Unauthorized" in str(e):
                logger.error("🔑 Groq API key invalid - disabling AI features for this session")
                self.groq_client = None
            
            return self._get_enhanced_default_strategy(campaign_data)    
        
    def _get_enhanced_default_strategy(self, campaign_data: CampaignData) -> Dict[str, Any]:
        """📋 Enhanced default strategy based on campaign data"""
        
        # ✅ ENHANCED: Smart defaults based on campaign characteristics
        budget = campaign_data.total_budget
        niche = campaign_data.product_niche.lower()
        
        # Determine approach based on budget and niche
        if budget > 10000:
            approach = "premium"
            max_creators = 4
            tier_priority = ["macro", "mega", "micro"]
        elif budget > 5000:
            approach = "collaborative"
            max_creators = 3
            tier_priority = ["macro", "micro", "mega"]
        else:
            approach = "collaborative"
            max_creators = 2
            tier_priority = ["micro", "macro", "mega"]
        
        # Niche-specific adjustments
        if niche in ["tech", "gaming"]:
            tier_priority = ["macro", "micro", "mega"]  # Tech audiences prefer established creators
        elif niche in ["beauty", "fashion"]:
            tier_priority = ["micro", "macro", "mega"]  # Beauty works well with micro-influencers
        
        strategy = {
            "creator_tier_priority": tier_priority,
            "budget_allocation": {
                "per_creator_max": 0.4 if budget > 10000 else 0.5,
                "reserve": 0.2
            },
            "success_criteria": {
                "min_creators": 1,
                "target_success_rate": 0.6
            },
            "risk_mitigation": "diversify_across_tiers",
            "negotiation_approach": approach,
            "max_creators_to_contact": max_creators,
            "strategy_source": "enhanced_default",
            "budget_tier": "high" if budget > 10000 else "medium" if budget > 5000 else "standard"
        }
        
        logger.info(f"📋 Enhanced default strategy: {approach} approach for {niche} niche")
        return strategy
    
    async def _run_discovery_phase(self, state: CampaignOrchestrationState, strategy: Dict[str, Any]):
        """🔍 Run the influencer discovery phase"""
        logger.info("🔍 Starting influencer discovery phase...")
        
        # Use strategy to determine how many creators to find
        max_creators = strategy.get("max_creators_to_contact", 3)
        
        # Find top matching influencers
        discovered_influencers = await self.discovery_agent.find_matches(
            state.campaign_data,
            max_results=max_creators
        )
        
        state.discovered_influencers = discovered_influencers
        
        logger.info(f"✅ Discovery complete: Found {len(discovered_influencers)} matching influencers")
        for i, match in enumerate(discovered_influencers):
            logger.info(f"  {i+1}. {match.creator.name} - {match.similarity_score:.2f} similarity, ${match.estimated_rate:,}")
    
    async def _run_negotiation_phase(
        self,
        state: CampaignOrchestrationState,
        task_id: str,
        strategy: Dict[str, Any]
    ):
        """📞 Run AI-guided negotiation phase"""
        logger.info("📞 Starting negotiation phase...")
        
        # Get creators to negotiate with based on strategy
        creators_to_contact = state.discovered_influencers[:strategy.get("max_creators_to_contact", 3)]
        
        for i, influencer_match in enumerate(creators_to_contact):
            logger.info(f"📞 Negotiating with {influencer_match.creator.name} ({i+1}/{len(creators_to_contact)})")
            
            # Update current influencer in state
            state.current_influencer = influencer_match.creator.name
            state.estimated_completion_minutes = (len(creators_to_contact) - i) * 1.5
            await self._update_active_campaign_state(task_id, state)
            
            # 🧠 AI decides negotiation approach for this specific creator
            if self.groq_client and len(state.negotiations) > 0:
                negotiation_strategy = await self._get_ai_negotiation_strategy(
                    influencer_match, state.campaign_data, state.negotiations, strategy
                )
            else:
                negotiation_strategy = {"approach": strategy.get("negotiation_approach", "collaborative")}
            
            # Run negotiation with AI guidance
            negotiation_result = await self.negotiation_agent.negotiate(
                influencer_match,
                state.campaign_data,
                ai_strategy=negotiation_strategy
            )
            
            # Add result to state
            state.add_negotiation_result(negotiation_result)
            
            # Log result
            if negotiation_result.status == NegotiationStatus.SUCCESS:
                logger.info(f"✅ Successful negotiation: ${negotiation_result.final_rate:,}")
            else:
                logger.info(f"❌ Failed negotiation: {negotiation_result.failure_reason}")
            
            # 🧠 AI analyzes progress and decides whether to continue
            if len(state.negotiations) >= 2 and self.groq_client:
                continue_decision = await self._analyze_progress_with_ai(state, strategy)
                
                if continue_decision.get("action") == "stop_early":
                    logger.info(f"🧠 AI Decision: Stop early - {continue_decision.get('reason')}")
                    break
                elif continue_decision.get("action") == "adjust_approach":
                    logger.info(f"🧠 AI Decision: Adjust approach - {continue_decision.get('reason')}")
                    # AI adjustments would be applied to remaining negotiations
            
            # Brief pause between calls for demo effect
            await asyncio.sleep(3)
        
        logger.info(f"📞 Negotiation phase complete: {state.successful_negotiations}/{len(creators_to_contact)} successful")
    
    async def _get_ai_negotiation_strategy(
        self, 
        creator_match, 
        campaign_data: CampaignData, 
        previous_results: list,
        overall_strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """🧠 Get AI-powered negotiation strategy for specific creator"""
        
        # Analyze previous results
        successes = len([r for r in previous_results if r.status == NegotiationStatus.SUCCESS])
        failures = len([r for r in previous_results if r.status == NegotiationStatus.FAILED])
        total_spent = sum(r.final_rate or 0 for r in previous_results)
        
        prompt = f"""
        Based on campaign progress, recommend negotiation strategy for this creator:
        
        Creator: {creator_match.creator.name}
        - Followers: {creator_match.creator.followers:,}
        - Engagement: {creator_match.creator.engagement_rate}%
        - Typical Rate: ${creator_match.creator.typical_rate:,}
        - Availability: {creator_match.creator.availability}
        - Platform: {creator_match.creator.platform}
        
        Campaign Progress:
        - Previous successes: {successes}
        - Previous failures: {failures}
        - Budget remaining: ${campaign_data.total_budget - total_spent:,}
        - Overall approach: {overall_strategy.get('negotiation_approach', 'collaborative')}
        
        Recommend strategy in JSON:
        1. approach: "aggressive", "collaborative", or "premium"
        2. opening_offer_multiplier: 0.8-1.2 (vs typical rate)
        3. key_selling_points: ["point1", "point2"]
        4. max_offer_multiplier: 0.9-1.3
        5. confidence_level: 0.0-1.0
        
        Respond only with JSON.
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama3-8b-8192",  # Faster model for quick decisions
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=300
            )
            
            strategy_text = response.choices[0].message.content
            strategy = json.loads(strategy_text)
            
            logger.info(f"🧠 AI Negotiation Strategy: {strategy.get('approach', 'collaborative')} approach")
            return strategy
            
        except Exception as e:
            logger.error(f"AI negotiation strategy failed: {e}")
            return {
                "approach": overall_strategy.get("negotiation_approach", "collaborative"), 
                "opening_offer_multiplier": 1.0,
                "max_offer_multiplier": 1.2
            }
    
    async def _analyze_progress_with_ai(self, state: CampaignOrchestrationState, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """🧠 AI analyzes campaign progress and recommends next steps"""
        
        total_attempts = len(state.negotiations)
        successes = state.successful_negotiations
        total_cost = state.total_cost
        remaining_budget = state.campaign_data.total_budget - total_cost
        target_success_rate = strategy.get("success_criteria", {}).get("target_success_rate", 0.6)
        
        prompt = f"""
        Analyze campaign progress and recommend action:
        
        Campaign: {state.campaign_data.product_name}
        Budget: ${state.campaign_data.total_budget:,}
        Target Success Rate: {target_success_rate*100:.0f}%
        
        Current Results:
        - Negotiations: {total_attempts}
        - Successes: {successes}
        - Success rate: {(successes/max(total_attempts,1))*100:.1f}%
        - Spent: ${total_cost:,}
        - Remaining: ${remaining_budget:,}
        
        Recommend action in JSON:
        1. action: "continue", "stop_early", or "adjust_approach"
        2. reason: Brief explanation
        3. confidence: 0.0-1.0
        4. recommended_changes: [] if continue, else list of changes
        
        Respond only with JSON.
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=200
            )
            
            decision_text = response.choices[0].message.content
            return json.loads(decision_text)
            
        except Exception as e:
            logger.error(f"AI progress analysis failed: {e}")
            return {"action": "continue", "reason": "Continue with standard approach"}
    
    async def _make_ai_completion_decision(self, state: CampaignOrchestrationState) -> Dict[str, Any]:
        """🧠 AI decides if campaign is complete or needs more work"""
        
        success_rate = (state.successful_negotiations / max(len(state.negotiations), 1)) * 100
        budget_utilization = (state.total_cost / state.campaign_data.total_budget) * 100
        
        prompt = f"""
        Campaign completion analysis:
        
        Results:
        - Negotiations: {len(state.negotiations)}
        - Successful: {state.successful_negotiations}
        - Success rate: {success_rate:.1f}%
        - Budget used: {budget_utilization:.1f}%
        - Remaining budget: ${state.campaign_data.total_budget - state.total_cost:,}
        
        Campaign goal: {state.campaign_data.campaign_goal}
        
        Recommend in JSON:
        1. action: "complete" or "continue"
        2. find_more: true/false (if continue)
        3. reason: explanation
        4. satisfaction_score: 0.0-1.0
        
        Consider: 2+ successful partnerships is usually sufficient.
        Respond only with JSON.
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=200
            )
            
            decision_text = response.choices[0].message.content
            return json.loads(decision_text)
            
        except Exception as e:
            logger.error(f"AI completion decision failed: {e}")
            return {"action": "complete", "reason": "Standard completion"}
    
    async def _find_additional_creators(self, state: CampaignOrchestrationState, decision: Dict[str, Any]):
        """🔍 Find additional creators based on AI recommendation"""
        logger.info(f"🔍 AI recommended finding more creators: {decision.get('reason')}")
        
        # This would involve running discovery again with adjusted criteria
        # For now, we'll log the decision but complete the campaign
        logger.info("📋 Additional creator search would be implemented here")
    
    async def _run_contract_phase(self, state: CampaignOrchestrationState):
        """📝 Generate contracts for successful negotiations"""
        logger.info("📝 Starting contract generation phase...")
        
        successful_negotiations = [
            neg for neg in state.negotiations 
            if neg.status == NegotiationStatus.SUCCESS
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
                
                logger.info(f"📝 Contract generated for {negotiation.creator_id}: {contract.get('contract_id')}")
                
            except Exception as e:
                logger.error(f"❌ Contract generation failed for {negotiation.creator_id}: {str(e)}")
        
        logger.info(f"📝 Contract phase complete: {len(successful_negotiations)} contracts generated")
    
    async def _sync_to_database(self, state: CampaignOrchestrationState):
        """💾 Sync all results to database"""
        logger.info("💾 Syncing results to database...")
        
        try:
            # Sync campaign results
            await self.database_service.sync_campaign_results(state)
            logger.info("✅ Database sync completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Database sync failed: {str(e)}")
            # Don't fail the entire orchestration for DB sync issues
    
    async def _generate_ai_campaign_summary(self, state: CampaignOrchestrationState) -> Dict[str, Any]:
        """🧠 Generate AI-powered campaign summary and insights"""
        
        summary = state.get_campaign_summary()
        
        prompt = f"""
        Generate insights for this influencer marketing campaign:
        
        Campaign: {summary['campaign_name']}
        Results: {summary['successful_partnerships']} partnerships, {summary['success_rate']} success rate
        Cost: ${summary['spent_amount']:,} of ${summary['total_budget']:,} budget
        Duration: {summary['duration']}
        
        Provide strategic insights in JSON:
        1. performance_grade: "A", "B", "C", "D", or "F"
        2. key_successes: ["success1", "success2"]
        3. improvement_areas: ["area1", "area2"] 
        4. recommendations: ["rec1", "rec2"]
        5. roi_outlook: "Excellent", "Good", "Fair", or "Poor"
        6. next_steps: ["step1", "step2"]
        
        Be realistic but positive in assessment.
        Respond only with JSON.
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=400
            )
            
            insights_text = response.choices[0].message.content
            return json.loads(insights_text)
            
        except Exception as e:
            logger.error(f"AI summary generation failed: {e}")
            return {
                "performance_grade": "B", 
                "roi_outlook": "Good",
                "key_successes": ["Campaign completed successfully"],
                "recommendations": ["Monitor campaign performance", "Prepare for follow-up campaigns"]
            }
    
    async def _update_active_campaign_state(
        self,
        task_id: str,
        state: CampaignOrchestrationState
    ):
        """🔄 Update the active campaign state for monitoring"""
        try:
            from main import active_campaigns
            active_campaigns[task_id] = state
        except Exception as e:
            logger.error(f"Failed to update active campaign state: {str(e)}")
    
    # Legacy method for backward compatibility
    async def run_campaign(self, campaign: CampaignData, task_id: str) -> CampaignOrchestrationState:
        """🔄 Legacy method - converts to new orchestration format"""
        orchestration_state = CampaignOrchestrationState(
            campaign_id=campaign.id,
            campaign_data=campaign
        )
        
        return await self.orchestrate_campaign(orchestration_state, task_id)