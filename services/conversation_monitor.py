# services/conversation_monitor.py
import asyncio
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable
from enum import Enum

from config.settings import settings

logger = logging.getLogger(__name__)

class ConversationStatus(str, Enum):
    """ElevenLabs conversation status values"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress" 
    COMPLETED = "completed"
    ENDED = "ended"
    FAILED = "failed"
    TIMEOUT = "timeout"
    ERROR = "error"

class ConversationMonitor:
    """
    🔄 CONVERSATION MONITOR - Polls ElevenLabs API and manages conversation lifecycle
    
    Key Features:
    - Configurable polling intervals (10-20 seconds)
    - Automatic status detection and transition
    - Callback system for status changes
    - Proper error handling and timeouts
    - Integration with existing orchestrator workflow
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.elevenlabs.io"):
        self.api_key = api_key
        self.base_url = base_url
        self.active_monitors = {}  # Track active conversation monitors
        
        # Configuration
        self.poll_interval_seconds = 15  # Poll every 15 seconds
        self.max_wait_minutes = 6        # Maximum 6 minutes per conversation
        self.timeout_buffer_seconds = 30  # Extra buffer for network delays
        
    async def start_monitoring(
        self, 
        conversation_id: str,
        completion_callback: Callable[[str, Dict[str, Any]], None] = None,
        error_callback: Callable[[str, str], None] = None
    ) -> None:
        """
        🚀 Start monitoring a conversation with automatic status polling
        
        Args:
            conversation_id: ElevenLabs conversation ID
            completion_callback: Called when conversation completes successfully
            error_callback: Called when conversation fails or times out
        """
        
        if conversation_id in self.active_monitors:
            logger.warning(f"⚠️ Conversation {conversation_id} already being monitored")
            return
            
        logger.info(f"🔄 Starting conversation monitoring: {conversation_id}")
        
        # Create monitoring task
        monitor_task = asyncio.create_task(
            self._monitor_conversation_loop(
                conversation_id, 
                completion_callback, 
                error_callback
            )
        )
        
        self.active_monitors[conversation_id] = {
            "task": monitor_task,
            "started_at": datetime.now(),
            "status": ConversationStatus.PENDING
        }
    
    async def _monitor_conversation_loop(
        self,
        conversation_id: str,
        completion_callback: Optional[Callable] = None,
        error_callback: Optional[Callable] = None
    ) -> None:
        """
        🔁 Main monitoring loop - polls ElevenLabs API until completion
        """
        
        start_time = datetime.now()
        max_duration = timedelta(minutes=self.max_wait_minutes)
        
        try:
            while datetime.now() - start_time < max_duration:
                # Get current conversation status
                status_result = await self._fetch_conversation_status(conversation_id)
                
                if not status_result:
                    logger.warning(f"⚠️ No status response for {conversation_id}")
                    await asyncio.sleep(self.poll_interval_seconds)
                    continue
                
                current_status = status_result.get("status", "unknown").lower()
                
                # Update monitoring record
                if conversation_id in self.active_monitors:
                    self.active_monitors[conversation_id]["status"] = current_status
                    self.active_monitors[conversation_id]["last_checked"] = datetime.now()
                
                logger.info(f"📞 Conversation {conversation_id}: {current_status}")
                
                # Check for completion states
                if current_status in ["completed", "ended"]:
                    logger.info(f"✅ Conversation {conversation_id} completed successfully")
                    
                    if completion_callback:
                        await self._safe_callback(
                            completion_callback, 
                            conversation_id, 
                            status_result
                        )
                    
                    # Clean up monitoring
                    self._cleanup_monitor(conversation_id)
                    return
                    
                elif current_status in ["failed", "error"]:
                    error_msg = f"Conversation failed with status: {current_status}"
                    logger.error(f"❌ {error_msg}")
                    
                    if error_callback:
                        await self._safe_callback(error_callback, conversation_id, error_msg)
                    
                    self._cleanup_monitor(conversation_id)
                    return
                
                # Continue monitoring
                await asyncio.sleep(self.poll_interval_seconds)
            
            # Timeout reached
            timeout_msg = f"Conversation timeout after {self.max_wait_minutes} minutes"
            logger.warning(f"⏰ {timeout_msg}")
            
            if error_callback:
                await self._safe_callback(error_callback, conversation_id, timeout_msg)
            
            self._cleanup_monitor(conversation_id)
            
        except Exception as e:
            error_msg = f"Monitoring error: {str(e)}"
            logger.error(f"❌ {error_msg}")
            
            if error_callback:
                await self._safe_callback(error_callback, conversation_id, error_msg)
            
            self._cleanup_monitor(conversation_id)
    
    async def _fetch_conversation_status(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        📡 Fetch conversation status from ElevenLabs API
        """
        
        try:
            # Use asyncio to run the requests call in a thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.get(
                    f"{self.base_url}/v1/convai/conversations/{conversation_id}",
                    headers={"Xi-Api-Key": self.api_key},
                    timeout=10
                )
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(
                    f"❌ ElevenLabs API error {response.status_code}: {response.text[:200]}"
                )
                return None
                
        except Exception as e:
            logger.error(f"❌ Error fetching conversation status: {e}")
            return None
    
    async def _safe_callback(self, callback: Callable, *args) -> None:
        """
        🛡️ Safely execute callback with error handling
        """
        
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(*args)
            else:
                callback(*args)
        except Exception as e:
            logger.error(f"❌ Callback error: {e}")
    
    def _cleanup_monitor(self, conversation_id: str) -> None:
        """
        🧹 Clean up monitoring resources
        """
        
        if conversation_id in self.active_monitors:
            monitor_info = self.active_monitors[conversation_id]
            task = monitor_info["task"]
            
            if not task.done():
                task.cancel()
            
            del self.active_monitors[conversation_id]
            logger.info(f"🧹 Cleaned up monitor for {conversation_id}")
    
    def get_monitoring_status(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        📊 Get current monitoring status for a conversation
        """
        
        return self.active_monitors.get(conversation_id)
    
    def stop_monitoring(self, conversation_id: str) -> bool:
        """
        🛑 Stop monitoring a specific conversation
        """
        
        if conversation_id in self.active_monitors:
            self._cleanup_monitor(conversation_id)
            return True
        return False
    
    def stop_all_monitoring(self) -> int:
        """
        🛑 Stop all active monitoring tasks
        """
        
        count = len(self.active_monitors)
        for conversation_id in list(self.active_monitors.keys()):
            self._cleanup_monitor(conversation_id)
        
        logger.info(f"🛑 Stopped {count} monitoring tasks")
        return count
    
    def get_active_conversations(self) -> Dict[str, Dict[str, Any]]:
        """
        📋 Get all active conversation monitoring status
        """
        
        active_status = {}
        
        for conv_id, monitor_info in self.active_monitors.items():
            active_status[conv_id] = {
                "status": monitor_info["status"],
                "started_at": monitor_info["started_at"].isoformat(),
                "duration_seconds": (datetime.now() - monitor_info["started_at"]).total_seconds(),
                "is_active": not monitor_info["task"].done()
            }
        
        return active_status


class ConversationEventHandler:
    """
    📢 EVENT HANDLER - Manages conversation completion events and orchestrator integration
    
    This class bridges the conversation monitor with the orchestrator workflow
    """
    
    def __init__(self, orchestrator_instance):
        self.orchestrator = orchestrator_instance
        self.conversation_results = {}  # Store results for orchestrator access
    
    async def on_conversation_completed(self, conversation_id: str, result: Dict[str, Any]) -> None:
        """
        ✅ Handle successful conversation completion
        """
        
        logger.info(f"🎉 Conversation completed: {conversation_id}")
        
        # Store result for orchestrator access
        self.conversation_results[conversation_id] = {
            "status": "completed",
            "result": result,
            "completed_at": datetime.now().isoformat()
        }
        
        # Trigger orchestrator to continue workflow
        await self._notify_orchestrator_continuation(conversation_id, result)
    
    async def on_conversation_failed(self, conversation_id: str, error_message: str) -> None:
        """
        ❌ Handle conversation failure
        """
        
        logger.error(f"💥 Conversation failed: {conversation_id} - {error_message}")
        
        # Store error result
        self.conversation_results[conversation_id] = {
            "status": "failed",
            "error": error_message,
            "failed_at": datetime.now().isoformat()
        }
        
        # Notify orchestrator of failure
        await self._notify_orchestrator_failure(conversation_id, error_message)
    
    async def _notify_orchestrator_continuation(self, conversation_id: str, result: Dict[str, Any]) -> None:
        """
        🔄 Notify orchestrator to continue with next step
        """
        
        try:
            # Find the negotiation state for this conversation
            if hasattr(self.orchestrator, 'current_orchestration_state'):
                state = self.orchestrator.current_orchestration_state
                
                # Find matching negotiation
                for negotiation in state.negotiations:
                    if negotiation.conversation_id == conversation_id:
                        logger.info(f"🎯 Found matching negotiation for {conversation_id}")
                        
                        # Update negotiation with results
                        await self._update_negotiation_with_results(negotiation, result)
                        
                        # Check if all negotiations are complete
                        if self._all_negotiations_complete(state):
                            logger.info("🏁 All negotiations complete - continuing orchestrator")
                            await self._continue_orchestrator_workflow(state)
                        
                        break
            
        except Exception as e:
            logger.error(f"❌ Error notifying orchestrator: {e}")
    
    async def _notify_orchestrator_failure(self, conversation_id: str, error_message: str) -> None:
        """
        🚨 Notify orchestrator of conversation failure
        """
        
        try:
            if hasattr(self.orchestrator, 'current_orchestration_state'):
                state = self.orchestrator.current_orchestration_state
                
                # Find and update the failed negotiation
                for negotiation in state.negotiations:
                    if negotiation.conversation_id == conversation_id:
                        negotiation.status = "failed"
                        negotiation.failure_reason = error_message
                        negotiation.completed_at = datetime.now()
                        break
                
                # Continue with remaining negotiations or move to next phase
                await self._handle_negotiation_failure(state, conversation_id)
            
        except Exception as e:
            logger.error(f"❌ Error handling orchestrator failure: {e}")
    
    async def _update_negotiation_with_results(self, negotiation, result: Dict[str, Any]) -> None:
        """
        📝 Update negotiation state with conversation results
        """
        
        # Extract structured data from ElevenLabs result
        analysis_data = result.get("analysis_data", {})
        
        negotiation.status = "success"
        negotiation.completed_at = datetime.now()
        negotiation.call_transcript = result.get("transcript", "")
        negotiation.call_recording_url = result.get("recording_url")
        
        # Extract negotiated terms
        negotiation.final_rate = analysis_data.get("final_rate_mentioned", 0)
        negotiation.negotiated_terms = {
            "deliverables": analysis_data.get("deliverables_discussed", ["video_review"]),
            "timeline": analysis_data.get("timeline_mentioned", "7 days"),
            "payment_schedule": "50% upfront, 50% on delivery",
            "conversation_summary": analysis_data.get("conversation_summary", ""),
            "creator_enthusiasm": analysis_data.get("creator_enthusiasm_level", 5)
        }
        
        logger.info(f"📝 Updated negotiation: ${negotiation.final_rate}")
    
    def _all_negotiations_complete(self, state) -> bool:
        """
        🔍 Check if all current negotiations are complete
        """
        
        for negotiation in state.negotiations:
            if negotiation.status in ["pending", "calling", "negotiating"]:
                return False
        
        return True
    
    async def _continue_orchestrator_workflow(self, state) -> None:
        """
        ⏭️ Continue orchestrator workflow to next phase
        """
        
        logger.info("⏭️ Continuing orchestrator workflow...")
        
        # Update orchestrator state
        state.current_stage = "contracts"
        
        # Trigger next phase (contract generation)
        if hasattr(self.orchestrator, '_run_enhanced_contract_phase'):
            await self.orchestrator._run_enhanced_contract_phase(state)
        
    async def _handle_negotiation_failure(self, state, conversation_id: str) -> None:
        """
        🔧 Handle individual negotiation failure
        """
        
        # Check if we should continue with other negotiations or move on
        successful_count = len([n for n in state.negotiations if n.status == "success"])
        
        if successful_count > 0 or self._all_negotiations_complete(state):
            logger.info("✅ Moving to next phase despite failures")
            await self._continue_orchestrator_workflow(state)
        else:
            logger.info("⏳ Waiting for other negotiations to complete")
    
    def get_conversation_result(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        📊 Get stored conversation result
        """
        
        return self.conversation_results.get(conversation_id)