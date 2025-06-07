# InfluencerFlow AI Platform - Production Ready

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![ElevenLabs](https://img.shields.io/badge/ElevenLabs-API-purple.svg)](https://elevenlabs.io/)
[![Groq](https://img.shields.io/badge/Groq-AI-orange.svg)](https://groq.com/)
[![WhatsApp](https://img.shields.io/badge/WhatsApp-Business-25D366.svg)](https://developers.facebook.com/docs/whatsapp)

> **AI-Native Conversational Influencer Marketing Platform**

InfluencerFlow is a next-generation AI platform that runs complete influencer marketing campaigns through natural conversation. Users simply message their requirements via WhatsApp, and our AI handles everything from creator discovery to contract generation - no buttons, no forms, just outcomes.

## 🎯 Key Features

### 🤖 **Conversational AI Interface**
- **WhatsApp Business Integration**: Complete campaigns via natural conversation
- **LLM-Powered Parsing**: Groq-based natural language understanding
- **Multi-Turn Conversations**: Smart clarifying questions when needed
- **Real-Time Updates**: Live progress notifications during campaign execution

### 📞 **Voice-Based Negotiations**
- **ElevenLabs Integration**: Automated voice calls with dynamic variables
- **Structured Conversation Analysis**: Extract negotiation outcomes and terms
- **Real-Time Monitoring**: Live call progress tracking
- **Enhanced Voice Service**: Professional AI negotiator with market intelligence

### 🎛️ **Enhanced AI Orchestration**
- **Enhanced Campaign Orchestrator**: Master coordinator with conversation monitoring
- **Enhanced Negotiation Agent**: Voice-based deal closing with structured analysis
- **Enhanced Contract Agent**: Comprehensive legal document generation
- **Discovery Agent**: AI-powered creator matching with vector similarity

### 📊 **Production-Ready Analytics**
- **Real-Time Campaign Monitoring**: Live progress tracking via WhatsApp and API
- **Enhanced Validation Systems**: Comprehensive data quality checks
- **Structured Data Flow**: Complete audit trail from conversation to contract
- **Performance Metrics**: Success rates, cost efficiency, ROI analysis

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                InfluencerFlow AI Platform v2.1               │
├─────────────────────────────────────────────────────────────┤
│  FastAPI Backend (main.py) - Production Ready              │
│  ├── Enhanced Webhook Endpoints (/api/webhook/)            │
│  ├── Enhanced Monitoring (/api/monitor/)                   │
│  └── WhatsApp Business API (/api/whatsapp/)                │
├─────────────────────────────────────────────────────────────┤
│  Enhanced AI Agents (/agents/) - Production Only           │
│  ├── EnhancedCampaignOrchestrator (Master Coordinator)     │
│  ├── EnhancedNegotiationAgent (Voice + Analysis)           │
│  ├── EnhancedContractAgent (Comprehensive Legal Docs)      │
│  └── InfluencerDiscoveryAgent (Vector Similarity)          │
├─────────────────────────────────────────────────────────────┤
│  Enhanced Services (/services/) - Production Ready         │
│  ├── EnhancedVoiceService (ElevenLabs + Dynamic Variables) │
│  ├── ConversationMonitor (Real-time Status Tracking)       │
│  ├── EmbeddingService (Vector Similarity Matching)         │
│  └── PricingService (Market Intelligence)                  │
├─────────────────────────────────────────────────────────────┤
│  WhatsApp Integration (/api/whatsapp/) - NEW               │
│  ├── WhatsApp Business API (Message Handling)              │
│  ├── LLM Parser (Groq Natural Language Processing)         │
│  ├── Conversation State Management                         │
│  └── Orchestration Bridge (Triggers Enhanced Workflows)    │
├─────────────────────────────────────────────────────────────┤
│  External Integrations                                     │
│  ├── WhatsApp Business API (Conversational Interface)      │
│  ├── ElevenLabs API (Voice Conversations + Analysis)       │
│  ├── Groq API (LLM Strategy + Natural Language)            │
│  └── Sentence Transformers (ML Embeddings)                 │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.13+**
- **UV Package Manager** (or pip)
- **WhatsApp Business Account** with API access
- **ElevenLabs Account** with API key and agent setup
- **Groq Account** with API key
- **Meta Developer Account** for WhatsApp Business API

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
# AI Services (Required)
GROQ_API_KEY=gsk_your_groq_key_here
ELEVENLABS_API_KEY=sk_your_elevenlabs_key_here
ELEVENLABS_AGENT_ID=your_agent_id_here
ELEVENLABS_PHONE_NUMBER_ID=your_phone_number_here

# WhatsApp Business API (Required for Conversational Interface)
WHATSAPP_ACCESS_TOKEN=your_whatsapp_access_token_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id_here
WHATSAPP_APP_SECRET=your_app_secret_here
WHATSAPP_VERIFY_TOKEN=influencerflow_verify_token

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

## 💬 WhatsApp Integration Setup

### Meta Developer Console Setup

1. **Create WhatsApp Business App**
   - Go to https://developers.facebook.com/
   - Create App → Business → WhatsApp Business Platform
   - Add WhatsApp Product to your app

2. **Configure Webhook**
   - URL: `https://yourdomain.com/api/whatsapp/webhook`
   - Verify Token: `influencerflow_verify_token`
   - Subscribe to: `messages`

3. **Get Credentials**
   - Access Token (from WhatsApp > API Setup)
   - Phone Number ID (from WhatsApp > API Setup)
   - App Secret (from App Settings > Basic)

4. **Test Webhook**
```bash
# Verify webhook endpoint
curl "https://yourdomain.com/api/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=influencerflow_verify_token&hub.challenge=test"
```

### Using ngrok for Development

```bash
# Start your server
python main.py

# In another terminal, expose to internet
ngrok http 8000

# Use the ngrok URL in Meta Developer Console
# Webhook URL: https://abc123.ngrok.io/api/whatsapp/webhook
```

## 📡 API Reference

### WhatsApp Conversational Interface

**Natural Language Campaign Creation:**
```
User: "Get me 20 fitness creators, budget $15K for protein powder launch"
AI: "Got it! What's your target audience?"
User: "Gym enthusiasts aged 18-35, focus on muscle building"
AI: "Perfect! Launching your campaign now..."
```

**Campaign Status:**
```
User: "status"
AI: "📊 Campaign Status
🎯 Nike AF1 Campaign
📍 Stage: negotiations  
👥 Discovered: 8 creators
✅ Successful: 3 negotiations
💰 Cost so far: $12,400"
```

### Enhanced API Endpoints

#### Start Enhanced Campaign
```http
POST /api/webhook/enhanced-campaign
Content-Type: application/json

{
  "campaign_id": "unique-id",
  "product_name": "FitPro Tracker",
  "brand_name": "TechFit Solutions",
  "product_description": "AI-powered fitness tracking device",
  "target_audience": "Fitness enthusiasts aged 18-35",
  "campaign_goal": "Launch new product",
  "product_niche": "fitness",
  "total_budget": 15000.0
}
```

#### Monitor Campaign Progress
```http
GET /api/monitor/enhanced-campaign/{task_id}
```

#### WhatsApp Webhook
```http
POST /api/whatsapp/webhook
Content-Type: application/json

{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "entry_id",
      "changes": [
        {
          "value": {
            "messaging_product": "whatsapp",
            "metadata": {
              "phone_number_id": "your_phone_number_id"
            },
            "messages": [
              {
                "from": "user_phone_number",
                "type": "text",
                "text": {
                  "body": "Get me 20 fitness creators, budget $15K"
                }
              }
            ]
          },
          "field": "messages"
        }
      ]
    }
  ]
}
```

## 🎭 Usage Examples

### Conversational Campaign Creation

**Fitness Campaign:**
```
User: "I need creators for my new protein powder launch"
AI: "Great! I can help you find fitness creators. What's your budget and target audience?"
User: "Budget is $15K, targeting gym-goers aged 20-35"  
AI: "Perfect! How many creators are you looking for?"
User: "Around 20 creators"
AI: "🚀 Launching your campaign: Protein Powder Launch, $15K budget, 20 fitness creators targeting gym-goers 20-35..."
```

**Tech Campaign:**
```
User: "Find me tech reviewers for iPhone campaign, budget $25K, target Gen-Z"
AI: "🚀 Got it! Launching tech reviewer campaign:
📱 iPhone Campaign  
💰 Budget: $25,000
🎯 Target: Gen-Z
🔍 Finding tech reviewers now..."
```

### Real-Time Updates

```
AI: "🔍 Discovery Phase: Found 12 potential creators in your niche..."
AI: "💬 Negotiation Phase: Starting outreach to top 8 creators..."
AI: "📋 Approval Needed: 5 creators responded positively:
1. TechReviewer_Sarah (500K followers) - $4,500
2. Mike_Fitness (300K followers) - $3,200
...
Reply with numbers to approve (e.g., '1,3,5')"
User: "1,2,4,5"
AI: "✅ Approved! Proceeding with 4 creators. Generating contracts..."
AI: "🎉 Campaign Complete! 4 successful partnerships, $14,200 total cost"
```

## 🛠️ Development Guide

### Project Structure (Post-Cleanup)
```
influencer-ai-backend/
├── main.py                          # FastAPI application - production ready
├── config/
│   └── settings.py                  # Environment configuration
├── models/
│   ├── campaign.py                  # Core data models
│   └── whatsapp.py                  # WhatsApp message models
├── agents/                          # Enhanced AI Agents (Production Only)
│   ├── enhanced_orchestrator.py     # Master campaign coordinator
│   ├── enhanced_negotiation.py      # Voice negotiations + analysis
│   ├── enhanced_contracts.py        # Comprehensive contract generation
│   └── discovery.py                 # Creator discovery and matching
├── services/                        # Enhanced Services (Production Only)
│   ├── enhanced_voice.py            # ElevenLabs with dynamic variables
│   ├── conversation_monitor.py      # Real-time conversation tracking
│   ├── embeddings.py                # ML similarity matching
│   ├── pricing.py                   # Market pricing intelligence
│   └── database.py                  # Data persistence
├── api/                             # Enhanced API Endpoints
│   ├── enhanced_webhooks.py         # Campaign webhook endpoints
│   ├── enhanced_monitoring.py       # Real-time progress monitoring
│   └── whatsapp/                    # WhatsApp Business Integration
│       ├── webhooks.py              # WhatsApp webhook handling
│       ├── enhanced_message_handler.py # LLM conversation logic
│       ├── llm_parser.py            # Groq natural language processing
│       ├── response_service.py      # Send WhatsApp messages
│       ├── conversation_state.py    # Track conversation state
│       └── orchestration_bridge.py  # Connect to enhanced workflows
└── data/                            # Static data files
    ├── creators.json                # Creator database
    └── market_data.json             # Market pricing data
```

### Adding New Conversational Features

#### 1. Extend LLM Parser
```python
# api/whatsapp/llm_parser.py
async def parse_campaign_request(self, user_message: str):
    # Add new parameter extraction logic
    # Update system prompt for new campaign types
```

#### 2. Add Conversation State
```python
# api/whatsapp/conversation_state.py  
@dataclass
class ConversationState:
    # Add new conversation stages
    stage: str  # "campaign_input", "approval_pending", "new_stage"
```

#### 3. Extend Message Handler
```python
# api/whatsapp/enhanced_message_handler.py
async def process_message(self, message, phone_number_id):
    # Add new conversation flow handling
```

### Testing

#### Test Conversational Interface
```bash
# Test LLM parsing
python -c "
import asyncio
from api.whatsapp.llm_parser import WhatsAppCampaignParser

async def test():
    parser = WhatsAppCampaignParser()
    result = await parser.parse_campaign_request(
        'Get me 20 fitness creators, budget \$15K for protein powder'
    )
    print(result)

asyncio.run(test())
"

# Test WhatsApp webhook
curl -X POST http://localhost:8000/api/whatsapp/webhook \
  -H "Content-Type: application/json" \
  -d '{"test": "message"}'
```

#### Test Enhanced Campaigns
```bash
# Test enhanced campaign endpoint
curl -X POST http://localhost:8000/api/webhook/test-enhanced-campaign

# Test ElevenLabs integration
curl -X GET http://localhost:8000/api/webhook/test-enhanced-elevenlabs

# Test system status
curl -X GET http://localhost:8000/api/webhook/system-status
```

## 🔍 Troubleshooting

### WhatsApp Integration Issues

#### Webhook Verification Failed
```bash
# Check webhook endpoint
curl "http://localhost:8000/api/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=influencerflow_verify_token&hub.challenge=test"

# Should return the challenge value
```

**Solutions:**
- Verify `WHATSAPP_VERIFY_TOKEN` matches Meta Developer Console
- Ensure webhook URL is publicly accessible (use ngrok for development)
- Check webhook endpoint is responding to GET requests

#### WhatsApp Messages Not Received
**Solutions:**
- Verify webhook is subscribed to `messages` in Meta Developer Console
- Check `WHATSAPP_APP_SECRET` for signature verification
- Ensure phone number is added to WhatsApp Business API
- Check server logs for webhook processing errors

#### LLM Parsing Issues
**Solutions:**
- Verify `GROQ_API_KEY` is valid and has sufficient credits
- Check Groq API rate limits
- Review LLM parser system prompts for accuracy
- Test with simpler campaign requests first

### Enhanced Integration Issues

#### ElevenLabs Connection Failed
```bash
# Test credentials
curl -X GET http://localhost:8000/api/webhook/test-enhanced-elevenlabs
```

**Solutions:**
- Verify API keys in `.env` file
- Check ElevenLabs agent configuration
- Ensure dynamic variables are set up in ElevenLabs dashboard
- Verify phone number configuration

#### Enhanced Orchestrator Errors
**Solutions:**
- Check import statements use enhanced versions only
- Verify cleanup removed legacy files
- Test with simple campaign first
- Check logs for specific error details

## 📊 Monitoring & Analytics

### Real-time Monitoring

**WhatsApp Conversation Tracking:**
- User message received and parsed
- LLM processing and parameter extraction
- Campaign launch and orchestration progress
- Real-time updates sent back to user

**Enhanced Campaign Analytics:**
- Discovery phase: creator matching scores
- Negotiation phase: call success rates and analysis
- Contract phase: agreement generation and validation
- Completion: comprehensive campaign summary

### Performance Metrics

**Conversational Interface:**
- Message processing time
- LLM parsing accuracy
- Conversation completion rates
- User satisfaction scores

**Enhanced Workflows:**
- Campaign success rates
- Cost efficiency metrics
- Time to completion
- Contract generation quality

## 🤝 Contributing

### Development Setup

1. **Fork and Clone**
```bash
git clone https://github.com/your-username/influencer-ai-backend.git
cd influencer-ai-backend
```

2. **Install Development Dependencies**
```bash
uv add --dev pytest black flake8 mypy
```

3. **Set Up Pre-commit Hooks**
```bash
pre-commit install
```

4. **Run Tests**
```bash
pytest tests/
python test_cleanup.py  # Test post-cleanup functionality
```

### Code Standards

- **Enhanced Only**: Use only enhanced/production agents and services
- **Type Hints**: Add type annotations for new functions
- **Documentation**: Include docstrings for public methods
- **Testing**: Add tests for new conversational features
- **Logging**: Use structured logging with appropriate levels

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Meta/WhatsApp** for WhatsApp Business API
- **ElevenLabs** for conversational AI technology
- **Groq** for high-performance LLM inference
- **FastAPI** for the robust web framework
- **Sentence Transformers** for semantic similarity

## 📞 Support

### Documentation
- **API Documentation**: `/docs` (when server is running)
- **Interactive API**: `/redoc` (when server is running)

### Community
- **Issues**: [GitHub Issues](https://github.com/your-org/influencer-ai-backend/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/influencer-ai-backend/discussions)

### Enterprise Support
For enterprise support and custom implementations, contact: [support@influencerflow.ai](mailto:support@influencerflow.ai)

---

**Built with ❤️ by the InfluencerFlow Team - AI-Native, Conversation-First, Outcome-Driven**