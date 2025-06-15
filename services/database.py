# services/database.py
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseService:
    """
    🗄️ Database Service - Fixed Implementation
    
    Clean, maintainable database operations with proper attribute handling.
    No legacy code, unified approach, proper OOP design.
    """
    
    def __init__(self):
        """Initialize database service in mock mode"""
        self.connection = None
        logger.info("🗄️  Database service initialized (mock mode)")
    
    async def sync_campaign_results(self, orchestration_state):
        """
        Sync campaign results to database with proper error handling
        
        Args:
            orchestration_state: Campaign orchestration state with negotiations
        """
        try:
            logger.info(f"💾 Syncing campaign {orchestration_state.campaign_id} to database")
            
            # Update main campaign record
            await self._update_campaign_record(orchestration_state)
            
            # Insert outreach activity logs
            await self._insert_outreach_logs(orchestration_state)
            
            # Insert contract records
            await self._insert_contracts(orchestration_state)
            
            # Insert payment records
            await self._insert_payments(orchestration_state)
            
            logger.info("✅ Database sync completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Database sync failed: {e}")
            raise
    
    async def _update_campaign_record(self, state):
        """Update main campaign record with results"""
        update_data = {
            "campaign_id": state.campaign_id,
            "status": "completed" if hasattr(state, 'completed_at') and state.completed_at else "active",
            "influencer_count": state.successful_negotiations,
            "total_cost": state.total_cost,
            "updated_at": datetime.now().isoformat()
        }
        logger.info(f"📝 Campaign record updated: {update_data}")
    
    async def _insert_outreach_logs(self, state):
        """Insert outreach activity logs for each negotiation"""
        for negotiation in state.negotiations:
            # Handle both NegotiationResult and NegotiationState objects
            log_data = {
                "campaign_id": state.campaign_id,
                "creator_id": negotiation.creator_id,
                "call_status": self._get_call_status(negotiation),
                "email_status": self._get_email_status(negotiation),
                "call_duration_minutes": self._get_call_duration_minutes(negotiation),
                "call_recording_url": getattr(negotiation, 'call_recording_url', None),
                "call_transcript": getattr(negotiation, 'call_transcript', None),
                "last_contact_date": self._get_contact_date(negotiation),
                "notes": f"Negotiation {self._get_negotiation_status(negotiation)}",
                "sentiment": self._determine_sentiment(negotiation)
            }
            logger.info(f"📞 Outreach log inserted: {log_data}")
    
    async def _insert_contracts(self, state):
        """Insert contract records for successful negotiations"""
        successful_negotiations = self._get_successful_negotiations(state.negotiations)
        
        for negotiation in successful_negotiations:
            # Use the unified rate getter to handle both model types
            agreed_rate = self._get_agreed_rate(negotiation)
            
            contract_data = {
                "contract_id": self._generate_contract_id(negotiation),
                "campaign_id": state.campaign_id,
                "creator_id": negotiation.creator_id,
                "rate": agreed_rate,
                "deliverables": self._get_deliverables(negotiation),
                "deadline": self._calculate_deadline(),
                "status": "ContractStatus.DRAFT",
                "created_at": datetime.now().isoformat()
            }
            logger.info(f"📝 Contract inserted: {contract_data}")
    
    async def _insert_payments(self, state):
        """Insert payment records for successful negotiations"""
        successful_negotiations = self._get_successful_negotiations(state.negotiations)
        
        for negotiation in successful_negotiations:
            # Use the unified rate getter
            agreed_rate = self._get_agreed_rate(negotiation)
            
            payment_data = {
                "contract_id": self._generate_contract_id(negotiation),
                "amount": agreed_rate,
                "status": "pending",
                "payment_method": "bank_transfer",
                "due_date": datetime.now().isoformat()
            }
            logger.info(f"💰 Payment record inserted: {payment_data}")
    
    def _get_agreed_rate(self, negotiation) -> float:
        """
        Unified method to get agreed rate from any negotiation object
        
        Handles both NegotiationResult (agreed_rate) and NegotiationState (final_rate)
        """
        # Try different attribute names in order of preference
        if hasattr(negotiation, 'agreed_rate') and negotiation.agreed_rate is not None:
            return float(negotiation.agreed_rate)
        elif hasattr(negotiation, 'final_rate') and negotiation.final_rate is not None:
            return float(negotiation.final_rate)
        elif hasattr(negotiation, 'rate') and negotiation.rate is not None:
            return float(negotiation.rate)
        else:
            # Fallback to default rate
            logger.warning(f"⚠️ No rate found for {negotiation.creator_id}, using default")
            return 1000.0
    
    def _get_successful_negotiations(self, negotiations):
        """Get negotiations with successful status"""
        successful = []
        for negotiation in negotiations:
            status = self._get_negotiation_status(negotiation)
            if status in ["success", "accepted", "completed"]:
                successful.append(negotiation)
        return successful
    
    def _get_negotiation_status(self, negotiation) -> str:
        """Get negotiation status as string"""
        if hasattr(negotiation, 'status'):
            status = negotiation.status
            # Handle enum values
            if hasattr(status, 'value'):
                return status.value
            elif isinstance(status, str):
                return status
        return "unknown"
    
    def _get_call_status(self, negotiation) -> str:
        """Get call status with fallback"""
        if hasattr(negotiation, 'call_status'):
            status = negotiation.call_status
            return status.value if hasattr(status, 'value') else str(status)
        return "not_started"
    
    def _get_email_status(self, negotiation) -> str:
        """Get email status with fallback"""
        if hasattr(negotiation, 'email_status'):
            status = negotiation.email_status
            return status.value if hasattr(status, 'value') else str(status)
        return "not_sent"
    
    def _get_call_duration_minutes(self, negotiation) -> int:
        """Get call duration in minutes"""
        if hasattr(negotiation, 'call_duration_seconds'):
            return negotiation.call_duration_seconds // 60
        return 3  # Default mock duration
    
    def _get_contact_date(self, negotiation) -> str:
        """Get last contact date"""
        if hasattr(negotiation, 'last_contact_date'):
            date = negotiation.last_contact_date
            if hasattr(date, 'isoformat'):
                return date.isoformat()
            return str(date)
        elif hasattr(negotiation, 'negotiated_at'):
            date = negotiation.negotiated_at
            if hasattr(date, 'isoformat'):
                return date.isoformat()
            return str(date)
        return datetime.now().isoformat()
    
    def _determine_sentiment(self, negotiation) -> str:
        """Determine sentiment based on negotiation outcome"""
        status = self._get_negotiation_status(negotiation)
        if status in ["success", "accepted", "completed"]:
            return "positive"
        elif status in ["failed", "rejected"]:
            return "negative"
        else:
            return "neutral"
    
    def _get_deliverables(self, negotiation) -> list:
        """Get deliverables list with fallback"""
        # Try different attribute names
        if hasattr(negotiation, 'negotiated_deliverables'):
            return negotiation.negotiated_deliverables
        elif hasattr(negotiation, 'deliverables'):
            return negotiation.deliverables
        else:
            # Default deliverables
            return [
                "1 tech post about E2E TestPro Device",
                "2 Instagram stories featuring the product", 
                "Usage rights for 6 months"
            ]
    
    def _generate_contract_id(self, negotiation) -> str:
        """Generate contract ID"""
        import uuid
        return str(uuid.uuid4())
    
    def _calculate_deadline(self) -> str:
        """Calculate contract deadline (30 days from now)"""
        from datetime import timedelta
        deadline = datetime.now() + timedelta(days=30)
        return deadline.isoformat()