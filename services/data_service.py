# services/data_service.py
import json
import os
from typing import Dict, List, Optional, Any
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class DataService:
    def __init__(self):
        self.data = self._load_mock_data()
    
    def _load_mock_data(self) -> Dict[str, Any]:
        """Load mock data from JSON files, with embedded fallback"""
        
        # Try to load from JSON files first
        try:
            return self._load_from_json_files()
        except Exception as e:
            logger.warning(f"Failed to load JSON files: {e}. Using embedded data as fallback.")
            return self._get_embedded_data()
    
    def _load_from_json_files(self) -> Dict[str, Any]:
        """Load data from separate JSON files"""
        
        # Get the project root directory
        project_root = Path(__file__).parent.parent
        data_dir = project_root / "data"
        
        # Load creators
        creators_file = data_dir / "creators.json"
        with open(creators_file, 'r', encoding='utf-8') as f:
            creators_data = json.load(f)
        
        # Load market data
        market_data_file = data_dir / "market_data.json"
        with open(market_data_file, 'r', encoding='utf-8') as f:
            market_data = json.load(f)
        
        logger.info("Successfully loaded data from JSON files")
        
        return {
            "creators": creators_data["creators"],
            "market_data": market_data
        }
    
    def _get_embedded_data(self) -> Dict[str, Any]:
        """Fallback embedded data (same as current implementation)"""
        logger.info("Using embedded data fallback")
        
        return {
            "creators": [
                {
                    "id": "sarah_tech",
                    "name": "TechReviewer_Sarah",
                    "platform": "YouTube",
                    "followers": 500000,
                    "niche": "tech",
                    "typical_rate": 4500,
                    "engagement_rate": 4.2,
                    "average_views": 180000,
                    "last_campaign_date": "2024-10-15",
                    "availability": "good",
                    "location": "Mumbai, India",
                    "languages": ["English", "Hindi"],
                    "specialties": ["smartphone_reviews", "gadget_unboxing", "tech_tutorials"],
                    "audience_demographics": {
                        "age_18_24": 35,
                        "age_25_34": 40,
                        "age_35_44": 20,
                        "age_45_plus": 5,
                        "male": 70,
                        "female": 30,
                        "top_countries": ["India", "USA", "UK", "Canada", "Australia"]
                    },
                    "performance_metrics": {
                        "avg_completion_rate": 98,
                        "brand_safety_score": 9.5,
                        "audience_quality": 8.8,
                        "delivery_punctuality": 95,
                        "content_quality_score": 9.2,
                        "collaboration_rating": 4.8
                    },
                    "recent_campaigns": [
                        {
                            "brand": "TechCorp",
                            "date": "2024-10-15",
                            "deliverables": ["video_review", "instagram_post"],
                            "price": 4200,
                            "performance": {
                                "views": 195000,
                                "engagement_rate": 4.6,
                                "click_through_rate": 2.1
                            }
                        }
                    ],
                    "rate_history": {"2024": 4500, "2023": 4000, "2022": 3200},
                    "preferred_collaboration_style": "Professional and detail-oriented. Prefers clear briefs and timeline flexibility."
                },
                {
                    "id": "mike_fitness",
                    "name": "FitnessGuru_Mike",
                    "platform": "Instagram",
                    "followers": 300000,
                    "niche": "fitness",
                    "typical_rate": 3200,
                    "engagement_rate": 5.8,
                    "average_views": 120000,
                    "last_campaign_date": "2024-11-01",
                    "availability": "limited",
                    "location": "Los Angeles, USA",
                    "languages": ["English", "Spanish"],
                    "specialties": ["workout_routines", "supplement_reviews", "fitness_gear"],
                    "audience_demographics": {
                        "age_18_24": 25,
                        "age_25_34": 45,
                        "age_35_44": 25,
                        "age_45_plus": 5,
                        "male": 60,
                        "female": 40,
                        "top_countries": ["USA", "Canada", "Mexico", "Brazil", "UK"]
                    },
                    "performance_metrics": {
                        "avg_completion_rate": 100,
                        "brand_safety_score": 9.8,
                        "audience_quality": 9.2,
                        "delivery_punctuality": 98,
                        "content_quality_score": 9.0,
                        "collaboration_rating": 4.9
                    },
                    "recent_campaigns": [
                        {
                            "brand": "ProteinPlus",
                            "date": "2024-11-01",
                            "deliverables": ["workout_video", "supplement_review", "stories"],
                            "price": 3500,
                            "performance": {
                                "views": 140000,
                                "engagement_rate": 6.2,
                                "click_through_rate": 3.1
                            }
                        }
                    ],
                    "rate_history": {"2024": 3200, "2023": 2800, "2022": 2200},
                    "preferred_collaboration_style": "High-energy and authentic. Requires product testing period. Strong on deadline adherence."
                },
                {
                    "id": "priya_beauty",
                    "name": "BeautyInfluencer_Priya",
                    "platform": "TikTok",
                    "followers": 1000000,
                    "niche": "beauty",
                    "typical_rate": 6000,
                    "engagement_rate": 7.2,
                    "average_views": 450000,
                    "last_campaign_date": "2024-11-20",
                    "availability": "busy",
                    "location": "Delhi, India",
                    "languages": ["English", "Hindi", "Punjabi"],
                    "specialties": ["makeup_tutorials", "skincare_reviews", "fashion_hauls"],
                    "audience_demographics": {
                        "age_18_24": 50,
                        "age_25_34": 35,
                        "age_35_44": 12,
                        "age_45_plus": 3,
                        "male": 15,
                        "female": 85,
                        "top_countries": ["India", "Pakistan", "Bangladesh", "UAE", "USA"]
                    },
                    "performance_metrics": {
                        "avg_completion_rate": 96,
                        "brand_safety_score": 9.0,
                        "audience_quality": 8.5,
                        "delivery_punctuality": 90,
                        "content_quality_score": 9.4,
                        "collaboration_rating": 4.6
                    },
                    "recent_campaigns": [
                        {
                            "brand": "GlowCosmetics",
                            "date": "2024-11-20",
                            "deliverables": ["makeup_tutorial", "product_review", "instagram_reels"],
                            "price": 6200,
                            "performance": {
                                "views": 520000,
                                "engagement_rate": 7.8,
                                "click_through_rate": 2.9
                            }
                        }
                    ],
                    "rate_history": {"2024": 6000, "2023": 5200, "2022": 4000},
                    "preferred_collaboration_style": "Creative freedom important. Prefers seasonal campaigns. Strong aesthetic requirements."
                },
                {
                    "id": "alex_gaming",
                    "name": "GamingStreamer_Alex",
                    "platform": "Twitch",
                    "followers": 800000,
                    "niche": "gaming",
                    "typical_rate": 5500,
                    "engagement_rate": 8.1,
                    "average_views": 350000,
                    "last_campaign_date": "2024-10-30",
                    "availability": "good",
                    "location": "Toronto, Canada",
                    "languages": ["English", "French"],
                    "specialties": ["fps_games", "game_reviews", "tech_hardware"],
                    "audience_demographics": {
                        "age_18_24": 60,
                        "age_25_34": 30,
                        "age_35_44": 8,
                        "age_45_plus": 2,
                        "male": 80,
                        "female": 20,
                        "top_countries": ["USA", "Canada", "UK", "Germany", "Australia"]
                    },
                    "performance_metrics": {
                        "avg_completion_rate": 94,
                        "brand_safety_score": 8.8,
                        "audience_quality": 9.0,
                        "delivery_punctuality": 92,
                        "content_quality_score": 8.9,
                        "collaboration_rating": 4.7
                    },
                    "recent_campaigns": [
                        {
                            "brand": "GameGear",
                            "date": "2024-10-30",
                            "deliverables": ["sponsored_stream", "equipment_review"],
                            "price": 5200,
                            "performance": {
                                "views": 380000,
                                "engagement_rate": 8.5,
                                "click_through_rate": 4.2
                            }
                        }
                    ],
                    "rate_history": {"2024": 5500, "2023": 4800, "2022": 3800},
                    "preferred_collaboration_style": "Flexible with gaming content. Prefers hardware/software that enhances gameplay. Community-focused."
                },
                {
                    "id": "lisa_food",
                    "name": "FoodBlogger_Lisa",
                    "platform": "YouTube",
                    "followers": 250000,
                    "niche": "food",
                    "typical_rate": 2800,
                    "engagement_rate": 6.5,
                    "average_views": 95000,
                    "last_campaign_date": "2024-11-10",
                    "availability": "excellent",
                    "location": "New York, USA",
                    "languages": ["English"],
                    "specialties": ["restaurant_reviews", "recipe_videos", "food_photography"],
                    "audience_demographics": {
                        "age_18_24": 20,
                        "age_25_34": 40,
                        "age_35_44": 30,
                        "age_45_plus": 10,
                        "male": 35,
                        "female": 65,
                        "top_countries": ["USA", "Canada", "UK", "Australia", "Germany"]
                    },
                    "performance_metrics": {
                        "avg_completion_rate": 99,
                        "brand_safety_score": 9.9,
                        "audience_quality": 8.9,
                        "delivery_punctuality": 97,
                        "content_quality_score": 9.1,
                        "collaboration_rating": 4.8
                    },
                    "recent_campaigns": [
                        {
                            "brand": "TastyTreats",
                            "date": "2024-11-10", 
                            "deliverables": ["recipe_video", "taste_test", "instagram_posts"],
                            "price": 2600,
                            "performance": {
                                "views": 105000,
                                "engagement_rate": 7.1,
                                "click_through_rate": 2.8
                            }
                        }
                    ],
                    "rate_history": {"2024": 2800, "2023": 2400, "2022": 2000},
                    "preferred_collaboration_style": "Detail-oriented with ingredients/preparation. Values authenticity. Prefers local/sustainable brands."
                }
            ],
            "market_data": {
                "rate_benchmarks": {
                    "tech": {
                        "micro_influencer": {"min": 2000, "max": 4000, "avg": 3000},
                        "macro_influencer": {"min": 4000, "max": 8000, "avg": 6000},
                        "mega_influencer": {"min": 8000, "max": 15000, "avg": 12000}
                    },
                    "beauty": {
                        "micro_influencer": {"min": 1500, "max": 3500, "avg": 2500},
                        "macro_influencer": {"min": 3500, "max": 7000, "avg": 5000},
                        "mega_influencer": {"min": 7000, "max": 12000, "avg": 9500}
                    },
                    "fitness": {
                        "micro_influencer": {"min": 1800, "max": 3800, "avg": 2800},
                        "macro_influencer": {"min": 3800, "max": 6500, "avg": 5000},
                        "mega_influencer": {"min": 6500, "max": 12000, "avg": 9000}
                    },
                    "gaming": {
                        "micro_influencer": {"min": 2200, "max": 4500, "avg": 3200},
                        "macro_influencer": {"min": 4500, "max": 8500, "avg": 6200},
                        "mega_influencer": {"min": 8500, "max": 15000, "avg": 11500}
                    },
                    "food": {
                        "micro_influencer": {"min": 1200, "max": 2800, "avg": 2000},
                        "macro_influencer": {"min": 2800, "max": 5500, "avg": 4000},
                        "mega_influencer": {"min": 5500, "max": 10000, "avg": 7500}
                    }
                },
                "engagement_benchmarks": {
                    "youtube": {"excellent": 8.0, "good": 4.0, "average": 2.0, "below_average": 1.0},
                    "instagram": {"excellent": 6.0, "good": 3.0, "average": 1.5, "below_average": 0.8},
                    "tiktok": {"excellent": 9.0, "good": 5.0, "average": 3.0, "below_average": 1.5},
                    "twitch": {"excellent": 10.0, "good": 6.0, "average": 3.5, "below_average": 2.0}
                },
                "pricing_factors": {
                    "rush_delivery": {"1_day": 2.0, "2_days": 1.5, "3_days": 1.3, "1_week": 1.2},
                    "exclusive_rights": {"3_months": 1.2, "6_months": 1.4, "1_year": 1.8, "perpetual": 2.5},
                    "multi_platform": {"2_platforms": 1.3, "3_platforms": 1.6, "4_plus_platforms": 2.0},
                    "seasonal_premium": {"holiday_season": 1.25, "back_to_school": 1.15, "summer": 1.1},
                    "usage_rights": {"organic_only": 1.0, "paid_ads": 1.4, "commercial_use": 1.8},
                    "deliverable_multipliers": {
                        "video_review": 1.0, "unboxing_video": 0.8, "tutorial_video": 1.2,
                        "instagram_post": 0.3, "instagram_story": 0.15, "instagram_reel": 0.4,
                        "tiktok_video": 0.5, "twitter_thread": 0.2, "blog_post": 0.6
                    }
                },
                "industry_trends": {
                    "2024_growth_rates": {"tech": 15, "beauty": 12, "fitness": 18, "gaming": 22, "food": 8},
                    "platform_shifts": {
                        "tiktok_growth": 35, "youtube_shorts_growth": 28, 
                        "instagram_reels_growth": 25, "twitch_growth": 20
                    },
                    "roi_benchmarks": {
                        "tech": {"views_per_dollar": 45, "engagement_per_dollar": 2.1},
                        "beauty": {"views_per_dollar": 65, "engagement_per_dollar": 3.8},
                        "fitness": {"views_per_dollar": 40, "engagement_per_dollar": 2.3},
                        "gaming": {"views_per_dollar": 55, "engagement_per_dollar": 4.2},
                        "food": {"views_per_dollar": 35, "engagement_per_dollar": 2.8}
                    }
                },
                "negotiation_insights": {
                    "success_factors": [
                        "Timeline flexibility increases acceptance rate by 40%",
                        "Long-term partnership mentions improve terms by 15%",
                        "Performance bonuses increase creator interest by 60%",
                        "Clear usage rights reduce negotiation time by 30%"
                    ],
                    "common_objections": {
                        "price_too_low": {
                            "frequency": 70,
                            "best_counters": ["Show ROI calculations", "Offer performance bonuses", "Add future campaign mentions"]
                        },
                        "timeline_too_tight": {
                            "frequency": 45,
                            "best_counters": ["Offer rush premium", "Reduce deliverable scope", "Provide detailed brief"]
                        },
                        "scope_too_broad": {
                            "frequency": 35,
                            "best_counters": ["Break into phases", "Prioritize core deliverables", "Increase compensation"]
                        }
                    },
                    "negotiation_psychology": {
                        "micro_influencers": "Price-sensitive, relationship-focused, growth-oriented",
                        "macro_influencers": "Value-driven, professional, efficiency-focused",
                        "mega_influencers": "Brand-selective, premium-positioned, exclusive-seeking"
                    }
                }
            }
        }
    
    def get_all_creators(self) -> List[Dict[str, Any]]:
        """Get all creator profiles"""
        return self.data.get("creators", [])
    
    def get_creator_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get creator by name (case insensitive)"""
        for creator in self.data.get("creators", []):
            if creator["name"].lower() == name.lower():
                return creator
        return None
    
    def get_creator_by_id(self, creator_id: str) -> Optional[Dict[str, Any]]:
        """Get creator by ID"""
        for creator in self.data.get("creators", []):
            if creator["id"] == creator_id:
                return creator
        return None
    
    def get_market_data(self) -> Dict[str, Any]:
        """Get market benchmarks and pricing data"""
        return self.data.get("market_data", {})
    
    def get_rate_benchmark(self, niche: str, tier: str) -> Optional[Dict[str, int]]:
        """Get rate benchmark for specific niche and tier"""
        market_data = self.get_market_data()
        rate_benchmarks = market_data.get("rate_benchmarks", {})
        niche_data = rate_benchmarks.get(niche, {})
        return niche_data.get(tier)
    
    def get_engagement_benchmark(self, platform: str) -> Optional[Dict[str, float]]:
        """Get engagement benchmarks for platform"""
        market_data = self.get_market_data()
        engagement_benchmarks = market_data.get("engagement_benchmarks", {})
        return engagement_benchmarks.get(platform.lower())
    
    def categorize_creator_by_followers(self, followers: int) -> str:
        """Categorize creator by follower count"""
        if followers < 100000:
            return "micro_influencer"
        elif followers < 1000000:
            return "macro_influencer"
        else:
            return "mega_influencer"
    
    def reload_data(self) -> bool:
        """Reload data from files (useful for development)"""
        try:
            self.data = self._load_mock_data()
            logger.info("Data reloaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to reload data: {e}")
            return False

# Create global instance
data_service = DataService()