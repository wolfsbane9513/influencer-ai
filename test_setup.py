# test_setup.py
"""
Quick test script to verify the basic setup is working
Run this before moving to the next phase
"""

import asyncio
import json
from pathlib import Path

# Test imports
try:
    from config.settings import settings
    from models.campaign import CampaignWebhook, CampaignData,Creator
    from agents.orchestrator import CampaignOrchestrator
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)

def test_configuration():
    """Test configuration loading"""
    print("\n🔧 Testing Configuration...")
    print(f"  Demo mode: {settings.demo_mode}")
    print(f"  Mock calls: {settings.mock_calls}")
    print(f"  Max negotiation duration: {settings.max_negotiation_duration}s")
    print(f"  Groq API key configured: {'Yes' if settings.groq_api_key else 'No'}")
    print(f"  ElevenLabs API key configured: {'Yes' if settings.elevenlabs_api_key else 'No'}")
    print("✅ Configuration test passed")

def test_data_models():
    """Test data model creation"""
    print("\n📊 Testing Data Models...")
    
    # Test campaign webhook
    webhook_data = {
        "campaign_id": "test-123",
        "product_name": "Test Product",
        "brand_name": "Test Brand",
        "product_description": "A test product for fitness enthusiasts",
        "target_audience": "Fitness lovers aged 18-35",
        "campaign_goal": "Brand awareness",
        "product_niche": "fitness",
        "total_budget": 10000.0
    }
    
    webhook = CampaignWebhook(**webhook_data)
    print(f"  Created webhook: {webhook.product_name}")
    
    # Convert to campaign data
    campaign = CampaignData(
        id=webhook.campaign_id,
        product_name=webhook.product_name,
        brand_name=webhook.brand_name,
        product_description=webhook.product_description,
        target_audience=webhook.target_audience,
        campaign_goal=webhook.campaign_goal,
        product_niche=webhook.product_niche,
        total_budget=webhook.total_budget
    )
    print(f"  Created campaign: {campaign.id}")
    print("✅ Data models test passed")

def test_creator_data_loading():
    """Test loading creator data from JSON"""
    print("\n👥 Testing Creator Data Loading...")
    
    # Mock creator data (replace with actual file loading)
    mock_creator_data = {
        "id": "test_creator",
        "name": "Test Creator",
        "platform": "YouTube",
        "followers": 500000,
        "niche": "fitness",
        "typical_rate": 3000,
        "engagement_rate": 4.5,
        "average_views": 100000,
        "last_campaign_date": "2024-01-01",
        "availability": "good",
        "location": "Test City",
        "phone_number": "+1234567890",
        "languages": ["English"],
        "specialties": ["fitness", "nutrition"],
        "audience_demographics": {"age_18_24": 40, "age_25_34": 35},
        "performance_metrics": {"brand_safety_score": 9.0},
        "recent_campaigns": [],
        "rate_history": {"2024": 3000},
        "preferred_collaboration_style": "Professional"
    }
    
    creator = Creator(**mock_creator_data)
    print(f"  Created creator: {creator.name}")
    print(f"  Creator tier: {creator.tier}")
    print(f"  Cost per view: ${creator.cost_per_view:.4f}")
    print("✅ Creator data test passed")

async def test_orchestrator_initialization():
    """Test orchestrator agent initialization"""
    print("\n🎯 Testing Orchestrator Initialization...")

    try:
        orchestrator = CampaignOrchestrator()
        print("  Orchestrator created successfully")

        # Verify core dependencies were initialized
        assert orchestrator.discovery_agent is not None, "Discovery agent missing"
        assert getattr(orchestrator, "negotiation_agent", None) is not None, "Negotiation agent missing"
        assert orchestrator.contract_agent is not None, "Contract agent missing"

        if hasattr(orchestrator, "database_service"):
            assert orchestrator.database_service is not None, "Database service missing"

        print("✅ Orchestrator test passed")
    except Exception as e:
        print(f"❌ Orchestrator initialization failed: {e}")

def create_env_template():
    """Create .env template file"""
    print("\n📝 Creating .env template...")
    
    env_content = """# InfluencerFlow AI Platform - Environment Variables

# Required API Keys
GROQ_API_KEY=your_groq_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# Optional Database URL (uses default if not provided)
DATABASE_URL=postgresql://localhost:5432/influencerflow

# Webhook Security
WEBHOOK_SECRET=your_super_secret_webhook_key_here

# Demo Configuration
DEMO_MODE=true
MOCK_CALLS=false

# Voice Configuration  
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM

# AI Configuration
MAX_NEGOTIATION_DURATION=45
SIMILARITY_THRESHOLD=0.6
BASE_SUCCESS_RATE=0.7
"""
    
    with open(".env.template", "w") as f:
        f.write(env_content)
    
    print("  Created .env.template file")
    print("  📋 Copy this to .env and add your API keys!")

async def main():
    """Run all tests"""
    print("🧪 InfluencerFlow AI Platform - Setup Verification")
    print("=" * 50)
    
    test_configuration()
    test_data_models()
    test_creator_data_loading()
    await test_orchestrator_initialization()
    create_env_template()
    
    print("\n" + "=" * 50)
    print("🎉 Setup verification completed!")
    print("\n📋 Next steps:")
    print("1. Copy .env.template to .env")
    print("2. Add your GROQ_API_KEY and ELEVENLABS_API_KEY")
    print("3. Copy creators.json and market_data.json to data/ folder")
    print("4. Run: uvicorn main:app --reload")
    print("5. Test webhook: POST /api/webhook/test-campaign")

if __name__ == "__main__":
    asyncio.run(main())