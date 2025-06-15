import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable
from enum import Enum

logger = logging.getLogger(__name__)

class ConversationStatus(str, Enum):
    """Standard conversation status values"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    ERROR = "error"

class ConversationMonitor:
    """
    🔄 CORRECTED CONVERSATION MONITOR
    
    Fixes:
    1. Proper state detection and transitions
    2. Better error handling for failed/ended calls
    3. Improved callback management
    4. Automatic cleanup and resource management
    """
    
    def __init__(self, voice_service):
        self.voice_service = voice_service
        self.active_monitors = {}
        
        # Configuration
        self.poll_interval_seconds = 15
        self.max_wait_minutes = 8
        self.timeout_buffer_seconds = 30
        
        # Status mapping from ElevenLabs to our states
        self.status_mapping = {
            "initiated": ConversationStatus.IN_PROGRESS,
            "in-progress": ConversationStatus.IN_PROGRESS,
            "processing": ConversationStatus.IN_PROGRESS,
            "done": ConversationStatus.COMPLETED,
            "completed": ConversationStatus.COMPLETED,
            "failed": ConversationStatus.FAILED,
            "error": ConversationStatus.FAILED,
            "timeout": ConversationStatus.TIMEOUT
        }
    
    async def start_monitoring(
        self,
        conversation_id: str,
        completion_callback: Optional[Callable] = None,
        error_callback: Optional[Callable] = None
    ) -> None:
        """
        🚀 Start monitoring conversation with proper state handling
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
            "start_time": datetime.now(),
            "completion_callback": completion_callback,
            "error_callback": error_callback
        }
    
    async def _monitor_conversation_loop(
        self,
        conversation_id: str,
        completion_callback: Optional[Callable] = None,
        error_callback: Optional[Callable] = None
    ) -> None:
        """
        🔄 Main monitoring loop with corrected state handling
        """
        
        start_time = datetime.now()
        max_wait_seconds = self.max_wait_minutes * 60
        
        try:
            while (datetime.now() - start_time).total_seconds() < max_wait_seconds:
                
                # Get conversation status
                status_data = await self.voice_service.get_conversation_status(conversation_id)
                
                if not status_data:
                    logger.warning(f"⚠️ No status data for {conversation_id}, continuing...")
                    await asyncio.sleep(self.poll_interval_seconds)
                    continue
                
                # Extract and normalize status
                raw_status = status_data.get("status", "unknown")
                normalized_status = status_data.get("normalized_status") or self._normalize_status(raw_status)
                
                logger.info(f"📊 Conversation {conversation_id} status: {normalized_status}")
                
                # Handle completed conversations
                if normalized_status == ConversationStatus.COMPLETED:
                    logger.info(f"✅ Conversation completed: {conversation_id}")
                    
                    if completion_callback:
                        try:
                            await self._safe_callback(
                                completion_callback,
                                conversation_id,
                                status_data
                            )
                        except Exception as e:
                            logger.error(f"❌ Completion callback error: {e}")
                    
                    self._cleanup_monitor(conversation_id)
                    return
                
                # Handle failed conversations
                elif normalized_status in [ConversationStatus.FAILED, ConversationStatus.ERROR]:
                    error_msg = status_data.get("error", f"Conversation failed with status: {raw_status}")
                    logger.error(f"❌ Conversation failed: {conversation_id} - {error_msg}")
                    
                    if error_callback:
                        try:
                            await self._safe_callback(
                                error_callback,
                                conversation_id,
                                error_msg
                            )
                        except Exception as e:
                            logger.error(f"❌ Error callback error: {e}")
                    
                    self._cleanup_monitor(conversation_id)
                    return
                
                # Continue monitoring for in-progress conversations
                elif normalized_status == ConversationStatus.IN_PROGRESS:
                    await asyncio.sleep(self.poll_interval_seconds)
                    continue
                
                # Handle unknown status
                else:
                    logger.warning(f"⚠️ Unknown status for {conversation_id}: {normalized_status}")
                    await asyncio.sleep(self.poll_interval_seconds)
                    continue
            
            # Timeout reached
            timeout_msg = f"Conversation timeout after {self.max_wait_minutes} minutes"
            logger.warning(f"⏰ {timeout_msg}: {conversation_id}")
            
            if error_callback:
                try:
                    await self._safe_callback(error_callback, conversation_id, timeout_msg)
                except Exception as e:
                    logger.error(f"❌ Timeout callback error: {e}")
            
            self._cleanup_monitor(conversation_id)
            
        except Exception as e:
            error_msg = f"Monitoring error: {str(e)}"
            logger.error(f"❌ {error_msg} for {conversation_id}")
            
            if error_callback:
                try:
                    await self._safe_callback(error_callback, conversation_id, error_msg)
                except Exception as e:
                    logger.error(f"❌ Exception callback error: {e}")
            
            self._cleanup_monitor(conversation_id)
    
    def _normalize_status(self, raw_status: str) -> ConversationStatus:
        """Normalize status from various sources"""
        return self.status_mapping.get(raw_status.lower(), ConversationStatus.ERROR)
    
    async def _safe_callback(self, callback: Callable, *args) -> None:
        """Execute callback safely with error handling"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(*args)
            else:
                callback(*args)
        except Exception as e:
            logger.error(f"❌ Callback execution failed: {e}")
    
    def _cleanup_monitor(self, conversation_id: str) -> None:
        """Clean up monitoring resources"""
        if conversation_id in self.active_monitors:
            monitor_info = self.active_monitors[conversation_id]
            
            # Cancel the task if it's still running
            task = monitor_info["task"]
            if not task.done():
                task.cancel()
            
            del self.active_monitors[conversation_id]
            logger.info(f"🧹 Cleaned up monitor for {conversation_id}")
    
    def stop_monitoring(self, conversation_id: str) -> None:
        """Stop monitoring a specific conversation"""
        if conversation_id in self.active_monitors:
            self._cleanup_monitor(conversation_id)
            logger.info(f"🛑 Stopped monitoring {conversation_id}")
    
    def stop_all_monitoring(self) -> None:
        """Stop all active monitoring"""
        for conversation_id in list(self.active_monitors.keys()):
            self._cleanup_monitor(conversation_id)
        logger.info("🛑 Stopped all conversation monitoring")
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get status of all active monitoring"""
        status = {
            "active_monitors": len(self.active_monitors),
            "conversations": {}
        }
        
        current_time = datetime.now()
        
        for conversation_id, monitor_info in self.active_monitors.items():
            start_time = monitor_info["start_time"]
            duration = (current_time - start_time).total_seconds()
            
            status["conversations"][conversation_id] = {
                "duration_seconds": duration,
                "start_time": start_time.isoformat(),
                "task_status": "running" if not monitor_info["task"].done() else "completed"
            }
        
        return status


class ConversationEventHandler:
    """
    📡 CONVERSATION EVENT HANDLER
    
    Integrates with orchestrator to handle conversation events properly
    """
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        logger.info("📡 ConversationEventHandler initialized")
    
    async def handle_conversation_completion(
        self,
        conversation_id: str,
        conversation_data: Dict[str, Any]
    ) -> None:
        """Handle successful conversation completion"""
        
        logger.info(f"✅ Handling conversation completion: {conversation_id}")
        
        try:
            # Extract analysis data
            analysis_data = conversation_data.get("analysis", {})
            
            # Notify orchestrator of completion
            await self.orchestrator.handle_conversation_completed(
                conversation_id,
                conversation_data,
                analysis_data
            )
            
            logger.info(f"✅ Successfully processed completion for {conversation_id}")
            
        except Exception as e:
            logger.error(f"❌ Error handling completion for {conversation_id}: {e}")
            
            # Notify orchestrator of processing error
            await self.orchestrator.handle_conversation_error(
                conversation_id,
                f"Completion processing error: {str(e)}"
            )
    
    async def handle_conversation_error(
        self,
        conversation_id: str,
        error_message: str
    ) -> None:
        """Handle conversation errors and failures"""
        
        logger.error(f"❌ Handling conversation error: {conversation_id} - {error_message}")
        
        try:
            # Notify orchestrator of error
            await self.orchestrator.handle_conversation_error(
                conversation_id,
                error_message
            )
            
            logger.info(f"✅ Successfully processed error for {conversation_id}")
            
        except Exception as e:
            logger.error(f"❌ Error handling error for {conversation_id}: {e}")