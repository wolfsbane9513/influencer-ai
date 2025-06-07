# InfluencerFlow AI Platform

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![ElevenLabs](https://img.shields.io/badge/ElevenLabs-API-purple.svg)](https://elevenlabs.io/)
[![Groq](https://img.shields.io/badge/Groq-AI-orange.svg)](https://groq.com/)

> **🤖 Next-Generation AI-Powered Influencer Marketing Automation Platform**

InfluencerFlow is the most advanced AI platform for automating influencer marketing campaigns - from intelligent creator discovery to contract execution - using cutting-edge AI agents, voice-based negotiations, and human-in-the-loop workflows.

## 🌟 What's New in v2.0

### 🔥 **Enhanced AI Features**
- **Real-time Voice Negotiations**: ElevenLabs integration with dynamic variables and structured analysis
- **AI Strategy Generation**: Groq-powered campaign optimization and creator-specific strategies
- **Conversation Monitoring**: Live tracking of negotiations with automatic workflow continuation
- **Human-in-the-Loop**: Approval workflows with sponsor oversight and human review
- **Smart Contract Generation**: Multi-template system with automated delivery

### 📈 **Advanced Workflows**
- **Unified Campaign Orchestrator**: Complete end-to-end automation
- **Multi-Data Collection**: Manual, file upload, conversational AI, and API integration
- **Enhanced Monitoring**: Real-time analytics and comprehensive reporting
- **Legacy Compatibility**: Backward compatibility for existing integrations

## 🎯 Core Features

### 🤖 **AI-Powered Automation**
- **Intelligent Creator Discovery**: Vector similarity matching with sentence transformers
- **AI Strategy Generation**: Groq-powered campaign optimization with creator-specific approaches
- **Automated Negotiations**: ElevenLabs voice calls with dynamic variables and real-time analysis
- **Smart Contract Generation**: Multi-template system (Premium, Standard, Micro-Influencer)
- **Conversation Monitoring**: Real-time call tracking with automatic workflow continuation

### 📞 **Voice-Based Negotiations**
- **Real-time Phone Calls**: ElevenLabs conversational AI with timeout handling and retry logic
- **Dynamic Variables**: Personalized conversation context for each creator
- **Structured Analysis**: Extract negotiation outcomes, rates, and terms automatically
- **Live Monitoring**: Real-time progress tracking during calls with conversation status polling
- **Fallback Systems**: Mock mode for testing and graceful error handling

### 🎛️ **Multi-Agent Orchestration**
- **Enhanced Campaign Orchestrator**: Master coordinator with conversation monitoring integration
- **Discovery Agent**: AI-powered creator matching and scoring with budget optimization
- **Negotiation Agent**: Voice-based deal closing with structured data extraction
- **Contract Agent**: Automated legal document generation with multiple templates
- **Email Service**: Contract delivery and notification system

### 📊 **Advanced Analytics & Monitoring**
- **Real-time Monitoring**: Live campaign progress tracking with WebSocket-style updates
- **Performance Metrics**: Success rates, cost efficiency, ROI analysis with trend tracking
- **Validation Systems**: Comprehensive data quality checks and error handling
- **Human Review Queue**: Approval workflow management with escalation
- **Comprehensive Reporting**: Detailed campaign summaries and business insights

### 🔄 **Workflow Management**
- **Enhanced Workflows**: Full automation with AI decision-making
- **Legacy Workflows**: Backward compatibility for existing integrations
- **Data Collection**: Multiple methods (manual, file upload, conversational, API)
- **Approval Processes**: Human review and sponsor approval workflows
- **Contract Delivery**: Automated email delivery with multiple signing options

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    InfluencerFlow AI Platform v2.0                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  FastAPI Backend (main.py)                                                 │
│  ├── Enhanced API (/api/enhanced/) - Full AI automation                    │
│  ├── Legacy API (/api/legacy/) - Backward compatibility                    │
│  ├── Webhook Endpoints (/api/webhook/) - Campaign triggers                 │
│  └── Monitoring Endpoints (/api/monitor/) - Real-time tracking             │
├─────────────────────────────────────────────────────────────────────────────┤
│  Enhanced AI Agents (/agents/)                                             │
│  ├── UnifiedCampaignOrchestrator - Complete workflow automation            │
│  ├── EnhancedCampaignOrchestrator - AI strategy with conversation monitor  │
│  ├── EnhancedInfluencerMatcher - Budget-optimized selection               │
│  ├── EnhancedNegotiationManager - Human-in-the-loop workflows             │
│  ├── EnhancedContractGenerator - Multi-template system                     │
│  └── CampaignDataCollector - Multi-source data collection                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  Enhanced Services (/services/)                                            │
│  ├── EnhancedVoiceService - ElevenLabs with dynamic variables & monitoring │
│  ├── ConversationMonitor - Real-time call status tracking                  │
│  ├── EmailService - Contract delivery and notifications                    │
│  ├── EmbeddingService - Vector similarity matching                         │
│  ├── PricingService - Market intelligence and rate optimization            │
│  └── DatabaseService - Comprehensive data persistence                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  Advanced Features                                                         │
│  ├── Multi-Template Contracts (Premium, Standard, Micro-Influencer)       │
│  ├── Human Approval Workflows (Review, Sponsor, Escalation)               │
│  ├── Real-time Conversation Monitoring with Auto-continuation             │
│  ├── Enhanced Analytics and Reporting                                      │
│  └── Legacy Compatibility Layer                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  External Integrations                                                     │
│  ├── ElevenLabs API (Voice Conversations + Real-time Status)              │
│  ├── Groq API (AI Strategy & Analysis)                                     │
│  ├── Sentence Transformers (ML Embeddings)                                 │
│  ├── SMTP Email (Contract Delivery)                                        │
│  └── PostgreSQL (Data Storage)                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.13+**
- **UV Package Manager** (recommended) or pip
- **ElevenLabs Account** with API key (for voice features)
- **Groq Account** with API key (for AI strategy)
- **SMTP Email Account** (for contract delivery)
- **PostgreSQL** (optional, uses mock by default)

### Installation

1. **Clone the Repository**
```bash
git clone https://github.com/your-org/influencer-ai-backend.git
cd influencer-ai-backend
```

2. **Install Dependencies**
```bash
# Using UV (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

3. **Environment Configuration**
```bash
# Copy environment template
cp .env.template .env

# Edit .env with your API keys
nano .env
```

4. **Required Environment Variables**
```bash
# Core API Keys (Required for full functionality)
GROQ_API_KEY=gsk_your_groq_key_here
ELEVENLABS_API_KEY=sk_your_elevenlabs_key_here
ELEVENLABS_AGENT_ID=your_agent_id_here
ELEVENLABS_PHONE_NUMBER_ID=your_phone_number_here

# Email Configuration (Optional but recommended)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Configuration
DEMO_MODE=true
MOCK_CALLS=false
DEBUG=true
```

5. **Start the Server**
```bash
# Development mode
uvicorn main:app --reload

# Production mode
python main.py
```

6. **Verify Installation**
```bash
curl http://localhost:8000/health
```

## 🔧 Configuration Guide

### ElevenLabs Setup (Voice Negotiations)

1. **Create Account**: Sign up at [ElevenLabs](https://elevenlabs.io/)
2. **Get API Key**: Navigate to Settings → API Keys
3. **Create Agent**: Go to Conversational AI → Create New Agent
4. **Configure Dynamic Variables**: Add these variables in your agent:

```json
{
  "InfluencerProfile": "Creator profile with engagement metrics",
  "campaignBrief": "Brand and product information",
  "negotiationStrategy": "AI-generated approach and tactics",
  "budgetStrategy": "Pricing strategy with flexibility ranges"
}
```

5. **Phone Integration**: Set up Twilio phone number in ElevenLabs dashboard
6. **Test Setup**: Use `/api/webhook/test-enhanced-elevenlabs` endpoint

### Groq Configuration (AI Strategy)

1. **Create Account**: Sign up at [Groq](https://groq.com/)
2. **Get API Key**: Navigate to API Keys section
3. **Model Selection**: Platform uses `llama3-70b-8192` for strategy, `llama3-8b-8192` for decisions

### Email Configuration (Contract Delivery)

1. **SMTP Setup**: Configure your email provider (Gmail, Outlook, etc.)
2. **App Password**: Generate app-specific password for security
3. **Test Configuration**: Use email service test endpoint

### Data Setup

1. **Creator Database**: Ensure `data/creators.json` exists (sample provided)
2. **Market Data**: Ensure `data/market_data.json` exists (sample provided)
3. **Contract Templates**: Templates in `data/templates/` (Premium, Standard, Micro-Influencer)

## 📡 API Reference

### Enhanced API Endpoints (v2.0)

#### Unified Workflow Management
```http
POST /api/enhanced/start-enhanced-workflow
Content-Type: application/json

{
  "data_collection_method": "manual",
  "selection_strategy": "budget_optimized",
  "max_influencers": 3,
  "require_human_review": true,
  "require_sponsor_approval": true,
  "initial_data": {
    "product_name": "AI Fitness Tracker",
    "brand_name": "TechFit Pro",
    "total_budget": 15000.0
  }
}
```

#### Campaign Data Collection
```http
POST /api/enhanced/start-file-upload-workflow
POST /api/enhanced/start-conversational-workflow
```

#### Real-time Monitoring
```http
GET /api/enhanced/workflow/{workflow_id}/status
GET /api/enhanced/workflow/{workflow_id}/analytics
GET /api/enhanced/workflows
```

#### Human Review & Approval
```http
GET  /api/enhanced/human-reviews
POST /api/enhanced/human-review/{negotiation_id}/decision
GET  /api/enhanced/sponsor-approvals
POST /api/enhanced/sponsor-approval/{campaign_id}/{decision}
```

#### Contract Management
```http
GET  /api/enhanced/contracts
GET  /api/enhanced/contracts/{contract_id}
GET  /api/enhanced/contracts/{contract_id}/download
POST /api/enhanced/contracts/{contract_id}/mark-signed
```

### Enhanced Webhook Endpoints

#### Campaign Creation
```http
POST /api/webhook/enhanced-campaign
POST /api/webhook/test-enhanced-campaign
POST /api/webhook/test-enhanced-beauty-campaign
```

#### System Testing
```http
GET  /api/webhook/test-enhanced-elevenlabs
POST /api/webhook/test-enhanced-call
GET  /api/webhook/validate-negotiation/{conversation_id}
GET  /api/webhook/system-status
```

### Legacy API Endpoints (Backward Compatibility)

#### Basic Workflows
```http
POST /api/legacy/webhook/campaign-created
POST /api/legacy/webhook/test-campaign
GET  /api/legacy/webhook/status
```

#### Basic Monitoring
```http
GET /api/legacy/monitor/campaign/{task_id}
GET /api/legacy/monitor/campaigns
GET /api/legacy/monitor/campaign/{task_id}/summary
```

## 📚 Usage Examples

### 1. Enhanced Workflow with File Upload

```python
import requests

# Upload campaign data file
files = {'file': open('campaign_brief.csv', 'rb')}
data = {
    'selection_strategy': 'engagement_focused',
    'max_influencers': 4,
    'require_human_review': True
}

response = requests.post(
    "http://localhost:8000/api/enhanced/start-file-upload-workflow",
    files=files,
    data=data
)

workflow_id = response.json()["workflow_id"]
print(f"Workflow started: {workflow_id}")
```

### 2. Real-time Monitoring

```python
import requests
import time

def monitor_workflow(workflow_id):
    while True:
        response = requests.get(
            f"http://localhost:8000/api/enhanced/workflow/{workflow_id}/status"
        )
        data = response.json()
        
        print(f"Phase: {data['current_phase']}")
        print(f"Progress: {data['progress_percentage']:.1f}%")
        print(f"Influencers: {data['influencer_status']}")
        
        if data['is_complete']:
            print("Workflow completed!")
            break
            
        time.sleep(30)

monitor_workflow("your-workflow-id")
```

### 3. Human Review Process

```python
# Get pending reviews
reviews = requests.get("http://localhost:8000/api/enhanced/human-reviews").json()

for review in reviews["reviews"]:
    print(f"Review: {review['creator_name']}")
    print(f"AI Recommendation: {review['ai_recommendation']}")
    
    # Submit decision
    decision_data = {
        "decision": "approve",  # or "reject", "request_changes"
        "notes": "Looks good for brand alignment"
    }
    
    requests.post(
        f"http://localhost:8000/api/enhanced/human-review/{review['negotiation_id']}/decision",
        json=decision_data
    )
```

### 4. Contract Management

```python
# Get all contracts
contracts = requests.get("http://localhost:8000/api/enhanced/contracts").json()

for contract in contracts["contracts"]:
    print(f"Contract: {contract['contract_id']}")
    print(f"Status: {contract['status']}")
    print(f"Value: ${contract['final_rate']:,}")
    
    # Download contract
    if contract['status'] == 'sent':
        pdf_response = requests.get(
            f"http://localhost:8000/api/enhanced/contracts/{contract['contract_id']}/download"
        )
        
        with open(f"contract_{contract['contract_id']}.pdf", 'wb') as f:
            f.write(pdf_response.content)
```

## 🛠️ Development Guide

### Project Structure
```
influencer-ai-backend/
├── main.py                           # FastAPI application entry point
├── config/
│   ├── settings.py                   # Configuration management
│   └── simple_settings.py            # Fallback configuration
├── models/
│   ├── campaign.py                   # Core data models
│   └── workflow.py                   # Workflow management models
├── agents/                           # AI agent implementations
│   ├── enhanced_orchestrator.py     # Enhanced campaign coordinator
│   ├── unified_campaign_orchestrator.py # Complete automation
│   ├── enhanced_influencer_matcher.py   # Budget-optimized selection
│   ├── enhanced_negotiation_manager.py  # Human-in-the-loop negotiations
│   ├── enhanced_contract_generator.py   # Multi-template contracts
│   ├── campaign_data_collector.py    # Multi-source data collection
│   └── discovery.py                  # Creator discovery and matching
├── services/                         # External service integrations
│   ├── enhanced_voice.py             # ElevenLabs integration
│   ├── conversation_monitor.py       # Real-time call tracking
│   ├── email_service.py              # Contract delivery system
│   ├── embeddings.py                 # ML embeddings service
│   ├── pricing.py                    # Market pricing intelligence
│   └── database.py                   # Data persistence
├── api/                              # API route handlers
│   ├── enhanced_campaign_endpoints.py # Enhanced workflow APIs
│   ├── enhanced_webhooks.py          # Enhanced webhook handlers
│   ├── enhanced_monitoring.py        # Real-time monitoring APIs
│   ├── webhooks.py                   # Legacy webhook handlers
│   └── monitoring.py                 # Legacy monitoring APIs
├── data/                             # Static data and templates
│   ├── creators.json                 # Creator database
│   ├── market_data.json              # Market pricing data
│   └── templates/                    # Contract templates
│       ├── premium_contract.html
│       ├── standard_contract.html
│       └── micro_influencer_contract.html
└── tests/                            # Test files
```

### Adding Enhanced Features

#### 1. Create New Enhanced Agent
```python
# agents/my_enhanced_agent.py
import logging
from typing import Dict, Any
from models.campaign import CampaignData

logger = logging.getLogger(__name__)

class MyEnhancedAgent:
    """Enhanced agent with AI capabilities"""
    
    def __init__(self):
        self.ai_enabled = True
        self.monitoring_enabled = True
    
    async def process_with_ai(self, data: CampaignData) -> Dict[str, Any]:
        """Process with AI enhancement"""
        logger.info("Processing with enhanced AI capabilities")
        
        # AI processing logic here
        return {
            "status": "enhanced_processing_complete",
            "ai_insights": {"confidence": 0.95},
            "result": data
        }
```

#### 2. Add Enhanced Service Integration
```python
# services/my_enhanced_service.py
import asyncio
from typing import Dict, Any

class MyEnhancedService:
    """Enhanced service with real-time capabilities"""
    
    def __init__(self):
        self.real_time_enabled = True
        self.monitoring_active = False
    
    async def start_enhanced_monitoring(self, callback):
        """Start real-time monitoring"""
        self.monitoring_active = True
        
        while self.monitoring_active:
            # Real-time monitoring logic
            status = await self.check_status()
            if callback:
                await callback(status)
            await asyncio.sleep(10)
    
    async def check_status(self) -> Dict[str, Any]:
        """Enhanced status checking"""
        return {"status": "operational", "enhanced": True}
```

#### 3. Extend Enhanced Orchestrator
```python
# In agents/enhanced_orchestrator.py
async def _run_my_enhanced_phase(self, state):
    """Add custom enhanced phase"""
    logger.info("🔄 Starting my enhanced phase...")
    
    my_agent = MyEnhancedAgent()
    result = await my_agent.process_with_ai(state.campaign_data)
    
    # Update state with AI insights
    state.ai_insights = result["ai_insights"]
    
    logger.info("✅ Enhanced phase completed with AI")
```

### Enhanced Testing

#### Run Comprehensive Tests
```bash
# Test enhanced features
python -m pytest tests/test_enhanced_agents.py

# Test voice integration
curl -X GET http://localhost:8000/api/webhook/test-enhanced-elevenlabs

# Test enhanced workflow
curl -X POST http://localhost:8000/api/enhanced/demo/fitness-campaign

# Test human review system
curl -X GET http://localhost:8000/api/enhanced/human-reviews
```

#### Performance Testing
```bash
# Load test enhanced endpoints
python tests/load_test_enhanced.py

# Monitor real-time performance
curl -X GET http://localhost:8000/api/enhanced/system-status
```

## 🔍 Troubleshooting

### Common Issues

#### 1. ElevenLabs Connection Issues
```bash
# Test credentials and setup
curl -X GET http://localhost:8000/api/webhook/test-enhanced-elevenlabs

# Check configuration
python -c "from config.settings import settings; print('ElevenLabs:', bool(settings.elevenlabs_api_key))"
```

**Solutions:**
- Verify API keys in `.env` file
- Check ElevenLabs agent configuration
- Ensure dynamic variables are set up
- Test with mock mode first

#### 2. Groq AI Strategy Issues
```bash
# Test Groq connection
curl -X POST http://localhost:8000/api/enhanced/demo/fitness-campaign
```

**Solutions:**
- Verify Groq API key
- Check model availability and credits
- Review rate limits
- Test with fallback strategies

#### 3. Enhanced Workflow Failures
```bash
# Check workflow status
curl -X GET http://localhost:8000/api/enhanced/workflow/{id}/status

# Review system status
curl -X GET http://localhost:8000/api/enhanced/system-status
```

**Solutions:**
- Check all service dependencies
- Verify conversation monitoring setup
- Review human approval queues
- Test individual components

#### 4. Contract Generation Issues
```bash
# Test contract system
curl -X GET http://localhost:8000/api/enhanced/contracts

# Check email service
python -c "from services.email_service import EmailService; svc = EmailService(); print(svc.test_email_configuration())"
```

**Solutions:**
- Verify email SMTP configuration
- Check contract template files
- Test PDF generation
- Review delivery settings

### Debug Mode

Enable comprehensive logging:
```python
# In config/settings.py
DEBUG=true

# Or environment variable
export DEBUG=true
export LOG_LEVEL=debug
```

### Enhanced Health Checks

```bash
# Comprehensive system health
curl http://localhost:8000/health

# Enhanced feature status
curl http://localhost:8000/api-status

# Service-specific status
curl http://localhost:8000/api/enhanced/system-status
```

## 📊 Monitoring & Analytics

### Real-time Enhanced Monitoring

#### Campaign Progress Tracking
- **Enhanced Discovery**: AI-powered matching with confidence scores
- **Live Negotiations**: Real-time call monitoring with automatic continuation
- **Human Review**: Queue management with escalation and approval tracking
- **Contract Pipeline**: Multi-template generation with delivery confirmation

#### Advanced Performance Metrics
- **AI Strategy Effectiveness**: Success rate by strategy type and creator segment
- **Conversation Quality**: Call success rates, duration analysis, outcome prediction
- **Human Review Efficiency**: Approval times, escalation rates, decision quality
- **Contract Completion**: Signing rates, delivery success, follow-up effectiveness

#### Enhanced Analytics Dashboard
```bash
# Workflow analytics
GET /api/enhanced/workflow/{id}/analytics

# System-wide metrics
GET /api/enhanced/workflows

# Contract analytics
GET /api/enhanced/contracts

# Human review metrics
GET /api/enhanced/human-reviews
```

## 🎮 Demo & Testing

### Enhanced Demo Campaigns

```bash
# Fitness campaign with enhanced features
curl -X POST http://localhost:8000/api/enhanced/demo/fitness-campaign

# Beauty campaign with file upload simulation
curl -X POST http://localhost:8000/api/enhanced/demo/beauty-campaign

# Test enhanced ElevenLabs integration
curl -X POST http://localhost:8000/api/webhook/test-enhanced-call
```

### Testing Enhanced Features

```bash
# Test conversation monitoring
curl -X GET http://localhost:8000/api/webhook/test-timeout-fixes

# Test enhanced workflow with fixes
curl -X POST http://localhost:8000/api/webhook/test-enhanced-campaign-with-fixes

# Test human review system
curl -X GET http://localhost:8000/api/enhanced/human-reviews

# Test contract generation
curl -X POST http://localhost:8000/api/webhook/generate-enhanced-contract
```

## 🤝 Contributing

### Development Setup

1. **Fork Repository & Create Feature Branch**
```bash
git checkout -b feature/enhanced-feature-name
```

2. **Install Development Dependencies**
```bash
uv add --dev pytest black flake8 mypy
```

3. **Enhanced Development Guidelines**
- Follow existing enhanced agent patterns
- Include comprehensive error handling
- Add real-time monitoring capabilities
- Implement human-in-the-loop where appropriate
- Include AI strategy integration

4. **Testing Requirements**
```bash
# Test enhanced features
pytest tests/test_enhanced_*.py

# Test legacy compatibility
pytest tests/test_legacy_*.py

# Format code
black .

# Type checking
mypy .
```

### Enhanced Contribution Guidelines

- **Enhanced Features**: Follow the enhanced agent pattern with AI integration
- **Real-time Capabilities**: Include monitoring and live updates
- **Human Workflows**: Consider approval and review processes
- **Legacy Compatibility**: Ensure backward compatibility where needed
- **Documentation**: Update README and add endpoint documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **ElevenLabs** for conversational AI and real-time voice technology
- **Groq** for high-performance LLM inference and AI strategy generation
- **FastAPI** for the robust and fast web framework
- **Sentence Transformers** for semantic similarity and creator matching
- **The Open Source Community** for tools, libraries, and inspiration

## 📞 Support & Documentation

### Enhanced Documentation
- **API Documentation**: `/docs` (when server is running)
- **Interactive API**: `/redoc` (when server is running)
- **Enhanced Features Guide**: See API documentation for detailed enhanced endpoints

### Community & Support
- **Issues**: [GitHub Issues](https://github.com/your-org/influencer-ai-backend/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/influencer-ai-backend/discussions)
- **Enhanced Features**: Check `/api/enhanced/system-status` for feature availability

### Enterprise & Custom Solutions
For enterprise support, custom enhanced features, and professional services:
- **Email**: [support@influencerflow.ai](mailto:support@influencerflow.ai)
- **Enhanced Features**: Custom AI strategies, advanced integrations, white-label solutions

---

**Built with ❤️ and 🤖 AI by the InfluencerFlow Team**

*Transforming influencer marketing through intelligent automation and human-AI collaboration.*