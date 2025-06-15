# agents/negotiation.py - CORRECTED NEGOTIATION AGENT
import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from core.models import Creator, CampaignData
from services.voice import VoiceService, CallStatus

logger = logging.getLogger(__name__)


@dataclass
class NegotiationResult:
    """Clean data class for negotiation outcomes"""
    creator_id: str
    status: str  # 'success', 'failed', 'timeout'
    conversation_id: Optional[str] = None
    final_rate: Optional[float] = None
    timeline: Optional[str] = None
    deliverables: Optional[str] = None
    error_message: Optional[str] = None
    negotiation_date: datetime = None
    
    def __post_init__(self):
        if self.negotiation_date is None:
            self.negotiation_date = datetime.now()


class NegotiationAgent:
    """
    🤝 Clean Negotiation Agent
    
    Manages voice-based negotiations with creators using proper OOP design:
    - Single responsibility: voice negotiations
    - Clean integration with VoiceService
    - No unnecessary helper functions
    - Maintainable modular structure
    """
    
    def __init__(self):
        """Initialize with voice service dependency"""
        self.voice_service = VoiceService()
        
        # Configuration
        self.max_wait_minutes = 8
        self.poll_interval_seconds = 30
        self.max_concurrent_calls = 5
        
        logger.info("🤝 Negotiation Agent initialized")
    
    async def negotiate_with_creators(
        self,
        creators: List[Creator],
        campaign_data: CampaignData
    ) -> List[NegotiationResult]:
        """
        Negotiate with multiple creators concurrently
        
        Args:
            creators: List of creators to contact
            campaign_data: Campaign information for context
            
        Returns:
            List of negotiation results
        """
        
        logger.info(f"🤝 Starting negotiations with {len(creators)} creators")
        
        # Process creators in batches to avoid overwhelming ElevenLabs API
        results = []
        
        for i in range(0, len(creators), self.max_concurrent_calls):
            batch = creators[i:i + self.max_concurrent_calls]
            batch_results = await self._process_creator_batch(batch, campaign_data)
            results.extend(batch_results)
        
        logger.info(f"🤝 Completed {len(results)} negotiations")
        
        return results
    
    async def _process_creator_batch(
        self,
        creators: List[Creator],
        campaign_data: CampaignData
    ) -> List[NegotiationResult]:
        """Process a batch of creators concurrently"""
        
        # Start all calls in the batch
        tasks = []
        for creator in creators:
            task = asyncio.create_task(
                self._negotiate_with_creator(creator, campaign_data)
            )
            tasks.append(task)
        
        # Wait for all negotiations to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle any exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"❌ Negotiation failed for {creators[i].name}: {result}")
                processed_results.append(
                    NegotiationResult(
                        creator_id=creators[i].id,
                        status="failed",
                        error_message=str(result)
                    )
                )
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _negotiate_with_creator(
        self,
        creator: Creator,
        campaign_data: CampaignData
    ) -> NegotiationResult:
        """
        Handle complete negotiation flow with single creator
        
        Args:
            creator: Creator to negotiate with
            campaign_data: Campaign context
            
        Returns:
            Negotiation result with outcome details
        """
        
        logger.info(f"🤝 Starting negotiation with {creator.name}")
        
        try:
            # Step 1: Initiate voice call
            call_result = await self.voice_service.initiate_call(
                creator=creator,
                campaign_data=campaign_data
            )
            
            if call_result["status"] == CallStatus.FAILED:
                return NegotiationResult(
                    creator_id=creator.id,
                    status="failed",
                    error_message=call_result.get("error", "Call initiation failed")
                )
            
            conversation_id = call_result["conversation_id"]
            logger.info(f"📞 Call initiated for {creator.name}: {conversation_id}")
            
            # Step 2: Monitor call until completion
            final_result = await self._monitor_call_completion(conversation_id)
            
            # Step 3: Create result object
            return self._create_negotiation_result(
                creator=creator,
                conversation_id=conversation_id,
                call_data=final_result
            )
            
        except Exception as e:
            logger.error(f"❌ Negotiation exception for {creator.name}: {e}")
            return NegotiationResult(
                creator_id=creator.id,
                status="failed",
                error_message=str(e)
            )
    
    async def _monitor_call_completion(
        self,
        conversation_id: str
    ) -> Dict[str, Any]:
        """
        Monitor call until completion or timeout
        
        Args:
            conversation_id: ElevenLabs conversation ID
            
        Returns:
            Final call results
        """
        
        start_time = datetime.now()
        max_duration = self.max_wait_minutes * 60  # Convert to seconds
        
        while True:
            # Check current call status
            status_result = await self.voice_service.check_call_status(conversation_id)
            current_status = status_result["status"]
            
            # Check if call is completed (success or failure)
            if current_status in [CallStatus.COMPLETED, CallStatus.FAILED, CallStatus.TIMEOUT]:
                logger.info(f"📞 Call {conversation_id} completed with status: {current_status}")
                return status_result
            
            # Check for timeout
            elapsed = (datetime.now() - start_time).total_seconds()
            if elapsed > max_duration:
                logger.warning(f"⏰ Call {conversation_id} timed out after {self.max_wait_minutes} minutes")
                return {
                    "status": CallStatus.TIMEOUT,
                    "conversation_id": conversation_id,
                    "error": f"Call monitoring timed out after {self.max_wait_minutes} minutes"
                }
            
            # Wait before next status check
            await asyncio.sleep(self.poll_interval_seconds)
    
    def _create_negotiation_result(
        self,
        creator: Creator,
        conversation_id: str,
        call_data: Dict[str, Any]
    ) -> NegotiationResult:
        """Create structured negotiation result from call data"""
        
        status = call_data["status"]
        
        # Determine negotiation outcome
        if status == CallStatus.COMPLETED and call_data.get("call_successful"):
            negotiation_status = "success"
        elif status == CallStatus.TIMEOUT:
            negotiation_status = "timeout"
        else:
            negotiation_status = "failed"
        
        # Log outcome
        if negotiation_status == "success":
            rate = call_data.get("final_rate", "No rate")
            logger.info(f"✅ Negotiation with {creator.name}: success - ${rate}")
        else:
            error = call_data.get("error", "Unknown error")
            logger.info(f"❌ Negotiation with {creator.name}: {negotiation_status} - {error}")
        
        return NegotiationResult(
            creator_id=creator.id,
            status=negotiation_status,
            conversation_id=conversation_id,
            final_rate=call_data.get("final_rate"),
            timeline=call_data.get("timeline"),
            deliverables=call_data.get("deliverables"),
            error_message=call_data.get("error")
        )
    
    async def close(self) -> None:
        """Clean up resources"""
        await self.voice_service.close()