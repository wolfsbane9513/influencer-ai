# services/email_service.py
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

from config.settings import settings

logger = logging.getLogger(__name__)

class EmailService:
    """
    📧 EMAIL SERVICE - Contract delivery and notifications
    
    Handles:
    - Contract delivery with PDF attachments
    - Approval request notifications
    - Follow-up reminders
    - System notifications
    """
    
    def __init__(self):
        self.smtp_host = getattr(settings, 'smtp_host', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'smtp_port', 587)
        self.smtp_username = getattr(settings, 'smtp_username', None)
        self.smtp_password = getattr(settings, 'smtp_password', None)
        
        # Check if email is configured
        self.email_configured = bool(self.smtp_username and self.smtp_password)
        
        if not self.email_configured:
            logger.warning("⚠️ Email service not configured - using mock mode")
        else:
            logger.info("✅ Email service configured")
    
    async def send_contract_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        contract_pdf_path: str,
        contract_data: Any
    ) -> Dict[str, Any]:
        """📝 Send contract email with PDF attachment"""
        
        if not self.email_configured:
            return await self._mock_contract_email(to_email, subject, contract_data)
        
        try:
            # Create message
            message = MIMEMultipart()
            message["From"] = self.smtp_username
            message["To"] = to_email
            message["Subject"] = subject
            
            # Add body
            message.attach(MIMEText(body, "plain"))
            
            # Add PDF attachment if it exists
            if Path(contract_pdf_path).exists():
                with open(contract_pdf_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {Path(contract_pdf_path).name}'
                )
                message.attach(part)
            
            # Send email
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            text = message.as_string()
            server.sendmail(self.smtp_username, to_email, text)
            server.quit()
            
            logger.info(f"📧 Contract email sent to {to_email}")
            
            return {
                "status": "sent",
                "message_id": f"email_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "to_email": to_email,
                "subject": subject,
                "sent_at": datetime.now().isoformat(),
                "attachment_included": Path(contract_pdf_path).exists()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to send contract email: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "to_email": to_email,
                "fallback": "mock_delivery"
            }
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        attachments: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """📧 Send regular email"""
        
        if not self.email_configured:
            return await self._mock_email(to_email, subject)
        
        try:
            message = MIMEMultipart()
            message["From"] = self.smtp_username
            message["To"] = to_email
            message["Subject"] = subject
            
            message.attach(MIMEText(body, "plain"))
            
            # Add attachments if provided
            if attachments:
                for file_path in attachments:
                    if Path(file_path).exists():
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {Path(file_path).name}'
                        )
                        message.attach(part)
            
            # Send email
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            text = message.as_string()
            server.sendmail(self.smtp_username, to_email, text)
            server.quit()
            
            logger.info(f"📧 Email sent to {to_email}")
            
            return {
                "status": "sent",
                "message_id": f"email_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "to_email": to_email,
                "sent_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to send email: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "to_email": to_email
            }
    
    async def send_approval_request_email(
        self,
        to_email: str,
        approval_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """📋 Send approval request email"""
        
        subject = f"Approval Required: {approval_request.get('title', 'Campaign Review')}"
        
        body = f"""
Dear Reviewer,

You have a new approval request that requires your attention.

Request Details:
• Title: {approval_request.get('title', 'N/A')}
• Type: {approval_request.get('approval_type', 'N/A')}
• Priority: {approval_request.get('priority', 'medium')}
• Due Date: {approval_request.get('due_date', 'N/A')}

Description:
{approval_request.get('description', 'No description provided')}

To review and approve this request, please use the following links:

• Approve: {approval_request.get('approval_url', '#')}
• Reject: {approval_request.get('rejection_url', '#')}
• Request Changes: {approval_request.get('revision_url', '#')}

If you have any questions, please contact the request initiator.

Best regards,
InfluencerFlow AI Platform
"""
        
        return await self.send_email(to_email, subject, body)
    
    async def send_sponsor_approval_email(
        self,
        to_email: str,
        approval_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """💰 Send sponsor approval email"""
        
        subject = f"Campaign Approval Required - Total Cost: ${approval_request.get('total_cost', 0):,}"
        
        body = f"""
Dear Sponsor,

A new influencer campaign requires your approval.

Campaign Summary:
• Campaign ID: {approval_request.get('campaign_id', 'N/A')}
• Total Cost: ${approval_request.get('total_cost', 0):,}
• Influencers: {len(approval_request.get('recommended_influencers', []))}
• Expected ROI: {approval_request.get('expected_roi', {}).get('projection', 'TBD')}

Recommended Influencers:
"""
        
        for influencer in approval_request.get('recommended_influencers', []):
            body += f"• {influencer.get('name', 'Unknown')} - ${influencer.get('rate', 0):,}\n"
        
        body += f"""

Approval Actions:
• Approve Campaign: {approval_request.get('approval_url', '#')}
• Reject Campaign: {approval_request.get('rejection_url', '#')}
• Request Revisions: {approval_request.get('revision_url', '#')}

Approval Deadline: {approval_request.get('approval_deadline', 'N/A')}

Best regards,
InfluencerFlow AI Platform
"""
        
        return await self.send_email(to_email, subject, body)
    
    async def send_contract_signed_notification(
        self,
        to_email: str,
        contract_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """✅ Send contract signed notification"""
        
        subject = f"Contract Signed - {contract_data.get('creator_info', {}).get('full_name', 'Creator')}"
        
        body = f"""
Great news! A contract has been signed.

Contract Details:
• Contract ID: {contract_data.get('contract_id', 'N/A')}
• Creator: {contract_data.get('creator_info', {}).get('full_name', 'N/A')}
• Campaign: {contract_data.get('brand_info', {}).get('product_name', 'N/A')}
• Value: ${contract_data.get('final_rate', 0):,}
• Signed: {datetime.now().strftime('%B %d, %Y')}

Next Steps:
1. Initiate payment process
2. Send creative brief to creator
3. Set up content review workflow
4. Schedule check-in calls

The campaign can now proceed to the execution phase.

Best regards,
InfluencerFlow AI Platform
"""
        
        return await self.send_email(to_email, subject, body)
    
    async def send_follow_up_email(
        self,
        to_email: str,
        follow_up_type: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """🔄 Send follow-up email"""
        
        if follow_up_type == "contract_reminder":
            subject = "Reminder: Contract Signature Required"
            body = f"""
Dear {context.get('creator_name', 'Creator')},

This is a friendly reminder about the partnership contract we sent.

Contract Details:
• Campaign: {context.get('campaign_name', 'N/A')}
• Value: ${context.get('contract_value', 0):,}
• Sent: {context.get('sent_date', 'N/A')}

If you have any questions about the terms or need clarification, please don't hesitate to reach out.

Best regards,
{context.get('brand_name', 'Campaign Team')}
"""
        
        elif follow_up_type == "payment_reminder":
            subject = "Payment Processing Update"
            body = f"""
Dear {context.get('creator_name', 'Creator')},

Your payment is being processed.

Payment Details:
• Amount: ${context.get('amount', 0):,}
• Method: {context.get('payment_method', 'Bank Transfer')}
• Expected: {context.get('expected_date', 'Within 3-5 business days')}

You will receive a confirmation email once the payment is completed.

Best regards,
Finance Team
"""
        
        else:  # generic follow-up
            subject = f"Follow-up: {context.get('subject', 'Campaign Update')}"
            body = context.get('message', 'This is a follow-up regarding your recent interaction.')
        
        return await self.send_email(to_email, subject, body)
    
    async def _mock_contract_email(
        self,
        to_email: str,
        subject: str,
        contract_data: Any
    ) -> Dict[str, Any]:
        """🎭 Mock contract email for testing"""
        
        logger.info(f"🎭 Mock contract email sent to {to_email}")
        logger.info(f"   Subject: {subject}")
        logger.info(f"   Contract Value: ${getattr(contract_data, 'final_rate', 0):,}")
        
        return {
            "status": "sent",
            "message_id": f"mock_email_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "to_email": to_email,
            "subject": subject,
            "sent_at": datetime.now().isoformat(),
            "mock_mode": True,
            "delivery_method": "mock_email_service"
        }
    
    async def _mock_email(self, to_email: str, subject: str) -> Dict[str, Any]:
        """🎭 Mock regular email for testing"""
        
        logger.info(f"🎭 Mock email sent to {to_email}: {subject}")
        
        return {
            "status": "sent",
            "message_id": f"mock_email_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "to_email": to_email,
            "sent_at": datetime.now().isoformat(),
            "mock_mode": True
        }
    
    def test_email_configuration(self) -> Dict[str, Any]:
        """🧪 Test email configuration"""
        
        if not self.email_configured:
            return {
                "status": "not_configured",
                "message": "Email credentials not provided",
                "required_settings": [
                    "SMTP_HOST", "SMTP_PORT", 
                    "SMTP_USERNAME", "SMTP_PASSWORD"
                ]
            }
        
        try:
            # Test SMTP connection
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.quit()
            
            return {
                "status": "configured",
                "message": "Email service ready",
                "smtp_host": self.smtp_host,
                "smtp_port": self.smtp_port
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Email configuration test failed: {str(e)}",
                "smtp_host": self.smtp_host,
                "smtp_port": self.smtp_port
            }