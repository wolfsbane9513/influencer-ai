# agents/discovery.py
import json
import logging
from typing import List, Dict, Any
from pathlib import Path

from models.campaign import CampaignData,Creator, CreatorMatch
from core.exceptions import (
    InfluencerFlowException,
    ValidationError,
    BusinessLogicError,
    create_error_context,
)
from services.embeddings import EmbeddingService
from services.pricing import PricingService

from config.settings import settings

logger = logging.getLogger(__name__)


class DiscoveryError(BusinessLogicError):
    """Discovery process failure"""
    pass

class InfluencerDiscoveryAgent:
    """
    AI agent that discovers and ranks influencers based on campaign requirements
    using vector similarity matching and market pricing analysis
    """
    
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.pricing_service = PricingService()
        self.creators_data = self._load_creators_data()
    
    def _load_creators_data(self) -> List[Creator]:
        """Load creators from JSON file"""
        try:
            creators_file = Path("data/creators.json")
            if not creators_file.exists():
                logger.warning("creators.json not found, using mock data")
                return self._get_mock_creators()
            
            with open(creators_file, 'r') as f:
                data = json.load(f)
            
            creators = []
            for creator_data in data.get("creators", []):
                try:
                    creator = Creator(**creator_data)
                    creators.append(creator)
                except Exception as e:
                    logger.error(f"Failed to parse creator {creator_data.get('name', 'unknown')}: {e}")
            
            logger.info(f"Loaded {len(creators)} creators from file")
            return creators
            
        except Exception as e:
            logger.error(f"Failed to load creators data: {e}")
            return self._get_mock_creators()
    
    def _get_mock_creators(self) -> List[Creator]:
        """Get mock creators for testing when file is not available"""
        mock_creators = [
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
                "phone_number": "+918806859890",
                "languages": ["English", "Hindi"],
                "specialties": ["smartphone_reviews", "gadget_unboxing", "tech_tutorials"],
                "audience_demographics": {"age_18_24": 35, "age_25_34": 40, "male": 70, "female": 30},
                "performance_metrics": {"brand_safety_score": 9.5, "collaboration_rating": 4.8},
                "recent_campaigns": [],
                "rate_history": {"2024": 4500},
                "preferred_collaboration_style": "Professional and detail-oriented"
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
                "phone_number": "+918806859890",
                "languages": ["English", "Spanish"],
                "specialties": ["workout_routines", "supplement_reviews", "fitness_gear"],
                "audience_demographics": {"age_18_24": 25, "age_25_34": 45, "male": 60, "female": 40},
                "performance_metrics": {"brand_safety_score": 9.8, "collaboration_rating": 4.9},
                "recent_campaigns": [],
                "rate_history": {"2024": 3200},
                "preferred_collaboration_style": "High-energy and authentic"
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
                "phone_number": "+918806859890",
                "languages": ["English", "Hindi", "Punjabi"],
                "specialties": ["makeup_tutorials", "skincare_reviews", "fashion_hauls"],
                "audience_demographics": {"age_18_24": 50, "age_25_34": 35, "male": 15, "female": 85},
                "performance_metrics": {"brand_safety_score": 9.0, "collaboration_rating": 4.6},
                "recent_campaigns": [],
                "rate_history": {"2024": 6000},
                "preferred_collaboration_style": "Creative freedom important"
            }
        ]
        
        creators = []
        for creator_data in mock_creators:
            try:
                creator = Creator(**creator_data)
                creators.append(creator)
            except Exception as e:
                logger.error(f"Failed to create mock creator: {e}")
        
        logger.info(f"Using {len(creators)} mock creators")
        return creators

    def _validate_campaign_data(self, campaign_data: CampaignData) -> None:
        """Validate basic campaign data before matching"""
        errors: Dict[str, List[str]] = {}

        if campaign_data.total_budget <= 0:
            errors.setdefault("total_budget", []).append("Budget must be positive")

        if not campaign_data.product_name:
            errors.setdefault("product_name", []).append("Product name required")

        if errors:
            raise ValidationError(
                message="Invalid campaign data",
                field_errors=errors,
                context=create_error_context(
                    operation="validate_campaign_data",
                    component="InfluencerDiscoveryAgent",
                    campaign_id=getattr(campaign_data, "id", None),
                ),
            )
    
    async def find_matches(self, campaign_data: CampaignData, max_results: int = 3) -> List[CreatorMatch]:
        """
        Find top matching influencers for the campaign using vector similarity
        """
        logger.info(f"🔍 Finding matches for campaign: {campaign_data.product_name}")

        # Validate campaign data
        self._validate_campaign_data(campaign_data)

        context = create_error_context(
            operation="find_matches",
            component="InfluencerDiscoveryAgent",
            campaign_id=getattr(campaign_data, "id", None),
        )
        
        try:
            # Generate campaign embedding
            campaign_text = self._create_campaign_text(campaign_data)
            campaign_embedding = await self.embedding_service.generate_embedding(campaign_text)
            
            matches = []
            
            for creator in self.creators_data:
                # Generate creator embedding
                creator_text = self._create_creator_text(creator)
                creator_embedding = await self.embedding_service.generate_embedding(creator_text)
                
                # Calculate similarity
                similarity_score = self.embedding_service.calculate_similarity(
                    campaign_embedding, creator_embedding
                )
                
                # Check rate compatibility
                rate_compatible, estimated_rate = self._check_rate_compatibility(
                    creator, campaign_data
                )
                
                # Check availability and other factors
                availability_score = self._calculate_availability_score(creator)
                niche_match = self._calculate_niche_match(creator, campaign_data)
                
                # Combined score
                combined_score = (
                    similarity_score * 0.4 +
                    niche_match * 0.3 +
                    availability_score * 0.2 +
                    (1.0 if rate_compatible else 0.3) * 0.1
                )
                
                # Generate match reasons
                match_reasons = self._generate_match_reasons(
                    creator, campaign_data, similarity_score, rate_compatible, niche_match
                )
                
                if combined_score >= settings.similarity_threshold:
                    match = CreatorMatch(
                        creator=creator,
                        similarity_score=combined_score,
                        rate_compatible=rate_compatible,
                        match_reasons=match_reasons,
                        estimated_rate=estimated_rate
                    )
                    matches.append(match)
            
            # Sort by similarity score and return top matches
            matches.sort(key=lambda x: x.similarity_score, reverse=True)
            top_matches = matches[:max_results]  # ✅ CHANGED: Use max_results parameter
            
            logger.info(f"✅ Found {len(top_matches)} matching influencers")
            for i, match in enumerate(top_matches[:3]):
                logger.info(f"  {i+1}. {match.creator.name} - {match.similarity_score:.3f} score")
            
            return top_matches
            
        except Exception as e:
            logger.error(f"❌ Error in find_matches: {e}")
            raise DiscoveryError(
                message=str(e),
                context=context,
            )

    def _create_campaign_text(self, campaign_data: CampaignData) -> str:
        """Create text representation of campaign for embedding"""
        return f"""
        Product: {campaign_data.product_name}
        Brand: {campaign_data.brand_name}
        Description: {campaign_data.product_description}
        Target Audience: {campaign_data.target_audience}
        Campaign Goal: {campaign_data.campaign_goal}
        Niche: {campaign_data.product_niche}
        Budget: {campaign_data.total_budget}
        """.strip()
    
    def _create_creator_text(self, creator: Creator) -> str:
        """Create text representation of creator for embedding"""
        specialties_text = " ".join(creator.specialties)
        languages_text = " ".join(creator.languages)
        
        return f"""
        Creator: {creator.name}
        Platform: {creator.platform}
        Niche: {creator.niche}
        Specialties: {specialties_text}
        Languages: {languages_text}
        Collaboration Style: {creator.preferred_collaboration_style}
        Location: {creator.location}
        Followers: {creator.followers}
        Engagement: {creator.engagement_rate}%
        """.strip()
    
    def _check_rate_compatibility(self, creator: Creator, campaign_data: CampaignData) -> tuple[bool, float]:
        """Check if creator's rate is compatible with campaign budget"""
        try:
            # Calculate estimated rate based on market data
            estimated_rate = self.pricing_service.calculate_estimated_rate(
                creator, campaign_data
            )
            
            # Check if rate fits within budget (assuming 3 influencers max)
            budget_per_influencer = campaign_data.total_budget / 3
            rate_compatible = estimated_rate <= budget_per_influencer * 1.2  # 20% buffer
            
            return rate_compatible, estimated_rate
            
        except Exception as e:
            logger.error(f"Rate compatibility check failed: {e}")
            return True, creator.typical_rate  # Default fallback
    
    def _calculate_availability_score(self, creator: Creator) -> float:
        """Calculate availability score"""
        availability_scores = {
            "excellent": 1.0,
            "good": 0.8,
            "limited": 0.5,
            "busy": 0.2
        }
        return availability_scores.get(creator.availability.value, 0.5)
    
    def _calculate_niche_match(self, creator: Creator, campaign_data: CampaignData) -> float:
        """Calculate how well creator's niche matches campaign"""
        if creator.niche.lower() == campaign_data.product_niche.lower():
            return 1.0
        elif creator.niche.lower() in campaign_data.product_description.lower():
            return 0.7
        elif campaign_data.product_niche.lower() in creator.preferred_collaboration_style.lower():
            return 0.5
        else:
            return 0.3
    
    def _generate_match_reasons(
        self, 
        creator: Creator, 
        campaign_data: CampaignData,
        similarity_score: float,
        rate_compatible: bool,
        niche_match: float
    ) -> List[str]:
        """Generate human-readable reasons for the match"""
        reasons = []
        
        if niche_match >= 0.8:
            reasons.append("Perfect niche alignment")
        elif niche_match >= 0.5:
            reasons.append("Good niche relevance")
        
        if creator.engagement_rate >= 5.0:
            reasons.append("High engagement rate")
        elif creator.engagement_rate >= 3.0:
            reasons.append("Good engagement rate")
        
        if rate_compatible:
            reasons.append("Budget compatible")
        else:
            reasons.append("Above budget range")
        
        if creator.availability.value == "excellent":
            reasons.append("Excellent availability")
        elif creator.availability.value == "good":
            reasons.append("Good availability")
        
        if similarity_score >= 0.8:
            reasons.append("Strong content alignment")
        elif similarity_score >= 0.6:
            reasons.append("Good content match")
        
        return reasons[:3]  # Limit to top 3 reasons
    
    def _get_mock_matches(self) -> List[CreatorMatch]:
        """Get mock matches for demo when embedding service fails"""
        mock_matches = []
        
        for i, creator in enumerate(self.creators_data[:3]):
            # Create realistic mock scores
            scores = [0.85, 0.72, 0.68]
            rate_compatible = [True, False, True]
            reasons = [
                ["Perfect niche alignment", "High engagement rate", "Budget compatible"],
                ["Different niche", "Above budget range", "Good content quality"],
                ["Good niche relevance", "Strong content alignment", "Excellent availability"]
            ]
            
            match = CreatorMatch(
                creator=creator,
                similarity_score=scores[i] if i < len(scores) else 0.6,
                rate_compatible=rate_compatible[i] if i < len(rate_compatible) else True,
                match_reasons=reasons[i] if i < len(reasons) else ["Mock match"],
                estimated_rate=creator.typical_rate
            )
            mock_matches.append(match)
        
        logger.info("🎭 Using mock matches for demo")
        return mock_matches
