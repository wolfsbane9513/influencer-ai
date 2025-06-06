# services/payment_service.py
import asyncio
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import requests
import hmac
import hashlib

from config.settings import settings
from models.campaign import NegotiationState

logger = logging.getLogger(__name__)

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"

class PaymentProvider(str, Enum):
    STRIPE = "stripe"
    RAZORPAY = "razorpay"
    MANUAL = "manual"

class MilestoneStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    APPROVED = "approved"
    PAID = "paid"

class PaymentService:
    """
    💰 PAYMENT SERVICE - Automated Creator Payment Management
    
    Features:
    - Multi-provider support (Stripe, Razorpay)
    - Milestone-based payments
    - Automated payment scheduling
    - Webhook processing
    - Creator payment dashboard data
    - Tax and compliance handling
    """
    
    def __init__(self):
        # Payment provider configuration
        self.stripe_key = getattr(settings, 'stripe_secret_key', None)
        self.razorpay_key = getattr(settings, 'razorpay_key_id', None)
        self.razorpay_secret = getattr(settings, 'razorpay_key_secret', None)
        
        # Default to Razorpay for Indian market, Stripe for international
        self.default_provider = PaymentProvider.RAZORPAY if self.razorpay_key else PaymentProvider.STRIPE
        
        # Payment processing settings
        self.auto_payment_enabled = getattr(settings, 'auto_payments_enabled', False)
        self.payment_hold_days = getattr(settings, 'payment_hold_days', 3)
        
        # Currency and regional settings
        self.default_currency = getattr(settings, 'default_currency', 'INR')
        self.supported_currencies = ['USD', 'INR', 'EUR', 'GBP']
        
        # Active payment records
        self.payment_records = {}
        
        logger.info(f"💰 Payment Service initialized - Provider: {self.default_provider.value}")
    
    async def create_campaign_payment_plan(
        self, 
        campaign_id: str,
        successful_negotiations: List[NegotiationState],
        payment_terms: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        📋 Create comprehensive payment plan for campaign
        """
        
        try:
            logger.info(f"💰 Creating payment plan for campaign {campaign_id}")
            
            # Calculate total campaign cost
            total_cost = sum(neg.final_rate or 0 for neg in successful_negotiations)
            
            # Create individual creator payment plans
            creator_payments = []
            
            for negotiation in successful_negotiations:
                if negotiation.final_rate:
                    payment_plan = await self._create_creator_payment_plan(
                        negotiation, payment_terms
                    )
                    creator_payments.append(payment_plan)
            
            # Create campaign-level payment tracking
            campaign_payment_plan = {
                "campaign_id": campaign_id,
                "total_amount": total_cost,
                "currency": self.default_currency,
                "creator_count": len(creator_payments),
                "creator_payments": creator_payments,
                "payment_provider": self.default_provider.value,
                "auto_payment_enabled": self.auto_payment_enabled,
                "created_at": datetime.now().isoformat(),
                "status": "active",
                "milestones": {
                    "total_milestones": sum(len(cp["milestones"]) for cp in creator_payments),
                    "completed_milestones": 0,
                    "pending_amount": total_cost,
                    "paid_amount": 0.0
                }
            }
            
            # Store payment plan
            self.payment_records[campaign_id] = campaign_payment_plan
            
            logger.info(f"✅ Payment plan created: {len(creator_payments)} creators, ${total_cost:,.2f} total")
            
            return {
                "status": "created",
                "campaign_payment_plan": campaign_payment_plan,
                "next_actions": self._get_payment_next_actions(campaign_payment_plan)
            }
            
        except Exception as e:
            logger.error(f"❌ Payment plan creation failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "campaign_id": campaign_id
            }
    
    async def _create_creator_payment_plan(
        self, 
        negotiation: NegotiationState,
        payment_terms: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        👤 Create payment plan for individual creator
        """
        
        creator_id = negotiation.creator_id
        total_amount = negotiation.final_rate
        
        # Get payment schedule from negotiated terms
        payment_schedule = negotiation.negotiated_terms.get("payment_schedule", "50% upfront, 50% on delivery")
        
        # Parse payment schedule into milestones
        milestones = self._parse_payment_schedule(payment_schedule, total_amount)
        
        # Generate payment IDs
        payment_plan = {
            "creator_id": creator_id,
            "negotiation_id": negotiation.conversation_id,
            "total_amount": total_amount,
            "currency": self.default_currency,
            "payment_schedule": payment_schedule,
            "milestones": milestones,
            "payment_method": "bank_transfer",  # Default for creators
            "creator_details": {
                "bank_account": None,  # To be collected
                "tax_details": None,   # To be collected
                "payment_preferences": {}
            },
            "compliance": {
                "tax_form_required": total_amount > 600,  # US tax requirement example
                "invoice_required": True,
                "contract_signed": False
            },
            "created_at": datetime.now().isoformat(),
            "status": "pending_setup"
        }
        
        return payment_plan
    
    def _parse_payment_schedule(self, schedule_text: str, total_amount: float) -> List[Dict[str, Any]]:
        """
        📅 Parse payment schedule text into structured milestones
        """
        
        milestones = []
        
        # Common schedule patterns
        if "25%" in schedule_text and "50%" in schedule_text:
            # Three-part payment
            milestones = [
                {
                    "milestone_id": f"m1_{datetime.now().strftime('%H%M%S')}",
                    "name": "Contract Signing",
                    "description": "Payment on contract execution",
                    "percentage": 25,
                    "amount": total_amount * 0.25,
                    "trigger": "contract_signed",
                    "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
                    "status": MilestoneStatus.NOT_STARTED.value
                },
                {
                    "milestone_id": f"m2_{datetime.now().strftime('%H%M%S')}",
                    "name": "Content Delivery",
                    "description": "Payment on content delivery and approval",
                    "percentage": 50,
                    "amount": total_amount * 0.50,
                    "trigger": "content_approved",
                    "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
                    "status": MilestoneStatus.NOT_STARTED.value
                },
                {
                    "milestone_id": f"m3_{datetime.now().strftime('%H%M%S')}",
                    "name": "Content Published",
                    "description": "Final payment after content goes live",
                    "percentage": 25,
                    "amount": total_amount * 0.25,
                    "trigger": "content_published",
                    "due_date": (datetime.now() + timedelta(days=14)).isoformat(),
                    "status": MilestoneStatus.NOT_STARTED.value
                }
            ]
        
        elif "50%" in schedule_text:
            # Two-part payment (most common)
            milestones = [
                {
                    "milestone_id": f"m1_{datetime.now().strftime('%H%M%S')}",
                    "name": "Upfront Payment",
                    "description": "50% payment on contract signing",
                    "percentage": 50,
                    "amount": total_amount * 0.50,
                    "trigger": "contract_signed",
                    "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
                    "status": MilestoneStatus.NOT_STARTED.value
                },
                {
                    "milestone_id": f"m2_{datetime.now().strftime('%H%M%S')}",
                    "name": "Final Payment",
                    "description": "50% payment on content delivery and approval",
                    "percentage": 50,
                    "amount": total_amount * 0.50,
                    "trigger": "content_approved",
                    "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
                    "status": MilestoneStatus.NOT_STARTED.value
                }
            ]
        
        else:
            # Single payment (fallback)
            milestones = [
                {
                    "milestone_id": f"m1_{datetime.now().strftime('%H%M%S')}",
                    "name": "Full Payment",
                    "description": "Full payment on content delivery",
                    "percentage": 100,
                    "amount": total_amount,
                    "trigger": "content_approved",
                    "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
                    "status": MilestoneStatus.NOT_STARTED.value
                }
            ]
        
        return milestones
    
    async def trigger_milestone_payment(
        self, 
        campaign_id: str,
        creator_id: str,
        milestone_trigger: str,
        verification_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        🎯 Trigger milestone payment when conditions are met
        """
        
        try:
            # Get payment plan
            payment_plan = self.payment_records.get(campaign_id)
            if not payment_plan:
                return {"status": "error", "error": "Payment plan not found"}
            
            # Find creator payment
            creator_payment = None
            for cp in payment_plan["creator_payments"]:
                if cp["creator_id"] == creator_id:
                    creator_payment = cp
                    break
            
            if not creator_payment:
                return {"status": "error", "error": "Creator payment not found"}
            
            # Find milestone to trigger
            triggered_milestone = None
            for milestone in creator_payment["milestones"]:
                if (milestone["trigger"] == milestone_trigger and 
                    milestone["status"] == MilestoneStatus.NOT_STARTED.value):
                    triggered_milestone = milestone
                    break
            
            if not triggered_milestone:
                return {"status": "error", "error": f"No pending milestone for trigger: {milestone_trigger}"}
            
            # Process payment
            payment_result = await self._process_milestone_payment(
                creator_payment, triggered_milestone, verification_data
            )
            
            # Update milestone status
            if payment_result["status"] == "success":
                triggered_milestone["status"] = MilestoneStatus.PAID.value
                triggered_milestone["paid_at"] = datetime.now().isoformat()
                triggered_milestone["payment_id"] = payment_result.get("payment_id")
                
                # Update campaign totals
                payment_plan["milestones"]["completed_milestones"] += 1
                payment_plan["milestones"]["paid_amount"] += triggered_milestone["amount"]
                payment_plan["milestones"]["pending_amount"] -= triggered_milestone["amount"]
            
            logger.info(f"💰 Milestone payment processed: {creator_id} - {milestone_trigger}")
            
            return {
                "status": "processed",
                "milestone": triggered_milestone,
                "payment_result": payment_result,
                "campaign_update": payment_plan["milestones"]
            }
            
        except Exception as e:
            logger.error(f"❌ Milestone payment failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _process_milestone_payment(
        self,
        creator_payment: Dict[str, Any],
        milestone: Dict[str, Any],
        verification_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        💳 Process actual payment through provider
        """
        
        if not self.auto_payment_enabled:
            return await self._create_manual_payment_record(creator_payment, milestone)
        
        # Choose payment provider
        provider = self.default_provider
        
        if provider == PaymentProvider.STRIPE:
            return await self._process_stripe_payment(creator_payment, milestone)
        elif provider == PaymentProvider.RAZORPAY:
            return await self._process_razorpay_payment(creator_payment, milestone)
        else:
            return await self._create_manual_payment_record(creator_payment, milestone)
    
    async def _process_stripe_payment(
        self,
        creator_payment: Dict[str, Any],
        milestone: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process payment through Stripe"""
        
        if not self.stripe_key:
            return {"status": "error", "error": "Stripe not configured"}
        
        try:
            # This would integrate with Stripe API
            # For demo, returning mock success
            payment_id = f"stripe_pay_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            logger.info(f"💳 Stripe payment processed: {payment_id}")
            
            return {
                "status": "success",
                "payment_id": payment_id,
                "provider": "stripe",
                "amount": milestone["amount"],
                "currency": self.default_currency,
                "processed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Stripe payment failed: {e}")
            return {"status": "error", "error": str(e), "provider": "stripe"}
    
    async def _process_razorpay_payment(
        self,
        creator_payment: Dict[str, Any],
        milestone: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process payment through Razorpay"""
        
        if not self.razorpay_key:
            return {"status": "error", "error": "Razorpay not configured"}
        
        try:
            # This would integrate with Razorpay API
            # For demo, returning mock success
            payment_id = f"razorpay_pay_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            logger.info(f"💳 Razorpay payment processed: {payment_id}")
            
            return {
                "status": "success",
                "payment_id": payment_id,
                "provider": "razorpay",
                "amount": milestone["amount"],
                "currency": self.default_currency,
                "processed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Razorpay payment failed: {e}")
            return {"status": "error", "error": str(e), "provider": "razorpay"}
    
    async def _create_manual_payment_record(
        self,
        creator_payment: Dict[str, Any],
        milestone: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create manual payment record for admin processing"""
        
        payment_id = f"manual_pay_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        manual_payment = {
            "payment_id": payment_id,
            "creator_id": creator_payment["creator_id"],
            "amount": milestone["amount"],
            "currency": self.default_currency,
            "milestone": milestone["name"],
            "status": "pending_manual_processing",
            "created_at": datetime.now().isoformat(),
            "instructions": {
                "payment_method": "Bank transfer",
                "admin_action_required": True,
                "verification_needed": True
            }
        }
        
        logger.info(f"📝 Manual payment record created: {payment_id}")
        
        return {
            "status": "success",
            "payment_id": payment_id,
            "provider": "manual",
            "requires_admin_action": True,
            "manual_payment": manual_payment
        }
    
    async def get_campaign_payment_status(self, campaign_id: str) -> Dict[str, Any]:
        """
        📊 Get comprehensive payment status for campaign
        """
        
        payment_plan = self.payment_records.get(campaign_id)
        if not payment_plan:
            return {"status": "not_found", "campaign_id": campaign_id}
        
        # Calculate payment statistics
        total_milestones = payment_plan["milestones"]["total_milestones"]
        completed_milestones = payment_plan["milestones"]["completed_milestones"]
        progress_percentage = (completed_milestones / max(total_milestones, 1)) * 100
        
        # Get upcoming payments
        upcoming_payments = []
        overdue_payments = []
        
        for creator_payment in payment_plan["creator_payments"]:
            for milestone in creator_payment["milestones"]:
                if milestone["status"] == MilestoneStatus.NOT_STARTED.value:
                    due_date = datetime.fromisoformat(milestone["due_date"])
                    if due_date < datetime.now():
                        overdue_payments.append({
                            "creator_id": creator_payment["creator_id"],
                            "milestone": milestone,
                            "days_overdue": (datetime.now() - due_date).days
                        })
                    else:
                        upcoming_payments.append({
                            "creator_id": creator_payment["creator_id"],
                            "milestone": milestone,
                            "days_until_due": (due_date - datetime.now()).days
                        })
        
        return {
            "status": "active",
            "campaign_id": campaign_id,
            "payment_summary": {
                "total_amount": payment_plan["total_amount"],
                "paid_amount": payment_plan["milestones"]["paid_amount"],
                "pending_amount": payment_plan["milestones"]["pending_amount"],
                "progress_percentage": progress_percentage
            },
            "milestone_progress": {
                "total_milestones": total_milestones,
                "completed_milestones": completed_milestones,
                "pending_milestones": total_milestones - completed_milestones
            },
            "upcoming_payments": upcoming_payments[:5],  # Next 5
            "overdue_payments": overdue_payments,
            "creator_count": payment_plan["creator_count"],
            "payment_provider": payment_plan["payment_provider"],
            "last_updated": datetime.now().isoformat()
        }
    
    async def get_creator_payment_dashboard(self, creator_id: str) -> Dict[str, Any]:
        """
        👤 Get payment dashboard data for creator
        """
        
        creator_payments = []
        total_earnings = 0.0
        pending_payments = 0.0
        
        # Find all payments for this creator across campaigns
        for campaign_id, payment_plan in self.payment_records.items():
            for creator_payment in payment_plan["creator_payments"]:
                if creator_payment["creator_id"] == creator_id:
                    
                    # Calculate earnings for this campaign
                    campaign_earnings = {
                        "campaign_id": campaign_id,
                        "total_amount": creator_payment["total_amount"],
                        "paid_amount": 0.0,
                        "pending_amount": 0.0,
                        "milestones": creator_payment["milestones"],
                        "status": creator_payment["status"]
                    }
                    
                    for milestone in creator_payment["milestones"]:
                        if milestone["status"] == MilestoneStatus.PAID.value:
                            campaign_earnings["paid_amount"] += milestone["amount"]
                            total_earnings += milestone["amount"]
                        else:
                            campaign_earnings["pending_amount"] += milestone["amount"]
                            pending_payments += milestone["amount"]
                    
                    creator_payments.append(campaign_earnings)
        
        return {
            "creator_id": creator_id,
            "earnings_summary": {
                "total_earned": total_earnings,
                "pending_payments": pending_payments,
                "total_campaigns": len(creator_payments),
                "average_campaign_value": total_earnings / max(len(creator_payments), 1)
            },
            "campaign_payments": creator_payments,
            "payment_history": self._get_creator_payment_history(creator_id),
            "next_payments": self._get_creator_next_payments(creator_id),
            "payment_preferences": self._get_creator_payment_preferences(creator_id),
            "tax_documents": self._get_creator_tax_documents(creator_id)
        }
    
    def _get_creator_payment_history(self, creator_id: str) -> List[Dict[str, Any]]:
        """Get payment history for creator"""
        
        history = []
        
        for payment_plan in self.payment_records.values():
            for creator_payment in payment_plan["creator_payments"]:
                if creator_payment["creator_id"] == creator_id:
                    for milestone in creator_payment["milestones"]:
                        if milestone["status"] == MilestoneStatus.PAID.value:
                            history.append({
                                "payment_date": milestone.get("paid_at"),
                                "amount": milestone["amount"],
                                "milestone": milestone["name"],
                                "payment_id": milestone.get("payment_id"),
                                "campaign_id": payment_plan["campaign_id"]
                            })
        
        # Sort by payment date (most recent first)
        history.sort(key=lambda x: x["payment_date"] or "", reverse=True)
        
        return history[:10]  # Last 10 payments
    
    def _get_creator_next_payments(self, creator_id: str) -> List[Dict[str, Any]]:
        """Get upcoming payments for creator"""
        
        next_payments = []
        
        for payment_plan in self.payment_records.values():
            for creator_payment in payment_plan["creator_payments"]:
                if creator_payment["creator_id"] == creator_id:
                    for milestone in creator_payment["milestones"]:
                        if milestone["status"] == MilestoneStatus.NOT_STARTED.value:
                            due_date = datetime.fromisoformat(milestone["due_date"])
                            next_payments.append({
                                "due_date": milestone["due_date"],
                                "amount": milestone["amount"],
                                "milestone": milestone["name"],
                                "trigger": milestone["trigger"],
                                "campaign_id": payment_plan["campaign_id"],
                                "days_until_due": (due_date - datetime.now()).days
                            })
        
        # Sort by due date
        next_payments.sort(key=lambda x: x["due_date"])
        
        return next_payments[:5]  # Next 5 payments
    
    def _get_creator_payment_preferences(self, creator_id: str) -> Dict[str, Any]:
        """Get creator payment preferences"""
        
        # In a real system, this would come from a database
        return {
            "preferred_method": "bank_transfer",
            "currency": self.default_currency,
            "minimum_payout": 100,
            "payment_schedule": "milestone_based",
            "tax_information_complete": False,
            "bank_details_verified": False
        }
    
    def _get_creator_tax_documents(self, creator_id: str) -> List[Dict[str, Any]]:
        """Get creator tax documents"""
        
        # Mock tax documents
        return [
            {
                "document_type": "1099_form",
                "year": 2024,
                "status": "pending",
                "download_url": None
            }
        ]
    
    def _get_payment_next_actions(self, payment_plan: Dict[str, Any]) -> List[str]:
        """Get next actions for payment plan"""
        
        actions = []
        
        if payment_plan["status"] == "active":
            actions.append("Collect creator bank details and tax information")
            actions.append("Set up payment milestones in campaign management")
            actions.append("Configure automatic payment triggers")
        
        if not self.auto_payment_enabled:
            actions.append("Enable automatic payments for streamlined processing")
        
        return actions
    
    async def handle_payment_webhook(self, provider: str, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        🔗 Handle payment provider webhooks
        """
        
        try:
            if provider == "stripe":
                return await self._handle_stripe_webhook(webhook_data)
            elif provider == "razorpay":
                return await self._handle_razorpay_webhook(webhook_data)
            else:
                return {"status": "error", "error": f"Unknown provider: {provider}"}
                
        except Exception as e:
            logger.error(f"❌ Webhook processing failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _handle_stripe_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Stripe webhook events"""
        
        event_type = webhook_data.get("type")
        
        if event_type == "payment_intent.succeeded":
            payment_intent = webhook_data.get("data", {}).get("object", {})
            payment_id = payment_intent.get("id")
            
            # Update payment status
            await self._update_payment_status_from_webhook(payment_id, "completed")
            
            return {"status": "processed", "event": "payment_succeeded"}
        
        return {"status": "ignored", "event_type": event_type}
    
    async def _handle_razorpay_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Razorpay webhook events"""
        
        event = webhook_data.get("event")
        
        if event == "payment.captured":
            payment = webhook_data.get("payload", {}).get("payment", {}).get("entity", {})
            payment_id = payment.get("id")
            
            # Update payment status
            await self._update_payment_status_from_webhook(payment_id, "completed")
            
            return {"status": "processed", "event": "payment_captured"}
        
        return {"status": "ignored", "event": event}
    
    async def _update_payment_status_from_webhook(self, payment_id: str, new_status: str):
        """Update payment status from webhook"""
        
        # Find and update the payment record
        for payment_plan in self.payment_records.values():
            for creator_payment in payment_plan["creator_payments"]:
                for milestone in creator_payment["milestones"]:
                    if milestone.get("payment_id") == payment_id:
                        milestone["status"] = new_status
                        milestone["webhook_confirmed_at"] = datetime.now().isoformat()
                        
                        logger.info(f"💰 Payment status updated via webhook: {payment_id} -> {new_status}")
                        return
        
        logger.warning(f"⚠️  Payment ID not found for webhook update: {payment_id}")

class PaymentAnalytics:
    """
    📊 PAYMENT ANALYTICS - Campaign and creator payment insights
    """
    
    def __init__(self, payment_service: PaymentService):
        self.payment_service = payment_service
    
    def generate_campaign_payment_report(self, campaign_id: str) -> Dict[str, Any]:
        """Generate comprehensive payment report for campaign"""
        
        payment_plan = self.payment_service.payment_records.get(campaign_id)
        if not payment_plan:
            return {"error": "Campaign not found"}
        
        # Calculate metrics
        total_creators = len(payment_plan["creator_payments"])
        total_amount = payment_plan["total_amount"]
        paid_amount = payment_plan["milestones"]["paid_amount"]
        
        # Payment efficiency metrics
        on_time_payments = 0
        late_payments = 0
        
        for creator_payment in payment_plan["creator_payments"]:
            for milestone in creator_payment["milestones"]:
                if milestone["status"] == MilestoneStatus.PAID.value:
                    due_date = datetime.fromisoformat(milestone["due_date"])
                    paid_date = datetime.fromisoformat(milestone.get("paid_at", milestone["due_date"]))
                    
                    if paid_date <= due_date:
                        on_time_payments += 1
                    else:
                        late_payments += 1
        
        return {
            "campaign_id": campaign_id,
            "financial_summary": {
                "total_budget": total_amount,
                "amount_paid": paid_amount,
                "amount_pending": total_amount - paid_amount,
                "budget_utilization": (paid_amount / total_amount) * 100
            },
            "creator_metrics": {
                "total_creators": total_creators,
                "average_payment_per_creator": total_amount / total_creators,
                "highest_payment": max((cp["total_amount"] for cp in payment_plan["creator_payments"]), default=0),
                "lowest_payment": min((cp["total_amount"] for cp in payment_plan["creator_payments"]), default=0)
            },
            "payment_efficiency": {
                "on_time_payments": on_time_payments,
                "late_payments": late_payments,
                "payment_efficiency_rate": (on_time_payments / max(on_time_payments + late_payments, 1)) * 100
            },
            "report_generated_at": datetime.now().isoformat()
        }
    
    def get_creator_payment_analytics(self, creator_id: str) -> Dict[str, Any]:
        """Get payment analytics for creator"""
        
        total_earned = 0.0
        campaign_count = 0
        payment_delays = []
        
        for payment_plan in self.payment_service.payment_records.values():
            for creator_payment in payment_plan["creator_payments"]:
                if creator_payment["creator_id"] == creator_id:
                    campaign_count += 1
                    
                    for milestone in creator_payment["milestones"]:
                        if milestone["status"] == MilestoneStatus.PAID.value:
                            total_earned += milestone["amount"]
                            
                            # Calculate payment delay
                            due_date = datetime.fromisoformat(milestone["due_date"])
                            paid_date = datetime.fromisoformat(milestone.get("paid_at", milestone["due_date"]))
                            delay_days = (paid_date - due_date).days
                            payment_delays.append(delay_days)
        
        avg_delay = sum(payment_delays) / len(payment_delays) if payment_delays else 0
        
        return {
            "creator_id": creator_id,
            "lifetime_earnings": total_earned,
            "campaign_count": campaign_count,
            "average_campaign_value": total_earned / max(campaign_count, 1),
            "payment_reliability": {
                "average_delay_days": avg_delay,
                "on_time_payment_rate": len([d for d in payment_delays if d <= 0]) / max(len(payment_delays), 1) * 100
            },
            "growth_metrics": {
                "earnings_trend": "stable",  # Would calculate from historical data
                "campaign_frequency": campaign_count / 12  # Campaigns per month
            }
        }