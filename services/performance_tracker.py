# services/performance_tracker.py
import asyncio
import logging
import json
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

import numpy as np
from groq import Groq
from config.settings import settings

logger = logging.getLogger(__name__)

class PerformanceStatus(str, Enum):
    TRACKING = "tracking"
    COMPLETED = "completed"
    UNDERPERFORMING = "underperforming"
    OVERPERFORMING = "overperforming"
    STALLED = "stalled"

@dataclass
class ContentMetrics:
    views: int
    likes: int
    comments: int
    shares: int
    saves: int
    clicks: int
    engagement_rate: float
    reach: int
    impressions: int
    
    @property
    def total_engagement(self) -> int:
        return self.likes + self.comments + self.shares + self.saves

class PerformanceTracker:
    """
    📊 PERFORMANCE TRACKER - Real-time Campaign Analytics
    
    Features:
    - Real-time content performance monitoring
    - Social media API integration
    - AI-powered performance analysis
    - Automated reporting and alerts
    - ROI calculation and attribution
    - Predictive performance modeling
    """
    
    def __init__(self):
        self.groq_client = Groq(api_key=settings.groq_api_key) if settings.groq_api_key else None
        
        # API connections for tracking
        self.api_connections = {
            "instagram": self._initialize_instagram_api(),
            "youtube": self._initialize_youtube_api(),
            "tiktok": self._initialize_tiktok_api(),
            "google_analytics": self._initialize_ga_api()
        }
        
        # Tracking configuration
        self.tracking_config = {
            "update_frequency_minutes": 30,
            "alert_thresholds": {
                "underperformance": 0.7,  # 70% of expected
                "overperformance": 1.5,   # 150% of expected
                "engagement_drop": 0.5    # 50% drop from baseline
            },
            "performance_windows": {
                "initial": 24,    # First 24 hours
                "short_term": 168, # First week
                "long_term": 720   # First month
            }
        }
        
        # Active tracking campaigns
        self.tracked_campaigns = {}
        
        logger.info("📊 Performance Tracker initialized")
    
    async def start_campaign_tracking(
        self,
        campaign_id: str,
        campaign_data: Dict[str, Any],
        creator_content: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        🚀 Start tracking a new campaign
        """
        
        try:
            logger.info(f"📊 Starting performance tracking for campaign {campaign_id}")
            
            # Initialize tracking record
            tracking_record = {
                "campaign_id": campaign_id,
                "campaign_data": campaign_data,
                "creators": {},
                "performance_metrics": {
                    "total_reach": 0,
                    "total_engagement": 0,
                    "total_clicks": 0,
                    "conversion_rate": 0.0,
                    "roi": 0.0
                },
                "status": PerformanceStatus.TRACKING.value,
                "started_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "alerts": [],
                "insights": []
            }
            
            # Set up creator content tracking
            for content in creator_content:
                creator_id = content["creator_id"]
                tracking_record["creators"][creator_id] = {
                    "creator_data": content,
                    "content_items": [],
                    "metrics": self._initialize_creator_metrics(),
                    "performance_predictions": {},
                    "status": "pending_content"
                }
            
            # Store tracking record
            self.tracked_campaigns[campaign_id] = tracking_record
            
            # Start background tracking task
            asyncio.create_task(self._background_tracking_loop(campaign_id))
            
            return {
                "status": "tracking_started",
                "campaign_id": campaign_id,
                "creators_tracked": len(creator_content),
                "tracking_frequency": f"{self.tracking_config['update_frequency_minutes']} minutes",
                "dashboard_url": f"/api/performance/campaign/{campaign_id}/dashboard"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to start campaign tracking: {e}")
            return {"status": "error", "error": str(e)}
    
    async def track_content_item(
        self,
        campaign_id: str,
        creator_id: str,
        content_url: str,
        platform: str,
        content_type: str = "post"
    ) -> Dict[str, Any]:
        """
        📱 Add specific content item for tracking
        """
        
        try:
            if campaign_id not in self.tracked_campaigns:
                return {"status": "error", "error": "Campaign not being tracked"}
            
            campaign = self.tracked_campaigns[campaign_id]
            
            if creator_id not in campaign["creators"]:
                return {"status": "error", "error": "Creator not found in campaign"}
            
            # Extract content ID from URL
            content_id = self._extract_content_id(content_url, platform)
            
            # Initialize content tracking
            content_item = {
                "content_id": content_id,
                "url": content_url,
                "platform": platform,
                "content_type": content_type,
                "posted_at": datetime.now().isoformat(),
                "metrics_history": [],
                "current_metrics": self._initialize_content_metrics(),
                "performance_score": 0.0,
                "tracking_status": "active"
            }
            
            # Add to creator's content items
            campaign["creators"][creator_id]["content_items"].append(content_item)
            campaign["creators"][creator_id]["status"] = "content_published"
            
            # Get initial metrics
            initial_metrics = await self._fetch_content_metrics(content_url, platform)
            if initial_metrics:
                content_item["current_metrics"] = initial_metrics
            
            logger.info(f"📱 Content tracking started: {platform} content for {creator_id}")
            
            return {
                "status": "tracking_added",
                "content_id": content_id,
                "platform": platform,
                "initial_metrics": initial_metrics
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to track content item: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_campaign_performance_dashboard(self, campaign_id: str) -> Dict[str, Any]:
        """
        📊 Get comprehensive performance dashboard
        """
        
        try:
            if campaign_id not in self.tracked_campaigns:
                return {"status": "not_found", "campaign_id": campaign_id}
            
            campaign = self.tracked_campaigns[campaign_id]
            
            # Calculate current performance metrics
            performance_summary = await self._calculate_campaign_performance(campaign)
            
            # Get creator performance breakdown
            creator_performance = await self._get_creator_performance_breakdown(campaign)
            
            # Generate AI insights
            ai_insights = await self._generate_ai_performance_insights(campaign)
            
            # Get performance trends
            performance_trends = self._calculate_performance_trends(campaign)
            
            # Check for alerts
            current_alerts = self._check_performance_alerts(campaign, performance_summary)
            
            return {
                "campaign_id": campaign_id,
                "campaign_info": {
                    "name": f"{campaign['campaign_data'].get('brand_name', 'Brand')} - {campaign['campaign_data'].get('product_name', 'Product')}",
                    "status": campaign["status"],
                    "started_at": campaign["started_at"],
                    "days_active": (datetime.now() - datetime.fromisoformat(campaign["started_at"])).days,
                    "creators_count": len(campaign["creators"])
                },
                "performance_summary": performance_summary,
                "creator_performance": creator_performance,
                "performance_trends": performance_trends,
                "ai_insights": ai_insights,
                "alerts": current_alerts,
                "recommendations": await self._generate_performance_recommendations(campaign),
                "export_options": {
                    "detailed_report": f"/api/performance/campaign/{campaign_id}/report",
                    "csv_export": f"/api/performance/campaign/{campaign_id}/export/csv",
                    "pdf_report": f"/api/performance/campaign/{campaign_id}/export/pdf"
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Dashboard generation failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _background_tracking_loop(self, campaign_id: str):
        """
        🔄 Background loop for continuous performance tracking
        """
        
        logger.info(f"🔄 Starting background tracking for {campaign_id}")
        
        try:
            while campaign_id in self.tracked_campaigns:
                campaign = self.tracked_campaigns[campaign_id]
                
                # Skip if campaign is completed
                if campaign["status"] == PerformanceStatus.COMPLETED.value:
                    break
                
                # Update metrics for all content items
                await self._update_all_content_metrics(campaign)
                
                # Check for performance alerts
                await self._check_and_send_alerts(campaign)
                
                # Update campaign status
                await self._update_campaign_status(campaign)
                
                # Sleep until next update
                await asyncio.sleep(self.tracking_config["update_frequency_minutes"] * 60)
                
        except Exception as e:
            logger.error(f"❌ Background tracking failed for {campaign_id}: {e}")
        
        logger.info(f"🔄 Background tracking stopped for {campaign_id}")
    
    async def _update_all_content_metrics(self, campaign: Dict[str, Any]):
        """Update metrics for all content items in campaign"""
        
        for creator_id, creator_data in campaign["creators"].items():
            for content_item in creator_data["content_items"]:
                if content_item["tracking_status"] == "active":
                    # Fetch latest metrics
                    latest_metrics = await self._fetch_content_metrics(
                        content_item["url"], 
                        content_item["platform"]
                    )
                    
                    if latest_metrics:
                        # Store metrics history
                        content_item["metrics_history"].append({
                            "timestamp": datetime.now().isoformat(),
                            "metrics": latest_metrics
                        })
                        
                        # Update current metrics
                        content_item["current_metrics"] = latest_metrics
                        
                        # Calculate performance score
                        content_item["performance_score"] = self._calculate_content_performance_score(
                            content_item, creator_data
                        )
        
        # Update campaign last updated timestamp
        campaign["last_updated"] = datetime.now().isoformat()
    
    async def _fetch_content_metrics(self, content_url: str, platform: str) -> Optional[ContentMetrics]:
        """
        📱 Fetch metrics from social media APIs
        """
        
        try:
            if platform.lower() == "instagram":
                return await self._fetch_instagram_metrics(content_url)
            elif platform.lower() == "youtube":
                return await self._fetch_youtube_metrics(content_url)
            elif platform.lower() == "tiktok":
                return await self._fetch_tiktok_metrics(content_url)
            else:
                return self._generate_mock_metrics(platform)
                
        except Exception as e:
            logger.error(f"❌ Failed to fetch {platform} metrics: {e}")
            return self._generate_mock_metrics(platform)
    
    async def _fetch_instagram_metrics(self, content_url: str) -> ContentMetrics:
        """Fetch Instagram metrics (mock implementation)"""
        
        # In production, this would use Instagram Graph API
        # For now, generate realistic mock data
        
        base_views = np.random.randint(5000, 50000)
        engagement_rate = np.random.uniform(3.0, 8.0)
        
        likes = int(base_views * engagement_rate * 0.6 / 100)
        comments = int(base_views * engagement_rate * 0.15 / 100)
        shares = int(base_views * engagement_rate * 0.1 / 100)
        saves = int(base_views * engagement_rate * 0.15 / 100)
        
        return ContentMetrics(
            views=base_views,
            likes=likes,
            comments=comments,
            shares=shares,
            saves=saves,
            clicks=int(base_views * 0.02),  # 2% click-through rate
            engagement_rate=engagement_rate,
            reach=int(base_views * 0.85),
            impressions=int(base_views * 1.2)
        )
    
    async def _fetch_youtube_metrics(self, content_url: str) -> ContentMetrics:
        """Fetch YouTube metrics (mock implementation)"""
        
        base_views = np.random.randint(10000, 100000)
        engagement_rate = np.random.uniform(4.0, 12.0)
        
        likes = int(base_views * engagement_rate * 0.7 / 100)
        comments = int(base_views * engagement_rate * 0.2 / 100)
        shares = int(base_views * engagement_rate * 0.1 / 100)
        
        return ContentMetrics(
            views=base_views,
            likes=likes,
            comments=comments,
            shares=shares,
            saves=0,  # YouTube doesn't have saves
            clicks=int(base_views * 0.03),  # 3% click-through rate
            engagement_rate=engagement_rate,
            reach=int(base_views * 0.9),
            impressions=int(base_views * 1.5)
        )
    
    async def _fetch_tiktok_metrics(self, content_url: str) -> ContentMetrics:
        """Fetch TikTok metrics (mock implementation)"""
        
        base_views = np.random.randint(20000, 200000)
        engagement_rate = np.random.uniform(6.0, 15.0)
        
        likes = int(base_views * engagement_rate * 0.8 / 100)
        comments = int(base_views * engagement_rate * 0.1 / 100)
        shares = int(base_views * engagement_rate * 0.1 / 100)
        
        return ContentMetrics(
            views=base_views,
            likes=likes,
            comments=comments,
            shares=shares,
            saves=0,
            clicks=int(base_views * 0.015),  # 1.5% click-through rate
            engagement_rate=engagement_rate,
            reach=int(base_views * 0.95),
            impressions=int(base_views * 1.1)
        )
    
    def _generate_mock_metrics(self, platform: str) -> ContentMetrics:
        """Generate mock metrics for testing"""
        
        platform_multipliers = {
            "instagram": 1.0,
            "youtube": 2.0,
            "tiktok": 3.0,
            "twitter": 0.5
        }
        
        multiplier = platform_multipliers.get(platform.lower(), 1.0)
        base_views = int(np.random.randint(5000, 30000) * multiplier)
        engagement_rate = np.random.uniform(3.0, 8.0)
        
        return ContentMetrics(
            views=base_views,
            likes=int(base_views * 0.05),
            comments=int(base_views * 0.01),
            shares=int(base_views * 0.005),
            saves=int(base_views * 0.008),
            clicks=int(base_views * 0.02),
            engagement_rate=engagement_rate,
            reach=int(base_views * 0.8),
            impressions=int(base_views * 1.2)
        )
    
    async def _calculate_campaign_performance(self, campaign: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall campaign performance metrics"""
        
        total_views = 0
        total_engagement = 0
        total_clicks = 0
        total_reach = 0
        content_count = 0
        
        # Aggregate metrics across all creators and content
        for creator_data in campaign["creators"].values():
            for content_item in creator_data["content_items"]:
                metrics = content_item["current_metrics"]
                if isinstance(metrics, dict):
                    total_views += metrics.get("views", 0)
                    total_engagement += (
                        metrics.get("likes", 0) + 
                        metrics.get("comments", 0) + 
                        metrics.get("shares", 0) + 
                        metrics.get("saves", 0)
                    )
                    total_clicks += metrics.get("clicks", 0)
                    total_reach += metrics.get("reach", 0)
                    content_count += 1
        
        # Calculate rates
        avg_engagement_rate = (total_engagement / max(total_views, 1)) * 100
        click_through_rate = (total_clicks / max(total_views, 1)) * 100
        
        # Calculate cost metrics
        campaign_cost = campaign["campaign_data"].get("total_budget", 0)
        cost_per_view = campaign_cost / max(total_views, 1)
        cost_per_click = campaign_cost / max(total_clicks, 1)
        
        # Estimate conversions (mock)
        estimated_conversions = int(total_clicks * 0.02)  # 2% conversion rate
        cost_per_conversion = campaign_cost / max(estimated_conversions, 1)
        
        # Calculate ROI (mock revenue)
        estimated_revenue = estimated_conversions * 75  # $75 average order value
        roi_percentage = ((estimated_revenue - campaign_cost) / max(campaign_cost, 1)) * 100
        
        return {
            "reach_metrics": {
                "total_views": total_views,
                "total_reach": total_reach,
                "unique_viewers_estimated": int(total_reach * 0.8)
            },
            "engagement_metrics": {
                "total_engagements": total_engagement,
                "average_engagement_rate": round(avg_engagement_rate, 2),
                "engagement_quality_score": self._calculate_engagement_quality_score(campaign)
            },
            "conversion_metrics": {
                "total_clicks": total_clicks,
                "click_through_rate": round(click_through_rate, 2),
                "estimated_conversions": estimated_conversions,
                "conversion_rate": 2.0  # Mock conversion rate
            },
            "cost_metrics": {
                "total_spend": campaign_cost,
                "cost_per_view": round(cost_per_view, 4),
                "cost_per_click": round(cost_per_click, 2),
                "cost_per_conversion": round(cost_per_conversion, 2)
            },
            "roi_metrics": {
                "estimated_revenue": estimated_revenue,
                "roi_percentage": round(roi_percentage, 2),
                "roas": round(estimated_revenue / max(campaign_cost, 1), 2)
            },
            "content_metrics": {
                "total_content_pieces": content_count,
                "average_performance_score": self._calculate_average_content_score(campaign)
            }
        }
    
    async def _get_creator_performance_breakdown(self, campaign: Dict[str, Any]) -> Dict[str, Any]:
        """Get performance breakdown by creator"""
        
        creator_breakdown = {}
        
        for creator_id, creator_data in campaign["creators"].items():
            creator_metrics = {
                "creator_info": {
                    "id": creator_id,
                    "name": creator_data["creator_data"].get("name", creator_id),
                    "platform": creator_data["creator_data"].get("platform", "Unknown"),
                    "content_count": len(creator_data["content_items"])
                },
                "performance": {
                    "total_views": 0,
                    "total_engagement": 0,
                    "total_clicks": 0,
                    "avg_engagement_rate": 0.0,
                    "performance_score": 0.0
                },
                "content_breakdown": [],
                "status": creator_data["status"]
            }
            
            # Calculate creator-specific metrics
            for content_item in creator_data["content_items"]:
                metrics = content_item["current_metrics"]
                
                if isinstance(metrics, dict):
                    creator_metrics["performance"]["total_views"] += metrics.get("views", 0)
                    creator_metrics["performance"]["total_engagement"] += (
                        metrics.get("likes", 0) + metrics.get("comments", 0) + 
                        metrics.get("shares", 0) + metrics.get("saves", 0)
                    )
                    creator_metrics["performance"]["total_clicks"] += metrics.get("clicks", 0)
                
                # Add content breakdown
                creator_metrics["content_breakdown"].append({
                    "content_type": content_item["content_type"],
                    "platform": content_item["platform"],
                    "posted_at": content_item["posted_at"],
                    "views": metrics.get("views", 0) if isinstance(metrics, dict) else 0,
                    "engagement_rate": metrics.get("engagement_rate", 0) if isinstance(metrics, dict) else 0,
                    "performance_score": content_item["performance_score"]
                })
            
            # Calculate averages
            total_views = creator_metrics["performance"]["total_views"]
            total_engagement = creator_metrics["performance"]["total_engagement"]
            
            if total_views > 0:
                creator_metrics["performance"]["avg_engagement_rate"] = (total_engagement / total_views) * 100
            
            creator_metrics["performance"]["performance_score"] = sum(
                item["performance_score"] for item in creator_metrics["content_breakdown"]
            ) / max(len(creator_metrics["content_breakdown"]), 1)
            
            creator_breakdown[creator_id] = creator_metrics
        
        return creator_breakdown
    
    async def _generate_ai_performance_insights(self, campaign: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        🧠 Generate AI-powered performance insights
        """
        
        if not self.groq_client:
            return self._generate_basic_insights(campaign)
        
        try:
            # Prepare performance data for AI analysis
            performance_summary = await self._calculate_campaign_performance(campaign)
            
            # Create analysis prompt
            prompt = f"""
            Analyze this influencer marketing campaign performance and provide insights.
            
            Campaign Performance:
            - Total Views: {performance_summary['reach_metrics']['total_views']:,}
            - Engagement Rate: {performance_summary['engagement_metrics']['average_engagement_rate']}%
            - Click-through Rate: {performance_summary['conversion_metrics']['click_through_rate']}%
            - ROI: {performance_summary['roi_metrics']['roi_percentage']}%
            - Content Pieces: {performance_summary['content_metrics']['total_content_pieces']}
            
            Campaign Details:
            - Brand: {campaign['campaign_data'].get('brand_name', 'N/A')}
            - Product: {campaign['campaign_data'].get('product_name', 'N/A')}
            - Budget: ${campaign['campaign_data'].get('total_budget', 0):,}
            - Creators: {len(campaign['creators'])}
            
            Provide 3-5 key insights in this JSON format:
            [
                {{
                    "insight_type": "performance|optimization|prediction|alert",
                    "title": "Brief insight title",
                    "description": "Detailed insight description",
                    "impact": "high|medium|low",
                    "action_required": "urgent|recommended|optional",
                    "recommendation": "Specific action to take"
                }}
            ]
            """
            
            response = self.groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=800
            )
            
            insights_text = response.choices[0].message.content.strip()
            
            # Extract JSON
            json_start = insights_text.find('[')
            json_end = insights_text.rfind(']') + 1
            
            if json_start >= 0 and json_end > json_start:
                insights = json.loads(insights_text[json_start:json_end])
                logger.info(f"🧠 AI insights generated: {len(insights)} insights")
                return insights
            else:
                return self._generate_basic_insights(campaign)
                
        except Exception as e:
            logger.error(f"❌ AI insights generation failed: {e}")
            return self._generate_basic_insights(campaign)
    
    def _generate_basic_insights(self, campaign: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate basic insights when AI fails"""
        
        insights = []
        
        # Calculate basic metrics for insights
        total_content = sum(len(creator["content_items"]) for creator in campaign["creators"].values())
        
        if total_content > 0:
            insights.append({
                "insight_type": "performance",
                "title": "Campaign Content Published",
                "description": f"Campaign has {total_content} pieces of content published across {len(campaign['creators'])} creators",
                "impact": "medium",
                "action_required": "optional",
                "recommendation": "Monitor performance over the next 48 hours for optimization opportunities"
            })
        
        # Check campaign duration
        days_active = (datetime.now() - datetime.fromisoformat(campaign["started_at"])).days
        
        if days_active > 7:
            insights.append({
                "insight_type": "optimization",
                "title": "Campaign Running for Week+",
                "description": f"Campaign has been active for {days_active} days. Consider analyzing performance for optimization.",
                "impact": "medium",
                "action_required": "recommended",
                "recommendation": "Review top-performing content and creators for future campaigns"
            })
        
        return insights
    
    def _calculate_performance_trends(self, campaign: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate performance trends over time"""
        
        # This would analyze metrics history to show trends
        # For now, return mock trend data
        
        return {
            "views_trend": {
                "direction": "increasing",
                "percentage_change": 15.3,
                "period": "last_24_hours"
            },
            "engagement_trend": {
                "direction": "stable",
                "percentage_change": 2.1,
                "period": "last_24_hours"
            },
            "clicks_trend": {
                "direction": "increasing",
                "percentage_change": 8.7,
                "period": "last_24_hours"
            },
            "trend_summary": "Campaign showing positive momentum with steady engagement and increasing clicks"
        }
    
    def _check_performance_alerts(self, campaign: Dict[str, Any], performance: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for performance alerts"""
        
        alerts = []
        
        # Check engagement rate
        avg_engagement = performance["engagement_metrics"]["average_engagement_rate"]
        if avg_engagement < 2.0:
            alerts.append({
                "type": "underperformance",
                "severity": "medium",
                "title": "Low Engagement Rate",
                "message": f"Average engagement rate ({avg_engagement}%) is below optimal range",
                "recommendation": "Review content quality and creator selection"
            })
        
        # Check ROI
        roi = performance["roi_metrics"]["roi_percentage"]
        if roi < 0:
            alerts.append({
                "type": "financial",
                "severity": "high",
                "title": "Negative ROI",
                "message": f"Current ROI is {roi}%",
                "recommendation": "Optimize conversion funnel and targeting"
            })
        
        # Check click-through rate
        ctr = performance["conversion_metrics"]["click_through_rate"]
        if ctr < 1.0:
            alerts.append({
                "type": "conversion",
                "severity": "medium",
                "title": "Low Click-through Rate",
                "message": f"Click-through rate ({ctr}%) could be improved",
                "recommendation": "Strengthen call-to-action in content"
            })
        
        return alerts
    
    async def _generate_performance_recommendations(self, campaign: Dict[str, Any]) -> List[str]:
        """Generate performance improvement recommendations"""
        
        recommendations = []
        
        # Analyze content performance
        all_content_scores = []
        for creator_data in campaign["creators"].values():
            for content_item in creator_data["content_items"]:
                all_content_scores.append(content_item["performance_score"])
        
        if all_content_scores:
            avg_score = sum(all_content_scores) / len(all_content_scores)
            
            if avg_score < 0.6:
                recommendations.append("Consider A/B testing different content formats and messaging")
                recommendations.append("Provide clearer brand guidelines to creators")
            elif avg_score > 0.8:
                recommendations.append("Scale successful content formats to more creators")
                recommendations.append("Increase budget allocation to top-performing creators")
        
        # Time-based recommendations
        days_active = (datetime.now() - datetime.fromisoformat(campaign["started_at"])).days
        
        if days_active < 3:
            recommendations.append("Allow 48-72 hours for initial performance data to stabilize")
        elif days_active > 14:
            recommendations.append("Consider campaign refresh with new creators or content angles")
        
        recommendations.append("Set up automated alerts for significant performance changes")
        recommendations.append("Schedule weekly performance review meetings with creators")
        
        return recommendations
    
    # Helper methods
    
    def _initialize_creator_metrics(self) -> Dict[str, Any]:
        """Initialize empty creator metrics"""
        return {
            "total_views": 0,
            "total_engagement": 0,
            "total_clicks": 0,
            "avg_engagement_rate": 0.0,
            "performance_score": 0.0
        }
    
    def _initialize_content_metrics(self) -> Dict[str, Any]:
        """Initialize empty content metrics"""
        return {
            "views": 0,
            "likes": 0,
            "comments": 0,
            "shares": 0,
            "saves": 0,
            "clicks": 0,
            "engagement_rate": 0.0,
            "reach": 0,
            "impressions": 0
        }
    
    def _extract_content_id(self, content_url: str, platform: str) -> str:
        """Extract content ID from URL"""
        
        # Simple extraction - would be more sophisticated in production
        if "instagram.com" in content_url:
            return content_url.split("/")[-2] if content_url.endswith("/") else content_url.split("/")[-1]
        elif "youtube.com" in content_url:
            return content_url.split("v=")[-1].split("&")[0] if "v=" in content_url else "unknown"
        elif "tiktok.com" in content_url:
            return content_url.split("/")[-1]
        else:
            return f"{platform}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def _calculate_content_performance_score(self, content_item: Dict[str, Any], creator_data: Dict[str, Any]) -> float:
        """Calculate performance score for content item"""
        
        metrics = content_item["current_metrics"]
        if not isinstance(metrics, dict):
            return 0.0
        
        # Normalize metrics based on creator's typical performance
        views = metrics.get("views", 0)
        engagement_rate = metrics.get("engagement_rate", 0)
        clicks = metrics.get("clicks", 0)
        
        # Simple scoring formula
        view_score = min(views / 10000, 1.0)  # Normalize to 10K views
        engagement_score = min(engagement_rate / 10, 1.0)  # Normalize to 10% engagement
        click_score = min(clicks / 500, 1.0)  # Normalize to 500 clicks
        
        # Weighted average
        performance_score = (view_score * 0.4 + engagement_score * 0.4 + click_score * 0.2)
        
        return round(performance_score, 2)
    
    def _calculate_engagement_quality_score(self, campaign: Dict[str, Any]) -> float:
        """Calculate engagement quality score"""
        
        # This would analyze the quality of engagement (comments vs likes ratio, etc.)
        return 7.5  # Mock score
    
    def _calculate_average_content_score(self, campaign: Dict[str, Any]) -> float:
        """Calculate average content performance score"""
        
        all_scores = []
        for creator_data in campaign["creators"].values():
            for content_item in creator_data["content_items"]:
                all_scores.append(content_item["performance_score"])
        
        return sum(all_scores) / len(all_scores) if all_scores else 0.0
    
    async def _check_and_send_alerts(self, campaign: Dict[str, Any]):
        """Check for alerts and send notifications"""
        
        # This would integrate with notification systems
        # For now, just log alerts
        
        performance = await self._calculate_campaign_performance(campaign)
        alerts = self._check_performance_alerts(campaign, performance)
        
        for alert in alerts:
            if alert["severity"] == "high":
                logger.warning(f"🚨 HIGH ALERT: {alert['title']} - {alert['message']}")
            elif alert["severity"] == "medium":
                logger.info(f"⚠️  MEDIUM ALERT: {alert['title']} - {alert['message']}")
        
        # Store alerts in campaign
        campaign["alerts"].extend(alerts)
    
    async def _update_campaign_status(self, campaign: Dict[str, Any]):
        """Update campaign status based on performance"""
        
        # Simple status logic - would be more sophisticated in production
        days_active = (datetime.now() - datetime.fromisoformat(campaign["started_at"])).days
        
        if days_active > 30:
            campaign["status"] = PerformanceStatus.COMPLETED.value
        else:
            performance = await self._calculate_campaign_performance(campaign)
            roi = performance["roi_metrics"]["roi_percentage"]
            
            if roi > 200:
                campaign["status"] = PerformanceStatus.OVERPERFORMING.value
            elif roi < 0:
                campaign["status"] = PerformanceStatus.UNDERPERFORMING.value
            else:
                campaign["status"] = PerformanceStatus.TRACKING.value
    
    # API initialization methods (mock)
    
    def _initialize_instagram_api(self):
        """Initialize Instagram Graph API connection"""
        return None  # Would return configured API client
    
    def _initialize_youtube_api(self):
        """Initialize YouTube Data API connection"""
        return None  # Would return configured API client
    
    def _initialize_tiktok_api(self):
        """Initialize TikTok Business API connection"""
        return None  # Would return configured API client
    
    def _initialize_ga_api(self):
        """Initialize Google Analytics API connection"""
        return None  # Would return configured API client