# services/elevenlabs_voice_service.py
"""
Consolidated ElevenLabs Voice Service with production-grade error handling
and clean architecture principles.
"""

import asyncio
import logging
import hashlib
import hmac
import json
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, Callable, List
from urllib.parse import urljoin

import aiohttp
import requests
from core.exceptions import (
    InfluencerFlowException,
    ValidationError,
    ElevenLabsAPIError,
    RateLimitError,
    create_error_context,
    elevenlabs_service,
    ErrorCategory,
)

logger = logging.getLogger(__name__)


class ConversationStatus(str, Enum):
    """ElevenLabs conversation status values"""

    INITIATED = "initiated"
    IN_PROGRESS = "in-progress"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"
    NO_ANSWER = "no-answer"
    BUSY = "busy"
    TIMEOUT = "timeout"


class CallResult(str, Enum):
    """Call outcome classifications"""

    SUCCESS = "success"
    NO_ANSWER = "no_answer"
    BUSY = "busy"
    FAILED = "failed"
    RATE_LIMITED = "rate_limited"
    INVALID_NUMBER = "invalid_number"


@dataclass
class CallConfiguration:
    """Configuration for voice calls"""

    agent_id: str
    phone_number_id: str
    timeout_seconds: int = 300
    retry_attempts: int = 3
    retry_delay_base: float = 2.0
    rate_limit_delay: float = 60.0


@dataclass
class ConversationResult:
    """Structured result from a completed conversation"""

    conversation_id: str
    status: ConversationStatus
    call_result: CallResult
    duration_seconds: Optional[int] = None
    transcript: Optional[str] = None
    recording_url: Optional[str] = None
    analysis_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_recommended: bool = False


class VoiceServiceException(InfluencerFlowException):
    """Base exception for voice service operations using structured errors"""

    def __init__(self, message: str, call_result: CallResult = CallResult.FAILED, **kwargs):
        context = kwargs.pop(
            "context",
            create_error_context(
                operation="voice_service",
                component="ElevenLabsVoiceService",
            ),
        )
        super().__init__(
            message=message,
            category=ErrorCategory.EXTERNAL_API,
            context=context,
            **kwargs,
        )
        self.call_result = call_result


class RateLimitException(RateLimitError):
    """Rate limit exceeded exception"""

    def __init__(self, retry_after: int = 60, **kwargs):
        super().__init__(
            message=f"Rate limit exceeded, retry after {retry_after}s",
            service="ElevenLabs",
            retry_after=retry_after,
            **kwargs,
        )
        self.call_result = CallResult.RATE_LIMITED


class IVoiceService(ABC):
    """Abstract interface for voice services"""

    @abstractmethod
    async def initiate_call(self, phone_number: str, conversation_context: Dict[str, Any]) -> str:
        """Initiate a voice call and return conversation ID"""
        pass

    @abstractmethod
    async def monitor_conversation(
        self, conversation_id: str, completion_callback: Optional[Callable] = None
    ) -> ConversationResult:
        """Monitor conversation until completion"""
        pass

    @abstractmethod
    async def get_conversation_status(self, conversation_id: str) -> Dict[str, Any]:
        """Get current conversation status"""
        pass


class ConnectionManager:
    """Manages HTTP connections and implements circuit breaker pattern"""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.session: Optional[aiohttp.ClientSession] = None
        self.failure_count = 0
        self.last_failure_time = 0
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_timeout = 300  # 5 minutes

    async def __aenter__(self):
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=60, connect=10)
            self.session = aiohttp.ClientSession(
                timeout=timeout, headers={"Xi-Api-Key": self.api_key, "Content-Type": "application/json"}
            )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            self.session = None

    def _is_circuit_open(self) -> bool:
        """Check if circuit breaker is open"""
        if self.failure_count < self.circuit_breaker_threshold:
            return False

        return (time.time() - self.last_failure_time) < self.circuit_breaker_timeout

    async def make_request(self, method: str, endpoint: str, **kwargs) -> aiohttp.ClientResponse:
        """Make HTTP request with circuit breaker"""
        if self._is_circuit_open():
            raise ElevenLabsAPIError(
                message="Circuit breaker is open - service unavailable",
                context=create_error_context(
                    operation="make_request",
                    component="ConnectionManager",
                ),
            )

        if not self.session:
            raise ElevenLabsAPIError(
                message="Connection manager not initialized",
                context=create_error_context(
                    operation="make_request",
                    component="ConnectionManager",
                ),
            )

        url = urljoin(self.base_url, endpoint)

        try:
            response = await self.session.request(method, url, **kwargs)

            # Reset failure count on successful request
            if response.status < 400:
                self.failure_count = 0

            return response

        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            logger.error(f"Request failed: {e}")
            raise ElevenLabsAPIError(
                message=f"Request failed: {e}",
                context=create_error_context(
                    operation="make_request",
                    component="ConnectionManager",
                ),
            )


class ConversationAnalyzer:
    """Analyzes conversation transcripts and extracts structured data"""

    def analyze_conversation(self, transcript: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured analysis from conversation transcript"""
        if not transcript:
            return {"analysis_source": "no_transcript", "analysis_confidence": 0.0, "negotiation_outcome": "unclear"}

        analysis_data = {
            "negotiation_outcome": self._determine_outcome(transcript),
            "final_rate_mentioned": self._extract_rate(transcript),
            "objections_raised": self._extract_objections(transcript),
            "deliverables_discussed": self._extract_deliverables(transcript),
            "timeline_mentioned": self._extract_timeline(transcript),
            "creator_enthusiasm_level": self._estimate_enthusiasm(transcript),
            "conversation_summary": self._generate_summary(transcript),
            "key_quotes": self._extract_key_quotes(transcript),
            "analysis_source": "nlp_analysis",
            "analysis_confidence": self._calculate_confidence(transcript),
            "processed_at": datetime.now().isoformat(),
        }

        return analysis_data

    def _determine_outcome(self, transcript: str) -> str:
        """Determine negotiation outcome from transcript"""
        transcript_lower = transcript.lower()

        success_indicators = ["yes", "accept", "agree", "sounds good", "deal", "interested"]
        failure_indicators = ["no", "decline", "reject", "not interested", "can't", "busy"]
        followup_indicators = ["think about it", "let me consider", "get back to you"]

        success_score = sum(1 for word in success_indicators if word in transcript_lower)
        failure_score = sum(1 for word in failure_indicators if word in transcript_lower)
        followup_score = sum(1 for word in followup_indicators if word in transcript_lower)

        if success_score > failure_score and success_score > followup_score:
            return "accepted"
        elif failure_score > success_score and failure_score > followup_score:
            return "declined"
        elif followup_score > 0:
            return "needs_followup"
        else:
            return "unclear"

    def _extract_rate(self, transcript: str) -> Optional[float]:
        """Extract mentioned rate from transcript"""
        import re

        money_pattern = r"\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)"
        matches = re.findall(money_pattern, transcript)

        if matches:
            try:
                return float(matches[-1].replace(",", ""))
            except ValueError:
                pass

        return None

    def _extract_objections(self, transcript: str) -> List[str]:
        """Extract objections from transcript"""
        transcript_lower = transcript.lower()
        objections = []

        objection_patterns = {
            "price_too_low": ["too low", "more money", "higher rate"],
            "timeline_tight": ["busy", "tight timeline", "not enough time"],
            "brand_misalignment": ["not a fit", "doesn't align", "different brand"],
            "already_committed": ["already working", "committed to", "exclusive"],
        }

        for objection_type, patterns in objection_patterns.items():
            if any(pattern in transcript_lower for pattern in patterns):
                objections.append(objection_type)

        return objections

    def _extract_deliverables(self, transcript: str) -> List[str]:
        """Extract discussed deliverables from transcript"""
        transcript_lower = transcript.lower()
        deliverables = []

        deliverable_patterns = {
            "video_review": ["video", "review video", "product review"],
            "instagram_post": ["instagram post", "feed post", "ig post"],
            "instagram_story": ["story", "stories", "instagram story"],
            "tiktok_video": ["tiktok", "tik tok", "short video"],
            "unboxing_video": ["unboxing", "unbox"],
        }

        for deliverable, patterns in deliverable_patterns.items():
            if any(pattern in transcript_lower for pattern in patterns):
                deliverables.append(deliverable)

        return deliverables if deliverables else ["video_review", "instagram_post"]

    def _extract_timeline(self, transcript: str) -> str:
        """Extract timeline from transcript"""
        import re

        time_pattern = r"(\d+)\s*(day|days|week|weeks)"
        matches = re.findall(time_pattern, transcript.lower())

        if matches:
            number, unit = matches[-1]
            return f"{number} {unit}"

        return "7 days"

    def _estimate_enthusiasm(self, transcript: str) -> int:
        """Estimate creator enthusiasm level (1-10) from transcript"""
        transcript_lower = transcript.lower()

        positive_words = ["excited", "love", "perfect", "amazing", "great", "awesome"]
        negative_words = ["concerned", "worried", "not sure", "maybe", "hesitant"]

        positive_score = sum(1 for word in positive_words if word in transcript_lower)
        negative_score = sum(1 for word in negative_words if word in transcript_lower)

        enthusiasm = 5 + positive_score - negative_score
        return max(1, min(10, enthusiasm))

    def _generate_summary(self, transcript: str) -> str:
        """Generate conversation summary"""
        if len(transcript) <= 200:
            return transcript
        return transcript[:200] + "..."

    def _extract_key_quotes(self, transcript: str) -> List[str]:
        """Extract key quotes from transcript"""
        sentences = transcript.split(".")
        key_quotes = []

        for sentence in sentences[:5]:
            sentence = sentence.strip()
            if 20 <= len(sentence) <= 100:
                key_quotes.append(sentence)

        return key_quotes[:3]

    def _calculate_confidence(self, transcript: str) -> float:
        """Calculate confidence in analysis results"""
        confidence_factors = []

        if len(transcript) > 200:
            confidence_factors.append(0.3)
        elif len(transcript) > 100:
            confidence_factors.append(0.2)

        if any(word in transcript.lower() for word in ["rate", "price", "dollars", "$"]):
            confidence_factors.append(0.2)

        if any(word in transcript.lower() for word in ["yes", "no", "accept", "decline"]):
            confidence_factors.append(0.3)

        if any(word in transcript.lower() for word in ["video", "post", "content"]):
            confidence_factors.append(0.2)

        return sum(confidence_factors)


class ElevenLabsVoiceService(IVoiceService):
    """Production-grade ElevenLabs voice service with comprehensive error handling"""

    def __init__(self, api_key: str, config: CallConfiguration):
        self.api_key = api_key
        self.config = config
        self.base_url = "https://api.elevenlabs.io"
        self.analyzer = ConversationAnalyzer()

        # Validate configuration
        if not api_key:
            raise VoiceServiceException("ElevenLabs API key is required")

        if not config.agent_id or not config.phone_number_id:
            raise VoiceServiceException("Agent ID and Phone Number ID are required")

    @elevenlabs_service()
    async def test_credentials(self) -> Dict[str, Any]:
        """Test API credentials and service availability"""
        context = create_error_context(
            operation="test_credentials",
            component="ElevenLabsVoiceService",
        )

        async with ConnectionManager(self.base_url, self.api_key) as conn:
            try:
                response = await conn.make_request("GET", "/v1/user")

                if response.status == 200:
                    user_data = await response.json()
                    return {
                        "status": "success",
                        "message": "Credentials verified",
                        "user": user_data.get("email", "Unknown"),
                        "service_available": True,
                    }
                else:
                    raise ElevenLabsAPIError(
                        message=f"Credential verification failed: {response.status}",
                        status_code=response.status,
                        context=context,
                    )

            except InfluencerFlowException:
                raise
            except Exception as e:
                raise ElevenLabsAPIError(
                    message=f"Service test failed: {str(e)}",
                    context=context,
                )

    @elevenlabs_service()
    async def initiate_call(
        self,
        phone_number: str,
        conversation_context: Dict[str, Any],
    ) -> str:
        """Initiate a voice call with comprehensive error handling"""

        context = create_error_context(
            operation="initiate_call",
            component="ElevenLabsVoiceService",
        )

        async with ConnectionManager(self.base_url, self.api_key) as conn:
            try:
                dynamic_vars = self._prepare_dynamic_variables(conversation_context)

                payload = {
                    "agent_id": self.config.agent_id,
                    "agent_phone_number_id": self.config.phone_number_id,
                    "to_number": phone_number,
                    "conversation_initiation_client_data": {"dynamic_variables": dynamic_vars},
                }

                response = await conn.make_request(
                    "POST",
                    "/v1/convai/twilio/outbound-call",
                    json=payload,
                )

                if response.status == 200:
                    result = await response.json()
                    conversation_id = result.get("conversation_id")

                    if not conversation_id:
                        raise ElevenLabsAPIError(
                            message="No conversation ID in response",
                            context=context,
                            status_code=response.status,
                        )

                    logger.info(f"Call initiated successfully: {conversation_id}")
                    return conversation_id

                if response.status == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    raise RateLimitException(retry_after=retry_after, context=context)

                if response.status == 400:
                    error_data = await response.json()
                    raise ValidationError(
                        message="Invalid phone number",
                        field_errors={"phone_number": ["invalid or unsupported"]},
                        context=context,
                        details={"response": error_data},
                    )

                error_text = await response.text()
                raise ElevenLabsAPIError(
                    message=f"Call initiation failed: {error_text}",
                    status_code=response.status,
                    context=context,
                )

            except InfluencerFlowException:
                raise
            except Exception as e:
                raise ElevenLabsAPIError(
                    message=f"Unexpected error during call initiation: {e}",
                    context=context,
                )

    @elevenlabs_service()
    async def monitor_conversation(
        self,
        conversation_id: str,
        completion_callback: Optional[Callable] = None,
    ) -> ConversationResult:
        """Monitor conversation with proper timeout and error handling"""

        context = create_error_context(
            operation="monitor_conversation",
            component="ElevenLabsVoiceService",
        )

        start_time = time.time()
        poll_interval = 10  # Poll every 10 seconds

        async with ConnectionManager(self.base_url, self.api_key) as conn:
            while (time.time() - start_time) < self.config.timeout_seconds:
                try:
                    status_data = await self.get_conversation_status(conversation_id)
                    status = ConversationStatus(status_data.get("status", "unknown"))

                    logger.debug(f"Conversation {conversation_id}: {status}")

                    if status in [
                        ConversationStatus.DONE,
                        ConversationStatus.FAILED,
                        ConversationStatus.NO_ANSWER,
                        ConversationStatus.BUSY,
                    ]:
                        result = await self._process_completed_conversation(conversation_id, status, status_data)

                        if completion_callback:
                            await self._safe_callback(completion_callback, result)

                        return result

                    await asyncio.sleep(poll_interval)

                except InfluencerFlowException:
                    raise
                except Exception as e:
                    logger.error(f"Error monitoring conversation {conversation_id}: {e}")
                    raise ElevenLabsAPIError(
                        message=f"Monitoring failed: {e}",
                        context=context,
                    )

            logger.warning(f"Conversation {conversation_id} timed out")
            return ConversationResult(
                conversation_id=conversation_id,
                status=ConversationStatus.TIMEOUT,
                call_result=CallResult.FAILED,
                error_message="Conversation monitoring timed out",
                retry_recommended=True,
            )

    @elevenlabs_service()
    async def get_conversation_status(self, conversation_id: str) -> Dict[str, Any]:
        """Get conversation status from ElevenLabs API"""
        context = create_error_context(
            operation="get_conversation_status",
            component="ElevenLabsVoiceService",
            additional_data={"conversation_id": conversation_id},
        )

        async with ConnectionManager(self.base_url, self.api_key) as conn:
            try:
                response = await conn.make_request(
                    "GET",
                    f"/v1/convai/conversations/{conversation_id}",
                )

                if response.status == 200:
                    return await response.json()

                error_text = await response.text()
                raise ElevenLabsAPIError(
                    message=f"Failed to get conversation status: {error_text}",
                    status_code=response.status,
                    context=context,
                )
            except InfluencerFlowException:
                raise
            except Exception as e:
                raise ElevenLabsAPIError(
                    message=f"Unexpected error fetching status: {e}",
                    context=context,
                )

    def _prepare_dynamic_variables(self, context: Dict[str, Any]) -> Dict[str, str]:
        """Prepare dynamic variables for ElevenLabs agent"""
        try:
            creator_profile = context.get("creator_profile", {})
            campaign_data = context.get("campaign_data", {})
            pricing_strategy = context.get("pricing_strategy", {})

            # Format influencer profile
            influencer_profile = self._format_influencer_profile(creator_profile)

            # Prepare campaign brief
            campaign_brief = json.dumps(
                {
                    "brand_name": campaign_data.get("brand_name", ""),
                    "product_name": campaign_data.get("product_name", ""),
                    "product_description": campaign_data.get("product_description", ""),
                    "target_audience": campaign_data.get("target_audience", ""),
                    "campaign_goal": campaign_data.get("campaign_goal", ""),
                }
            )

            # Budget strategy
            initial_offer = pricing_strategy.get("initial_offer", 0)
            max_offer = pricing_strategy.get("max_offer", initial_offer * 1.2)

            return {
                "InfluencerProfile": influencer_profile,
                "campaignBrief": campaign_brief,
                "budgetStrategy": f"${initial_offer:.0f} initial, max ${max_offer:.0f}",
                "influencerName": creator_profile.get("name", "Creator"),
                "conversationMode": "negotiation",
            }

        except Exception as e:
            logger.error(f"Error preparing dynamic variables: {e}")
            # Return minimal fallback
            return {
                "influencerName": context.get("creator_profile", {}).get("name", "Creator"),
                "campaignBrief": "Brand collaboration opportunity",
                "conversationMode": "negotiation",
            }

    def _format_influencer_profile(self, creator_profile: Dict[str, Any]) -> str:
        """Format creator profile for ElevenLabs"""
        name = creator_profile.get("name", "Unknown")
        niche = creator_profile.get("niche", "general")
        followers = creator_profile.get("followers", 0)
        engagement = creator_profile.get("engagement_rate", 0)
        platform = creator_profile.get("platform", "social media")

        return (
            f"name:{name}, "
            f"platform:{platform}, "
            f"niche:{niche}, "
            f"followers:{followers//1000}K, "
            f"engagement:{engagement}%"
        )

    async def _process_completed_conversation(
        self, conversation_id: str, status: ConversationStatus, status_data: Dict[str, Any]
    ) -> ConversationResult:
        """Process completed conversation and extract results"""

        call_result = self._map_status_to_result(status)
        transcript = status_data.get("transcript", "")

        # Analyze conversation if successful
        analysis_data = None
        if status == ConversationStatus.DONE and transcript:
            analysis_data = self.analyzer.analyze_conversation(transcript, {})

        # Determine if retry is recommended
        retry_recommended = call_result in [CallResult.NO_ANSWER, CallResult.BUSY]

        return ConversationResult(
            conversation_id=conversation_id,
            status=status,
            call_result=call_result,
            transcript=transcript,
            recording_url=status_data.get("recording_url"),
            analysis_data=analysis_data,
            error_message=status_data.get("error_message"),
            retry_recommended=retry_recommended,
        )

    def _map_status_to_result(self, status: ConversationStatus) -> CallResult:
        """Map ElevenLabs status to call result"""
        mapping = {
            ConversationStatus.DONE: CallResult.SUCCESS,
            ConversationStatus.FAILED: CallResult.FAILED,
            ConversationStatus.NO_ANSWER: CallResult.NO_ANSWER,
            ConversationStatus.BUSY: CallResult.BUSY,
            ConversationStatus.TIMEOUT: CallResult.FAILED,
        }
        return mapping.get(status, CallResult.FAILED)

    async def _safe_callback(self, callback: Callable, *args) -> None:
        """Safely execute callback with error handling"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(*args)
            else:
                callback(*args)
        except Exception as e:
            logger.error(f"Callback error: {e}")


class MockVoiceService(IVoiceService):
    """Mock voice service for testing and development"""

    def __init__(self):
        self.analyzer = ConversationAnalyzer()

    async def initiate_call(self, phone_number: str, conversation_context: Dict[str, Any]) -> str:
        """Mock call initiation"""
        await asyncio.sleep(1)  # Simulate API delay
        conversation_id = f"mock_{int(time.time())}"
        logger.info(f"Mock call initiated: {conversation_id}")
        return conversation_id

    async def monitor_conversation(
        self, conversation_id: str, completion_callback: Optional[Callable] = None
    ) -> ConversationResult:
        """Mock conversation monitoring"""
        # Simulate conversation duration
        await asyncio.sleep(random.randint(30, 90))

        # Generate realistic mock result
        success = random.random() < 0.75  # 75% success rate

        if success:
            transcript = "Creator: Yes, I'm interested in working with you. The rate sounds good."
            analysis_data = self.analyzer.analyze_conversation(transcript, {})

            result = ConversationResult(
                conversation_id=conversation_id,
                status=ConversationStatus.DONE,
                call_result=CallResult.SUCCESS,
                duration_seconds=random.randint(60, 180),
                transcript=transcript,
                analysis_data=analysis_data,
            )
        else:
            # Mock failure scenarios
            failure_types = [CallResult.NO_ANSWER, CallResult.BUSY, CallResult.FAILED]
            call_result = random.choice(failure_types)

            result = ConversationResult(
                conversation_id=conversation_id,
                status=ConversationStatus.FAILED,
                call_result=call_result,
                error_message=f"Mock {call_result.value}",
                retry_recommended=call_result in [CallResult.NO_ANSWER, CallResult.BUSY],
            )

        if completion_callback:
            await self._safe_callback(completion_callback, result)

        return result

    async def get_conversation_status(self, conversation_id: str) -> Dict[str, Any]:
        """Mock status check"""
        return {"status": "done", "conversation_id": conversation_id, "mock_mode": True}

    async def _safe_callback(self, callback: Callable, *args) -> None:
        """Safely execute callback"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(*args)
            else:
                callback(*args)
        except Exception as e:
            logger.error(f"Mock callback error: {e}")


class VoiceServiceFactory:
    """Factory for creating voice service instances"""

    @staticmethod
    def create_voice_service(
        api_key: Optional[str] = None,
        agent_id: Optional[str] = None,
        phone_number_id: Optional[str] = None,
        use_mock: bool = False,
    ) -> IVoiceService:
        """Create appropriate voice service instance"""

        if use_mock or not all([api_key, agent_id, phone_number_id]):
            logger.info("Creating mock voice service")
            return MockVoiceService()

        config = CallConfiguration(agent_id=agent_id, phone_number_id=phone_number_id)

        logger.info("Creating ElevenLabs voice service")
        return ElevenLabsVoiceService(api_key, config)


# Webhook signature verification utility
def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify ElevenLabs webhook signature"""
    try:
        timestamp, provided_hash = signature.split(".", 1)

        # Create expected signature
        message = f"{timestamp}.{payload.decode()}"
        expected_hash = hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()

        return hmac.compare_digest(provided_hash, expected_hash)

    except Exception as e:
        logger.error(f"Webhook signature verification failed: {e}")
        return False
