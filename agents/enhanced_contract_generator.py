# agents/enhanced_contract_generator.py
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum
from pathlib import Path
import jinja2
from pydantic import BaseModel

from models.campaign import CampaignData, NegotiationState, Creator
from services.email_service import EmailService

logger = logging.getLogger(__name__)

class ContractTemplate(str, Enum):
    STANDARD = "standard"
    PREMIUM = "premium"
    MICRO_INFLUENCER = "micro_influencer"
    ENTERPRISE = "enterprise"
    RUSH_DELIVERY = "rush_delivery"

class ContractStatus(str, Enum):
    DRAFT = "draft"
    GENERATED = "generated"
    SENT = "sent"
    VIEWED = "viewed"
    SIGNED = "signed"
    EXECUTED = "executed"
    CANCELLED = "cancelled"

class DeliveryMethod(str, Enum):
    EMAIL = "email"
    DOCUSIGN = "docusign"
    HELLOSIGN = "hellosign"
    DOWNLOAD_LINK = "download_link"

class ContractData(BaseModel):
    """Complete contract data structure"""
    contract_id: str
    campaign_id: str
    creator_id: str
    
    # Contract details
    final_rate: float
    deliverables: List[str]
    timeline: str
    usage_rights: str
    payment_schedule: str
    
    # Party information
    brand_info: Dict[str, Any]
    creator_info: Dict[str, Any]
    
    # Legal terms
    contract_template: ContractTemplate
    custom_terms: Dict[str, Any]
    compliance_requirements: List[str]
    
    # Workflow
    status: ContractStatus
    delivery_method: DeliveryMethod
    created_at: datetime
    sent_at: Optional[datetime] = None
    signed_at: Optional[datetime] = None

class EnhancedContractGenerator:
    """
    📝 ENHANCED CONTRACT GENERATOR
    
    Features:
    1. Template-based contract generation
    2. Custom terms integration
    3. Multiple delivery methods
    4. E-signature integration
    5. Automated follow-up
    """
    
    def __init__(self):
        self.email_service = EmailService()
        self.template_engine = jinja2.Environment(
            loader=jinja2.FileSystemLoader("data/templates")
        )
        
        # Contract tracking
        self.active_contracts: Dict[str, ContractData] = {}
        
        # Configuration
        self.contract_templates = self._load_contract_templates()
        self.default_terms = self._load_default_terms()
        
        # E-signature integrations
        self.docusign_enabled = False  # Would be configured
        self.hellosign_enabled = False
    
    async def generate_enhanced_contract(
        self,
        negotiation_state: NegotiationState,
        campaign_data: CampaignData,
        creator_data: Optional[Creator] = None,
        custom_terms: Optional[Dict[str, Any]] = None
    ) -> ContractData:
        """
        📝 Generate enhanced contract with all negotiated terms
        """
        
        contract_id = f"CONTRACT_{negotiation_state.creator_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"📝 Generating enhanced contract: {contract_id}")
        logger.info(f"💰 Value: ${negotiation_state.final_rate:,}")
        
        # Determine appropriate template
        template_type = self._select_contract_template(negotiation_state, campaign_data, creator_data)
        
        # Prepare contract data
        contract_data = ContractData(
            contract_id=contract_id,
            campaign_id=campaign_data.id,
            creator_id=negotiation_state.creator_id,
            final_rate=negotiation_state.final_rate,
            deliverables=negotiation_state.negotiated_terms.get("deliverables", []),
            timeline=negotiation_state.negotiated_terms.get("timeline", "7 days"),
            usage_rights=negotiation_state.negotiated_terms.get("usage_rights", "organic_only"),
            payment_schedule=negotiation_state.negotiated_terms.get("payment_schedule", "50% upfront"),
            brand_info=self._prepare_brand_info(campaign_data),
            creator_info=self._prepare_creator_info(creator_data, negotiation_state),
            contract_template=template_type,
            custom_terms=custom_terms or {},
            compliance_requirements=self._get_compliance_requirements(campaign_data),
            status=ContractStatus.DRAFT,
            delivery_method=self._determine_delivery_method(negotiation_state.final_rate),
            created_at=datetime.now()
        )
        
        # Generate contract content
        contract_content = await self._generate_contract_content(contract_data)
        
        # Save contract
        self.active_contracts[contract_id] = contract_data
        
        # Generate PDF
        contract_pdf_path = await self._generate_contract_pdf(contract_data, contract_content)
        
        logger.info(f"✅ Contract generated successfully: {contract_id}")
        
        return contract_data
    
    async def send_contract_for_signature(
        self,
        contract_id: str,
        delivery_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        📧 Send contract for signature via chosen delivery method
        """
        
        contract_data = self.active_contracts.get(contract_id)
        if not contract_data:
            raise ValueError(f"Contract {contract_id} not found")
        
        logger.info(f"📧 Sending contract {contract_id} via {contract_data.delivery_method.value}")
        
        # Route to appropriate delivery method
        if contract_data.delivery_method == DeliveryMethod.EMAIL:
            result = await self._send_via_email(contract_data, delivery_options)
        elif contract_data.delivery_method == DeliveryMethod.DOCUSIGN:
            result = await self._send_via_docusign(contract_data, delivery_options)
        elif contract_data.delivery_method == DeliveryMethod.HELLOSIGN:
            result = await self._send_via_hellosign(contract_data, delivery_options)
        else:
            result = await self._generate_download_link(contract_data, delivery_options)
        
        # Update contract status
        contract_data.status = ContractStatus.SENT
        contract_data.sent_at = datetime.now()
        
        # Schedule follow-up
        await self._schedule_contract_follow_up(contract_data)
        
        logger.info(f"✅ Contract sent successfully: {result}")
        
        return {
            "contract_id": contract_id,
            "delivery_method": contract_data.delivery_method.value,
            "sent_at": contract_data.sent_at.isoformat(),
            "delivery_result": result,
            "follow_up_scheduled": True
        }
    
    def _select_contract_template(
        self,
        negotiation_state: NegotiationState,
        campaign_data: CampaignData,
        creator_data: Optional[Creator]
    ) -> ContractTemplate:
        """Select appropriate contract template"""
        
        final_rate = negotiation_state.final_rate
        timeline = negotiation_state.negotiated_terms.get("timeline", "7 days")
        
        # Template selection logic
        if final_rate >= 10000:
            return ContractTemplate.ENTERPRISE
        elif final_rate >= 5000:
            return ContractTemplate.PREMIUM
        elif creator_data and creator_data.tier.value == "micro_influencer":
            return ContractTemplate.MICRO_INFLUENCER
        elif "rush" in timeline.lower() or "urgent" in timeline.lower():
            return ContractTemplate.RUSH_DELIVERY
        else:
            return ContractTemplate.STANDARD
    
    def _prepare_brand_info(self, campaign_data: CampaignData) -> Dict[str, Any]:
        """Prepare brand information for contract"""
        
        return {
            "company_name": campaign_data.brand_name,
            "product_name": campaign_data.product_name,
            "campaign_description": campaign_data.product_description,
            "campaign_goal": campaign_data.campaign_goal,
            "target_audience": campaign_data.target_audience,
            "contact_email": f"partnerships@{campaign_data.brand_name.lower().replace(' ', '')}.com",
            "legal_name": f"{campaign_data.brand_name} Inc.",
            "address": "123 Brand Street, Business City, BC 12345",  # Would be from database
            "tax_id": "XX-XXXXXXX"  # Would be from database
        }
    
    def _prepare_creator_info(self, creator_data: Optional[Creator], negotiation_state: NegotiationState) -> Dict[str, Any]:
        """Prepare creator information for contract"""
        
        if creator_data:
            return {
                "full_name": creator_data.name,
                "handle": creator_data.id,
                "platform": creator_data.platform.value,
                "followers": creator_data.followers,
                "engagement_rate": creator_data.engagement_rate,
                "email": f"{creator_data.id}@email.com",  # Would be from database
                "phone": creator_data.phone_number,
                "address": creator_data.location,
                "tax_status": "Individual"  # Would be from creator profile
            }
        else:
            return {
                "full_name": negotiation_state.creator_id,
                "handle": negotiation_state.creator_id,
                "email": f"{negotiation_state.creator_id}@email.com",
                "phone": "TBD",
                "address": "TBD",
                "tax_status": "Individual"
            }
    
    def _determine_delivery_method(self, contract_value: float) -> DeliveryMethod:
        """Determine optimal delivery method based on contract value"""
        
        if contract_value >= 10000 and self.docusign_enabled:
            return DeliveryMethod.DOCUSIGN
        elif contract_value >= 5000 and self.hellosign_enabled:
            return DeliveryMethod.HELLOSIGN
        else:
            return DeliveryMethod.EMAIL
    
    async def _generate_contract_content(self, contract_data: ContractData) -> str:
        """Generate contract content using templates"""
        
        template_name = f"{contract_data.contract_template.value}_contract.html"
        
        try:
            template = self.template_engine.get_template(template_name)
        except jinja2.TemplateNotFound:
            # Fallback to standard template
            template = self.template_engine.get_template("standard_contract.html")
        
        # Prepare template variables
        template_vars = {
            "contract": contract_data,
            "brand": contract_data.brand_info,
            "creator": contract_data.creator_info,
            "terms": self._prepare_contract_terms(contract_data),
            "deliverables": self._format_deliverables(contract_data.deliverables),
            "payment_schedule": self._format_payment_schedule(contract_data),
            "legal_terms": self._get_legal_terms(contract_data),
            "signature_date": datetime.now().strftime("%B %d, %Y"),
            "effective_date": (datetime.now() + timedelta(days=1)).strftime("%B %d, %Y"),
            "completion_date": self._calculate_completion_date(contract_data.timeline)
        }
        
        contract_content = template.render(**template_vars)
        return contract_content
    
    def _prepare_contract_terms(self, contract_data: ContractData) -> Dict[str, Any]:
        """Prepare formatted contract terms"""
        
        return {
            "compensation": {
                "total_amount": contract_data.final_rate,
                "currency": "USD",
                "payment_schedule": contract_data.payment_schedule,
                "payment_method": "Bank transfer or digital payment"
            },
            "deliverables": {
                "primary": contract_data.deliverables,
                "timeline": contract_data.timeline,
                "quality_standards": "Professional quality, brand-appropriate content",
                "approval_process": "Brand review within 24-48 hours, up to 2 revisions"
            },
            "usage_rights": {
                "type": contract_data.usage_rights,
                "duration": self._get_usage_duration(contract_data.usage_rights),
                "geographic_scope": "Worldwide",
                "platforms": "All social media platforms",
                "attribution": "Required"
            },
            "performance": {
                "expected_deliverables": len(contract_data.deliverables),
                "timeline_commitment": contract_data.timeline,
                "quality_commitment": "Professional standards",
                "brand_safety": "Full compliance required"
            }
        }
    
    def _format_deliverables(self, deliverables: List[str]) -> List[Dict[str, Any]]:
        """Format deliverables for contract display"""
        
        deliverable_details = {
            "video_review": {
                "name": "Product Review Video",
                "description": "2-5 minute video showcasing product features and honest review",
                "specifications": "1080p minimum, good lighting, authentic presentation"
            },
            "instagram_post": {
                "name": "Instagram Feed Post",
                "description": "High-quality feed post with product showcase",
                "specifications": "Professional photography, engaging caption, proper hashtags"
            },
            "instagram_story": {
                "name": "Instagram Story Series",
                "description": "3-5 story slides featuring product",
                "specifications": "Interactive elements encouraged, brand tag required"
            },
            "tiktok_video": {
                "name": "TikTok Video",
                "description": "Platform-appropriate video showcasing product",
                "specifications": "Trending audio/effects, engaging format, proper disclosure"
            }
        }
        
        formatted_deliverables = []
        for deliverable in deliverables:
            if deliverable in deliverable_details:
                formatted_deliverables.append(deliverable_details[deliverable])
            else:
                formatted_deliverables.append({
                    "name": deliverable.replace("_", " ").title(),
                    "description": f"Custom deliverable: {deliverable}",
                    "specifications": "To be defined"
                })
        
        return formatted_deliverables
    
    def _format_payment_schedule(self, contract_data: ContractData) -> List[Dict[str, Any]]:
        """Format payment schedule for contract"""
        
        schedule_text = contract_data.payment_schedule.lower()
        total_amount = contract_data.final_rate
        
        if "50%" in schedule_text and "upfront" in schedule_text:
            return [
                {
                    "milestone": "Contract Execution",
                    "amount": total_amount * 0.5,
                    "percentage": 50,
                    "due_date": "Within 3 business days of contract signing",
                    "description": "50% upfront payment"
                },
                {
                    "milestone": "Content Delivery & Approval",
                    "amount": total_amount * 0.5,
                    "percentage": 50,
                    "due_date": "Within 5 business days of content approval",
                    "description": "50% completion payment"
                }
            ]
        elif "25%" in schedule_text:
            return [
                {
                    "milestone": "Contract Execution",
                    "amount": total_amount * 0.25,
                    "percentage": 25,
                    "due_date": "Within 3 business days of contract signing"
                },
                {
                    "milestone": "Content Delivery",
                    "amount": total_amount * 0.50,
                    "percentage": 50,
                    "due_date": "Within 3 business days of content delivery"
                },
                {
                    "milestone": "Content Published",
                    "amount": total_amount * 0.25,
                    "percentage": 25,
                    "due_date": "Within 7 days of content publication"
                }
            ]
        else:
            return [
                {
                    "milestone": "Content Delivery & Approval",
                    "amount": total_amount,
                    "percentage": 100,
                    "due_date": "Within 5 business days of content approval",
                    "description": "Full payment upon completion"
                }
            ]
    
    async def _send_via_email(self, contract_data: ContractData, options: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Send contract via email with PDF attachment"""
        
        # Generate email content
        email_subject = f"Influencer Partnership Contract - {contract_data.brand_info['company_name']}"
        
        email_body = f"""
        Dear {contract_data.creator_info['full_name']},

        Thank you for agreeing to partner with {contract_data.brand_info['company_name']}! 

        Please find attached your influencer partnership contract for the {contract_data.brand_info['product_name']} campaign.

        Contract Details:
        • Total Compensation: ${contract_data.final_rate:,}
        • Deliverables: {len(contract_data.deliverables)} content pieces
        • Timeline: {contract_data.timeline}
        • Payment Schedule: {contract_data.payment_schedule}

        Please review the contract carefully and reply with your signed copy. If you have any questions, don't hesitate to reach out.

        We're excited to work with you!

        Best regards,
        {contract_data.brand_info['company_name']} Partnership Team
        {contract_data.brand_info['contact_email']}
        """
        
        # Send email with attachment
        email_result = await self.email_service.send_contract_email(
            to_email=contract_data.creator_info['email'],
            subject=email_subject,
            body=email_body,
            contract_pdf_path=f"contracts/{contract_data.contract_id}.pdf",
            contract_data=contract_data
        )
        
        return email_result
    
    async def _send_via_docusign(self, contract_data: ContractData, options: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Send contract via DocuSign for e-signature"""
        
        # DocuSign integration would go here
        logger.info(f"📄 Sending contract via DocuSign: {contract_data.contract_id}")
        
        # Mock implementation
        return {
            "provider": "docusign",
            "envelope_id": f"docusign_env_{contract_data.contract_id}",
            "signing_url": f"https://docusign.com/sign/{contract_data.contract_id}",
            "status": "sent"
        }
    
    async def _send_via_hellosign(self, contract_data: ContractData, options: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Send contract via HelloSign for e-signature"""
        
        # HelloSign integration would go here
        logger.info(f"📄 Sending contract via HelloSign: {contract_data.contract_id}")
        
        # Mock implementation
        return {
            "provider": "hellosign",
            "signature_request_id": f"hellosign_req_{contract_data.contract_id}",
            "signing_url": f"https://hellosign.com/sign/{contract_data.contract_id}",
            "status": "sent"
        }
    
    async def _generate_download_link(self, contract_data: ContractData, options: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate secure download link for contract"""
        
        # Generate secure download link
        download_token = f"download_{contract_data.contract_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        download_url = f"/api/contracts/download/{download_token}"
        
        # Send email with download link
        email_subject = f"Contract Ready for Download - {contract_data.brand_info['company_name']}"
        email_body = f"""
        Dear {contract_data.creator_info['full_name']},

        Your partnership contract is ready for download!

        Click here to download: {download_url}

        This link will expire in 7 days for security.

        Contract Value: ${contract_data.final_rate:,}
        Campaign: {contract_data.brand_info['product_name']}

        Best regards,
        {contract_data.brand_info['company_name']} Team
        """
        
        await self.email_service.send_email(
            to_email=contract_data.creator_info['email'],
            subject=email_subject,
            body=email_body
        )
        
        return {
            "provider": "download_link",
            "download_url": download_url,
            "download_token": download_token,
            "expires_at": (datetime.now() + timedelta(days=7)).isoformat(),
            "status": "sent"
        }
    
    async def _schedule_contract_follow_up(self, contract_data: ContractData):
        """Schedule automatic follow-up for unsigned contracts"""
        
        # Schedule follow-up reminders
        follow_up_schedule = [
            {"days": 2, "type": "gentle_reminder"},
            {"days": 5, "type": "urgent_reminder"},
            {"days": 7, "type": "final_notice"}
        ]
        
        for follow_up in follow_up_schedule:
            # In real implementation, this would use a task scheduler
            logger.info(f"📅 Scheduled {follow_up['type']} for {contract_data.contract_id} in {follow_up['days']} days")
    
    async def _generate_contract_pdf(self, contract_data: ContractData, contract_content: str) -> str:
        """Generate PDF version of contract"""
        
        # PDF generation would use libraries like weasyprint or pdfkit
        # For now, saving HTML version
        
        pdf_path = f"contracts/{contract_data.contract_id}.pdf"
        html_path = f"contracts/{contract_data.contract_id}.html"
        
        # Ensure directory exists
        Path("contracts").mkdir(exist_ok=True)
        
        # Save HTML version
        with open(html_path, 'w') as f:
            f.write(contract_content)
        
        logger.info(f"📄 Contract saved: {html_path}")
        return pdf_path
    
    def _load_contract_templates(self) -> Dict[str, str]:
        """Load contract templates"""
        
        # In real implementation, these would be loaded from files
        return {
            "standard": "Standard Influencer Partnership Agreement Template",
            "premium": "Premium Influencer Partnership Agreement Template",
            "micro_influencer": "Micro-Influencer Partnership Agreement Template",
            "enterprise": "Enterprise Influencer Partnership Agreement Template",
            "rush_delivery": "Rush Delivery Influencer Partnership Agreement Template"
        }
    
    def _load_default_terms(self) -> Dict[str, Any]:
        """Load default contract terms"""
        
        return {
            "cancellation_policy": "48 hours notice required, 50% payment for cancellation after approval",
            "revision_policy": "Up to 2 minor revisions included in base rate",
            "brand_safety": "Content must comply with brand guidelines and platform policies",
            "disclosure_requirements": "FTC-compliant disclosure required (#ad, #sponsored, etc.)",
            "intellectual_property": "Creator retains content ownership, brand receives usage rights as specified",
            "confidentiality": "Campaign details confidential until public launch",
            "force_majeure": "Standard force majeure clauses for unforeseeable circumstances"
        }
    
    def _get_compliance_requirements(self, campaign_data: CampaignData) -> List[str]:
        """Get compliance requirements based on campaign"""
        
        requirements = [
            "FTC disclosure compliance required",
            "Platform community guidelines compliance",
            "Brand safety guidelines adherence"
        ]
        
        # Add specific requirements based on campaign niche
        if campaign_data.product_niche.lower() in ["health", "wellness", "supplements"]:
            requirements.append("Health claims must be FDA compliant")
        
        if campaign_data.product_niche.lower() in ["finance", "investment"]:
            requirements.append("Financial disclaimers required")
        
        return requirements
    
    def _get_usage_duration(self, usage_rights: str) -> str:
        """Get usage duration based on rights type"""
        
        usage_durations = {
            "organic_only": "12 months from publication date",
            "paid_ads": "6 months from publication date",
            "commercial_use": "18 months from publication date",
            "exclusive": "24 months from publication date"
        }
        
        return usage_durations.get(usage_rights, "12 months from publication date")
    
    def _calculate_completion_date(self, timeline: str) -> str:
        """Calculate contract completion date"""
        
        try:
            if "day" in timeline.lower():
                days = int(timeline.split()[0])
                completion_date = datetime.now() + timedelta(days=days + 5)  # +5 for buffer
            else:
                completion_date = datetime.now() + timedelta(days=12)  # Default
        except:
            completion_date = datetime.now() + timedelta(days=12)  # Default
        
        return completion_date.strftime("%B %d, %Y")
    
    def _get_legal_terms(self, contract_data: ContractData) -> Dict[str, str]:
        """Get legal terms for contract"""
        
        return {
            "governing_law": "This agreement shall be governed by the laws of [State/Country]",
            "dispute_resolution": "Disputes resolved through good faith negotiation, then binding arbitration",
            "entire_agreement": "This agreement constitutes the entire agreement between parties",
            "modification": "Modifications must be in writing and signed by both parties",
            "severability": "If any provision is unenforceable, remainder remains in effect",
            "assignment": "Agreement may not be assigned without written consent"
        }
    
    # API methods for contract management
    
    def get_contract_status(self, contract_id: str) -> Optional[ContractData]:
        """Get contract status"""
        return self.active_contracts.get(contract_id)
    
    def get_pending_contracts(self) -> List[ContractData]:
        """Get all pending contracts"""
        return [
            contract for contract in self.active_contracts.values()
            if contract.status in [ContractStatus.SENT, ContractStatus.VIEWED]
        ]
    
    def mark_contract_signed(self, contract_id: str, signed_at: Optional[datetime] = None):
        """Mark contract as signed"""
        contract = self.active_contracts.get(contract_id)
        if contract:
            contract.status = ContractStatus.SIGNED
            contract.signed_at = signed_at or datetime.now()
            logger.info(f"✅ Contract {contract_id} marked as signed")
    
    def get_contract_analytics(self) -> Dict[str, Any]:
        """Get contract analytics"""
        
        contracts = list(self.active_contracts.values())
        
        if not contracts:
            return {"total_contracts": 0}
        
        total_value = sum(c.final_rate for c in contracts)
        signed_contracts = [c for c in contracts if c.status == ContractStatus.SIGNED]
        pending_contracts = [c for c in contracts if c.status in [ContractStatus.SENT, ContractStatus.VIEWED]]
        
        return {
            "total_contracts": len(contracts),
            "total_value": total_value,
            "signed_contracts": len(signed_contracts),
            "pending_contracts": len(pending_contracts),
            "signing_rate": len(signed_contracts) / len(contracts) * 100 if contracts else 0,
            "average_contract_value": total_value / len(contracts) if contracts else 0,
            "templates_used": list(set(c.contract_template.value for c in contracts))
        }

# Email Service for Contract Delivery
class EmailService:
    """Email service for contract delivery and communication"""
    
    async def send_contract_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        contract_pdf_path: str,
        contract_data: ContractData
    ) -> Dict[str, Any]:
        """Send contract via email with attachment"""
        
        logger.info(f"📧 Sending contract email to {to_email}")
        
        # Mock email sending
        return {
            "status": "sent",
            "message_id": f"email_msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "to_email": to_email,
            "subject": subject,
            "sent_at": datetime.now().isoformat()
        }
    
    async def send_email(self, to_email: str, subject: str, body: str) -> Dict[str, Any]:
        """Send regular email"""
        
        logger.info(f"📧 Sending email to {to_email}: {subject}")
        
        return {
            "status": "sent",
            "message_id": f"email_msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "to_email": to_email,
            "sent_at": datetime.now().isoformat()
        }