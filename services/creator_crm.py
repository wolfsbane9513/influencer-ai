# services/creator_crm.py
import asyncio
import logging
import json
import requests
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict

import numpy as np
from groq import Groq
from config.settings import settings
from models.campaign import Creator, Platform, CreatorTier, Availability

logger = logging.getLogger(__name__)

class CreatorStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLACKLISTED = "blacklisted"
    PENDING_VERIFICATION = "pending_verification"
    SUSPENDED = "suspended"

class RelationshipQuality(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"
    UNKNOWN = "unknown"

@dataclass
class CreatorInsights:
    """Advanced creator insights and analytics"""
    performance_score: float
    reliability_score: float
    growth_trend: str
    market_rate_trend: str
    collaboration_history_count: int
    average_campaign_performance: float
    preferred_brands: List[str]
    content_quality_score: float
    audience_authenticity_score: float
    response_time_hours: float

@dataclass
class CreatorRelationship:
    """Creator relationship management data"""
    relationship_quality: RelationshipQuality
    total_collaborations: int
    total_revenue_generated: float
    average_campaign_satisfaction: float
    last_interaction_date: datetime
    preferred_communication_method: str
    special_rates: Optional[Dict[str, float]]
    exclusivity_agreements: List[Dict[str, Any]]
    notes: List[Dict[str, Any]]

class CreatorCRM:
    """
    👥 CREATOR CRM - Advanced Creator Relationship Management
    
    Features:
    - Comprehensive creator database management
    - Performance tracking and analytics
    - Relationship quality scoring
    - AI-powered creator insights
    - Automated outreach and follow-ups
    - Contract and payment history
    - Audience analytics and verification
    - Market rate intelligence
    """
    
    def __init__(self):
        self.groq_client = Groq(api_key=settings.groq_api_key) if settings.groq_api_key else None
        
        # Creator database (in-memory for demo, would be actual DB)
        self.creator_database = {}
        self.creator_insights = {}
        self.creator_relationships = {}
        
        # Performance tracking
        self.performance_history = {}
        self.market_intelligence = {}
        
        # AI analysis configuration
        self.ai_analysis_config = {
            "personality_analysis": True,
            "content_quality_scoring": True,
            "audience_authenticity_check": True,
            "market_rate_prediction": True,
            "performance_forecasting": True
        }
        
        # Initialize with existing creators
        self._initialize_creator_database()
        
        logger.info(f"👥 Creator CRM initialized with {len(self.creator_database)} creators")
    
    async def add_creator(
        self,
        creator_data: Dict[str, Any],
        source: str = "manual",
        verification_level: str = "basic"
    ) -> Dict[str, Any]:
        """
        ➕ Add new creator to CRM system
        """
        
        try:
            # Validate creator data
            validation_result = await self._validate_creator_data(creator_data)
            
            if not validation_result["is_valid"]:
                return {
                    "status": "error",
                    "errors": validation_result["errors"],
                    "suggestions": validation_result["suggestions"]
                }
            
            # Create creator object
            creator = Creator(**creator_data)
            
            # Generate AI insights
            insights = await self._generate_creator_insights(creator)
            
            # Initialize relationship data
            relationship = CreatorRelationship(
                relationship_quality=RelationshipQuality.UNKNOWN,
                total_collaborations=0,
                total_revenue_generated=0.0,
                average_campaign_satisfaction=0.0,
                last_interaction_date=datetime.now(),
                preferred_communication_method="email",
                special_rates=None,
                exclusivity_agreements=[],
                notes=[]
            )
            
            # Store in database
            self.creator_database[creator.id] = creator
            self.creator_insights[creator.id] = insights
            self.creator_relationships[creator.id] = relationship
            
            # Perform additional verification if needed
            if verification_level == "comprehensive":
                verification_result = await self._comprehensive_creator_verification(creator)
                insights.audience_authenticity_score = verification_result["authenticity_score"]
            
            logger.info(f"➕ Creator added: {creator.name} ({creator.platform.value})")
            
            return {
                "status": "success",
                "creator_id": creator.id,
                "insights": asdict(insights),
                "verification_level": verification_level,
                "next_steps": [
                    "Review AI-generated insights",
                    "Set up performance tracking",
                    "Configure outreach preferences"
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to add creator: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_creator_profile(self, creator_id: str, include_insights: bool = True) -> Dict[str, Any]:
        """
        👤 Get comprehensive creator profile
        """
        
        if creator_id not in self.creator_database:
            return {"status": "not_found", "creator_id": creator_id}
        
        creator = self.creator_database[creator_id]
        insights = self.creator_insights.get(creator_id)
        relationship = self.creator_relationships.get(creator_id)
        
        profile = {
            "creator_info": asdict(creator),
            "crm_metadata": {
                "added_date": "2024-01-15",  # Would be actual date
                "last_updated": datetime.now().isoformat(),
                "verification_status": "verified",
                "data_completeness": self._calculate_profile_completeness(creator)
            }
        }
        
        if include_insights and insights:
            profile["insights"] = asdict(insights)
            profile["relationship"] = asdict(relationship)
            profile["performance_summary"] = await self._get_creator_performance_summary(creator_id)
            profile["collaboration_history"] = await self._get_collaboration_history(creator_id)
            profile["market_analysis"] = await self._get_creator_market_analysis(creator)
        
        return {
            "status": "found",
            "profile": profile,
            "recommendations": await self._generate_creator_recommendations(creator_id)
        }
    
    async def search_creators(
        self,
        filters: Dict[str, Any],
        sort_by: str = "performance_score",
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        🔍 Advanced creator search with filters
        """
        
        try:
            # Apply filters
            filtered_creators = await self._apply_search_filters(filters)
            
            # Apply AI scoring if available
            if self.groq_client and filters.get("ai_ranking", False):
                filtered_creators = await self._apply_ai_ranking(filtered_creators, filters)
            
            # Sort results
            sorted_creators = await self._sort_creators(filtered_creators, sort_by)
            
            # Limit results
            results = sorted_creators[:limit]
            
            # Generate search insights
            search_insights = await self._generate_search_insights(filters, results)
            
            return {
                "status": "success",
                "results": results,
                "total_found": len(filtered_creators),
                "returned": len(results),
                "search_insights": search_insights,
                "filters_applied": filters,
                "suggestions": await self._generate_search_suggestions(filters, results)
            }
            
        except Exception as e:
            logger.error(f"❌ Creator search failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def update_creator_performance(
        self,
        creator_id: str,
        campaign_id: str,
        performance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        📊 Update creator performance data
        """
        
        try:
            if creator_id not in self.creator_database:
                return {"status": "error", "error": "Creator not found"}
            
            # Store performance data
            if creator_id not in self.performance_history:
                self.performance_history[creator_id] = []
            
            performance_record = {
                "campaign_id": campaign_id,
                "date": datetime.now().isoformat(),
                "metrics": performance_data,
                "calculated_scores": {}
            }
            
            # Calculate performance scores
            performance_record["calculated_scores"] = {
                "engagement_score": self._calculate_engagement_score(performance_data),
                "roi_score": self._calculate_roi_score(performance_data),
                "quality_score": self._calculate_content_quality_score(performance_data)
            }
            
            self.performance_history[creator_id].append(performance_record)
            
            # Update creator insights
            await self._update_creator_insights(creator_id)
            
            # Update relationship quality
            await self._update_relationship_quality(creator_id, performance_data)
            
            logger.info(f"📊 Performance updated for {creator_id}")
            
            return {
                "status": "updated",
                "performance_record": performance_record,
                "updated_insights": asdict(self.creator_insights[creator_id]),
                "trend_analysis": await self._analyze_performance_trends(creator_id)
            }
            
        except Exception as e:
            logger.error(f"❌ Performance update failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_creator_recommendations(
        self,
        campaign_brief: Dict[str, Any],
        max_recommendations: int = 10
    ) -> Dict[str, Any]:
        """
        🎯 Get AI-powered creator recommendations for campaign
        """
        
        try:
            # Generate AI-powered recommendations
            if self.groq_client:
                recommendations = await self._ai_creator_recommendations(campaign_brief)
            else:
                recommendations = await self._basic_creator_recommendations(campaign_brief)
            
            # Enhance with CRM data
            enhanced_recommendations = []
            
            for rec in recommendations[:max_recommendations]:
                creator_id = rec["creator_id"]
                if creator_id in self.creator_database:
                    creator = self.creator_database[creator_id]
                    insights = self.creator_insights.get(creator_id)
                    relationship = self.creator_relationships.get(creator_id)
                    
                    enhanced_rec = {
                        **rec,
                        "creator_profile": {
                            "name": creator.name,
                            "platform": creator.platform.value,
                            "followers": creator.followers,
                            "engagement_rate": creator.engagement_rate,
                            "typical_rate": creator.typical_rate
                        },
                        "crm_insights": {
                            "performance_score": insights.performance_score if insights else 0,
                            "reliability_score": insights.reliability_score if insights else 0,
                            "relationship_quality": relationship.relationship_quality.value if relationship else "unknown",
                            "collaboration_history": relationship.total_collaborations if relationship else 0
                        },
                        "recommendation_reasons": rec.get("reasons", []),
                        "estimated_performance": await self._predict_campaign_performance(creator_id, campaign_brief)
                    }
                    
                    enhanced_recommendations.append(enhanced_rec)
            
            return {
                "status": "success",
                "recommendations": enhanced_recommendations,
                "campaign_brief": campaign_brief,
                "recommendation_strategy": "ai_powered_crm_enhanced",
                "alternatives": await self._get_alternative_recommendations(campaign_brief, enhanced_recommendations)
            }
            
        except Exception as e:
            logger.error(f"❌ Creator recommendations failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def manage_creator_outreach(
        self,
        creator_ids: List[str],
        campaign_id: str,
        outreach_template: str,
        scheduling: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        📧 Manage automated creator outreach
        """
        
        try:
            outreach_results = []
            
            for creator_id in creator_ids:
                if creator_id not in self.creator_database:
                    outreach_results.append({
                        "creator_id": creator_id,
                        "status": "error",
                        "error": "Creator not found"
                    })
                    continue
                
                creator = self.creator_database[creator_id]
                relationship = self.creator_relationships.get(creator_id)
                
                # Personalize outreach message
                personalized_message = await self._personalize_outreach_message(
                    outreach_template, creator, relationship
                )
                
                # Determine optimal outreach time
                optimal_time = await self._calculate_optimal_outreach_time(creator_id)
                
                # Send outreach (mock for demo)
                outreach_result = await self._send_outreach_message(
                    creator, personalized_message, optimal_time
                )
                
                # Update relationship tracking
                if relationship:
                    relationship.last_interaction_date = datetime.now()
                    if "notes" not in relationship.__dict__:
                        relationship.notes = []
                    relationship.notes.append({
                        "date": datetime.now().isoformat(),
                        "type": "outreach",
                        "campaign_id": campaign_id,
                        "message": personalized_message[:100] + "..."
                    })
                
                outreach_results.append({
                    "creator_id": creator_id,
                    "creator_name": creator.name,
                    "status": outreach_result["status"],
                    "scheduled_time": optimal_time,
                    "personalization_applied": True,
                    "message_preview": personalized_message[:100] + "..."
                })
            
            return {
                "status": "processed",
                "campaign_id": campaign_id,
                "outreach_results": outreach_results,
                "summary": {
                    "total_creators": len(creator_ids),
                    "successful_outreach": len([r for r in outreach_results if r["status"] == "success"]),
                    "failed_outreach": len([r for r in outreach_results if r["status"] == "error"])
                },
                "follow_up_scheduled": True
            }
            
        except Exception as e:
            logger.error(f"❌ Outreach management failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_crm_analytics(self, time_period: str = "30_days") -> Dict[str, Any]:
        """
        📈 Get comprehensive CRM analytics
        """
        
        try:
            # Calculate time range
            if time_period == "30_days":
                start_date = datetime.now() - timedelta(days=30)
            elif time_period == "90_days":
                start_date = datetime.now() - timedelta(days=90)
            else:
                start_date = datetime.now() - timedelta(days=30)
            
            # Creator metrics
            total_creators = len(self.creator_database)
            active_creators = len([c for c in self.creator_database.values() if c.availability != Availability.BUSY])
            
            # Platform distribution
            platform_distribution = {}
            for creator in self.creator_database.values():
                platform = creator.platform.value
                platform_distribution[platform] = platform_distribution.get(platform, 0) + 1
            
            # Tier distribution
            tier_distribution = {}
            for creator in self.creator_database.values():
                tier = creator.tier.value
                tier_distribution[tier] = tier_distribution.get(tier, 0) + 1
            
            # Performance insights
            avg_performance_score = np.mean([
                insights.performance_score for insights in self.creator_insights.values()
            ]) if self.creator_insights else 0
            
            # Relationship quality distribution
            relationship_quality_dist = {}
            for relationship in self.creator_relationships.values():
                quality = relationship.relationship_quality.value
                relationship_quality_dist[quality] = relationship_quality_dist.get(quality, 0) + 1
            
            # Market insights
            market_insights = await self._generate_market_insights()
            
            return {
                "time_period": time_period,
                "creator_metrics": {
                    "total_creators": total_creators,
                    "active_creators": active_creators,
                    "activation_rate": (active_creators / max(total_creators, 1)) * 100,
                    "new_creators_this_period": 5,  # Mock data
                    "average_performance_score": round(avg_performance_score, 2)
                },
                "distribution_analysis": {
                    "by_platform": platform_distribution,
                    "by_tier": tier_distribution,
                    "by_relationship_quality": relationship_quality_dist
                },
                "performance_trends": {
                    "top_performing_creators": await self._get_top_performers(5),
                    "improving_creators": await self._get_improving_creators(5),
                    "at_risk_creators": await self._get_at_risk_creators(5)
                },
                "market_insights": market_insights,
                "recommendations": await self._generate_crm_recommendations()
            }
            
        except Exception as e:
            logger.error(f"❌ CRM analytics failed: {e}")
            return {"status": "error", "error": str(e)}
    
    # Private helper methods
    
    def _initialize_creator_database(self):
        """Initialize CRM with existing creators"""
        
        try:
            # Load existing creators from discovery agent
            from agents.discovery import InfluencerDiscoveryAgent
            discovery_agent = InfluencerDiscoveryAgent()
            
            for creator in discovery_agent.creators_data:
                # Add to CRM database
                self.creator_database[creator.id] = creator
                
                # Generate initial insights
                insights = CreatorInsights(
                    performance_score=0.75 + np.random.uniform(-0.15, 0.15),
                    reliability_score=0.8 + np.random.uniform(-0.2, 0.15),
                    growth_trend="stable",
                    market_rate_trend="increasing",
                    collaboration_history_count=np.random.randint(0, 8),
                    average_campaign_performance=0.7 + np.random.uniform(-0.2, 0.2),
                    preferred_brands=[],
                    content_quality_score=0.8 + np.random.uniform(-0.15, 0.15),
                    audience_authenticity_score=0.85 + np.random.uniform(-0.1, 0.1),
                    response_time_hours=np.random.uniform(2, 24)
                )
                
                self.creator_insights[creator.id] = insights
                
                # Initialize relationship
                relationship = CreatorRelationship(
                    relationship_quality=RelationshipQuality.UNKNOWN,
                    total_collaborations=np.random.randint(0, 5),
                    total_revenue_generated=np.random.uniform(0, 25000),
                    average_campaign_satisfaction=0.7 + np.random.uniform(-0.2, 0.25),
                    last_interaction_date=datetime.now() - timedelta(days=np.random.randint(1, 90)),
                    preferred_communication_method="email",
                    special_rates=None,
                    exclusivity_agreements=[],
                    notes=[]
                )
                
                self.creator_relationships[creator.id] = relationship
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize creator database: {e}")
    
    async def _validate_creator_data(self, creator_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate creator data before adding to CRM"""
        
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        # Required fields
        required_fields = ["id", "name", "platform", "followers", "niche"]
        for field in required_fields:
            if field not in creator_data or not creator_data[field]:
                validation_result["errors"].append(f"Missing required field: {field}")
                validation_result["is_valid"] = False
        
        # Data quality checks
        if "followers" in creator_data:
            followers = creator_data["followers"]
            if not isinstance(followers, int) or followers < 100:
                validation_result["warnings"].append("Follower count seems low or invalid")
        
        if "engagement_rate" in creator_data:
            engagement = creator_data["engagement_rate"]
            if engagement > 20 or engagement < 0.5:
                validation_result["warnings"].append("Engagement rate outside normal range")
        
        return validation_result
    
    async def _generate_creator_insights(self, creator: Creator) -> CreatorInsights:
        """Generate AI-powered creator insights"""
        
        if not self.groq_client:
            return self._generate_basic_insights(creator)
        
        try:
            # Create analysis prompt
            prompt = f"""
            Analyze this creator and provide insights. Return JSON only.
            
            Creator: {creator.name}
            Platform: {creator.platform.value}
            Followers: {creator.followers:,}
            Niche: {creator.niche}
            Engagement: {creator.engagement_rate}%
            Location: {creator.location}
            
            Return insights as JSON:
            {{
                "performance_score": 0.0-1.0,
                "reliability_score": 0.0-1.0,
                "growth_trend": "growing|stable|declining",
                "market_rate_trend": "increasing|stable|decreasing",
                "content_quality_score": 0.0-1.0,
                "audience_authenticity_score": 0.0-1.0,
                "response_time_hours": 1.0-48.0
            }}
            """
            
            response = self.groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=300
            )
            
            insights_text = response.choices[0].message.content.strip()
            json_start = insights_text.find('{')
            json_end = insights_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                insights_data = json.loads(insights_text[json_start:json_end])
                
                return CreatorInsights(
                    performance_score=insights_data.get("performance_score", 0.7),
                    reliability_score=insights_data.get("reliability_score", 0.8),
                    growth_trend=insights_data.get("growth_trend", "stable"),
                    market_rate_trend=insights_data.get("market_rate_trend", "stable"),
                    collaboration_history_count=0,
                    average_campaign_performance=0.7,
                    preferred_brands=[],
                    content_quality_score=insights_data.get("content_quality_score", 0.8),
                    audience_authenticity_score=insights_data.get("audience_authenticity_score", 0.85),
                    response_time_hours=insights_data.get("response_time_hours", 12.0)
                )
            else:
                return self._generate_basic_insights(creator)
                
        except Exception as e:
            logger.error(f"❌ AI insights generation failed: {e}")
            return self._generate_basic_insights(creator)
    
    def _generate_basic_insights(self, creator: Creator) -> CreatorInsights:
        """Generate basic insights when AI fails"""
        
        # Simple heuristic-based insights
        performance_score = min(creator.engagement_rate / 10, 1.0)
        
        tier_score_map = {
            CreatorTier.MICRO: 0.8,
            CreatorTier.MACRO: 0.75,
            CreatorTier.MEGA: 0.7
        }
        
        reliability_score = tier_score_map.get(creator.tier, 0.75)
        
        return CreatorInsights(
            performance_score=performance_score,
            reliability_score=reliability_score,
            growth_trend="stable",
            market_rate_trend="stable",
            collaboration_history_count=0,
            average_campaign_performance=0.7,
            preferred_brands=[],
            content_quality_score=0.8,
            audience_authenticity_score=0.85,
            response_time_hours=12.0
        )
    
    async def _apply_search_filters(self, filters: Dict[str, Any]) -> List[str]:
        """Apply search filters to creator database"""
        
        filtered_creator_ids = []
        
        for creator_id, creator in self.creator_database.items():
            # Platform filter
            if "platforms" in filters:
                if creator.platform.value not in filters["platforms"]:
                    continue
            
            # Follower range filter
            if "min_followers" in filters:
                if creator.followers < filters["min_followers"]:
                    continue
            
            if "max_followers" in filters:
                if creator.followers > filters["max_followers"]:
                    continue
            
            # Niche filter
            if "niches" in filters:
                if creator.niche not in filters["niches"]:
                    continue
            
            # Engagement filter
            if "min_engagement" in filters:
                if creator.engagement_rate < filters["min_engagement"]:
                    continue
            
            # Performance score filter
            if "min_performance_score" in filters:
                insights = self.creator_insights.get(creator_id)
                if not insights or insights.performance_score < filters["min_performance_score"]:
                    continue
            
            # Location filter
            if "locations" in filters:
                if not any(loc.lower() in creator.location.lower() for loc in filters["locations"]):
                    continue
            
            filtered_creator_ids.append(creator_id)
        
        return filtered_creator_ids
    
    async def _sort_creators(self, creator_ids: List[str], sort_by: str) -> List[Dict[str, Any]]:
        """Sort creators by specified criteria"""
        
        creator_data = []
        
        for creator_id in creator_ids:
            creator = self.creator_database[creator_id]
            insights = self.creator_insights.get(creator_id)
            relationship = self.creator_relationships.get(creator_id)
            
            sort_value = 0
            
            if sort_by == "performance_score":
                sort_value = insights.performance_score if insights else 0
            elif sort_by == "followers":
                sort_value = creator.followers
            elif sort_by == "engagement_rate":
                sort_value = creator.engagement_rate
            elif sort_by == "reliability_score":
                sort_value = insights.reliability_score if insights else 0
            elif sort_by == "collaboration_count":
                sort_value = relationship.total_collaborations if relationship else 0
            
            creator_data.append({
                "creator_id": creator_id,
                "creator": asdict(creator),
                "insights": asdict(insights) if insights else {},
                "relationship": asdict(relationship) if relationship else {},
                "sort_value": sort_value
            })
        
        # Sort by sort_value in descending order
        creator_data.sort(key=lambda x: x["sort_value"], reverse=True)
        
        return creator_data
    
    # Additional helper methods would continue here...
    # For brevity, I'll add a few key ones:
    
    def _calculate_profile_completeness(self, creator: Creator) -> float:
        """Calculate how complete a creator profile is"""
        
        required_fields = [
            creator.name, creator.platform, creator.followers, creator.niche,
            creator.typical_rate, creator.engagement_rate, creator.location,
            creator.phone_number, creator.languages, creator.specialties
        ]
        
        completed_fields = sum(1 for field in required_fields if field)
        return completed_fields / len(required_fields)
    
    async def _get_creator_performance_summary(self, creator_id: str) -> Dict[str, Any]:
        """Get performance summary for creator"""
        
        performance_data = self.performance_history.get(creator_id, [])
        
        if not performance_data:
            return {"status": "no_data", "message": "No performance data available"}
        
        # Calculate averages
        avg_engagement = np.mean([p["calculated_scores"]["engagement_score"] for p in performance_data])
        avg_roi = np.mean([p["calculated_scores"]["roi_score"] for p in performance_data])
        
        return {
            "total_campaigns": len(performance_data),
            "average_engagement_score": round(avg_engagement, 2),
            "average_roi_score": round(avg_roi, 2),
            "trend": "improving" if len(performance_data) > 1 else "insufficient_data",
            "last_campaign_date": performance_data[-1]["date"] if performance_data else None
        }
    
    async def _get_collaboration_history(self, creator_id: str) -> List[Dict[str, Any]]:
        """Get collaboration history for creator"""
        
        # Mock collaboration history
        return [
            {
                "campaign_id": "camp_001",
                "brand": "FitTech",
                "date": "2024-11-15",
                "performance": "excellent",
                "satisfaction_score": 4.8
            }
        ]
    
    async def _generate_creator_recommendations(self, creator_id: str) -> List[str]:
        """Generate recommendations for creator optimization"""
        
        creator = self.creator_database[creator_id]
        insights = self.creator_insights.get(creator_id)
        
        recommendations = []
        
        if insights and insights.performance_score < 0.6:
            recommendations.append("Consider providing content guidelines to improve performance")
        
        if insights and insights.response_time_hours > 24:
            recommendations.append("Follow up on communication response times")
        
        if creator.engagement_rate < 3.0:
            recommendations.append("Monitor for potential audience quality issues")
        
        return recommendations
    
    # Mock methods for demo purposes
    
    async def _comprehensive_creator_verification(self, creator: Creator) -> Dict[str, Any]:
        """Comprehensive creator verification (mock)"""
        return {"authenticity_score": 0.85 + np.random.uniform(-0.1, 0.1)}
    
    async def _ai_creator_recommendations(self, campaign_brief: Dict[str, Any]) -> List[Dict[str, Any]]:
        """AI-powered creator recommendations (mock)"""
        
        # Return top creators from database
        recommendations = []
        for creator_id, creator in list(self.creator_database.items())[:5]:
            recommendations.append({
                "creator_id": creator_id,
                "match_score": 0.7 + np.random.uniform(0, 0.25),
                "reasons": ["Strong niche alignment", "Good engagement rate", "Reliable history"]
            })
        
        return recommendations
    
    async def _basic_creator_recommendations(self, campaign_brief: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Basic creator recommendations fallback"""
        return await self._ai_creator_recommendations(campaign_brief)
    
    def _calculate_engagement_score(self, performance_data: Dict[str, Any]) -> float:
        """Calculate engagement score from performance data"""
        return performance_data.get("engagement_rate", 5.0) / 10
    
    def _calculate_roi_score(self, performance_data: Dict[str, Any]) -> float:
        """Calculate ROI score from performance data"""
        return min(performance_data.get("roi_percentage", 100) / 200, 1.0)
    
    def _calculate_content_quality_score(self, performance_data: Dict[str, Any]) -> float:
        """Calculate content quality score"""
        return performance_data.get("quality_rating", 8.0) / 10
    
    async def _update_creator_insights(self, creator_id: str):
        """Update creator insights based on new performance data"""
        
        insights = self.creator_insights.get(creator_id)
        if insights:
            # Recalculate performance score based on recent data
            performance_data = self.performance_history.get(creator_id, [])
            if performance_data:
                recent_scores = [p["calculated_scores"]["engagement_score"] for p in performance_data[-3:]]
                insights.performance_score = np.mean(recent_scores)
    
    async def _update_relationship_quality(self, creator_id: str, performance_data: Dict[str, Any]):
        """Update relationship quality based on performance"""
        
        relationship = self.creator_relationships.get(creator_id)
        if relationship:
            # Improve relationship quality for good performance
            roi_score = self._calculate_roi_score(performance_data)
            if roi_score > 0.8:
                if relationship.relationship_quality == RelationshipQuality.AVERAGE:
                    relationship.relationship_quality = RelationshipQuality.GOOD
                elif relationship.relationship_quality == RelationshipQuality.GOOD:
                    relationship.relationship_quality = RelationshipQuality.EXCELLENT
    
    # Additional mock methods for completeness
    
    async def _generate_market_insights(self) -> Dict[str, Any]:
        """Generate market insights (mock)"""
        return {
            "trending_niches": ["fitness", "tech", "sustainability"],
            "rate_trends": "increasing",
            "platform_performance": {"Instagram": "stable", "TikTok": "growing", "YouTube": "stable"}
        }
    
    async def _get_top_performers(self, limit: int) -> List[Dict[str, Any]]:
        """Get top performing creators"""
        return [{"creator_id": "sarah_tech", "score": 0.92}]
    
    async def _get_improving_creators(self, limit: int) -> List[Dict[str, Any]]:
        """Get creators showing improvement"""
        return [{"creator_id": "mike_fitness", "improvement": 15.3}]
    
    async def _get_at_risk_creators(self, limit: int) -> List[Dict[str, Any]]:
        """Get creators at risk"""
        return [{"creator_id": "priya_beauty", "risk_factors": ["declining engagement"]}]
    
    async def _generate_crm_recommendations(self) -> List[str]:
        """Generate CRM recommendations"""
        return [
            "Focus on nurturing high-performing creators",
            "Improve outreach response rates",
            "Expand creator base in trending niches"
        ]