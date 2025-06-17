# services/contract_service.py
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import uuid

from .email_service import email_service
from config.settings import settings

# Set up logging
logger = logging.getLogger(__name__)

class ContractService:
    """
    Service for generating and sending contracts after successful calls
    """
    
    def __init__(self):
        """Initialize the contract service"""
        self.email_service = email_service
        logger.info("✅ Contract service initialized")
    
    async def process_successful_call(
        self,
        call_data: Dict[str, Any],
        influencer_data: Dict[str, Any],
        campaign_data: Dict[str, Any]
    ) -> bool:
        """
        Process a successful call by generating and sending a contract
        
        Args:
            call_data: Information about the completed call
            influencer_data: Influencer information (name, email, etc.)
            campaign_data: Campaign details for the contract
            
        Returns:
            bool: True if contract was generated and sent successfully
        """
        try:
            logger.info(f"🔄 Processing successful call for {influencer_data.get('name', 'Unknown')}")
            
            # 🚀 NEW: Validate email address exists
            influencer_email = influencer_data.get('email')
            if not influencer_email:
                logger.error(f"❌ No email address found for influencer: {influencer_data.get('name', 'Unknown')}")
                logger.error(f"   Influencer data: {influencer_data}")
                return False
            
            # Validate email format (basic validation)
            if '@' not in influencer_email or '.' not in influencer_email:
                logger.error(f"❌ Invalid email format: {influencer_email}")
                return False
            
            logger.info(f"✅ Email validation passed: {influencer_email}")
            
            # Generate the contract
            contract_content = self._generate_contract(
                influencer_data=influencer_data,
                campaign_data=campaign_data,
                call_data=call_data
            )
            
            # Create contract filename
            contract_filename = self._generate_contract_filename(
                influencer_data=influencer_data,
                campaign_data=campaign_data
            )
            
            # Send the contract via email
            success = await self.email_service.send_contract_email(
                to_email=influencer_email,
                to_name=influencer_data.get('name', 'Influencer'),
                contract_content=contract_content,
                campaign_details=campaign_data,
                contract_filename=contract_filename
            )
            
            if success:
                logger.info(f"✅ Contract successfully sent to {influencer_email}")
                
                # Log the contract generation for tracking
                await self._log_contract_sent(
                    influencer_data=influencer_data,
                    campaign_data=campaign_data,
                    contract_filename=contract_filename
                )
            else:
                logger.error(f"❌ Failed to send contract to {influencer_email}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error processing successful call: {str(e)}")
            return False
    
    def _generate_contract(
        self,
        influencer_data: Dict[str, Any],
        campaign_data: Dict[str, Any],
        call_data: Dict[str, Any]
    ) -> str:
        """
        Generate a contract based on the call results and campaign details
        """
        try:
            # Extract data with defaults
            influencer_name = influencer_data.get('name', 'Influencer')
            influencer_email = influencer_data.get('email', 'email@example.com')
            
            campaign_name = campaign_data.get('campaign_name', 'Marketing Campaign')
            brand_name = campaign_data.get('brand_name', 'Brand')
            campaign_budget = campaign_data.get('budget', 'TBD')
            deliverables = campaign_data.get('deliverables', ['Social media posts'])
            timeline = campaign_data.get('timeline', '30 days')
            
            # Get negotiated terms from call data
            agreed_rate = call_data.get('agreed_rate', campaign_data.get('offered_rate', 'TBD'))
            special_terms = call_data.get('special_terms', [])
            
            # Generate contract ID
            contract_id = f"IFC-{uuid.uuid4().hex[:8].upper()}"
            
            # Calculate dates
            start_date = datetime.now() + timedelta(days=7)  # Contract starts in 7 days
            end_date = start_date + timedelta(days=int(timeline.split()[0]) if timeline.split()[0].isdigit() else 30)
            
            # Create the contract content
            contract_content = f"""
INFLUENCER COLLABORATION CONTRACT
Contract ID: {contract_id}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

═══════════════════════════════════════════════════════════════

PARTIES:
Brand: {brand_name}
Influencer: {influencer_name} ({influencer_email})

CAMPAIGN DETAILS:
Campaign Name: {campaign_name}
Campaign Budget: ${campaign_budget}
Agreed Rate: ${agreed_rate}

DELIVERABLES:
{chr(10).join(f"• {deliverable}" for deliverable in deliverables)}

TIMELINE:
Start Date: {start_date.strftime('%Y-%m-%d')}
End Date: {end_date.strftime('%Y-%m-%d')}
Duration: {timeline}

TERMS AND CONDITIONS:

1. SCOPE OF WORK
   The Influencer agrees to create and publish content as specified in the 
   deliverables section above, promoting {brand_name}'s products/services.

2. COMPENSATION
   Total compensation: ${agreed_rate}
   Payment terms: 50% upfront, 50% upon completion
   Payment method: Bank transfer or PayPal

3. CONTENT REQUIREMENTS
   • All content must align with brand guidelines
   • Content must include required hashtags and mentions
   • Brand approval required before publishing
   • Content must comply with FTC disclosure requirements

4. INTELLECTUAL PROPERTY
   • Influencer retains rights to their likeness and personal brand
   • Brand receives usage rights for campaign content
   • Content may be repurposed by brand for marketing purposes

5. PERFORMANCE METRICS
   • Minimum engagement rate: As discussed
   • Reporting requirements: Weekly performance reports
   • Analytics access: To be provided to brand

6. CANCELLATION POLICY
   • Either party may cancel with 48 hours notice
   • Compensation for completed work will be honored
   • Unused advance payments to be returned

7. CONFIDENTIALITY
   Both parties agree to maintain confidentiality of campaign details
   and any proprietary information shared during collaboration.

SPECIAL TERMS:
{chr(10).join(f"• {term}" for term in special_terms) if special_terms else "• None"}

═══════════════════════════════════════════════════════════════

AGREEMENT:
By proceeding with this collaboration, both parties agree to the 
terms outlined above. This contract is governed by applicable 
local laws and regulations.

For questions or concerns, please contact:
InfluencerFlow AI Support
Email: support@influencerflow.ai
Phone: 1-800-INFLUENCE

═══════════════════════════════════════════════════════════════

Generated by InfluencerFlow AI Platform
Contract ID: {contract_id}
            """
            
            return contract_content.strip()
            
        except Exception as e:
            logger.error(f"❌ Error generating contract: {str(e)}")
            return "Error generating contract. Please contact support."
    
    def _generate_contract_filename(
        self,
        influencer_data: Dict[str, Any],
        campaign_data: Dict[str, Any]
    ) -> str:
        """
        Generate a filename for the contract
        """
        try:
            influencer_name = influencer_data.get('name', 'Influencer').replace(' ', '_')
            campaign_name = campaign_data.get('campaign_name', 'Campaign').replace(' ', '_')
            date_str = datetime.now().strftime('%Y%m%d')
            
            return f"Contract_{campaign_name}_{influencer_name}_{date_str}.txt"
            
        except Exception as e:
            logger.error(f"❌ Error generating contract filename: {str(e)}")
            return f"Contract_{datetime.now().strftime('%Y%m%d')}.txt"
    
    async def _log_contract_sent(
        self,
        influencer_data: Dict[str, Any],
        campaign_data: Dict[str, Any],
        contract_filename: str
    ) -> None:
        """
        Log that a contract was sent (for tracking and analytics)
        """
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'influencer_email': influencer_data.get('email'),
                'influencer_name': influencer_data.get('name'),
                'campaign_name': campaign_data.get('campaign_name'),
                'contract_filename': contract_filename,
                'status': 'sent'
            }
            
            # In a real application, you might save this to a database
            logger.info(f"📋 Contract log: {log_entry}")
            
        except Exception as e:
            logger.error(f"❌ Error logging contract: {str(e)}")
    
    async def send_follow_up_email(
        self,
        influencer_email: str,
        influencer_name: str,
        campaign_name: str,
        days_since_sent: int = 3
    ) -> bool:
        """
        Send a follow-up email if contract hasn't been signed
        """
        try:
            subject = f"📋 Follow-up: Contract for {campaign_name}"
            
            message = f"""
Hi {influencer_name}!

We wanted to follow up on the contract we sent you {days_since_sent} days ago for the {campaign_name} campaign.

If you have any questions about the terms or need any clarifications, please don't hesitate to reach out to us. We're here to help!

If you're ready to proceed, please sign and return the contract at your earliest convenience.

Looking forward to working with you!

Best regards,
InfluencerFlow AI Team
            """
            
            success = await self.email_service.send_notification_email(
                to_email=influencer_email,
                subject=subject,
                message=message
            )
            
            if success:
                logger.info(f"✅ Follow-up email sent to {influencer_email}")
            else:
                logger.error(f"❌ Failed to send follow-up email to {influencer_email}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error sending follow-up email: {str(e)}")
            return False

# Create global contract service instance
contract_service = ContractService() 