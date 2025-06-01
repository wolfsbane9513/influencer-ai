# services/enhanced_voice.py - FIXED VERSION
import asyncio
import logging
import requests
import random
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from config.settings import settings

logger = logging.getLogger(__name__)

class EnhancedVoiceService:
    """
    🎯 ENHANCED ELEVENLABS INTEGRATION - FIXED VERSION
    Complete system with dynamic variables and structured conversation analysis
    """
    
    def __init__(self):
        self.api_key = settings.elevenlabs_api_key
        self.agent_id = settings.elevenlabs_agent_id  
        self.phone_number_id = settings.elevenlabs_phone_number_id
        self.base_url = "https://api.elevenlabs.io"
        
        # Check if real integration is possible
        self.use_mock = not all([self.api_key, self.agent_id, self.phone_number_id])
        
        self._debug_credentials()
    
    def _debug_credentials(self):
        """Debug credential status"""
        logger.info("🔍 Enhanced ElevenLabs Service Status:")
        logger.info(f"   API Key: {'✅ Set' if self.api_key else '❌ Missing'}")
        logger.info(f"   Agent ID: {'✅ Set' if self.agent_id else '❌ Missing'}")
        logger.info(f"   Phone Number ID: {'✅ Set' if self.phone_number_id else '❌ Missing'}")
        logger.info(f"   Mode: {'🎭 Mock' if self.use_mock else '🔥 Live API'}")
    
    async def test_credentials(self) -> Dict[str, Any]:
        """🧪 Test ElevenLabs credentials and setup"""
        if self.use_mock:
            return {
                "status": "mock_mode",
                "message": "ElevenLabs credentials not configured - using mock mode",
                "missing": [
                    field for field, value in [
                        ("api_key", self.api_key),
                        ("agent_id", self.agent_id), 
                        ("phone_number_id", self.phone_number_id)
                    ] if not value
                ]
            }
        
        try:
            response = requests.get(
                f"{self.base_url}/v1/user",
                headers={"Xi-Api-Key": self.api_key},
                timeout=10
            )
            
            if response.status_code == 200:
                user_info = response.json()
                return {
                    "status": "success",
                    "message": "ElevenLabs credentials verified - Enhanced mode ready",
                    "user": user_info.get("email", "Unknown"),
                    "agent_id": self.agent_id,
                    "phone_number_id": self.phone_number_id,
                    "dynamic_variables_ready": True,
                    "enhanced_analysis_ready": True
                }
            else:
                return {
                    "status": "failed",
                    "message": f"API key validation failed: {response.status_code}",
                    "error": response.text[:200]
                }
                
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Credential test failed: {str(e)}"
            }
    
    async def initiate_negotiation_call(
        self,
        creator_phone: str,
        creator_profile: Dict[str, Any],
        campaign_data: Dict[str, Any],
        pricing_strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """🔥 Enhanced ElevenLabs call with dynamic variables"""
        
        if self.use_mock:
            return await self._mock_enhanced_call(creator_phone, creator_profile, campaign_data)
        
        try:
            # Prepare dynamic variables
            dynamic_variables = self._prepare_dynamic_variables(
                creator_profile, campaign_data, pricing_strategy
            )
            
            logger.info(f"📱 Initiating Enhanced ElevenLabs call to {creator_phone}")
            logger.info(f"🎯 Dynamic Variables: {list(dynamic_variables.keys())}")
            
            # ElevenLabs API call
            response = requests.post(
                f"{self.base_url}/v1/convai/twilio/outbound-call",
                headers={
                    "Xi-Api-Key": self.api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "agent_id": self.agent_id,
                    "agent_phone_number_id": self.phone_number_id,
                    "to_number": creator_phone,
                    "conversation_initiation_client_data": {
                        "dynamic_variables": dynamic_variables
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                conversation_id = result.get("conversation_id")
                
                logger.info(f"✅ Enhanced call initiated successfully!")
                logger.info(f"   Conversation ID: {conversation_id}")
                
                return {
                    "status": "success",
                    "conversation_id": conversation_id,
                    "call_id": result.get("call_id"),
                    "phone_number": creator_phone,
                    "dynamic_variables": dynamic_variables,
                    "enhanced_features": [
                        "Dynamic variables integration",
                        "Structured negotiation flow", 
                        "Enhanced data extraction",
                        "Market-aware pricing"
                    ],
                    "raw_response": result
                }
            else:
                error_msg = f"API Error {response.status_code}: {response.text}"
                logger.error(f"❌ Enhanced call failed: {error_msg}")
                return {
                    "status": "failed",
                    "error": error_msg,
                    "phone_number": creator_phone
                }
                
        except Exception as e:
            logger.error(f"❌ Enhanced call exception: {e}")
            return {
                "status": "failed", 
                "error": str(e),
                "phone_number": creator_phone
            }
    
    def _prepare_dynamic_variables(
        self, 
        creator_profile: Dict[str, Any], 
        campaign_data: Dict[str, Any],
        pricing_strategy: Dict[str, Any]
    ) -> Dict[str, str]:
        """📝 Prepare dynamic variables for ElevenLabs agent"""
        
        # Enhanced InfluencerProfile
        influencer_profile = self._format_influencer_profile(creator_profile)
        
        # Campaign brief
        campaign_brief = json.dumps({
            "brand_name": campaign_data.get('brand_name', 'TechFit Solutions'),
            "product_name": campaign_data.get('product_name', 'Enhanced Fitness Tracker'),
            "product_description": campaign_data.get('product_description', 'Advanced fitness tracking with AI coaching'),
            "unique_value": self._get_unique_value_proposition(campaign_data),
            "target_audience": campaign_data.get('target_audience', 'Fitness enthusiasts'),
            "campaign_goal": campaign_data.get('campaign_goal', 'Launch new product'),
            "product_niche": campaign_data.get('product_niche', 'fitness')
        })
        
        # Negotiation strategy
        negotiation_strategy = json.dumps(self._generate_negotiation_strategy(creator_profile, campaign_data))
        
        # Deliverable requirements
        deliverable_requirements = json.dumps(self._generate_deliverable_requirements(creator_profile, campaign_data))
        
        # Timeline expectations
        timeline_expectations = json.dumps(self._generate_timeline_expectations(campaign_data))
        
        # Usage rights
        usage_rights = json.dumps(self._generate_usage_rights_strategy(creator_profile, campaign_data))
        
        # Budget strategy
        budget_strategy = json.dumps(self._generate_budget_strategy(creator_profile, pricing_strategy))
        
        # Competitor context
        competitor_context = json.dumps(self._generate_competitor_context(creator_profile, campaign_data))
        
        return {
            "InfluencerProfile": influencer_profile,
            "campaignBrief": campaign_brief,
            "negotiationStrategy": negotiation_strategy,
            "deliverableRequirements": deliverable_requirements,
            "timelineExpectations": timeline_expectations,
            "usageRights": usage_rights,
            "budgetStrategy": budget_strategy,
            "competitorContext": competitor_context,
            "influencerName": creator_profile.get('name', 'Creator')
        }
    
    def _format_influencer_profile(self, creator_profile: Dict[str, Any]) -> str:
        """📝 Format influencer profile for ElevenLabs"""
        
        name = creator_profile.get("name", "Unknown")
        channel = creator_profile.get("id", "unknown_channel")
        niche = creator_profile.get("niche", "fitness")
        followers = creator_profile.get("followers", 100000)
        engagement = creator_profile.get("engagement_rate", 5.0)
        avg_views = creator_profile.get("average_views", 50000)
        location = creator_profile.get("location", "Mumbai, India")
        languages = creator_profile.get("languages", ["English"])
        collaboration_rate = creator_profile.get("typical_rate", 3000)
        platform = creator_profile.get("platform", "Instagram")
        
        return (
            f"name:{name}, "
            f"channel:{channel}, "
            f"platform:{platform}, "
            f"niche:{niche}, "
            f"followers:{followers//1000}K, "
            f"audienceType:{niche.title()} Enthusiasts, "
            f"engagement:{engagement}%, "
            f"avgViews:{avg_views//1000}K, "
            f"location:{location}, "
            f"languages:{', '.join(languages) if isinstance(languages, list) else languages}, "
            f"collaboration_rate:{collaboration_rate}"
        )
    
    def _generate_negotiation_strategy(self, creator_profile: Dict[str, Any], campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """🎯 Generate negotiation strategy"""
        
        niche_match = creator_profile.get("niche", "").lower() == campaign_data.get("product_niche", "").lower()
        engagement = creator_profile.get("engagement_rate", 0)
        
        if niche_match and engagement > 5.0:
            approach = "collaborative"
        else:
            approach = "value_focused"
        
        return {
            "approach": approach,
            "matchReasons": self._generate_match_reasons(creator_profile, campaign_data),
            "brandAlignment": f"Creator's {creator_profile.get('niche')} expertise aligns with our {campaign_data.get('product_niche')} product",
            "objectionHandling": "flexible_on_timeline_firm_on_quality",
            "priorityPoints": ["content_authenticity", "audience_engagement"]
        }
    
    def _generate_match_reasons(self, creator_profile: Dict[str, Any], campaign_data: Dict[str, Any]) -> list:
        """Generate match reasons"""
        reasons = []
        
        engagement = creator_profile.get("engagement_rate", 0)
        if engagement > 6.0:
            reasons.append(f"Exceptional {engagement}% engagement rate")
        elif engagement > 3.0:
            reasons.append(f"Strong {engagement}% engagement rate")
        
        if creator_profile.get("niche", "").lower() == campaign_data.get("product_niche", "").lower():
            reasons.append("Perfect niche alignment")
        
        followers = creator_profile.get("followers", 0)
        if followers > 500000:
            reasons.append("Large, established audience")
        elif followers > 100000:
            reasons.append("Strong mid-tier following")
        else:
            reasons.append("Highly engaged micro-community")
        
        return reasons[:3]
    
    def _generate_deliverable_requirements(self, creator_profile: Dict[str, Any], campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """📋 Generate deliverable requirements"""
        
        platform = creator_profile.get("platform", "Instagram").lower()
        
        if platform == "youtube":
            primary = "60-90 second product review video with authentic testing"
            secondary = "YouTube Short showcasing key features"
        elif platform == "tiktok":
            primary = "60-second authentic product demo with trending audio"
            secondary = "Follow-up video showing results after 7 days"
        else:  # Instagram or general
            primary = "Instagram Reel (60-90 seconds) showing authentic product experience"
            secondary = "Feed post with 3-5 high-quality lifestyle images"
        
        return {
            "primary": primary,
            "secondary": secondary,
            "specifications": {
                "video_length": "60-90 seconds for optimal engagement",
                "quality_requirements": "1080p minimum, natural lighting preferred",
                "brand_integration": "Natural product placement, not overly promotional"
            }
        }
    
    def _generate_timeline_expectations(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """📅 Generate timeline expectations"""
        
        launch_date = datetime.now() + timedelta(days=14)
        
        return {
            "preferred": "7 days from contract signing",
            "deadline": "10 days maximum",
            "launchDate": launch_date.strftime("%B %d coordinated campaign launch"),
            "flexibility": "Can extend to 10 days if needed for quality content"
        }
    
    def _generate_usage_rights_strategy(self, creator_profile: Dict[str, Any], campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """📜 Generate usage rights"""
        
        followers = creator_profile.get("followers", 0)
        
        if followers > 500000:
            usage_type = "organic_plus_website_features"
            duration = "18 months"
        else:
            usage_type = "organic_social_media_only"
            duration = "12 months"
        
        return {
            "type": usage_type,
            "duration": f"{duration} from posting date",
            "exclusivity_period": "30 days in product category"
        }
    
    def _generate_budget_strategy(self, creator_profile: Dict[str, Any], pricing_strategy: Dict[str, Any]) -> Dict[str, Any]:
        """💰 Generate budget strategy"""
        
        initial_offer = pricing_strategy.get('initial_offer', creator_profile.get('typical_rate', 3000))
        max_offer = pricing_strategy.get('max_offer', initial_offer * 1.3)
        
        return {
            "initialOffer": initial_offer,
            "maxOffer": max_offer,
            "negotiationRoom": max_offer - initial_offer,
            "rushPremium": "+20% for 5-day delivery",
            "paymentTerms": "50% upfront, 50% on content delivery and approval"
        }
    
    def _generate_competitor_context(self, creator_profile: Dict[str, Any], campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """🏆 Generate competitive context"""
        
        return {
            "marketRates": {
                "tier_average": f"${creator_profile.get('typical_rate', 3000) * 0.9:.0f}-{creator_profile.get('typical_rate', 3000) * 1.2:.0f} for similar creators",
                "niche_premium": f"15-20% premium for {creator_profile.get('niche')} specialists"
            },
            "competitive_advantage": f"First {campaign_data.get('product_niche')} brand to offer AI-powered personalization",
            "brand_prestige": "Working with industry-leading innovators"
        }
    
    def _get_unique_value_proposition(self, campaign_data: Dict[str, Any]) -> str:
        """Get unique value proposition"""
        niche = campaign_data.get('product_niche', 'fitness')
        if niche == 'fitness':
            return "Only fitness tracker with personalized AI coaching based on individual biometrics"
        elif niche == 'tech':
            return "Revolutionary tech that adapts to user behavior through machine learning"
        else:
            return f"Industry-first innovation in {niche} space with AI-powered features"
    
    async def wait_for_conversation_completion_with_analysis(
        self, 
        conversation_id: str, 
        max_wait_seconds: int = 360
    ) -> Dict[str, Any]:
        """
        ⏳ FIXED: Wait for conversation completion with proper error handling
        """
        
        if self.use_mock:
            return await self._mock_conversation_analysis(conversation_id)
        
        if not conversation_id:
            logger.error("❌ No conversation ID provided")
            return {
                "status": "failed",
                "error": "No conversation ID provided",
                "analysis_data": {}
            }
        
        try:
            logger.info(f"⏳ Waiting for conversation {conversation_id} to complete...")
            
            start_time = asyncio.get_event_loop().time()
            poll_interval = 5  # Check every 5 seconds
            
            while (asyncio.get_event_loop().time() - start_time) < max_wait_seconds:
                # Get conversation status
                status_result = await self._get_conversation_status(conversation_id)
                
                if not status_result:
                    logger.warning("⚠️ No status result from ElevenLabs API")
                    await asyncio.sleep(poll_interval)
                    continue
                
                conversation_status = status_result.get("status", "unknown")
                logger.info(f"📞 Conversation status: {conversation_status}")
                
                # Check if conversation is complete
                if conversation_status in ["completed", "ended"]:
                    logger.info(f"✅ Conversation completed successfully")
                    
                    # Return structured result
                    return {
                        "status": "completed",
                        "conversation_id": conversation_id,
                        "transcript": status_result.get("transcript", ""),
                        "recording_url": status_result.get("recording_url"),
                        "analysis_data": self._extract_analysis_from_conversation(status_result)
                    }
                
                elif conversation_status in ["failed", "error"]:
                    logger.error(f"❌ Conversation failed with status: {conversation_status}")
                    return {
                        "status": "failed",
                        "conversation_id": conversation_id,
                        "error": f"Conversation failed: {conversation_status}",
                        "analysis_data": {}
                    }
                
                # Wait before next poll
                await asyncio.sleep(poll_interval)
            
            # Timeout reached
            logger.warning(f"⏰ Conversation timeout after {max_wait_seconds} seconds")
            return {
                "status": "timeout",
                "conversation_id": conversation_id,
                "error": f"Conversation did not complete within {max_wait_seconds} seconds",
                "analysis_data": {}
            }
            
        except Exception as e:
            logger.error(f"❌ Error waiting for conversation completion: {e}")
            return {
                "status": "error",
                "conversation_id": conversation_id,
                "error": str(e),
                "analysis_data": {}
            }
    
    async def _get_conversation_status(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation status from ElevenLabs API with proper error handling"""
        
        try:
            response = requests.get(
                f"{self.base_url}/v1/convai/conversations/{conversation_id}",
                headers={"Xi-Api-Key": self.api_key},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                logger.error(f"❌ ElevenLabs API error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting conversation status: {e}")
            return None
    
    def _extract_analysis_from_conversation(self, conversation_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract analysis data from ElevenLabs conversation result
        """
        
        # Get transcript for analysis
        transcript = conversation_result.get("transcript", "")
        
        if not transcript:
            logger.warning("⚠️ No transcript available for analysis")
            return {}
        
        # Simple keyword-based analysis (you can enhance this with your AI)
        analysis_data = {
            "negotiation_outcome": self._determine_outcome_from_transcript(transcript),
            "final_rate_mentioned": self._extract_rate_from_transcript(transcript),
            "objections_raised": self._extract_objections_from_transcript(transcript),
            "deliverables_discussed": ["video_review", "instagram_post"],  # Default
            "timeline_mentioned": "7 days",  # Default
            "creator_enthusiasm_level": self._estimate_enthusiasm_from_transcript(transcript),
            "conversation_summary": transcript[:200] + "..." if len(transcript) > 200 else transcript,
            "analysis_source": "elevenlabs_transcript"
        }
        
        logger.info(f"📊 Analysis extracted: {analysis_data['negotiation_outcome']}")
        return analysis_data
    
    def _determine_outcome_from_transcript(self, transcript: str) -> str:
        """Determine negotiation outcome from transcript"""
        
        transcript_lower = transcript.lower()
        
        # Success indicators
        success_words = ["yes", "accept", "agree", "sounds good", "deal", "interested", "perfect", "great"]
        failure_words = ["no", "decline", "reject", "not interested", "can't", "busy", "pass"]
        
        success_score = sum(1 for word in success_words if word in transcript_lower)
        failure_score = sum(1 for word in failure_words if word in transcript_lower)
        
        if success_score > failure_score:
            return "accepted"
        elif failure_score > success_score:
            return "declined"
        else:
            return "unclear"
    
    def _extract_rate_from_transcript(self, transcript: str) -> Optional[float]:
        """Extract mentioned rate from transcript"""
        
        import re
        
        # Look for dollar amounts in transcript
        money_pattern = r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
        matches = re.findall(money_pattern, transcript)
        
        if matches:
            # Return the last mentioned amount (likely the agreed rate)
            try:
                return float(matches[-1].replace(',', ''))
            except ValueError:
                pass
        
        return None
    
    def _extract_objections_from_transcript(self, transcript: str) -> list:
        """Extract objections from transcript"""
        
        transcript_lower = transcript.lower()
        objections = []
        
        if "too low" in transcript_lower or "more money" in transcript_lower:
            objections.append("price_too_low")
        if "busy" in transcript_lower or "time" in transcript_lower:
            objections.append("timeline_tight")
        if "not a fit" in transcript_lower:
            objections.append("brand_misalignment")
        
        return objections
    
    def _estimate_enthusiasm_from_transcript(self, transcript: str) -> int:
        """Estimate creator enthusiasm level (1-10) from transcript"""
        
        transcript_lower = transcript.lower()
        
        positive_words = ["excited", "love", "perfect", "amazing", "great", "awesome", "fantastic"]
        negative_words = ["concerned", "worried", "not sure", "maybe", "hesitant"]
        
        positive_score = sum(1 for word in positive_words if word in transcript_lower)
        negative_score = sum(1 for word in negative_words if word in transcript_lower)
        
        base_score = 5  # Neutral
        enthusiasm = base_score + positive_score - negative_score
        
        return max(1, min(10, enthusiasm))  # Clamp between 1-10
    
    async def _mock_enhanced_call(
        self, 
        creator_phone: str, 
        creator_profile: Dict[str, Any],
        campaign_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhanced mock call"""
        
        logger.info(f"🎭 Enhanced mock call to {creator_phone}")
        await asyncio.sleep(2)
        
        mock_conversation_id = f"mock_enhanced_{creator_profile.get('id', 'unknown')}"
        
        return {
            "status": "success",
            "conversation_id": mock_conversation_id,
            "call_id": f"mock_call_{creator_phone[-4:]}",
            "phone_number": creator_phone,
            "enhanced_mode": True
        }
    
    async def _mock_conversation_analysis(self, conversation_id: str) -> Dict[str, Any]:
        """Enhanced mock analysis with proper structure"""
        
        await asyncio.sleep(random.randint(30, 60))
        
        success = random.random() < 0.75  # 75% success rate
        
        if success:
            final_rate = random.randint(3200, 5800)
            return {
                "status": "completed",
                "conversation_id": conversation_id,
                "transcript": f"Enhanced mock conversation - Creator accepted ${final_rate}",
                "recording_url": f"https://mock-recordings.example.com/{conversation_id}",
                "analysis_data": {
                    "negotiation_outcome": "accepted",
                    "final_rate_mentioned": final_rate,
                    "objections_raised": [],
                    "deliverables_discussed": ["video_review", "instagram_post"],
                    "timeline_mentioned": "7 days",
                    "creator_enthusiasm_level": random.randint(7, 10),
                    "conversation_summary": f"Creator accepted collaboration for ${final_rate}",
                    "analysis_source": "enhanced_mock"
                }
            }
        else:
            objections = random.choice([
                ["price_too_low"],
                ["timeline_tight"], 
                ["brand_misalignment"],
                ["already_committed"]
            ])
            
            return {
                "status": "completed",
                "conversation_id": conversation_id,
                "transcript": "Enhanced mock conversation - Creator declined",
                "recording_url": f"https://mock-recordings.example.com/{conversation_id}",
                "analysis_data": {
                    "negotiation_outcome": "declined",
                    "objections_raised": objections,
                    "creator_enthusiasm_level": random.randint(3, 6),
                    "conversation_summary": f"Creator declined due to {objections[0].replace('_', ' ')}",
                    "analysis_source": "enhanced_mock"
                }
            }

# Backward compatibility aliases
ComprehensiveVoiceService = EnhancedVoiceService