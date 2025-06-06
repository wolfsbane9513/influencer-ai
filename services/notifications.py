# services/notifications.py
import asyncio
import logging
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config.settings import settings

logger = logging.getLogger(__name__)

class NotificationType(str, Enum):
    CAMPAIGN_CREATED = "campaign_created"
    CAMPAIGN_COMPLETED = "campaign_completed"
    NEGOTIATION_SUCCESS = "negotiation_success"
    NEGOTIATION_FAILED = "negotiation_failed"
    PAYMENT_DUE = "payment_due"
    PAYMENT_COMPLETED = "payment_completed"
    PERFORMANCE_ALERT = "performance_alert"
    SYSTEM_ALERT = "system_alert"
    CREATOR_RESPONSE = "creator_response"
    MILESTONE_REACHED = "milestone_reached"

class NotificationChannel(str, Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    WEBHOOK = "webhook"
    SLACK = "slack"
    SMS = "sms"
    IN_APP = "in_app"

class NotificationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class NotificationService:
    """
    🔔 REAL-TIME NOTIFICATIONS SERVICE
    
    Features:
    - Multi-channel notifications (Email, WhatsApp, Webhook, Slack)
    - Real-time alerts and updates
    - Campaign progress notifications
    - Performance alerts and insights
    - Automated stakeholder communication
    - Notification templates and personalization
    """
    
    def __init__(self):
        # Notification channels configuration
        self.channels = {
            NotificationChannel.EMAIL: self._initialize_email_service(),
            NotificationChannel.WHATSAPP: self._initialize_whatsapp_service(),
            NotificationChannel.WEBHOOK: self._initialize_webhook_service(),
            NotificationChannel.SLACK: self._initialize_slack_service(),
            NotificationChannel.SMS: self._initialize_sms_service()
        }
        
        # Notification templates
        self.templates = self._load_notification_templates()
        
        # Subscriber management
        self.subscribers = {
            "campaigns": {},  # campaign_id -> [subscribers]
            "global": [],     # Global notifications
            "users": {}       # user_id -> notification preferences
        }
        
        # Notification queue for batch processing
        self.notification_queue = []
        self.batch_size = 10
        
        # Real-time connections (WebSocket subscribers)
        self.realtime_connections = {}
        
        logger.info("🔔 Notification Service initialized")
    
    async def send_notification(
        self,
        notification_type: NotificationType,
        recipients: List[str],
        data: Dict[str, Any],
        channels: List[NotificationChannel] = None,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        template_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        📤 Send notification to specified recipients
        """
        
        try:
            # Default channels based on priority
            if channels is None:
                channels = self._get_default_channels(priority)
            
            notification_id = f"notif_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            
            # Prepare notification data
            notification = {
                "id": notification_id,
                "type": notification_type.value,
                "recipients": recipients,
                "data": data,
                "channels": [c.value for c in channels],
                "priority": priority.value,
                "created_at": datetime.now().isoformat(),
                "status": "sending",
                "delivery_results": {}
            }
            
            # Generate content for each channel
            content = await self._generate_notification_content(
                notification_type, data, template_override
            )
            
            # Send via each channel
            delivery_tasks = []
            for channel in channels:
                if channel in self.channels and self.channels[channel]["enabled"]:
                    task = self._send_via_channel(
                        channel, recipients, content, notification
                    )
                    delivery_tasks.append(task)
            
            # Execute all delivery tasks
            delivery_results = await asyncio.gather(*delivery_tasks, return_exceptions=True)
            
            # Update notification status
            notification["status"] = "sent"
            notification["delivery_results"] = {
                channels[i].value: result for i, result in enumerate(delivery_results)
            }
            
            # Log notification
            logger.info(f"🔔 Notification sent: {notification_type.value} to {len(recipients)} recipients")
            
            return {
                "status": "success",
                "notification_id": notification_id,
                "delivery_summary": self._summarize_delivery_results(delivery_results),
                "channels_used": [c.value for c in channels]
            }
            
        except Exception as e:
            logger.error(f"❌ Notification sending failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "notification_type": notification_type.value
            }
    
    async def subscribe_to_campaign(
        self,
        campaign_id: str,
        user_id: str,
        notification_types: List[NotificationType] = None,
        channels: List[NotificationChannel] = None
    ) -> Dict[str, Any]:
        """
        🔔 Subscribe user to campaign notifications
        """
        
        if notification_types is None:
            notification_types = [
                NotificationType.CAMPAIGN_COMPLETED,
                NotificationType.NEGOTIATION_SUCCESS,
                NotificationType.PERFORMANCE_ALERT
            ]
        
        if channels is None:
            channels = [NotificationChannel.EMAIL, NotificationChannel.IN_APP]
        
        subscription = {
            "user_id": user_id,
            "notification_types": [nt.value for nt in notification_types],
            "channels": [c.value for c in channels],
            "subscribed_at": datetime.now().isoformat(),
            "active": True
        }
        
        # Add to campaign subscribers
        if campaign_id not in self.subscribers["campaigns"]:
            self.subscribers["campaigns"][campaign_id] = []
        
        self.subscribers["campaigns"][campaign_id].append(subscription)
        
        logger.info(f"🔔 User {user_id} subscribed to campaign {campaign_id} notifications")
        
        return {
            "status": "subscribed",
            "campaign_id": campaign_id,
            "user_id": user_id,
            "subscription": subscription
        }
    
    async def notify_campaign_progress(
        self,
        campaign_id: str,
        stage: str,
        progress_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        📊 Send campaign progress notifications
        """
        
        # Get campaign subscribers
        subscribers = self.subscribers["campaigns"].get(campaign_id, [])
        recipients = [sub["user_id"] for sub in subscribers if sub["active"]]
        
        if not recipients:
            return {"status": "no_subscribers"}
        
        # Determine notification type based on stage
        if stage == "completed":
            notification_type = NotificationType.CAMPAIGN_COMPLETED
            priority = NotificationPriority.HIGH
        elif stage == "negotiations" and progress_data.get("successful_negotiations", 0) > 0:
            notification_type = NotificationType.NEGOTIATION_SUCCESS
            priority = NotificationPriority.MEDIUM
        else:
            notification_type = NotificationType.MILESTONE_REACHED
            priority = NotificationPriority.LOW
        
        # Send notification
        return await self.send_notification(
            notification_type=notification_type,
            recipients=recipients,
            data={
                "campaign_id": campaign_id,
                "stage": stage,
                "progress": progress_data,
                "timestamp": datetime.now().isoformat()
            },
            priority=priority
        )
    
    async def notify_negotiation_result(
        self,
        campaign_id: str,
        creator_id: str,
        negotiation_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        📞 Send negotiation result notifications
        """
        
        success = negotiation_result.get("status") == "success"
        
        notification_type = (
            NotificationType.NEGOTIATION_SUCCESS if success 
            else NotificationType.NEGOTIATION_FAILED
        )
        
        # Get subscribers
        subscribers = self.subscribers["campaigns"].get(campaign_id, [])
        recipients = [sub["user_id"] for sub in subscribers if sub["active"]]
        
        return await self.send_notification(
            notification_type=notification_type,
            recipients=recipients,
            data={
                "campaign_id": campaign_id,
                "creator_id": creator_id,
                "negotiation_result": negotiation_result,
                "final_rate": negotiation_result.get("final_rate"),
                "success": success
            },
            priority=NotificationPriority.HIGH if success else NotificationPriority.MEDIUM
        )
    
    async def notify_performance_alert(
        self,
        campaign_id: str,
        alert_type: str,
        alert_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        ⚠️ Send performance alert notifications
        """
        
        # Determine priority based on alert type
        priority_map = {
            "underperformance": NotificationPriority.HIGH,
            "overperformance": NotificationPriority.MEDIUM,
            "budget_exceeded": NotificationPriority.URGENT,
            "low_engagement": NotificationPriority.HIGH
        }
        
        priority = priority_map.get(alert_type, NotificationPriority.MEDIUM)
        
        # Get subscribers
        subscribers = self.subscribers["campaigns"].get(campaign_id, [])
        recipients = [sub["user_id"] for sub in subscribers if sub["active"]]
        
        return await self.send_notification(
            notification_type=NotificationType.PERFORMANCE_ALERT,
            recipients=recipients,
            data={
                "campaign_id": campaign_id,
                "alert_type": alert_type,
                "alert_data": alert_data,
                "recommended_actions": alert_data.get("recommendations", [])
            },
            priority=priority
        )
    
    async def notify_payment_milestone(
        self,
        campaign_id: str,
        creator_id: str,
        milestone_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        💰 Send payment milestone notifications
        """
        
        milestone_type = milestone_data.get("type", "payment_due")
        
        notification_type = (
            NotificationPriority.PAYMENT_COMPLETED if milestone_type == "payment_completed"
            else NotificationPriority.PAYMENT_DUE
        )
        
        # Get subscribers + creator
        subscribers = self.subscribers["campaigns"].get(campaign_id, [])
        recipients = [sub["user_id"] for sub in subscribers if sub["active"]]
        recipients.append(creator_id)  # Always notify the creator
        
        return await self.send_notification(
            notification_type=notification_type,
            recipients=list(set(recipients)),  # Remove duplicates
            data={
                "campaign_id": campaign_id,
                "creator_id": creator_id,
                "milestone": milestone_data,
                "amount": milestone_data.get("amount"),
                "due_date": milestone_data.get("due_date")
            },
            priority=NotificationPriority.HIGH
        )
    
    async def send_whatsapp_update(
        self,
        user_phone: str,
        message: str,
        campaign_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        📱 Send WhatsApp update message
        """
        
        try:
            whatsapp_service = self.channels[NotificationChannel.WHATSAPP]
            
            if not whatsapp_service["enabled"]:
                return {"status": "whatsapp_disabled"}
            
            # Send via WhatsApp API
            result = await self._send_whatsapp_message(user_phone, message)
            
            logger.info(f"📱 WhatsApp update sent to {user_phone}")
            
            return {
                "status": "sent",
                "platform": "whatsapp",
                "recipient": user_phone,
                "message_length": len(message)
            }
            
        except Exception as e:
            logger.error(f"❌ WhatsApp update failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def broadcast_system_alert(
        self,
        alert_message: str,
        alert_level: str = "info",
        affected_services: List[str] = None
    ) -> Dict[str, Any]:
        """
        📢 Broadcast system-wide alert
        """
        
        # Get all global subscribers
        recipients = self.subscribers["global"]
        
        priority = {
            "info": NotificationPriority.LOW,
            "warning": NotificationPriority.MEDIUM,
            "error": NotificationPriority.HIGH,
            "critical": NotificationPriority.URGENT
        }.get(alert_level, NotificationPriority.MEDIUM)
        
        return await self.send_notification(
            notification_type=NotificationType.SYSTEM_ALERT,
            recipients=recipients,
            data={
                "alert_message": alert_message,
                "alert_level": alert_level,
                "affected_services": affected_services or [],
                "timestamp": datetime.now().isoformat()
            },
            priority=priority,
            channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK]
        )
    
    # Channel-specific sending methods
    
    async def _send_via_channel(
        self,
        channel: NotificationChannel,
        recipients: List[str],
        content: Dict[str, str],
        notification: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send notification via specific channel"""
        
        try:
            if channel == NotificationChannel.EMAIL:
                return await self._send_email_notification(recipients, content)
            elif channel == NotificationChannel.WHATSAPP:
                return await self._send_whatsapp_notification(recipients, content)
            elif channel == NotificationChannel.WEBHOOK:
                return await self._send_webhook_notification(recipients, notification)
            elif channel == NotificationChannel.SLACK:
                return await self._send_slack_notification(recipients, content)
            elif channel == NotificationChannel.SMS:
                return await self._send_sms_notification(recipients, content)
            elif channel == NotificationChannel.IN_APP:
                return await self._send_in_app_notification(recipients, content, notification)
            else:
                return {"status": "unsupported_channel", "channel": channel.value}
                
        except Exception as e:
            logger.error(f"❌ Channel {channel.value} delivery failed: {e}")
            return {"status": "error", "error": str(e), "channel": channel.value}
    
    async def _send_email_notification(self, recipients: List[str], content: Dict[str, str]) -> Dict[str, Any]:
        """Send email notification"""
        
        email_config = self.channels[NotificationChannel.EMAIL]
        
        if not email_config["enabled"]:
            return {"status": "email_disabled"}
        
        try:
            # Mock email sending for demo
            logger.info(f"📧 Email notification sent to {len(recipients)} recipients")
            logger.info(f"   Subject: {content.get('subject', 'InfluencerFlow Notification')}")
            logger.info(f"   Preview: {content.get('body', '')[:100]}...")
            
            return {
                "status": "sent",
                "channel": "email",
                "recipients_count": len(recipients),
                "delivery_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _send_whatsapp_notification(self, recipients: List[str], content: Dict[str, str]) -> Dict[str, Any]:
        """Send WhatsApp notification"""
        
        whatsapp_config = self.channels[NotificationChannel.WHATSAPP]
        
        if not whatsapp_config["enabled"]:
            return {"status": "whatsapp_disabled"}
        
        try:
            sent_count = 0
            for recipient in recipients:
                await self._send_whatsapp_message(recipient, content.get("message", ""))
                sent_count += 1
            
            return {
                "status": "sent",
                "channel": "whatsapp",
                "recipients_count": sent_count
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _send_webhook_notification(self, recipients: List[str], notification: Dict[str, Any]) -> Dict[str, Any]:
        """Send webhook notification"""
        
        webhook_config = self.channels[NotificationChannel.WEBHOOK]
        
        if not webhook_config["enabled"]:
            return {"status": "webhook_disabled"}
        
        try:
            # Send to configured webhook URLs
            webhook_urls = webhook_config.get("urls", [])
            
            for url in webhook_urls:
                response = requests.post(
                    url,
                    json=notification,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code != 200:
                    logger.warning(f"⚠️  Webhook delivery failed to {url}: {response.status_code}")
            
            return {
                "status": "sent",
                "channel": "webhook",
                "webhooks_called": len(webhook_urls)
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _send_slack_notification(self, recipients: List[str], content: Dict[str, str]) -> Dict[str, Any]:
        """Send Slack notification"""
        
        slack_config = self.channels[NotificationChannel.SLACK]
        
        if not slack_config["enabled"]:
            return {"status": "slack_disabled"}
        
        # Mock Slack sending
        logger.info(f"💬 Slack notification: {content.get('message', '')}")
        
        return {
            "status": "sent",
            "channel": "slack",
            "message_sent": True
        }
    
    async def _send_sms_notification(self, recipients: List[str], content: Dict[str, str]) -> Dict[str, Any]:
        """Send SMS notification"""
        
        # Mock SMS sending
        logger.info(f"📱 SMS notification sent to {len(recipients)} numbers")
        
        return {
            "status": "sent",
            "channel": "sms",
            "recipients_count": len(recipients)
        }
    
    async def _send_in_app_notification(self, recipients: List[str], content: Dict[str, str], notification: Dict[str, Any]) -> Dict[str, Any]:
        """Send in-app notification"""
        
        # Store in-app notifications for retrieval
        for recipient in recipients:
            if recipient not in self.realtime_connections:
                self.realtime_connections[recipient] = []
            
            self.realtime_connections[recipient].append({
                "id": notification["id"],
                "type": notification["type"],
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "read": False
            })
        
        logger.info(f"🔔 In-app notification sent to {len(recipients)} users")
        
        return {
            "status": "sent",
            "channel": "in_app",
            "recipients_count": len(recipients)
        }
    
    async def _send_whatsapp_message(self, phone: str, message: str) -> bool:
        """Send individual WhatsApp message"""
        
        # Mock WhatsApp message sending
        logger.info(f"📱 WhatsApp to {phone}: {message[:50]}...")
        return True
    
    # Content generation and templates
    
    async def _generate_notification_content(
        self,
        notification_type: NotificationType,
        data: Dict[str, Any],
        template_override: Optional[str] = None
    ) -> Dict[str, str]:
        """Generate notification content using templates"""
        
        template_key = template_override or notification_type.value
        template = self.templates.get(template_key, self.templates["default"])
        
        # Generate content for different formats
        content = {
            "subject": self._render_template(template["email"]["subject"], data),
            "body": self._render_template(template["email"]["body"], data),
            "message": self._render_template(template["message"], data),
            "slack": self._render_template(template["slack"], data)
        }
        
        return content
    
    def _render_template(self, template: str, data: Dict[str, Any]) -> str:
        """Render template with data"""
        
        try:
            return template.format(**data)
        except KeyError as e:
            logger.warning(f"⚠️  Template rendering failed: missing key {e}")
            return template
    
    def _load_notification_templates(self) -> Dict[str, Any]:
        """Load notification templates"""
        
        return {
            "campaign_created": {
                "email": {
                    "subject": "🎯 Campaign Created: {campaign_id}",
                    "body": "Your campaign '{campaign_id}' has been created and AI workflow started. Expected completion: 8 minutes."
                },
                "message": "🎯 Campaign '{campaign_id}' created! AI workflow started. Expected completion: 8 minutes.",
                "slack": "🎯 *Campaign Created*\nCampaign: {campaign_id}\nStatus: AI workflow started"
            },
            "campaign_completed": {
                "email": {
                    "subject": "✅ Campaign Completed: {campaign_id}",
                    "body": "Your campaign has completed successfully! {successful_negotiations} creators secured for ${total_cost:,}."
                },
                "message": "✅ Campaign completed! {successful_negotiations} creators secured for ${total_cost:,}. View results in dashboard.",
                "slack": "✅ *Campaign Completed*\nCreators: {successful_negotiations}\nCost: ${total_cost:,}"
            },
            "negotiation_success": {
                "email": {
                    "subject": "🎉 Negotiation Success: {creator_id}",
                    "body": "Successfully negotiated with {creator_id} for ${final_rate:,}!"
                },
                "message": "🎉 Negotiation success! {creator_id} agreed to ${final_rate:,}",
                "slack": "🎉 *Negotiation Success*\nCreator: {creator_id}\nRate: ${final_rate:,}"
            },
            "negotiation_failed": {
                "email": {
                    "subject": "❌ Negotiation Failed: {creator_id}",
                    "body": "Negotiation with {creator_id} was unsuccessful. Reason: {failure_reason}"
                },
                "message": "❌ Negotiation with {creator_id} failed. Continuing with other creators.",
                "slack": "❌ *Negotiation Failed*\nCreator: {creator_id}\nReason: {failure_reason}"
            },
            "performance_alert": {
                "email": {
                    "subject": "⚠️ Performance Alert: {campaign_id}",
                    "body": "Performance alert for campaign {campaign_id}: {alert_type}. Recommended actions: {recommended_actions}"
                },
                "message": "⚠️ Performance alert: {alert_type}. Check dashboard for details.",
                "slack": "⚠️ *Performance Alert*\nCampaign: {campaign_id}\nType: {alert_type}"
            },
            "payment_due": {
                "email": {
                    "subject": "💰 Payment Due: {creator_id}",
                    "body": "Payment of ${amount:,} is due for {creator_id} by {due_date}."
                },
                "message": "💰 Payment reminder: ${amount:,} due for {creator_id} by {due_date}",
                "slack": "💰 *Payment Due*\nCreator: {creator_id}\nAmount: ${amount:,}"
            },
            "default": {
                "email": {
                    "subject": "📱 InfluencerFlow Notification",
                    "body": "You have a new notification from InfluencerFlow."
                },
                "message": "📱 New notification from InfluencerFlow",
                "slack": "📱 *InfluencerFlow Notification*"
            }
        }
    
    # Configuration and setup methods
    
    def _get_default_channels(self, priority: NotificationPriority) -> List[NotificationChannel]:
        """Get default channels based on priority"""
        
        channel_map = {
            NotificationPriority.LOW: [NotificationChannel.IN_APP],
            NotificationPriority.MEDIUM: [NotificationChannel.EMAIL, NotificationChannel.IN_APP],
            NotificationPriority.HIGH: [NotificationChannel.EMAIL, NotificationChannel.WHATSAPP, NotificationChannel.IN_APP],
            NotificationPriority.URGENT: [NotificationChannel.EMAIL, NotificationChannel.WHATSAPP, NotificationChannel.SMS, NotificationChannel.IN_APP]
        }
        
        return channel_map.get(priority, [NotificationChannel.EMAIL])
    
    def _initialize_email_service(self) -> Dict[str, Any]:
        """Initialize email service configuration"""
        
        return {
            "enabled": hasattr(settings, 'smtp_server') and bool(getattr(settings, 'smtp_server', None)),
            "smtp_server": getattr(settings, 'smtp_server', None),
            "smtp_port": getattr(settings, 'smtp_port', 587),
            "smtp_username": getattr(settings, 'smtp_username', None),
            "smtp_password": getattr(settings, 'smtp_password', None),
            "from_email": getattr(settings, 'from_email', 'noreply@influencerflow.ai')
        }
    
    def _initialize_whatsapp_service(self) -> Dict[str, Any]:
        """Initialize WhatsApp service configuration"""
        
        return {
            "enabled": hasattr(settings, 'whatsapp_token') and bool(getattr(settings, 'whatsapp_token', None)),
            "token": getattr(settings, 'whatsapp_token', None),
            "phone_number_id": getattr(settings, 'whatsapp_phone_id', None)
        }
    
    def _initialize_webhook_service(self) -> Dict[str, Any]:
        """Initialize webhook service configuration"""
        
        return {
            "enabled": True,
            "urls": getattr(settings, 'notification_webhook_urls', [])
        }
    
    def _initialize_slack_service(self) -> Dict[str, Any]:
        """Initialize Slack service configuration"""
        
        return {
            "enabled": hasattr(settings, 'slack_webhook_url') and bool(getattr(settings, 'slack_webhook_url', None)),
            "webhook_url": getattr(settings, 'slack_webhook_url', None)
        }
    
    def _initialize_sms_service(self) -> Dict[str, Any]:
        """Initialize SMS service configuration"""
        
        return {
            "enabled": hasattr(settings, 'twilio_account_sid') and bool(getattr(settings, 'twilio_account_sid', None)),
            "account_sid": getattr(settings, 'twilio_account_sid', None),
            "auth_token": getattr(settings, 'twilio_auth_token', None),
            "from_number": getattr(settings, 'twilio_from_number', None)
        }
    
    def _summarize_delivery_results(self, results: List[Any]) -> Dict[str, Any]:
        """Summarize delivery results"""
        
        successful = len([r for r in results if isinstance(r, dict) and r.get("status") == "sent"])
        failed = len(results) - successful
        
        return {
            "total_deliveries": len(results),
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / max(len(results), 1)) * 100
        }
    
    # Public API methods for getting notifications
    
    async def get_user_notifications(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get in-app notifications for user"""
        
        user_notifications = self.realtime_connections.get(user_id, [])
        
        # Sort by timestamp (newest first)
        sorted_notifications = sorted(
            user_notifications, 
            key=lambda x: x["timestamp"], 
            reverse=True
        )
        
        return sorted_notifications[:limit]
    
    async def mark_notification_read(self, user_id: str, notification_id: str) -> bool:
        """Mark notification as read"""
        
        user_notifications = self.realtime_connections.get(user_id, [])
        
        for notification in user_notifications:
            if notification["id"] == notification_id:
                notification["read"] = True
                return True
        
        return False