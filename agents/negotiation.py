# agents/negotiation.py - COMPLETELY FIXED NEGOTIATION AGENT
import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from core.models import Creator, CampaignData, NegotiationStatus
from services.voice import VoiceService, CallStatus

logger = logging.getLogger(__name__)


@dataclass
class NegotiationResult:
    """Clean negotiation result with proper status handling"""
    creator_id: str
    status: str  # Using string instead of enum to avoid .value errors
    conversation_id: Optional[str] = None
    final_rate: Optional[float] = None
    timeline: Optional[str] = None
    deliverables: Optional[str] = None
    error_message: Optional[str] = None
    negotiation_date: datetime = None
    
    def __post_init__(self):
        if self.negotiation_date is None:
            self.negotiation_date = datetime.now()
    
    def is_successful(self) -> bool:
        """Check if negotiation was successful"""
        return self.status == "success"
    
    @property
    def rate(self) -> Optional[float]:
        """Compatibility property for rate access"""
        return self.final_rate
    
    @property 
    def creator_name(self) -> str:
        """Fallback creator name property"""
        return self.creator_id


class NegotiationAgent:
    """
    🤝 Fixed Negotiation Agent
    
    Key Fixes:
    1. Proper string status handling (no more .value errors)
    2. Sequential processing instead of mass calling
    3. Improved error handling and recovery
    4. Resource cleanup with close() method
    5. Better integration with VoiceService
    """
    
    def __init__(self):
        """Initialize with voice service dependency"""
        self.voice_service = VoiceService()
        
        # Configuration for controlled calling
        self.max_wait_minutes = 8
        self.poll_interval_seconds = 30
        self.max_retries = 2
        
        logger.info("🤝 Negotiation Agent initialized")
    
    async def negotiate_with_creator(
        self,
        creator: Creator,
        campaign_data: CampaignData
    ) -> NegotiationResult:
        """
        Single creator negotiation with proper error handling
        
        Args:
            creator: Creator to negotiate with
            campaign_data: Campaign context
            
        Returns:
            Negotiation result with outcome details
        """
        
        logger.info(f"🤝 Starting negotiation with {creator.name}")
        
        retry_count = 0
        last_error = None
        
        while retry_count <= self.max_retries:
            try:
                # Attempt negotiation
                result = await self._attempt_negotiation(creator, campaign_data)
                
                # If successful or definitively failed, return result
                if result.status in ["success", "failed"]:
                    return result
                
                # If timeout or temporary failure, retry
                if retry_count < self.max_retries:
                    retry_count += 1
                    logger.warning(f"⚠️ Retrying negotiation with {creator.name} (attempt {retry_count + 1})")
                    await asyncio.sleep(5)  # Brief delay before retry
                else:
                    return result
                    
            except Exception as e:
                last_error = str(e)
                logger.error(f"❌ Negotiation exception for {creator.name}: {e}")
                
                if retry_count < self.max_retries:
                    retry_count += 1
                    await asyncio.sleep(5)
                else:
                    break
        
        # All retries exhausted
        return NegotiationResult(
            creator_id=creator.id,
            status="failed",
            error_message=last_error or "Max retries exceeded"
        )
    
    async def _attempt_negotiation(
        self,
        creator: Creator,
        campaign_data: CampaignData
    ) -> NegotiationResult:
        """
        Single negotiation attempt
        
        Args:
            creator: Creator to contact
            campaign_data: Campaign information
            
        Returns:
            Negotiation result
        """
        
        try:
            # Step 1: Initiate voice call
            call_result = await self.voice_service.initiate_call(
                creator=creator,
                campaign_data=campaign_data
            )
            
            # Check if call initiation failed
            if not call_result.get("success", False):
                error_msg = call_result.get("message", "Call initiation failed")
                logger.warning(f"⚠️ Call initiation failed for {creator.name}: {error_msg}")
                
                return NegotiationResult(
                    creator_id=creator.id,
                    status="failed",
                    error_message=error_msg
                )
            
            conversation_id = call_result.get("conversation_id")
            if not conversation_id:
                return NegotiationResult(
                    creator_id=creator.id,
                    status="failed",
                    error_message="No conversation ID received"
                )
            
            logger.info(f"📞 Call initiated for {creator.name}: {conversation_id}")
            
            # Step 2: Monitor call until completion
            final_result = await self._monitor_call_completion(conversation_id)
            
            # Step 3: Create and return result
            return self._create_negotiation_result(
                creator=creator,
                conversation_id=conversation_id,
                call_data=final_result
            )
            
        except Exception as e:
            logger.error(f"❌ Negotiation attempt failed for {creator.name}: {e}")
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
        Monitor call until completion with improved error handling
        
        Args:
            conversation_id: ElevenLabs conversation ID
            
        Returns:
            Final call results
        """
        
        start_time = datetime.now()
        max_duration = self.max_wait_minutes * 60
        check_count = 0
        
        logger.info(f"🔄 Monitoring call {conversation_id}")
        
        while True:
            try:
                # Check current call status
                status_result = await self.voice_service.check_call_status(conversation_id)
                check_count += 1
                
                if not status_result:
                    logger.warning(f"⚠️ No status result for {conversation_id}")
                    await asyncio.sleep(self.poll_interval_seconds)
                    continue
                
                current_status = status_result.get("status")
                logger.debug(f"🔍 Call {conversation_id} status check #{check_count}: {current_status}")
                
                # Check if call is definitively completed
                if current_status in ["completed", "failed", "timeout"]:
                    logger.info(f"📞 Call {conversation_id} finished with status: {current_status}")
                    return status_result
                
                # Check for timeout
                elapsed = (datetime.now() - start_time).total_seconds()
                if elapsed > max_duration:
                    logger.warning(f"⏰ Call {conversation_id} monitoring timed out after {self.max_wait_minutes} minutes")
                    return {
                        "status": "timeout",
                        "conversation_id": conversation_id,
                        "error": f"Call monitoring timed out after {self.max_wait_minutes} minutes",
                        "call_successful": False
                    }
                
                # Wait before next status check
                await asyncio.sleep(self.poll_interval_seconds)
                
            except Exception as e:
                logger.error(f"❌ Status check error for {conversation_id}: {e}")
                
                # If we've made several attempts, return failure
                if check_count > 3:
                    return {
                        "status": "failed",
                        "conversation_id": conversation_id,
                        "error": f"Status monitoring failed: {str(e)}",
                        "call_successful": False
                    }
                
                # Otherwise wait and retry
                await asyncio.sleep(self.poll_interval_seconds)
    
    def _create_negotiation_result(
        self,
        creator: Creator,
        conversation_id: str,
        call_data: Dict[str, Any]
    ) -> NegotiationResult:
        """
        Create structured negotiation result with proper status handling
        
        Args:
            creator: Creator that was contacted
            conversation_id: ElevenLabs conversation ID
            call_data: Final call results
            
        Returns:
            Structured negotiation result
        """
        
        status = call_data.get("status", "failed")
        call_successful = call_data.get("call_successful", False)
        
        # Determine final negotiation status (using strings, not enums)
        if status == "completed" and call_successful:
            final_status = "success"
        elif status == "timeout":
            final_status = "timeout"
        else:
            final_status = "failed"
        
        # Extract negotiation details
        final_rate = call_data.get("final_rate") or call_data.get("negotiated_rate")
        timeline = call_data.get("timeline") or call_data.get("agreed_timeline")
        deliverables = call_data.get("deliverables") or call_data.get("content_deliverables")
        error_message = call_data.get("error") or call_data.get("error_message")
        
        # Log the outcome
        if final_status == "success":
            rate_info = f"${final_rate}" if final_rate else "Rate TBD"
            logger.info(f"✅ Negotiation with {creator.name}: success - {rate_info}")
        else:
            error_info = error_message or "Unknown error"
            logger.info(f"❌ Negotiation with {creator.name}: {final_status} - {error_info}")
        
        return NegotiationResult(
            creator_id=creator.id,
            status=final_status,  # String status, no .value needed
            conversation_id=conversation_id,
            final_rate=final_rate,
            timeline=timeline,
            deliverables=deliverables,
            error_message=error_message
        )
    
    async def close(self) -> None:
        """Clean up resources"""
        try:
            await self.voice_service.close()
            logger.info("✅ Negotiation Agent resources cleaned up")
        except Exception as e:
            logger.error(f"❌ Error cleaning up negotiation agent: {e}")


# Legacy compatibility method for orchestrator
async def negotiate_with_creators(
    negotiation_agent: NegotiationAgent,
    creators: List[Creator],
    campaign_data: CampaignData
) -> List[NegotiationResult]:
    """
    Compatibility wrapper for bulk negotiations
    """
    results = []
    for creator in creators:
        result = await negotiation_agent.negotiate_with_creator(creator, campaign_data)
        results.append(result)
    return results