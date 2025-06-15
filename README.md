# InfluencerFlow AI Platform

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![ElevenLabs](https://img.shields.io/badge/ElevenLabs-API-purple.svg)](https://elevenlabs.io/)
[![Groq](https://img.shields.io/badge/Groq-AI-orange.svg)](https://groq.com/)

> **AI-Powered Influencer Marketing Campaign Automation Platform**

InfluencerFlow is a comprehensive AI platform that automates the entire influencer marketing workflow - from creator discovery to contract generation - using advanced AI agents, voice-based negotiations, and intelligent matching algorithms.

## 🎯 Key Features

### 🤖 **AI-Powered Automation**
- **Intelligent Creator Discovery**: Vector similarity matching with sentence transformers
- **AI Strategy Generation**: Groq-powered campaign optimization
- **Automated Negotiations**: ElevenLabs voice calls with dynamic variables
- **Smart Contract Generation**: Comprehensive legal agreements with structured terms

### 📞 **Voice-Based Negotiations**
- **Real-time Phone Calls**: ElevenLabs conversational AI integration
- **Dynamic Variables**: Personalized conversation context for each creator
- **Structured Analysis**: Extract negotiation outcomes, rates, and terms
- **Live Monitoring**: Real-time progress tracking during calls

### 🎛️ **Multi-Agent Orchestration**
- **Campaign Orchestrator**: Master coordinator managing entire workflow
- **Discovery Agent**: AI-powered creator matching and scoring
- **Negotiation Agent**: Voice-based deal closing with market intelligence
- **Contract Agent**: Automated legal document generation

### 📊 **Advanced Analytics**
- **Real-time Monitoring**: Live campaign progress tracking
- **Performance Metrics**: Success rates, cost efficiency, ROI analysis
- **Validation Systems**: Data quality checks and error handling
- **Comprehensive Reporting**: Detailed campaign summaries and insights

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    InfluencerFlow AI Platform                │
├─────────────────────────────────────────────────────────────┤
│  FastAPI Backend (main.py)                                 │
│  ├── Webhook Endpoints (/api/webhook/)                     │
│  ├── Monitoring Endpoints (/api/monitor/)                  │
│  └── Enhanced Endpoints (/api/webhook/enhanced-*)          │
├─────────────────────────────────────────────────────────────┤
│  AI Agents (/agents/)                                      │
│  ├── CampaignOrchestrator (Master Coordinator)             │
│  ├── InfluencerDiscoveryAgent (Creator Matching)           │
│  ├── NegotiationAgent (Voice Negotiations)                 │
│  └── ContractAgent (Legal Document Generation)             │
├─────────────────────────────────────────────────────────────┤
│  Services (/services/)                                     │
│  ├── EnhancedVoiceService (ElevenLabs Integration)         │
│  ├── EmbeddingService (Vector Similarity)                  │
│  ├── PricingService (Market Data & Rates)                  │
│  └── DatabaseService (Data Persistence)                    │
├─────────────────────────────────────────────────────────────┤
│  External Integrations                                     │
│  ├── ElevenLabs API (Voice Conversations)                  │
│  ├── Groq API (AI Strategy & Analysis)                     │
│  ├── Sentence Transformers (ML Embeddings)                 │
│  └── PostgreSQL (Data Storage)                             │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.13+**
- **UV Package Manager** (or pip)
- **ElevenLabs Account** with API key
- **Groq Account** with API key
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
# Create a `.env` file and add your API keys
nano .env
```

4. **Required Environment Variables**
```bash
# API Keys (Required)
GROQ_API_KEY=gsk_your_groq_key_here
ELEVENLABS_API_KEY=sk_your_elevenlabs_key_here
ELEVENLABS_AGENT_ID=your_agent_id_here
ELEVENLABS_PHONE_NUMBER_ID=your_phone_number_here

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

### ElevenLabs Setup

1. **Create Account**: Sign up at [ElevenLabs](https://elevenlabs.io/)
2. **Get API Key**: Navigate to Settings → API Keys
3. **Create Agent**: Go to Conversational AI → Create New Agent
4. **Configure Dynamic Variables**: Add the following variables in your agent:

```json
{
  "InfluencerProfile": "name:Creator, niche:fitness, followers:250K, engagement:5.8%",
  "campaignBrief": "brand_name:TechFit, product_name:Fitness Tracker",
  "negotiationStrategy": "approach:collaborative, matchReasons:[...]",
  "budgetStrategy": "initialOffer:4200, maxOffer:5500"
}
```

5. **Phone Integration**: Set up Twilio phone number in ElevenLabs

### Groq Configuration

1. **Create Account**: Sign up at [Groq](https://groq.com/)
2. **Get API Key**: Navigate to API Keys section
3. **Choose Model**: Platform uses `llama3-70b-8192` for strategy, `llama3-8b-8192` for quick decisions

### Data Setup

1. **Creator Database**: Place `creators.json` in `/data/` folder
2. **Market Data**: Place `market_data.json` in `/data/` folder
3. **Sample files are provided in the repository**

## 📡 API Reference

### Webhook Endpoints

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

#### Test Endpoints
```http
POST /api/webhook/test-enhanced-campaign     # Create test campaign
GET  /api/webhook/test-enhanced-elevenlabs   # Test ElevenLabs setup
POST /api/webhook/test-enhanced-call         # Test actual phone call
GET  /api/webhook/system-status              # System health check
```

### Response Examples

#### Campaign Started Response
```json
{
  "message": "🎯 Enhanced AI campaign workflow started",
  "task_id": "uuid-task-id",
  "campaign_id": "campaign-id",
  "estimated_duration_minutes": 8,
  "monitor_url": "/api/monitor/enhanced-campaign/uuid-task-id",
  "status": "started",
  "enhancements": [
    "ElevenLabs dynamic variables integration",
    "Structured conversation analysis",
    "AI-powered negotiation strategies"
  ]
}
```

#### Progress Monitoring Response
```json
{
  "task_id": "uuid-task-id",
  "current_stage": "negotiations",
  "progress": {
    "overall_percentage": 45.0,
    "discovered_influencers": 3,
    "completed_negotiations": 1,
    "successful_negotiations": 1
  },
  "real_time_analytics": {
    "success_rate": 100.0,
    "average_final_rate": 4800.0,
    "budget_utilization": 32.0
  },
  "live_updates": [
    "✅ Successful negotiation: mike_fitness - $4,800",
    "📞 Enhanced call in progress: sarah_tech"
  ]
}
```

## 🎭 Usage Examples

### Basic Campaign Workflow

1. **Start Campaign**
```bash
curl -X POST http://localhost:8000/api/webhook/test-enhanced-campaign
```

2. **Monitor Progress**
```bash
curl -X GET http://localhost:8000/api/monitor/enhanced-campaign/{task_id}
```

3. **Get Final Results**
```bash
curl -X GET http://localhost:8000/api/monitor/enhanced-campaign/{task_id}/detailed-summary
```

### Custom Campaign
```python
import requests

campaign_data = {
    "campaign_id": "custom-campaign-001",
    "product_name": "Smart Water Bottle",
    "brand_name": "HydroTech",
    "product_description": "IoT-enabled water bottle with hydration tracking",
    "target_audience": "Health-conscious millennials and athletes",
    "campaign_goal": "Drive pre-orders for product launch",
    "product_niche": "fitness",
    "total_budget": 12000.0
}

response = requests.post(
    "http://localhost:8000/api/webhook/enhanced-campaign",
    json=campaign_data
)

task_id = response.json()["task_id"]
print(f"Campaign started: {task_id}")
```

### Real-time Monitoring
```python
import requests
import time

def monitor_campaign(task_id):
    while True:
        response = requests.get(f"http://localhost:8000/api/monitor/enhanced-campaign/{task_id}")
        data = response.json()
        
        print(f"Stage: {data['current_stage']}")
        print(f"Progress: {data['progress']['overall_percentage']:.1f}%")
        
        if data['is_complete']:
            print("Campaign completed!")
            break
            
        time.sleep(30)  # Check every 30 seconds

monitor_campaign("your-task-id")
```

## 🛠️ Development Guide

### Project Structure
```
influencer-ai-backend/
├── main.py                 # FastAPI application entry point
├── config/
│   └── settings.py         # Configuration management
├── models/
│   └── campaign.py         # Data models and schemas
├── agents/                 # AI agent implementations
│   ├── orchestrator.py     # Master campaign coordinator
│   ├── discovery.py        # Creator discovery and matching
│   ├── negotiation.py      # Voice-based negotiations
│   └── contracts.py        # Contract generation
├── services/               # External service integrations
│   ├── enhanced_voice.py   # ElevenLabs integration
│   ├── embeddings.py       # ML embeddings service
│   ├── pricing.py          # Market pricing logic
│   └── database.py         # Data persistence
├── api/                    # API route handlers
│   ├── webhooks.py         # Campaign webhook endpoints
│   └── monitoring.py       # Progress monitoring endpoints
├── data/                   # Static data files
│   ├── creators.json       # Creator database
│   └── market_data.json    # Market pricing data
├── end_to_end_test.py      # End-to-end workflow test
```

### Adding New Features

#### 1. Create New Agent
```python
# agents/my_new_agent.py
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class MyNewAgent:
    """Custom agent for specialized functionality"""
    
    def __init__(self):
        self.initialized = True
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data according to agent logic"""
        logger.info("Processing with MyNewAgent")
        # Your logic here
        return {"status": "processed", "result": data}
```

#### 2. Add Service Integration
```python
# services/my_service.py
import requests
from config.settings import settings

class MyService:
    """Integration with external service"""
    
    def __init__(self):
        self.api_key = settings.my_service_api_key
        self.base_url = "https://api.myservice.com"
    
    async def call_api(self, data):
        """Make API call to external service"""
        response = requests.post(
            f"{self.base_url}/endpoint",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json=data
        )
        return response.json()
```

#### 3. Extend Orchestrator
```python
# In agents/orchestrator.py, add new phase
async def _run_my_new_phase(self, state):
    """Add custom processing phase"""
    logger.info("🔄 Starting my new phase...")
    
    my_agent = MyNewAgent()
    result = await my_agent.process(state.campaign_data)
    
    # Update state with results
    state.my_new_data = result
    
    logger.info("✅ My new phase completed")
```

### Testing

#### Run Tests
```bash
# Run any available unit tests
python -m pytest

# Run with coverage
python -m pytest --cov=.
```

#### Test Campaign
```bash
# Quick system test
python end_to_end_test.py

# Test enhanced workflow
curl -X POST http://localhost:8000/api/webhook/test-enhanced-campaign

# Test ElevenLabs integration
curl -X GET http://localhost:8000/api/webhook/test-enhanced-elevenlabs
```

### Performance Optimization

#### Database Optimization
```python
# Use connection pooling
from sqlalchemy.pool import QueuePool

engine = create_engine(
    database_url,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

#### Async Processing
```python
# Use asyncio for concurrent operations
import asyncio

async def process_multiple_creators(creators):
    tasks = [
        negotiate_with_creator(creator) 
        for creator in creators
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

## 🔍 Troubleshooting

### Common Issues

#### 1. ElevenLabs Connection Failed
```bash
# Check credentials
curl -X GET http://localhost:8000/api/webhook/test-enhanced-elevenlabs

# Verify environment variables
python debug_env.py
```

**Solutions:**
- Verify API keys in `.env` file
- Check ElevenLabs account status
- Ensure agent is properly configured
- Verify phone number setup

#### 2. Groq API Errors
```bash
# Test Groq connection
python -c "from config.settings import settings; print(settings.groq_api_key[:10])"
```

**Solutions:**
- Check API key validity
- Verify model availability
- Check rate limits
- Ensure sufficient credits

#### 3. Import Errors
```bash
# Fix dependencies
python fix_imports.py

# Check Python version
python --version  # Should be 3.13+
```

**Solutions:**
- Run `uv sync` or `pip install -r requirements.txt`
- Check Python version compatibility
- Verify virtual environment activation

#### 4. Mock Mode Issues
```bash
# Check system status
curl http://localhost:8000/api/webhook/system-status
```

**Solutions:**
- Set `MOCK_CALLS=true` in `.env` for testing
- Verify creator data files exist in `/data/`
- Check demo mode configuration

### Debug Mode

Enable detailed logging:
```python
# In config/settings.py
DEBUG=true

# Or set environment variable
export DEBUG=true
```

### Health Checks

```bash
# System health
curl http://localhost:8000/health

# Service status
curl http://localhost:8000/api/webhook/system-status

# Test endpoints
curl -X POST http://localhost:8000/api/webhook/test-enhanced-campaign
```

## 📊 Monitoring & Analytics

### Real-time Monitoring

The platform provides comprehensive real-time monitoring:

#### Campaign Progress
- **Discovery Phase**: Creator matching and scoring
- **Negotiation Phase**: Live phone call progress
- **Contract Phase**: Document generation
- **Completion**: Final results and analytics

#### Performance Metrics
- **Success Rate**: Percentage of successful negotiations
- **Cost Efficiency**: Budget utilization and ROI
- **Time Efficiency**: Average campaign completion time
- **Quality Score**: Data completeness and validation

#### Live Updates
- Real-time progress notifications
- Call status updates
- Error tracking and alerts
- Performance trend analysis

### Analytics Dashboard

Access comprehensive analytics:
```bash
# Campaign summary
GET /api/monitor/enhanced-campaign/{task_id}/detailed-summary

# System-wide metrics
GET /api/monitor/campaigns

# Export data
GET /api/monitor/enhanced-campaign/{task_id}/export
```

## 🤝 Contributing

### Development Setup

1. **Fork the Repository**
2. **Create Feature Branch**
```bash
git checkout -b feature/your-feature-name
```

3. **Install Development Dependencies**
```bash
uv add --dev pytest black flake8
```

4. **Follow Code Style**
```bash
# Format code
black .

# Check linting
flake8 .

# Run tests
pytest
```

### Contribution Guidelines

- **Code Quality**: Follow PEP 8 standards
- **Documentation**: Add docstrings and comments
- **Testing**: Include unit tests for new features
- **Logging**: Use structured logging with appropriate levels
- **Error Handling**: Implement proper exception handling

### Pull Request Process

1. **Update Documentation**: Include README updates if needed
2. **Add Tests**: Ensure new features have test coverage
3. **Check CI**: Verify all tests pass
4. **Review**: Submit PR for review

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **ElevenLabs** for conversational AI technology
- **Groq** for high-performance LLM inference
- **FastAPI** for the robust web framework
- **Sentence Transformers** for semantic similarity
- **The Open Source Community** for various tools and libraries

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

**Built with ❤️ by the InfluencerFlow Team**