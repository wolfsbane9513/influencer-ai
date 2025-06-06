# services/email_service.py
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from config.settings import settings

logger = logging.getLogger(__name__)

class EmailService:
    """
    📧 EMAIL SERVICE - Contract distribution and communication
    
    Features:
    - Contract delivery via email
    - Professional email templates
    - Attachment handling
    - Delivery confirmation
    - Multiple email providers support
    """
    
    def __init__(self):
        self.smtp_server = getattr(settings, 'smtp_server', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'smtp_port', 587)
        self.email_username = getattr(settings, 'email_username', None)
        self.email_password = getattr(settings, 'email_password', None)
        self.sender_name = getattr(settings, 'sender_name', 'InfluencerFlow AI')
        self.sender_email = getattr(settings, 'sender_email', self.email_username)
        
        # Check if email is configured
        self.email_configured = bool(self.email_username and self.email_password)
        
        if not self.email_configured:
            logger.warning("⚠️ Email not configured - will log emails instead of sending")
    
    async def send_contract_email(
        self,
        contract_data: Dict[str, Any],
        creator_email: str,
        creator_name: str
    ) -> Dict[str, Any]:
        """
        📧 Send contract via email to creator
        """
        try:
            contract_id = contract_data.get("contract_id")
            brand_name = contract_data.get("brand_name", "Brand")
            product_name = contract_data.get("product_name", "Product")
            final_rate = contract_data.get("final_rate", 0)
            
            logger.info(f"📧 Sending contract {contract_id} to {creator_email}")
            
            # Generate email content
            email_subject = f"Partnership Contract - {brand_name} x {creator_name}"
            email_body = self._generate_contract_email_body(
                contract_data, creator_name, brand_name, product_name
            )
            
            # Generate contract PDF (mock for now)
            contract_pdf = self._generate_contract_pdf(contract_data)
            
            if self.email_configured:
                # Send real email
                result = await self._send_email_smtp(
                    to_email=creator_email,
                    subject=email_subject,
                    body=email_body,
                    attachments=[{
                        "filename": f"Contract_{contract_id}.pdf",
                        "content": contract_pdf,
                        "type": "application/pdf"
                    }]
                )
            else:
                # Mock email sending
                result = await self._mock_email_sending(
                    creator_email, email_subject, contract_id
                )
            
            # Log email activity
            await self._log_email_activity(
                contract_id=contract_id,
                recipient=creator_email,
                subject=email_subject,
                status=result.get("status", "unknown"),
                timestamp=datetime.now()
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to send contract email: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "contract_id": contract_data.get("contract_id"),
                "recipient": creator_email
            }
    
    def _generate_contract_email_body(
        self, 
        contract_data: Dict[str, Any], 
        creator_name: str,
        brand_name: str,
        product_name: str
    ) -> str:
        """Generate professional email body for contract delivery"""
        
        final_rate = contract_data.get("final_rate", 0)
        payment_schedule = contract_data.get("payment_schedule", [])
        deliverables = contract_data.get("deliverables", {}).get("primary_deliverables", [])
        
        # Format deliverables nicely
        deliverable_list = "\n".join([f"• {d.replace('_', ' ').title()}" for d in deliverables])
        
        # Format payment schedule
        payment_details = []
        for payment in payment_schedule:
            milestone = payment.get("milestone", "Payment")
            amount = payment.get("amount", 0)
            percentage = payment.get("percentage", 0)
            payment_details.append(f"• {milestone}: ${amount:,.2f} ({percentage}%)")
        
        payment_schedule_text = "\n".join(payment_details) if payment_details else "Full payment on delivery"
        
        return f"""Dear {creator_name},

Thank you for agreeing to partner with {brand_name}! We're excited to work together on promoting {product_name}.

🎯 PARTNERSHIP DETAILS:
━━━━━━━━━━━━━━━━━━━━━━━━
Total Compensation: ${final_rate:,.2f}
Campaign: {product_name} Content Creation

📋 DELIVERABLES:
{deliverable_list}

💰 PAYMENT SCHEDULE:
{payment_schedule_text}

📄 CONTRACT ATTACHED:
Your comprehensive partnership agreement is attached as a PDF. Please review all terms carefully and let us know if you have any questions.

🔄 NEXT STEPS:
1. Review the attached contract thoroughly
2. Sign and return the contract within 48 hours
3. Provide your banking details for payment processing
4. We'll send the product samples and creative brief within 24 hours of contract signing

📞 SUPPORT:
If you have any questions about the contract or campaign, please don't hesitate to reach out:
• Email: partnerships@{brand_name.lower().replace(' ', '')}.com
• Response time: Within 4 hours during business hours

We're looking forward to creating amazing content together!

Best regards,
The {brand_name} Partnerships Team

---
This email was sent by InfluencerFlow AI Platform
Contract ID: {contract_data.get('contract_id')}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    def _generate_contract_pdf(self, contract_data: Dict[str, Any]) -> bytes:
        """Generate contract PDF (mock implementation)"""
        
        # In a real implementation, this would use a PDF library like reportlab
        # For now, return mock PDF content
        
        contract_content = contract_data.get("contract_content", "Contract content not available")
        
        # Mock PDF content
        pdf_content = f"""
%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length {len(contract_content)}
>>
stream
{contract_content}
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000206 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
{len(contract_content) + 300}
%%EOF
"""
        
        return pdf_content.encode('utf-8')
    
    async def _send_email_smtp(
        self,
        to_email: str,
        subject: str,
        body: str,
        attachments: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send email via SMTP"""
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{self.sender_name} <{self.sender_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Add attachments
            if attachments:
                for attachment in attachments:
                    part = MIMEApplication(
                        attachment["content"],
                        _subtype=attachment.get("type", "application/octet-stream")
                    )
                    part.add_header(
                        'Content-Disposition',
                        'attachment',
                        filename=attachment["filename"]
                    )
                    msg.attach(part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_username, self.email_password)
                server.send_message(msg)
            
            logger.info(f"✅ Email sent successfully to {to_email}")
            return {
                "status": "sent",
                "recipient": to_email,
                "timestamp": datetime.now().isoformat(),
                "message_id": f"smtp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "attachments_count": len(attachments) if attachments else 0
            }
            
        except Exception as e:
            logger.error(f"❌ SMTP email failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "recipient": to_email
            }
    
    async def _mock_email_sending(
        self, 
        recipient: str, 
        subject: str, 
        contract_id: str
    ) -> Dict[str, Any]:
        """Mock email sending for testing/demo"""
        
        logger.info(f"📧 [MOCK] Email sent to {recipient}")
        logger.info(f"📧 [MOCK] Subject: {subject}")
        logger.info(f"📧 [MOCK] Contract ID: {contract_id}")
        
        return {
            "status": "sent_mock",
            "recipient": recipient,
            "timestamp": datetime.now().isoformat(),
            "message_id": f"mock_{contract_id}_{datetime.now().strftime('%H%M%S')}",
            "mock_mode": True,
            "note": "Email not actually sent - configure SMTP credentials for real sending"
        }
    
    async def _log_email_activity(
        self,
        contract_id: str,
        recipient: str,
        subject: str,
        status: str,
        timestamp: datetime
    ):
        """Log email activity for tracking and debugging"""
        
        activity_log = {
            "contract_id": contract_id,
            "recipient": recipient,
            "subject": subject,
            "status": status,
            "timestamp": timestamp.isoformat(),
            "service": "email_service"
        }
        
        logger.info(f"📧 Email Activity: {activity_log}")
        
        # In a real implementation, this would store to database
        # For now, just log the activity
    
    async def send_campaign_update_email(
        self,
        recipient_email: str,
        recipient_name: str,
        campaign_data: Dict[str, Any],
        update_type: str
    ) -> Dict[str, Any]:
        """Send campaign update emails (completion, milestone, etc.)"""
        
        try:
            subject = f"Campaign Update - {campaign_data.get('product_name', 'Your Campaign')}"
            
            if update_type == "completion":
                body = self._generate_campaign_completion_email(recipient_name, campaign_data)
            elif update_type == "milestone":
                body = self._generate_milestone_email(recipient_name, campaign_data)
            else:
                body = self._generate_generic_update_email(recipient_name, campaign_data, update_type)
            
            if self.email_configured:
                result = await self._send_email_smtp(recipient_email, subject, body)
            else:
                result = await self._mock_email_sending(recipient_email, subject, "campaign_update")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Campaign update email failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    def _generate_campaign_completion_email(self, creator_name: str, campaign_data: Dict[str, Any]) -> str:
        """Generate campaign completion email"""
        
        return f"""Dear {creator_name},

🎉 Congratulations! Your campaign for {campaign_data.get('product_name')} has been completed successfully.

📊 CAMPAIGN RESULTS:
• Content delivered on time ✅
• Quality standards met ✅
• Campaign objectives achieved ✅

💰 FINAL PAYMENT:
Your final payment has been processed and should arrive within 3-5 business days.

📈 PERFORMANCE METRICS:
We'll share detailed performance metrics within 48 hours, including:
• Reach and engagement data
• Conversion tracking results
• ROI analysis

🤝 FUTURE PARTNERSHIPS:
Based on the success of this campaign, we'd love to explore future collaboration opportunities. We'll be in touch soon with new partnership proposals.

Thank you for your professionalism and high-quality content creation!

Best regards,
The Partnerships Team

---
Campaign ID: {campaign_data.get('id', 'N/A')}
Completion Date: {datetime.now().strftime('%Y-%m-%d')}
"""
    
    def _generate_milestone_email(self, creator_name: str, campaign_data: Dict[str, Any]) -> str:
        """Generate milestone notification email"""
        
        return f"""Dear {creator_name},

📋 Campaign Milestone Update for {campaign_data.get('product_name')}

✅ MILESTONE ACHIEVED:
A key milestone in your campaign has been reached. Check your dashboard for details.

🔄 NEXT STEPS:
Please review your campaign dashboard for upcoming deliverables and deadlines.

📞 SUPPORT:
If you need any assistance, please don't hesitate to reach out.

Best regards,
The Campaign Management Team
"""
    
    def _generate_generic_update_email(
        self, 
        creator_name: str, 
        campaign_data: Dict[str, Any], 
        update_type: str
    ) -> str:
        """Generate generic update email"""
        
        return f"""Dear {creator_name},

📢 Campaign Update: {update_type.replace('_', ' ').title()}

Your campaign for {campaign_data.get('product_name')} has an important update.

Please check your campaign dashboard for complete details.

Best regards,
The Campaign Team
"""


class ContractEmailManager:
    """
    📄 CONTRACT EMAIL MANAGER - Integrates with contract generation workflow
    """
    
    def __init__(self):
        self.email_service = EmailService()
    
    async def send_contract_after_generation(
        self,
        contract_data: Dict[str, Any],
        creator_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        📧 Send contract immediately after generation
        Called by EnhancedContractAgent
        """
        
        try:
            # Extract creator contact information
            creator_email = self._get_creator_email(contract_data, creator_data)
            creator_name = self._get_creator_name(contract_data, creator_data)
            
            if not creator_email:
                logger.warning(f"⚠️ No email found for creator {contract_data.get('creator_id')}")
                return {
                    "status": "skipped",
                    "reason": "no_email_available",
                    "contract_id": contract_data.get("contract_id")
                }
            
            # Send contract email
            email_result = await self.email_service.send_contract_email(
                contract_data=contract_data,
                creator_email=creator_email,
                creator_name=creator_name
            )
            
            # Update contract record with email status
            contract_data["email_status"] = email_result.get("status")
            contract_data["email_sent_at"] = datetime.now().isoformat()
            contract_data["email_recipient"] = creator_email
            
            logger.info(f"📧 Contract email process completed: {email_result.get('status')}")
            
            return {
                "contract_email_result": email_result,
                "contract_updated": True,
                "email_integration": "successful"
            }
            
        except Exception as e:
            logger.error(f"❌ Contract email integration failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "contract_id": contract_data.get("contract_id")
            }
    
    def _get_creator_email(
        self, 
        contract_data: Dict[str, Any], 
        creator_data: Optional[Dict[str, Any]]
    ) -> Optional[str]:
        """Extract creator email from available data"""
        
        # Try contract data first
        creator_email = contract_data.get("creator_email")
        if creator_email and "@" in creator_email:
            return creator_email
        
        # Try creator data
        if creator_data:
            creator_email = creator_data.get("email") or creator_data.get("contact_email")
            if creator_email and "@" in creator_email:
                return creator_email
        
        # Generate mock email for demo
        creator_id = contract_data.get("creator_id", "unknown")
        return f"{creator_id}@demo-creator.com"
    
    def _get_creator_name(
        self, 
        contract_data: Dict[str, Any], 
        creator_data: Optional[Dict[str, Any]]
    ) -> str:
        """Extract creator name from available data"""
        
        # Try creator data first
        if creator_data:
            name = creator_data.get("name")
            if name:
                return name
        
        # Try contract data
        creator_name = contract_data.get("creator_name")
        if creator_name:
            return creator_name
        
        # Fallback
        return contract_data.get("creator_id", "Creator")