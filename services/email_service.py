# services/email_service.py
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import base64
import os
from pathlib import Path

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from config.settings import settings

# Set up logging
logger = logging.getLogger(__name__)

class EmailService:
    """
    Email service using SendGrid for sending contracts and notifications
    """
    
    def __init__(self):
        """Initialize the email service with SendGrid configuration"""
        self.api_key = settings.sendgrid_api_key
        self.from_email = settings.sendgrid_from_email
        self.from_name = settings.sendgrid_from_name
        
        # Initialize SendGrid client if API key is available
        if self.api_key:
            self.sg = SendGridAPIClient(api_key=self.api_key)
            logger.info("✅ SendGrid email service initialized successfully")
        else:
            self.sg = None
            logger.warning("⚠️ SendGrid API key not found. Email service will run in mock mode.")
    
    async def send_contract_email(
        self,
        to_email: str,
        to_name: str,
        contract_content: str,
        campaign_details: Dict[str, Any],
        contract_filename: Optional[str] = None
    ) -> bool:
        """
        Send a contract via email after a successful call
        
        Args:
            to_email: Recipient's email address
            to_name: Recipient's name
            contract_content: The contract content (text or HTML)
            campaign_details: Details about the campaign
            contract_filename: Optional filename for the contract attachment
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            # Create email subject
            campaign_name = campaign_details.get('campaign_name', 'Your Campaign')
            subject = f"🎯 Contract for {campaign_name} - InfluencerFlow AI"
            
            # Create email body
            html_content = self._create_contract_email_template(
                to_name=to_name,
                contract_content=contract_content,
                campaign_details=campaign_details
            )
            
            # Create plain text version
            text_content = self._create_contract_text_template(
                to_name=to_name,
                contract_content=contract_content,
                campaign_details=campaign_details
            )
            
            # Send the email
            success = await self._send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                contract_content=contract_content,
                contract_filename=contract_filename
            )
            
            if success:
                logger.info(f"✅ Contract email sent successfully to {to_email}")
            else:
                logger.error(f"❌ Failed to send contract email to {to_email}")
                
            return success
            
        except Exception as e:
            logger.error(f"❌ Error sending contract email: {str(e)}")
            return False
    
    async def send_notification_email(
        self,
        to_email: str,
        subject: str,
        message: str,
        is_html: bool = False
    ) -> bool:
        """
        Send a general notification email
        
        Args:
            to_email: Recipient's email address
            subject: Email subject
            message: Email message content
            is_html: Whether the message is HTML formatted
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            html_content = message if is_html else f"<p>{message}</p>"
            text_content = message if not is_html else message  # SendGrid will auto-generate text from HTML
            
            success = await self._send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
            if success:
                logger.info(f"✅ Notification email sent successfully to {to_email}")
            else:
                logger.error(f"❌ Failed to send notification email to {to_email}")
                
            return success
            
        except Exception as e:
            logger.error(f"❌ Error sending notification email: {str(e)}")
            return False
    
    async def _send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str,
        contract_content: Optional[str] = None,
        contract_filename: Optional[str] = None
    ) -> bool:
        """
        Internal method to send email using SendGrid
        """
        try:
            # If no SendGrid client, run in mock mode
            if not self.sg:
                logger.info(f"📧 MOCK EMAIL: Would send to {to_email}")
                logger.info(f"   Subject: {subject}")
                logger.info(f"   Content preview: {text_content[:100]}...")
                return True
            
            # Create the email message
            message = Mail(
                from_email=(self.from_email, self.from_name),
                to_emails=to_email,
                subject=subject,
                html_content=html_content,
                plain_text_content=text_content
            )
            
            # Add contract as attachment if provided
            if contract_content and contract_filename:
                attachment = self._create_contract_attachment(contract_content, contract_filename)
                if attachment:
                    message.attachment = attachment
            
            # Send the email
            response = self.sg.send(message)
            
            # Check if email was sent successfully
            if response.status_code in [200, 201, 202]:
                logger.info(f"✅ Email sent successfully. Status: {response.status_code}")
                return True
            else:
                logger.error(f"❌ SendGrid returned status: {response.status_code}")
                logger.error(f"   Response body: {response.body}")
                return False
                
        except Exception as e:
            logger.error(f"❌ SendGrid API error: {str(e)}")
            return False
    
    def _create_contract_attachment(self, contract_content: str, filename: str) -> Optional[Attachment]:
        """
        Create a contract attachment for the email
        """
        try:
            # Encode the contract content
            encoded_content = base64.b64encode(contract_content.encode()).decode()
            
            # Create attachment
            attachment = Attachment(
                FileContent(encoded_content),
                FileName(filename),
                FileType("text/plain"),
                Disposition("attachment")
            )
            
            return attachment
            
        except Exception as e:
            logger.error(f"❌ Error creating contract attachment: {str(e)}")
            return None
    
    def _create_contract_email_template(
        self,
        to_name: str,
        contract_content: str,
        campaign_details: Dict[str, Any]
    ) -> str:
        """
        Create HTML email template for contract delivery
        """
        campaign_name = campaign_details.get('campaign_name', 'Your Campaign')
        brand_name = campaign_details.get('brand_name', 'Our Brand')
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Contract - {campaign_name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .contract-box {{ background: white; padding: 20px; border-radius: 8px; border-left: 4px solid #667eea; margin: 20px 0; }}
                .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎯 Contract Ready!</h1>
                    <p>Your collaboration agreement for {campaign_name}</p>
                </div>
                
                <div class="content">
                    <h2>Hi {to_name}! 👋</h2>
                    
                    <p>Great news! We've prepared your collaboration contract for the <strong>{campaign_name}</strong> campaign with <strong>{brand_name}</strong>.</p>
                    
                    <div class="contract-box">
                        <h3>📋 Contract Details</h3>
                        <pre style="white-space: pre-wrap; font-family: Arial, sans-serif;">{contract_content}</pre>
                    </div>
                    
                    <p><strong>Next Steps:</strong></p>
                    <ul>
                        <li>📖 Review the contract terms carefully</li>
                        <li>✍️ Sign and return if you agree to the terms</li>
                        <li>🚀 Start creating amazing content!</li>
                    </ul>
                    
                    <p>If you have any questions about this contract, please don't hesitate to reach out to us.</p>
                    
                    <div class="footer">
                        <p>Best regards,<br>
                        <strong>InfluencerFlow AI Team</strong></p>
                        <p><em>Connecting brands with the perfect influencers</em></p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_contract_text_template(
        self,
        to_name: str,
        contract_content: str,
        campaign_details: Dict[str, Any]
    ) -> str:
        """
        Create plain text email template for contract delivery
        """
        campaign_name = campaign_details.get('campaign_name', 'Your Campaign')
        brand_name = campaign_details.get('brand_name', 'Our Brand')
        
        return f"""
Hi {to_name}!

Great news! We've prepared your collaboration contract for the {campaign_name} campaign with {brand_name}.

CONTRACT DETAILS:
{'-' * 50}
{contract_content}
{'-' * 50}

NEXT STEPS:
- Review the contract terms carefully
- Sign and return if you agree to the terms  
- Start creating amazing content!

If you have any questions about this contract, please don't hesitate to reach out to us.

Best regards,
InfluencerFlow AI Team
Connecting brands with the perfect influencers
        """

# Create global email service instance
email_service = EmailService() 