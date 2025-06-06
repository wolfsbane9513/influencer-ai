# InfluencerFlow AI Platform

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![ElevenLabs](https://img.shields.io/badge/ElevenLabs-API-purple.svg)](https://elevenlabs.io/)
[![Groq](https://img.shields.io/badge/Groq-AI-orange.svg)](https://groq.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Complete AI-Powered Influencer Marketing Campaign Automation Platform**

InfluencerFlow AI is a comprehensive platform that automates the entire influencer marketing workflow - from intelligent creator discovery to contract generation and email delivery - using advanced AI agents, voice-based negotiations, automated contract generation, and intelligent notification systems.

## 🎯 Key Features

### 🤖 **AI-Powered Automation**
- **Intelligent Creator Discovery**: Vector similarity matching with sentence transformers
- **AI Strategy Generation**: Groq-powered campaign optimization and negotiation strategies
- **Automated Negotiations**: ElevenLabs voice calls with dynamic variables and real-time analysis
- **Smart Contract Generation**: Comprehensive legal agreements with structured terms
- **Email Automation**: Professional contract delivery and campaign communications

### 📞 **Voice-Based Negotiations**
- **Real-time Phone Calls**: ElevenLabs conversational AI integration
- **Dynamic Variables**: Personalized conversation context for each creator
- **Structured Analysis**: Extract negotiation outcomes, rates, and terms automatically
- **Live Monitoring**: Real-time progress tracking during calls with automatic workflow continuation
- **Conversation Analytics**: Detailed analysis of call outcomes and creator sentiment

### 🎛️ **Multi-Agent Orchestration**
- **Enhanced Campaign Orchestrator**: Master coordinator with AI strategy integration
- **Discovery Agent**: AI-powered creator matching and scoring with market intelligence
- **Negotiation Agent**: Voice-based deal closing with real-time conversation monitoring
- **Contract Agent**: Automated legal document generation with email delivery
- **Email Service**: Professional contract distribution and campaign communications

### 📧 **Comprehensive Communication System**
- **Contract Email Delivery**: Automated sending of professionally formatted contracts
- **Multi-channel Notifications**: Email, Slack, Discord, webhooks, and SMS support
- **Template Engine**: Professional email templates with dynamic content rendering
- **Delivery Confirmation**: Track email delivery status and recipient engagement
- **Campaign Updates**: Automated milestone and completion notifications

### 📊 **Advanced Analytics & Monitoring**
- **Real-time Campaign Tracking**: Live progress monitoring with detailed metrics
- **Performance Analytics**: Success rates, cost efficiency, ROI analysis
- **Conversation Intelligence**: Detailed analysis of negotiation calls and outcomes
- **Validation Systems**: Comprehensive data quality checks and error handling
- **Detailed Reporting**: Campaign summaries, creator insights, and performance predictions

### 🔔 **Standalone Notification Service**
- **Independent Operation**: Self-contained notification service with queue processing
- **Multiple Channels**: Email, webhooks, Slack, Discord, SMS (configurable)
- **Smart Templates**: Professional notification templates with dynamic content
- **Background Processing**: Automated queue processing with retry logic
- **Event-Driven**: Responds to campaign events and external triggers

## 🏗️ Enhanced Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    InfluencerFlow AI Platform                │
│                        Version 2.0.0                        │
├─────────────────────────────────────────────────────────────┤
│  FastAPI Backend (main.py)                                 │
│  ├── Enhanced Webhook Endpoints (/api/webhook/)            │
│  ├── Real-time Monitoring (/api/monitor/)                  │
│  ├── Email Integration (services/email_service.py)         │
│  └── Notifications API (services/notifications.py)         │
├─────────────────────────────────────────────────────────────┤
│  Enhanced AI Agents (/agents/)                             │
│  ├── EnhancedCampaignOrchestrator (Master + AI Strategy)   │
│  ├── InfluencerDiscoveryAgent (ML-powered Matching)        │
│  ├── EnhancedNegotiationAgent (Voice + Analysis)           │
│  ├── EnhancedContractAgent (Generation + Email)            │
│  └── ConversationMonitor (Real-time Call Tracking)         │
├─────────────────────────────────────────────────────────────┤
│  Comprehensive Services (/services/)                       │
│  ├── EnhancedVoiceService (ElevenLabs + Dynamic Variables) │
│  ├── EmailService (SMTP + Professional Templates)          │
│  ├── NotificationService (Multi-channel + Queue)           │
│  ├── EmbeddingService (Vector Similarity)                  │
│  ├── PricingService (Market Intelligence)                  │
│  └── DatabaseService (Complete Data Persistence)           │
├─────────────────────────────────────────────────────────────┤
│  External Integrations                                     │
│  ├── ElevenLabs API (Voice Conversations + Monitoring)     │
│  ├── Groq API (AI Strategy + Optimization)                 │
│  ├── SMTP Servers (Email Delivery)                         │
│  ├── Slack/Discord APIs (Team Notifications)               │
│  ├── Webhook Endpoints (External System Integration)       │
│  ├── Sentence Transformers (ML Embeddings)                 │
│  └── PostgreSQL (Comprehensive Data Storage)               │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.13+**
- **UV Package Manager** (recommended) or pip
- **ElevenLabs Account** with API key and configured agent
- **Groq Account** with API key
- **SMTP Email Account** (Gmail, Outlook, etc.) for contract delivery
- **PostgreSQL** (optional, uses mock by default)

### Installation

1. **Clone the Repository**
```bash
git clone https://github.com/influencerflow/influencerflow-ai.git
cd influencerflow-ai
```

2. **Install Dependencies**
```bash
# Using UV (recommended)
uv sync

# Or using pip
pip install -r requirements.txt

# For development with all features
uv sync --extra dev,notifications,documents,analytics
```

3. **Environment Configuration**
```bash
# Copy environment template
cp .env.template .env

# Edit .env with your credentials
nano .env
```

4. **Complete Environment Variables**
```bash
# Core API Keys (Required)
GROQ_API_KEY=gsk_your_groq_key_here
ELEVENLABS_API_KEY=sk_your_elevenlabs_key_here
ELEVENLABS_AGENT_ID=your_agent_id_here
ELEVENLABS_PHONE_NUMBER_ID=your_phone_number_here

# Email Configuration (Required for contract delivery)
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_NAME=InfluencerFlow AI
SENDER_EMAIL=partnerships@yourcompany.com

# Notification Services (Optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/your/webhook/url
WEBHOOK_URLS=https://your-webhook-endpoint.com/notifications

# Database (Optional)
DATABASE_URL=postgresql://user:password@localhost:5432/influencerflow

# Application Configuration
DEMO_MODE=true
MOCK_CALLS=false
DEBUG=true
```

5. **Email Setup Guide**

**For Gmail:**
```bash
# 1. Enable 2-Factor Authentication on your Google account
# 2. Generate an App Password:
#    - Go to Google Account settings
#    - Security → App passwords
#    - Select "Mail" and generate password
# 3. Use the app password as EMAIL_PASSWORD
```

**For Outlook:**
```bash
# Set these values in .env:
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
EMAIL_USERNAME=your_email@outlook.com
EMAIL_PASSWORD=your_password
```

6. **Start the Platform**
```bash
# Development mode
uvicorn main:app --reload

# Or using the provided script
python main.py
```

7. **Start Notifications Service** (Optional, runs independently)
```bash
# In a separate terminal
python services/notifications.py
```

8. **Verify Installation**
```bash
# Health check
curl http://localhost:8000/health

# System status
curl http://localhost:8000/api/webhook/system-status

# Test email configuration
curl http://localhost:8000/api/webhook/test-enhanced-elevenlabs
```

## 🔧 Complete Configuration Guide

### ElevenLabs Advanced Setup

1. **Create and Configure Agent**
   - Sign up at [ElevenLabs](https://elevenlabs.io/)
   - Navigate to Conversational AI → Create New Agent
   - Configure with the following system prompt:

```
You are an AI negotiation specialist for InfluencerFlow, representing brands in influencer partnerships. 

Your goal is to negotiate fair collaborations while maintaining positive relationships.

CONTEXT VARIABLES:
- InfluencerProfile: {InfluencerProfile}
- campaignBrief: {campaignBrief}
- negotiationStrategy: {negotiationStrategy}
- budgetStrategy: {budgetStrategy}

CONVERSATION STRUCTURE:
1. Professional greeting and introduction
2. Present campaign opportunity with enthusiasm
3. Discuss collaboration terms and deliverables
4. Address any concerns or objections
5. Reach agreement or schedule follow-up

ANALYSIS REQUIREMENTS:
Extract and provide:
- negotiation_outcome: "accepted", "declined", "needs_followup", or "unclear"
- final_rate_mentioned: numeric value if discussed
- deliverables_discussed: list of content types mentioned
- timeline_mentioned: timeline agreed upon
- creator_enthusiasm_level: 1-10 scale
- objections_raised: list of concerns mentioned
- conversation_summary: brief overview

Be professional, respectful, and focus on creating win-win partnerships.
```

2. **Add Dynamic Variables** in ElevenLabs dashboard:
   - `InfluencerProfile` (string)
   - `campaignBrief` (string)  
   - `negotiationStrategy` (string)
   - `budgetStrategy` (string)
   - `influencerName` (string)

3. **Configure Phone Integration**
   - Set up Twilio phone number
   - Link to your ElevenLabs agent
   - Test call functionality

### Email Service Configuration

**Advanced SMTP Settings:**
```python
# In .env file
EMAIL_USERNAME=partnerships@yourcompany.com
EMAIL_PASSWORD=your_secure_app_password
SMTP_SERVER=smtp.yourcompany.com
SMTP_PORT=587
SENDER_NAME=YourCompany Partnerships
SENDER_EMAIL=partnerships@yourcompany.com

# Optional: Custom email templates
EMAIL_TEMPLATE_DIR=templates/emails/
```

**Custom Email Templates:**
Create custom templates in `templates/emails/`:
- `contract_delivery.html`
- `campaign_completion.html` 
- `milestone_notification.html`

### Notification Service Configuration

Create `config/notifications.json`:
```json
{
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "notifications@yourcompany.com",
    "password": "your_app_password",
    "sender_name": "InfluencerFlow Notifications"
  },
  "slack": {
    "slack_webhook_url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
    "default_channel": "#influencer-campaigns",
    "bot_name": "InfluencerFlow AI"
  },
  "webhook": {
    "webhook_urls": [
      "https://your-system.com/webhooks/influencer-updates"
    ],
    "timeout": 30,
    "retry_count": 3
  },
  "processing": {
    "batch_size": 10,
    "processing_interval": 30,
    "max_retries": 3
  }
}
```

## 📡 Complete API Reference

### Enhanced Campaign Endpoints

#### Start Enhanced Campaign with Email Delivery
```http
POST /api/webhook/enhanced-campaign
Content-Type: application/json

{
  "campaign_id": "campaign-2024-001",
  "product_name": "SmartFit Pro Tracker",
  "brand_name": "TechFit Solutions",
  "product_description": "AI-powered fitness tracking device with personalized coaching",
  "target_audience": "Fitness enthusiasts aged 22-40",
  "campaign_goal": "Launch premium fitness tech product",
  "product_niche": "fitness",
  "total_budget": 18000.0
}
```

**Response:**
```json
{
  "message": "🎯 Enhanced AI campaign workflow started",
  "task_id": "uuid-task-id",
  "campaign_id": "campaign-2024-001",
  "estimated_duration_minutes": 8,
  "monitor_url": "/api/monitor/enhanced-campaign/uuid-task-id",
  "status": "started",
  "enhancements": [
    "ElevenLabs dynamic variables integration",
    "Structured conversation analysis",
    "Automated contract generation",
    "Professional email delivery",
    "Real-time notification system"
  ]
}
```

#### Monitor Campaign with Email Status
```http
GET /api/monitor/enhanced-campaign/{task_id}
```

**Response includes email delivery status:**
```json
{
  "task_id": "uuid-task-id",
  "current_stage": "completed",
  "progress": {
    "overall_percentage": 100.0,
    "contracts_generated": 2,
    "emails_sent": 2,
    "email_delivery_rate": "100%"
  },
  "email_delivery_summary": {
    "contracts_sent": 2,
    "successful_deliveries": 2,
    "failed_deliveries": 0,
    "recipients": [
      "creator1@demo-creator.com",
      "creator2@demo-creator.com"
    ]
  }
}
```

### Email & Notification Endpoints

#### Send Contract Email Manually
```http
POST /api/webhook/send-contract-email
Content-Type: application/json

{
  "contract_id": "IFC-ABC123",
  "creator_email": "creator@example.com",
  "creator_name": "Amazing Creator"
}
```

#### Trigger Notification
```http
POST /api/notifications/send
Content-Type: application/json

{
  "type": "email",
  "recipient": "user@example.com",
  "subject": "Campaign Update",
  "message": "Your campaign has been completed successfully!",
  "priority": "medium",
  "template": "campaign_completed",
  "template_data": {
    "campaign_name": "SmartFit Launch",
    "total_spend": 15000,
    "successful_partnerships": 3
  }
}
```

### Testing Endpoints

```http
POST /api/webhook/test-enhanced-campaign     # Test complete workflow
GET  /api/webhook/test-enhanced-elevenlabs   # Test ElevenLabs setup
POST /api/webhook/test-enhanced-call         # Test voice negotiations
POST /api/webhook/test-email-delivery        # Test email functionality
POST /api/webhook/test-notifications         # Test notification system
GET  /api/webhook/system-status              # Complete system status
```

## 🎯 Complete Usage Examples

### 1. Full Campaign Workflow

```python
import requests
import time

# Step 1: Start enhanced campaign
campaign_data = {
    "campaign_id": "fitness-tracker-2024",
    "product_name": "FitTrack Pro",
    "brand_name": "HealthTech Inc",
    "product_description": "Advanced fitness tracker with AI coaching",
    "target_audience": "Health-conscious millennials and Gen Z",
    "campaign_goal": "Drive 10,000 pre-orders through authentic reviews",
    "product_niche": "fitness",
    "total_budget": 25000.0
}

response = requests.post(
    "http://localhost:8000/api/webhook/enhanced-campaign",
    json=campaign_data
)

task_id = response.json()["task_id"]
print(f"🚀 Campaign started: {task_id}")

# Step 2: Monitor with email tracking
while True:
    status = requests.get(f"http://localhost:8000/api/monitor/enhanced-campaign/{task_id}")
    data = status.json()
    
    print(f"📊 Stage: {data['current_stage']}")
    print(f"📈 Progress: {data['progress']['overall_percentage']:.1f}%")
    
    # Check email delivery
    if 'email_delivery_summary' in data:
        email_summary = data['email_delivery_summary']
        print(f"📧 Emails sent: {email_summary['contracts_sent']}")
        print(f"✅ Successful deliveries: {email_summary['successful_deliveries']}")
    
    if data['is_complete']:
        print("🎉 Campaign completed!")
        break
        
    time.sleep(30)

# Step 3: Get detailed results
final_results = requests.get(
    f"http://localhost:8000/api/monitor/enhanced-campaign/{task_id}/detailed-summary"
)

print("📋 Final Results:")
print(f"💰 Total spend: ${final_results.json()['total_spend']:,.2f}")
print(f"🤝 Successful partnerships: {final_results.json()['successful_partnerships']}")
print(f"📧 Contract delivery rate: {final_results.json()['email_delivery_rate']}")
```

### 2. Email Service Integration

```python
from services.email_service import EmailService
import asyncio

async def send_campaign_emails():
    email_service = EmailService()
    
    # Send contract
    contract_data = {
        "contract_id": "IFC-123456",
        "brand_name": "TechFit",
        "product_name": "SmartTracker Pro",
        "final_rate": 5500.0,
        "deliverables": {
            "primary_deliverables": ["video_review", "instagram_post", "instagram_story"]
        },
        "payment_schedule": [
            {"milestone": "Contract Signing", "amount": 2750, "percentage": 50},
            {"milestone": "Content Delivery", "amount": 2750, "percentage": 50}
        ]
    }
    
    result = await email_service.send_contract_email(
        contract_data=contract_data,
        creator_email="influencer@example.com",
        creator_name="Top Creator"
    )
    
    print(f"📧 Email result: {result}")

# Run email sending
asyncio.run(send_campaign_emails())
```

### 3. Standalone Notifications Service

```python
from services.notifications import NotificationService, NotificationType, NotificationPriority
import asyncio

async def notification_examples():
    # Initialize service
    notification_service = NotificationService("config/notifications.json")
    
    # Send campaign completion notification
    await notification_service.send_notification(
        notification_type=NotificationType.EMAIL,
        recipient="brand@company.com",
        subject="🎉 Campaign Completed Successfully",
        message="Your influencer campaign has finished with great results!",
        priority=NotificationPriority.HIGH,
        template="campaign_completed",
        template_data={
            "campaign_name": "SmartFit Launch",
            "total_spend": 18500,
            "successful_partnerships": 3,
            "total_reach": 1250000,
            "avg_engagement": 6.8,
            "roi": 285
        }
    )
    
    # Send Slack notification to team
    await notification_service.send_notification(
        notification_type=NotificationType.SLACK,
        recipient="#marketing-team",
        subject="Campaign Alert",
        message="New influencer campaign has exceeded performance targets!",
        priority=NotificationPriority.MEDIUM
    )
    
    # Bulk notifications
    notifications = [
        {
            "notification_type": NotificationType.EMAIL,
            "recipient": "creator1@example.com",
            "subject": "Payment Processed",
            "template": "payment_processed",
            "template_data": {"amount": 5500, "campaign_name": "SmartFit Pro"}
        },
        {
            "notification_type": NotificationType.EMAIL,
            "recipient": "creator2@example.com", 
            "subject": "Payment Processed",
            "template": "payment_processed",
            "template_data": {"amount": 4200, "campaign_name": "SmartFit Pro"}
        }
    ]
    
    results = await notification_service.send_bulk_notifications(notifications)
    print(f"📊 Bulk notification results: {results}")

# Run notification examples
asyncio.run(notification_examples())
```

## 🛠️ Advanced Development Guide

### Project Structure
```
influencerflow-ai/
├── main.py                          # FastAPI application entry point
├── config/
│   ├── settings.py                  # Enhanced configuration management
│   └── notifications.json           # Notification service config
├── models/
│   └── campaign.py                  # Complete data models and schemas
├── agents/                          # Enhanced AI agent implementations
│   ├── enhanced_orchestrator.py     # Master coordinator with AI strategy
│   ├── discovery.py                 # ML-powered creator discovery
│   ├── enhanced_negotiation.py      # Voice negotiations + analysis
│   └── enhanced_contracts.py        # Contract generation + email
├── services/                        # Comprehensive service layer
│   ├── enhanced_voice.py            # ElevenLabs integration + monitoring
│   ├── email_service.py             # Professional email delivery
│   ├── notifications.py             # Multi-channel notification system
│   ├── conversation_monitor.py      # Real-time call monitoring
│   ├── embeddings.py                # ML embeddings service
│   ├── pricing.py                   # Market intelligence
│   └── database.py                  # Complete data persistence
├── api/                             # Enhanced API route handlers
│   ├── enhanced_webhooks.py         # Campaign webhook endpoints
│   └── enhanced_monitoring.py       # Real-time progress monitoring
├── data/                            # Static data and templates
│   ├── creators.json                # Creator database
│   ├── market_data.json             # Market pricing intelligence
│   └── templates/                   # Email and document templates
├── tests/                           # Comprehensive test suite
│   ├── test_agents.py
│   ├── test_services.py
│   ├── test_email.py
│   └── test_notifications.py
├── templates/                       # Email and document templates
│   ├── emails/
│   │   ├── contract_delivery.html
│   │   ├── campaign_completion.html
│   │   └── payment_notification.html
│   └── contracts/
│       ├── standard_contract.html
│       └── premium_contract.html
└── docs/                           # Documentation
    ├── api_reference.md
    ├── email_setup.md
    └── deployment_guide.md
```

### Custom Email Templates

Create professional email templates in `templates/emails/`:

**Contract Delivery Template** (`contract_delivery.html`):
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Partnership Contract - {{brand_name}}</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .header { background: #2c3e50; color: white; padding: 20px; text-align: center; }
        .content { padding: 30px; max-width: 600px; margin: 0 auto; }
        .highlight { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .cta-button { background: #3498db; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }
        .footer { background: #ecf0f1; padding: 20px; text-align: center; font-size: 12px; color: #7f8c8d; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤝 Partnership Contract Ready</h1>
        <h2>{{brand_name}} x {{creator_name}}</h2>
    </div>
    
    <div class="content">
        <p>Dear {{creator_name}},</p>
        
        <p>Congratulations! Your partnership contract with <strong>{{brand_name}}</strong> is ready for review.</p>
        
        <div class="highlight">
            <h3>📋 Partnership Details:</h3>
            <ul>
                <li><strong>Campaign:</strong> {{product_name}}</li>
                <li><strong>Total Compensation:</strong> ${{final_rate:,.2f}}</li>
                <li><strong>Deliverables:</strong> {{deliverable_count}} content pieces</li>
                <li><strong>Timeline:</strong> {{timeline}}</li>
                <li><strong>Payment Schedule:</strong> {{payment_schedule_summary}}</li>
            </ul>
        </div>
        
        <h3>📎 Contract Attached</h3>
        <p>Please find your comprehensive partnership agreement attached as a PDF. Review all terms carefully and don't hesitate to reach out with any questions.</p>
        
        <a href="#" class="cta-button">📄 Download Contract PDF</a>
        
        <h3>🔄 Next Steps:</h3>
        <ol>
            <li>Review the attached contract thoroughly</li>
            <li>Sign and return within 48 hours</li>
            <li>Provide banking details for payment setup</li>
            <li>Receive product samples and creative brief</li>
            <li>Start creating amazing content!</li>
        </ol>
        
        <div class="highlight">
            <h4>📞 Questions or Support:</h4>
            <p>Email: <a href="mailto:partnerships@{{brand_domain}}">partnerships@{{brand_domain}}</a><br>
            Response time: Within 4 hours during business hours</p>
        </div>
        
        <p>We're excited to work together and create content that resonates with your audience!</p>
        
        <p>Best regards,<br>
        The {{brand_name}} Partnerships Team</p>
    </div>
    
    <div class="footer">
        <p>This email was sent by InfluencerFlow AI Platform<br>
        Contract ID: {{contract_id}} | Generated: {{timestamp}}</p>
        <p>© {{current_year}} {{brand_name}}. All rights reserved.</p>
    </div>
</body>
</html>
```

### Adding Custom Notification Channels

```python
# services/custom_notification_channel.py
from services.notifications import NotificationRequest
import requests

class TeamsNotificationChannel:
    """Microsoft Teams notification channel"""
    
    def __init__(self, config: Dict[str, Any]):
        self.webhook_url = config.get('teams_webhook_url')
        self.enabled = bool(self.webhook_url)
    
    async def send_notification(self, request: NotificationRequest) -> Dict[str, Any]:
        if not self.enabled:
            return {"status": "skipped", "reason": "teams_not_configured"}
        
        teams_payload = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "0076D7",
            "summary": request.subject,
            "sections": [{
                "activityTitle": request.subject,
                "activitySubtitle": f"Priority: {request.priority.value.title()}",
                "text": request.message,
                "facts": [
                    {"name": "Type", "value": request.type.value.title()},
                    {"name": "Recipient", "value": request.recipient},
                    {"name": "Time", "value": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                ]
            }]
        }
        
        try:
            response = requests.post(self.webhook_url, json=teams_payload, timeout=30)
            return {
                "status": "sent" if response.status_code == 200 else "failed",
                "channel": "teams"
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "channel": "teams"}
```

### Database Integration

```python
# services/enhanced_database.py
from sqlalchemy import create_engine, Column, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(String, primary_key=True)
    brand_name = Column(String, nullable=False)
    product_name = Column(String, nullable=False)
    total_budget = Column(Float, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)

class Contract(Base):
    __tablename__ = "contracts"
    
    id = Column(String, primary_key=True)
    campaign_id = Column(String, nullable=False)
    creator_id = Column(String, nullable=False)
    final_rate = Column(Float, nullable=False)
    contract_content = Column(String)
    email_status = Column(String)
    email_sent_at = Column(DateTime)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)

class EmailDelivery(Base):
    __tablename__ = "email_deliveries"
    
    id = Column(String, primary_key=True)
    contract_id = Column(String, nullable=False)
    recipient_email = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    delivery_status = Column(String, nullable=False)
    sent_at = Column(DateTime, nullable=False)
    delivered_at = Column(DateTime)
    metadata = Column(JSON)
```

## 🧪 Testing & Quality Assurance

### Running Tests
```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/test_email.py -v
pytest tests/test_notifications.py -v
pytest tests/test_agents.py -v

# Run with coverage
pytest --cov=. --cov-report=html

# Run integration tests
pytest tests/integration/ -v
```

### Test Email Configuration
```bash
# Test email service directly
python -c "
from services.email_service import EmailService
import asyncio

async def test():
    service = EmailService()
    result = await service.test_credentials()
    print(f'Email test: {result}')

asyncio.run(test())
"
```

### Performance Testing
```bash
# Install performance testing tools
pip install locust

# Run performance tests
locust -f tests/performance/test_campaign_load.py --host=http://localhost:8000
```

## 🚀 Production Deployment

### Docker Configuration
```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### Docker Compose with Services
```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/influencerflow
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - ./data:/app/data
      - ./templates:/app/templates

  notifications:
    build: .
    command: python services/notifications.py
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/influencerflow
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=influencerflow
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### Environment-Specific Configuration

**Production (.env.production):**
```bash
# Production Environment Configuration
DEBUG=false
DEMO_MODE=false
MOCK_CALLS=false

# Production API Keys
GROQ_API_KEY=gsk_production_key
ELEVENLABS_API_KEY=sk_production_key
ELEVENLABS_AGENT_ID=production_agent_id

# Production Email
EMAIL_USERNAME=partnerships@yourcompany.com
EMAIL_PASSWORD=secure_production_password
SMTP_SERVER=smtp.yourcompany.com
SENDER_NAME=YourCompany Partnerships

# Production Database
DATABASE_URL=postgresql://user:password@production-db:5432/influencerflow

# Production Monitoring
SENTRY_DSN=https://your-sentry-dsn
NEW_RELIC_LICENSE_KEY=your_newrelic_key

# Security
SECRET_KEY=your_super_secure_secret_key
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com
```

### Kubernetes Deployment
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: influencerflow-ai
spec:
  replicas: 3
  selector:
    matchLabels:
      app: influencerflow-ai
  template:
    metadata:
      labels:
        app: influencerflow-ai
    spec:
      containers:
      - name: app
        image: influencerflow/influencerflow-ai:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
        - name: GROQ_API_KEY
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: groq-api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: influencerflow-ai-service
spec:
  selector:
    app: influencerflow-ai
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

## 📊 Monitoring & Analytics

### Application Metrics

The platform provides comprehensive monitoring:

```python
# monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Campaign metrics
campaigns_started = Counter('campaigns_started_total', 'Total campaigns started')
campaigns_completed = Counter('campaigns_completed_total', 'Total campaigns completed')
negotiation_success_rate = Gauge('negotiation_success_rate', 'Current negotiation success rate')

# Email metrics
emails_sent = Counter('emails_sent_total', 'Total emails sent', ['type'])
email_delivery_rate = Gauge('email_delivery_rate', 'Email delivery success rate')

# Performance metrics
api_request_duration = Histogram('api_request_duration_seconds', 'API request duration')
voice_call_duration = Histogram('voice_call_duration_seconds', 'Voice call duration')
```

### Health Monitoring

```bash
# Health check endpoints
curl http://localhost:8000/health                    # Application health
curl http://localhost:8000/health/database           # Database connectivity
curl http://localhost:8000/health/email              # Email service status
curl http://localhost:8000/health/integrations       # External APIs status
```

### Logging Configuration

```python
# config/logging.py
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
```

## 🔒 Security & Compliance

### Security Features
- **API Key Encryption**: Secure storage of sensitive credentials
- **Input Validation**: Comprehensive data validation using Pydantic
- **Rate Limiting**: API rate limiting to prevent abuse
- **CORS Configuration**: Secure cross-origin resource sharing
- **Email Security**: SMTP with TLS encryption
- **Contract Security**: PDF generation with watermarks and metadata

### Data Privacy
- **GDPR Compliance**: Data retention and deletion policies
- **Creator Privacy**: Secure handling of creator contact information
- **Audit Logging**: Complete audit trail of all operations
- **Data Encryption**: Encryption at rest and in transit

### Compliance
- **FTC Guidelines**: Automated disclosure requirements in contracts
- **Platform Policies**: Compliance with social media platform guidelines
- **Financial Regulations**: Secure payment processing and reporting

## 🤝 Contributing

### Development Setup

1. **Fork and Clone**
```bash
git clone https://github.com/yourusername/influencerflow-ai.git
cd influencerflow-ai
```

2. **Install Development Dependencies**
```bash
uv sync --extra dev,notifications,documents,analytics
```

3. **Set Up Pre-commit Hooks**
```bash
pre-commit install
```

4. **Run Tests**
```bash
pytest tests/ -v
```

### Code Standards

- **Code Formatting**: Black (line length: 88)
- **Linting**: Flake8 with custom configuration
- **Type Checking**: MyPy for static type analysis
- **Documentation**: Docstrings for all public functions
- **Testing**: Minimum 80% test coverage required

### Pull Request Process

1. **Create Feature Branch**: `git checkout -b feature/your-feature-name`
2. **Write Tests**: Include comprehensive tests for new features
3. **Update Documentation**: Update README and API documentation
4. **Pass CI/CD**: Ensure all tests and checks pass
5. **Request Review**: Submit PR with detailed description

### Feature Roadmap

**Version 2.1.0:**
- [ ] Advanced analytics dashboard
- [ ] Multi-language support for negotiations
- [ ] Custom contract templates
- [ ] Advanced creator scoring algorithms

**Version 2.2.0:**
- [ ] Mobile app for creators
- [ ] Blockchain-based payments
- [ ] AI-powered content optimization
- [ ] Advanced performance predictions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **ElevenLabs** for conversational AI technology and real-time monitoring
- **Groq** for high-performance LLM inference and AI strategy generation
- **FastAPI** for the robust and modern web framework
- **Sentence Transformers** for semantic similarity matching
- **The Open Source Community** for various tools and libraries

## 📞 Support & Community

### Documentation
- **API Documentation**: `/docs` (when server is running)
- **Interactive API Explorer**: `/redoc` (when server is running)
- **Email Setup Guide**: `docs/email_setup.md`
- **Deployment Guide**: `docs/deployment_guide.md`

### Community
- **GitHub Issues**: [Report bugs and request features](https://github.com/influencerflow/influencerflow-ai/issues)
- **GitHub Discussions**: [Community discussions and support](https://github.com/influencerflow/influencerflow-ai/discussions)
- **Discord Server**: [Join our developer community](https://discord.gg/influencerflow)

### Enterprise Support
For enterprise deployments, custom integrations, and priority support:
- **Email**: enterprise@influencerflow.ai
- **Website**: https://enterprise.influencerflow.ai
- **Phone**: +1 (555) 123-FLOW

### Status Page
Monitor platform status and uptime: https://status.influencerflow.ai

---

**Built with ❤️ by the InfluencerFlow Team**

*InfluencerFlow AI Platform - Revolutionizing influencer marketing through artificial intelligence, voice technology, and intelligent automation.*