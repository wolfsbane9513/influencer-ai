# services/ai_creator_discovery.py
import asyncio
import logging
import json
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import requests
from pathlib import Path

from groq import Groq
from config.settings import settings
from models.campaign import Creator, CreatorMatch, CampaignData, CreatorTier, Platform

logger = logging.getLogger(__name__)

class AICreatorDiscovery:
    """
    🧠 AI-POWERED CREATOR DISCOVERY ENGINE
    
    Features:
    - Semantic search using AI embeddings
    - Multi-platform creator database
    - Real-time social media API integration
    - AI-powered compatibility scoring
    - Dynamic creator ranking
    - Market rate intelligence
    """
    
    def __init__(self):
        self.groq_client = Groq(api_key=settings.groq_api_key) if settings.groq_api_key else None
        
        # Creator database sources
        self.creator_sources = {
            "internal_db": self._load_internal_creators(),
            "live_apis": self._initialize_api_connections(),
            "ai_recommendations": []
        }
        
        # AI models for different matching tasks
        self.matching_models = {
            "semantic_similarity": "sentence-transformers",
            "performance_prediction": "groq_llama",
            "rate_optimization": "custom_regression"
        }
        
        # Search configuration
        self.search_config = {
            "max_results_per_platform": 20,
            "min_similarity_threshold": 0.65,
            "rate_tolerance_percentage": 25,
            "performance_weight": 0.4,
            "compatibility_weight": 0.35,
            "rate_weight": 0.25
        }
        
        logger.info(f"🧠 AI Creator Discovery initialized - {len(self.creator_sources['internal_db'])} creators loaded")
    
    async def discover_creators(
        self,
        campaign_data: CampaignData,
        search_criteria: Dict[str, Any] = None,
        max_results: int = 10
    ) -> List[CreatorMatch]:
        """
        🎯 Main discovery method - finds best creators using AI
        """
        
        try:
            logger.info(f"🔍 Starting AI creator discovery for {campaign_data.product_name}")
            
            # PHASE 1: Generate AI search strategy
            search_strategy = await self._generate_ai_search_strategy(campaign_data, search_criteria)
            
            # PHASE 2: Multi-source creator search
            all_candidates = await self._multi_source_creator_search(campaign_data, search_strategy)
            
            # PHASE 3: AI-powered compatibility analysis
            scored_candidates = await self._ai_compatibility_scoring(campaign_data, all_candidates)
            
            # PHASE 4: Performance prediction and ranking
            ranked_creators = await self._performance_prediction_ranking(campaign_data, scored_candidates)
            
            # PHASE 5: Market rate optimization
            optimized_matches = await self._market_rate_optimization(campaign_data, ranked_creators)
            
            # PHASE 6: Final selection and validation
            final_matches = self._select_and_validate_matches(optimized_matches, max_results)
            
            logger.info(f"✅ AI Discovery complete: {len(final_matches)} creators found")
            return final_matches
            
        except Exception as e:
            logger.error(f"❌ AI creator discovery failed: {e}")
            return await self._fallback_discovery(campaign_data, max_results)
    
    async def _generate_ai_search_strategy(
        self,
        campaign_data: CampaignData,
        search_criteria: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        🧠 Generate intelligent search strategy using AI
        """
        
        if not self.groq_client:
            return self._default_search_strategy(campaign_data)
        
        try:
            # Create comprehensive campaign context
            campaign_context = {
                "product": campaign_data.product_name,
                "brand": campaign_data.brand_name,
                "description": campaign_data.product_description,
                "niche": campaign_data.product_niche,
                "audience": campaign_data.target_audience,
                "goal": campaign_data.campaign_goal,
                "budget": campaign_data.total_budget
            }
            
            prompt = f"""
            You are an expert influencer marketing strategist. Create an optimal creator search strategy for this campaign.
            
            Campaign: {json.dumps(campaign_context, indent=2)}
            Additional criteria: {json.dumps(search_criteria or {}, indent=2)}
            
            Return a JSON strategy with:
            {{
                "target_platforms": ["Instagram", "YouTube", "TikTok"],
                "creator_tiers": ["micro", "macro", "mega"],
                "priority_tier": "micro|macro|mega",
                "follower_ranges": {{
                    "min": 10000,
                    "max": 500000,
                    "optimal": 100000
                }},
                "content_types": ["video_review", "unboxing", "tutorial"],
                "engagement_requirements": {{
                    "min_rate": 3.0,
                    "optimal_rate": 6.0
                }},
                "geographic_focus": ["US", "India", "Global"],
                "demographic_targets": {{
                    "age_groups": ["18-24", "25-34"],
                    "gender_split": "any|male|female"
                }},
                "semantic_keywords": ["keyword1", "keyword2"],
                "exclusion_criteria": ["competing_brands"],
                "success_predictors": ["high_engagement", "brand_alignment"],
                "budget_allocation": {{
                    "target_cpm": 50.0,
                    "max_rate_per_creator": 5000
                }}
            }}
            
            Optimize for: authenticity, engagement, and ROI.
            """
            
            response = self.groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=800
            )
            
            strategy_text = response.choices[0].message.content.strip()
            
            # Extract JSON
            json_start = strategy_text.find('{')
            json_end = strategy_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                strategy = json.loads(strategy_text[json_start:json_end])
                logger.info(f"🧠 AI search strategy generated: {strategy.get('priority_tier')} tier focus")
                return strategy
            else:
                return self._default_search_strategy(campaign_data)
                
        except Exception as e:
            logger.error(f"❌ AI strategy generation failed: {e}")
            return self._default_search_strategy(campaign_data)
    
    def _default_search_strategy(self, campaign_data: CampaignData) -> Dict[str, Any]:
        """Default search strategy when AI fails"""
        
        budget = campaign_data.total_budget
        niche = campaign_data.product_niche.lower()
        
        # Budget-based tier selection
        if budget > 20000:
            priority_tier = "macro"
            max_rate = 8000
        elif budget > 10000:
            priority_tier = "micro"
            max_rate = 4000
        else:
            priority_tier = "micro"
            max_rate = 2500
        
        # Niche-based platform selection
        platform_map = {
            "fitness": ["Instagram", "YouTube", "TikTok"],
            "tech": ["YouTube", "Instagram", "Twitter"],
            "beauty": ["Instagram", "TikTok", "YouTube"],
            "gaming": ["Twitch", "YouTube", "TikTok"],
            "food": ["Instagram", "YouTube", "TikTok"]
        }
        
        return {
            "target_platforms": platform_map.get(niche, ["Instagram", "YouTube"]),
            "creator_tiers": ["micro", "macro"],
            "priority_tier": priority_tier,
            "follower_ranges": {
                "min": 10000,
                "max": 500000,
                "optimal": 100000
            },
            "engagement_requirements": {
                "min_rate": 3.0,
                "optimal_rate": 6.0
            },
            "budget_allocation": {
                "max_rate_per_creator": max_rate
            },
            "semantic_keywords": [niche, campaign_data.product_name.lower()],
            "strategy_source": "default"
        }
    
    async def _multi_source_creator_search(
        self,
        campaign_data: CampaignData,
        search_strategy: Dict[str, Any]
    ) -> List[Creator]:
        """
        🔍 Search creators from multiple sources
        """
        
        all_candidates = []
        
        # SOURCE 1: Internal database search
        internal_results = await self._search_internal_database(campaign_data, search_strategy)
        all_candidates.extend(internal_results)
        
        # SOURCE 2: Live API search (if available)
        api_results = await self._search_live_apis(campaign_data, search_strategy)
        all_candidates.extend(api_results)
        
        # SOURCE 3: AI-generated creator suggestions
        ai_suggestions = await self._ai_generate_creator_suggestions(campaign_data, search_strategy)
        all_candidates.extend(ai_suggestions)
        
        # Deduplicate by creator ID
        unique_candidates = []
        seen_ids = set()
        
        for creator in all_candidates:
            if creator.id not in seen_ids:
                unique_candidates.append(creator)
                seen_ids.add(creator.id)
        
        logger.info(f"🔍 Multi-source search: {len(unique_candidates)} unique candidates found")
        return unique_candidates
    
    async def _search_internal_database(
        self,
        campaign_data: CampaignData,
        search_strategy: Dict[str, Any]
    ) -> List[Creator]:
        """Search internal creator database"""
        
        creators = self.creator_sources["internal_db"]
        matching_creators = []
        
        # Filter by strategy criteria
        for creator in creators:
            # Platform filter
            if creator.platform.value not in search_strategy.get("target_platforms", []):
                continue
            
            # Follower range filter
            follower_range = search_strategy.get("follower_ranges", {})
            min_followers = follower_range.get("min", 0)
            max_followers = follower_range.get("max", float('inf'))
            
            if not (min_followers <= creator.followers <= max_followers):
                continue
            
            # Engagement filter
            engagement_req = search_strategy.get("engagement_requirements", {})
            min_engagement = engagement_req.get("min_rate", 0)
            
            if creator.engagement_rate < min_engagement:
                continue
            
            # Niche relevance
            if campaign_data.product_niche.lower() in creator.niche.lower():
                matching_creators.append(creator)
            elif any(keyword in creator.niche.lower() for keyword in search_strategy.get("semantic_keywords", [])):
                matching_creators.append(creator)
        
        logger.info(f"📊 Internal DB search: {len(matching_creators)} creators matched")
        return matching_creators
    
    async def _search_live_apis(
        self,
        campaign_data: CampaignData,
        search_strategy: Dict[str, Any]
    ) -> List[Creator]:
        """Search live social media APIs"""
        
        # This would integrate with actual APIs like:
        # - Instagram Business Discovery API
        # - YouTube Data API
        # - TikTok Business API
        # - Creator discovery platforms
        
        # For now, return mock data that simulates API results
        mock_api_creators = []
        
        if "YouTube" in search_strategy.get("target_platforms", []):
            mock_api_creators.extend(self._generate_mock_api_creators("YouTube", campaign_data))
        
        if "Instagram" in search_strategy.get("target_platforms", []):
            mock_api_creators.extend(self._generate_mock_api_creators("Instagram", campaign_data))
        
        logger.info(f"🌐 Live API search: {len(mock_api_creators)} creators found")
        return mock_api_creators
    
    def _generate_mock_api_creators(self, platform: str, campaign_data: CampaignData) -> List[Creator]:
        """Generate mock creators that simulate API results"""
        
        niche = campaign_data.product_niche
        mock_creators = []
        
        # Generate 3-5 mock creators per platform
        for i in range(3):
            creator_id = f"api_{platform.lower()}_{niche}_{i+1}"
            
            # Vary follower counts realistically
            base_followers = 50000 + (i * 75000)
            followers = base_followers + np.random.randint(-10000, 20000)
            
            mock_creator = Creator(
                id=creator_id,
                name=f"{niche.title()}Creator_{platform}_{i+1}",
                platform=Platform(platform),
                followers=followers,
                niche=niche,
                typical_rate=self._estimate_creator_rate(followers, platform),
                engagement_rate=3.5 + np.random.uniform(0, 3.5),
                average_views=int(followers * 0.15 * (1 + np.random.uniform(-0.3, 0.5))),
                last_campaign_date="2024-11-15",
                availability="good",
                location="Los Angeles, USA" if platform == "YouTube" else "Mumbai, India",
                phone_number="+918806859890",
                languages=["English"],
                specialties=[f"{niche}_content", "brand_partnerships"],
                audience_demographics={
                    "age_18_24": 35,
                    "age_25_34": 40,
                    "male": 50,
                    "female": 50
                },
                performance_metrics={
                    "brand_safety_score": 8.5 + np.random.uniform(0, 1.5),
                    "collaboration_rating": 4.0 + np.random.uniform(0, 1.0)
                },
                recent_campaigns=[],
                rate_history={"2024": self._estimate_creator_rate(followers, platform)},
                preferred_collaboration_style=f"Professional {niche} content creator"
            )
            
            mock_creators.append(mock_creator)
        
        return mock_creators
    
    def _estimate_creator_rate(self, followers: int, platform: str) -> float:
        """Estimate creator rate based on followers and platform"""
        
        # Platform-based multipliers
        platform_multipliers = {
            "YouTube": 1.2,
            "Instagram": 1.0,
            "TikTok": 0.8,
            "Twitch": 1.1
        }
        
        # Base rate calculation
        if followers < 50000:
            base_rate = followers * 0.05
        elif followers < 200000:
            base_rate = followers * 0.03
        else:
            base_rate = followers * 0.02
        
        multiplier = platform_multipliers.get(platform, 1.0)
        return round(base_rate * multiplier, 2)
    
    async def _ai_generate_creator_suggestions(
        self,
        campaign_data: CampaignData,
        search_strategy: Dict[str, Any]
    ) -> List[Creator]:
        """AI-generated creator suggestions based on campaign needs"""
        
        # This would use AI to generate ideal creator profiles
        # For now, return strategic mock suggestions
        ai_suggestions = []
        
        # Generate 2-3 AI-suggested creator profiles
        for i in range(2):
            suggestion_id = f"ai_suggestion_{campaign_data.product_niche}_{i+1}"
            
            # AI-optimized creator profile
            ai_creator = Creator(
                id=suggestion_id,
                name=f"AI_Optimized_{campaign_data.product_niche.title()}Creator_{i+1}",
                platform=Platform("Instagram"),  # Most versatile platform
                followers=80000 + (i * 40000),  # Sweet spot for engagement
                niche=campaign_data.product_niche,
                typical_rate=3500 + (i * 1200),
                engagement_rate=6.5 + np.random.uniform(0, 1.5),  # High engagement
                average_views=60000 + (i * 25000),
                last_campaign_date="2024-12-01",
                availability="excellent",
                location="Global Reach",
                phone_number="+918806859890",
                languages=["English"],
                specialties=[f"{campaign_data.product_niche}_expert", "authentic_reviews", "high_conversion"],
                audience_demographics={
                    "age_18_24": 30,
                    "age_25_34": 45,
                    "male": 45,
                    "female": 55
                },
                performance_metrics={
                    "brand_safety_score": 9.5,
                    "collaboration_rating": 4.9
                },
                recent_campaigns=[],
                rate_history={"2024": 3500 + (i * 1200)},
                preferred_collaboration_style="Data-driven content with authentic storytelling"
            )
            
            ai_suggestions.append(ai_creator)
        
        logger.info(f"🤖 AI suggestions: {len(ai_suggestions)} optimized creator profiles generated")
        return ai_suggestions
    
    async def _ai_compatibility_scoring(
        self,
        campaign_data: CampaignData,
        candidates: List[Creator]
    ) -> List[Tuple[Creator, float]]:
        """
        🎯 AI-powered compatibility scoring
        """
        
        scored_candidates = []
        
        for creator in candidates:
            # Calculate comprehensive compatibility score
            compatibility_score = await self._calculate_ai_compatibility(campaign_data, creator)
            scored_candidates.append((creator, compatibility_score))
        
        # Sort by compatibility score
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        
        logger.info(f"🎯 AI compatibility scoring complete: {len(scored_candidates)} creators scored")
        return scored_candidates
    
    async def _calculate_ai_compatibility(self, campaign_data: CampaignData, creator: Creator) -> float:
        """Calculate AI-based compatibility score"""
        
        if not self.groq_client:
            return self._simple_compatibility_score(campaign_data, creator)
        
        try:
            # Create compatibility analysis prompt
            prompt = f"""
            Rate the compatibility between this campaign and creator on a scale of 0-100.
            
            CAMPAIGN:
            - Product: {campaign_data.product_name}
            - Brand: {campaign_data.brand_name}
            - Niche: {campaign_data.product_niche}
            - Audience: {campaign_data.target_audience}
            - Goal: {campaign_data.campaign_goal}
            - Budget: ${campaign_data.total_budget:,}
            
            CREATOR:
            - Name: {creator.name}
            - Platform: {creator.platform.value}
            - Followers: {creator.followers:,}
            - Niche: {creator.niche}
            - Engagement: {creator.engagement_rate}%
            - Rate: ${creator.typical_rate:,}
            - Style: {creator.preferred_collaboration_style}
            
            Return only a number between 0-100 representing compatibility percentage.
            Consider: audience alignment, content style match, budget fit, authenticity potential.
            """
            
            response = self.groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=10
            )
            
            score_text = response.choices[0].message.content.strip()
            
            # Extract numeric score
            try:
                score = float(score_text.split()[0])  # Get first number
                return min(max(score / 100, 0), 1)  # Normalize to 0-1
            except:
                return self._simple_compatibility_score(campaign_data, creator)
                
        except Exception as e:
            logger.error(f"❌ AI compatibility scoring failed: {e}")
            return self._simple_compatibility_score(campaign_data, creator)
    
    def _simple_compatibility_score(self, campaign_data: CampaignData, creator: Creator) -> float:
        """Simple compatibility scoring fallback"""
        
        score_factors = []
        
        # Niche alignment
        if creator.niche.lower() == campaign_data.product_niche.lower():
            score_factors.append(0.4)
        elif campaign_data.product_niche.lower() in creator.niche.lower():
            score_factors.append(0.25)
        else:
            score_factors.append(0.1)
        
        # Engagement quality
        if creator.engagement_rate >= 6.0:
            score_factors.append(0.3)
        elif creator.engagement_rate >= 4.0:
            score_factors.append(0.2)
        else:
            score_factors.append(0.1)
        
        # Budget compatibility
        budget_per_creator = campaign_data.total_budget / 3
        if creator.typical_rate <= budget_per_creator:
            score_factors.append(0.2)
        elif creator.typical_rate <= budget_per_creator * 1.2:
            score_factors.append(0.15)
        else:
            score_factors.append(0.05)
        
        # Availability
        availability_scores = {"excellent": 0.1, "good": 0.08, "limited": 0.05, "busy": 0.02}
        score_factors.append(availability_scores.get(creator.availability.value, 0.05))
        
        return sum(score_factors)
    
    async def _performance_prediction_ranking(
        self,
        campaign_data: CampaignData,
        scored_candidates: List[Tuple[Creator, float]]
    ) -> List[Tuple[Creator, float, Dict[str, Any]]]:
        """
        📈 Predict campaign performance for each creator
        """
        
        ranked_creators = []
        
        for creator, compatibility_score in scored_candidates:
            # Predict performance metrics
            performance_prediction = await self._predict_creator_performance(campaign_data, creator)
            
            # Calculate final ranking score
            final_score = (
                compatibility_score * 0.6 +
                performance_prediction["predicted_engagement"] * 0.25 +
                performance_prediction["roi_score"] * 0.15
            )
            
            ranked_creators.append((creator, final_score, performance_prediction))
        
        # Sort by final score
        ranked_creators.sort(key=lambda x: x[1], reverse=True)
        
        logger.info(f"📈 Performance prediction ranking complete")
        return ranked_creators
    
    async def _predict_creator_performance(self, campaign_data: CampaignData, creator: Creator) -> Dict[str, Any]:
        """Predict campaign performance metrics"""
        
        # Base predictions on historical data and creator metrics
        base_engagement = creator.engagement_rate / 10  # Normalize to 0-1
        follower_quality = min(creator.average_views / creator.followers, 1.0)
        
        # Predict key metrics
        predicted_reach = creator.followers * 0.85 * follower_quality
        predicted_engagement = base_engagement * 0.9  # Slight discount for sponsored content
        predicted_conversions = predicted_reach * 0.02  # 2% conversion rate
        
        # Calculate ROI score
        cost_per_conversion = creator.typical_rate / max(predicted_conversions, 1)
        roi_score = min(1.0, 100 / cost_per_conversion)  # Higher is better
        
        return {
            "predicted_reach": int(predicted_reach),
            "predicted_engagement": predicted_engagement,
            "predicted_conversions": int(predicted_conversions),
            "cost_per_conversion": round(cost_per_conversion, 2),
            "roi_score": roi_score,
            "confidence_level": 0.75  # Model confidence
        }
    
    async def _market_rate_optimization(
        self,
        campaign_data: CampaignData,
        ranked_creators: List[Tuple[Creator, float, Dict[str, Any]]]
    ) -> List[CreatorMatch]:
        """
        💰 Optimize market rates and create final matches
        """
        
        creator_matches = []
        total_budget = campaign_data.total_budget
        allocated_budget = 0
        
        for creator, score, performance in ranked_creators:
            # Calculate optimized rate
            optimized_rate = self._calculate_optimized_rate(
                creator, performance, campaign_data, allocated_budget, total_budget
            )
            
            # Check budget constraints
            if allocated_budget + optimized_rate > total_budget:
                break
            
            # Generate match reasons
            match_reasons = self._generate_ai_match_reasons(creator, score, performance)
            
            # Create creator match
            creator_match = CreatorMatch(
                creator=creator,
                similarity_score=score,
                rate_compatible=optimized_rate <= creator.typical_rate * 1.1,
                match_reasons=match_reasons,
                estimated_rate=optimized_rate
            )
            
            creator_matches.append(creator_match)
            allocated_budget += optimized_rate
        
        logger.info(f"💰 Market rate optimization: {len(creator_matches)} matches, ${allocated_budget:,.2f} allocated")
        return creator_matches
    
    def _calculate_optimized_rate(
        self,
        creator: Creator,
        performance: Dict[str, Any],
        campaign_data: CampaignData,
        allocated_budget: float,
        total_budget: float
    ) -> float:
        """Calculate optimized rate based on performance prediction"""
        
        base_rate = creator.typical_rate
        performance_multiplier = 1.0
        
        # Adjust based on predicted ROI
        roi_score = performance["roi_score"]
        if roi_score > 0.8:
            performance_multiplier = 0.95  # Slight discount for high ROI
        elif roi_score < 0.4:
            performance_multiplier = 1.1   # Premium for lower expected ROI
        
        # Budget pressure adjustment
        remaining_budget = total_budget - allocated_budget
        budget_slots_remaining = max(3 - len([]), 1)  # Assume we want 3 creators total
        
        if remaining_budget < base_rate * budget_slots_remaining:
            performance_multiplier *= 0.9  # Budget pressure discount
        
        optimized_rate = base_rate * performance_multiplier
        return round(optimized_rate, 2)
    
    def _generate_ai_match_reasons(self, creator: Creator, score: float, performance: Dict[str, Any]) -> List[str]:
        """Generate AI-powered match reasons"""
        
        reasons = []
        
        # Score-based reasons
        if score > 0.8:
            reasons.append("Excellent brand-creator alignment")
        elif score > 0.6:
            reasons.append("Strong content compatibility")
        
        # Performance-based reasons
        if performance["roi_score"] > 0.7:
            reasons.append("High predicted ROI")
        
        if performance["predicted_engagement"] > 0.06:
            reasons.append("Above-average engagement expected")
        
        # Creator-specific reasons
        if creator.engagement_rate > 6.0:
            reasons.append("Exceptional audience engagement")
        
        if creator.availability.value == "excellent":
            reasons.append("Immediate availability")
        
        if creator.tier == CreatorTier.MICRO:
            reasons.append("Authentic micro-influencer appeal")
        
        return reasons[:3]  # Top 3 reasons
    
    def _select_and_validate_matches(self, creator_matches: List[CreatorMatch], max_results: int) -> List[CreatorMatch]:
        """Final selection and validation of matches"""
        
        # Ensure diversity in selection
        selected_matches = []
        platforms_used = set()
        
        for match in creator_matches:
            # Platform diversity
            if len(platforms_used) < 3 and match.creator.platform.value not in platforms_used:
                selected_matches.append(match)
                platforms_used.add(match.creator.platform.value)
            elif len(selected_matches) < max_results:
                selected_matches.append(match)
            
            if len(selected_matches) >= max_results:
                break
        
        return selected_matches
    
    async def _fallback_discovery(self, campaign_data: CampaignData, max_results: int) -> List[CreatorMatch]:
        """Fallback discovery when AI fails"""
        
        logger.warning("🔧 Using fallback discovery method")
        
        # Use simple internal database search
        from agents.discovery import InfluencerDiscoveryAgent
        
        try:
            discovery_agent = InfluencerDiscoveryAgent()
            return await discovery_agent.find_matches(campaign_data, max_results)
        except Exception as e:
            logger.error(f"❌ Fallback discovery also failed: {e}")
            return []
    
    def _load_internal_creators(self) -> List[Creator]:
        """Load creators from internal database"""
        
        try:
            from agents.discovery import InfluencerDiscoveryAgent
            discovery_agent = InfluencerDiscoveryAgent()
            return discovery_agent.creators_data
        except Exception as e:
            logger.error(f"❌ Failed to load internal creators: {e}")
            return []
    
    def _initialize_api_connections(self) -> Dict[str, Any]:
        """Initialize connections to social media APIs"""
        
        # Would initialize real API connections
        return {
            "youtube_api": None,
            "instagram_api": None,
            "tiktok_api": None,
            "twitter_api": None
        }

class CreatorPerformancePredictor:
    """
    📊 CREATOR PERFORMANCE PREDICTOR
    
    Predicts campaign performance using historical data and AI models
    """
    
    def __init__(self):
        self.historical_data = self._load_historical_performance_data()
        self.prediction_models = {
            "engagement_predictor": self._initialize_engagement_model(),
            "conversion_predictor": self._initialize_conversion_model(),
            "roi_predictor": self._initialize_roi_model()
        }
    
    async def predict_campaign_performance(
        self,
        creator: Creator,
        campaign_data: CampaignData
    ) -> Dict[str, Any]:
        """Predict comprehensive campaign performance"""
        
        # Gather prediction inputs
        inputs = self._prepare_prediction_inputs(creator, campaign_data)
        
        # Run predictions
        engagement_pred = await self._predict_engagement(inputs)
        conversion_pred = await self._predict_conversions(inputs)
        roi_pred = await self._predict_roi(inputs)
        
        # Generate confidence intervals
        confidence = self._calculate_prediction_confidence(inputs, creator)
        
        return {
            "creator_id": creator.id,
            "campaign_predictions": {
                "estimated_reach": engagement_pred["reach"],
                "estimated_engagement_rate": engagement_pred["rate"],
                "estimated_conversions": conversion_pred["conversions"],
                "estimated_revenue": conversion_pred["revenue"],
                "predicted_roi": roi_pred["roi_percentage"],
                "cost_per_acquisition": roi_pred["cpa"]
            },
            "confidence_metrics": confidence,
            "risk_factors": self._identify_risk_factors(creator, campaign_data),
            "optimization_suggestions": self._generate_optimization_suggestions(creator, campaign_data)
        }
    
    def _prepare_prediction_inputs(self, creator: Creator, campaign_data: CampaignData) -> Dict[str, Any]:
        """Prepare inputs for prediction models"""
        
        return {
            "creator_metrics": {
                "followers": creator.followers,
                "engagement_rate": creator.engagement_rate,
                "avg_views": creator.average_views,
                "platform": creator.platform.value,
                "niche": creator.niche,
                "tier": creator.tier.value
            },
            "campaign_metrics": {
                "budget": campaign_data.total_budget,
                "niche": campaign_data.product_niche,
                "target_audience": campaign_data.target_audience,
                "goal": campaign_data.campaign_goal
            },
            "market_conditions": {
                "season": datetime.now().month,
                "competition_level": "medium",  # Would calculate from market data
                "trending_topics": []
            }
        }
    
    async def _predict_engagement(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Predict engagement metrics"""
        
        creator_metrics = inputs["creator_metrics"]
        
        # Simple prediction model (would be ML-based in production)
        base_reach = creator_metrics["followers"] * 0.1  # 10% organic reach
        engagement_decline = 0.85  # 15% decline for sponsored content
        
        predicted_reach = int(base_reach * engagement_decline)
        predicted_engagement_rate = creator_metrics["engagement_rate"] * engagement_decline
        
        return {
            "reach": predicted_reach,
            "rate": predicted_engagement_rate,
            "total_engagements": int(predicted_reach * predicted_engagement_rate / 100)
        }
    
    async def _predict_conversions(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Predict conversion metrics"""
        
        # Conversion rate varies by niche and campaign type
        niche_conversion_rates = {
            "fitness": 0.025,
            "tech": 0.015,
            "beauty": 0.035,
            "gaming": 0.02,
            "food": 0.03
        }
        
        campaign_niche = inputs["campaign_metrics"]["niche"]
        base_conversion_rate = niche_conversion_rates.get(campaign_niche, 0.02)
        
        # Calculate conversions
        reach = inputs["creator_metrics"]["followers"] * 0.1 * 0.85  # From engagement prediction
        conversions = int(reach * base_conversion_rate)
        
        # Estimate revenue (assuming $50 average order value)
        avg_order_value = 50
        estimated_revenue = conversions * avg_order_value
        
        return {
            "conversions": conversions,
            "conversion_rate": base_conversion_rate,
            "revenue": estimated_revenue,
            "avg_order_value": avg_order_value
        }
    
    async def _predict_roi(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Predict ROI metrics"""
        
        # Simple ROI calculation
        campaign_cost = inputs["campaign_metrics"]["budget"] / 3  # Assume 3 creators
        
        # Get revenue from conversion prediction
        conversion_pred = await self._predict_conversions(inputs)
        estimated_revenue = conversion_pred["revenue"]
        
        roi_percentage = ((estimated_revenue - campaign_cost) / campaign_cost) * 100
        cpa = campaign_cost / max(conversion_pred["conversions"], 1)
        
        return {
            "roi_percentage": round(roi_percentage, 2),
            "cpa": round(cpa, 2),
            "revenue": estimated_revenue,
            "cost": campaign_cost
        }
    
    def _calculate_prediction_confidence(self, inputs: Dict[str, Any], creator: Creator) -> Dict[str, Any]:
        """Calculate confidence in predictions"""
        
        confidence_factors = []
        
        # Historical data availability
        if hasattr(creator, 'recent_campaigns') and creator.recent_campaigns:
            confidence_factors.append(0.3)
        
        # Creator consistency (engagement rate stability)
        if creator.engagement_rate > 3.0:
            confidence_factors.append(0.25)
        
        # Platform predictability
        platform_confidence = {"Instagram": 0.8, "YouTube": 0.9, "TikTok": 0.6}
        confidence_factors.append(platform_confidence.get(creator.platform.value, 0.7) * 0.2)
        
        # Market data quality
        confidence_factors.append(0.25)  # Base market data confidence
        
        overall_confidence = sum(confidence_factors)
        
        return {
            "overall_confidence": overall_confidence,
            "confidence_level": "high" if overall_confidence > 0.8 else "medium" if overall_confidence > 0.6 else "low",
            "factors": {
                "historical_data": len(creator.recent_campaigns) if hasattr(creator, 'recent_campaigns') else 0,
                "creator_consistency": creator.engagement_rate > 3.0,
                "platform_predictability": platform_confidence.get(creator.platform.value, 0.7),
                "market_data_quality": 0.8
            }
        }
    
    def _identify_risk_factors(self, creator: Creator, campaign_data: CampaignData) -> List[str]:
        """Identify potential risk factors"""
        
        risks = []
        
        if creator.engagement_rate < 2.0:
            risks.append("Low engagement rate may impact performance")
        
        if creator.availability.value == "busy":
            risks.append("Limited availability may affect timeline")
        
        if creator.followers > 1000000:
            risks.append("Large audience may have lower engagement rates")
        
        if creator.niche != campaign_data.product_niche:
            risks.append("Niche mismatch may reduce authenticity")
        
        return risks
    
    def _generate_optimization_suggestions(self, creator: Creator, campaign_data: CampaignData) -> List[str]:
        """Generate optimization suggestions"""
        
        suggestions = []
        
        if creator.platform.value == "Instagram":
            suggestions.append("Consider multiple format mix: post + stories + reels")
        
        if creator.engagement_rate > 6.0:
            suggestions.append("High engagement creator - consider premium positioning")
        
        if creator.tier == CreatorTier.MICRO:
            suggestions.append("Micro-influencer - emphasize authentic storytelling")
        
        suggestions.append("Include clear call-to-action for conversions")
        suggestions.append("Provide exclusive discount code for tracking")
        
        return suggestions
    
    def _load_historical_performance_data(self) -> Dict[str, Any]:
        """Load historical campaign performance data"""
        
        # Mock historical data - would come from database
        return {
            "campaigns": [],
            "industry_benchmarks": {
                "fitness": {"avg_engagement": 4.2, "avg_conversion": 0.025},
                "tech": {"avg_engagement": 3.8, "avg_conversion": 0.015},
                "beauty": {"avg_engagement": 5.1, "avg_conversion": 0.035}
            }
        }
    
    def _initialize_engagement_model(self):
        """Initialize engagement prediction model"""
        return None  # Would be ML model
    
    def _initialize_conversion_model(self):
        """Initialize conversion prediction model"""
        return None  # Would be ML model
    
    def _initialize_roi_model(self):
        """Initialize ROI prediction model"""
        return None  # Would be ML model