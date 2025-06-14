#!/usr/bin/env python3
"""
InfluencerFlow AI Platform - Quick Setup Script
Automates the initial setup process for new installations
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header():
    """Print setup header"""
    print("=" * 60)
    print("🚀 InfluencerFlow AI Platform - Quick Setup")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("🔍 Checking Python version...")
    
    if sys.version_info < (3, 13):
        print("❌ Python 3.13+ is required")
        print(f"   Current version: {sys.version}")
        print("   Please upgrade Python and try again")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    print()

def check_uv():
    """Check if UV package manager is available"""
    print("🔍 Checking UV package manager...")
    
    try:
        subprocess.run(["uv", "--version"], capture_output=True, check=True)
        print("✅ UV package manager found")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  UV not found, will use pip instead")
        return False

def install_dependencies(use_uv=True):
    """Install project dependencies"""
    print("📦 Installing dependencies...")
    
    try:
        if use_uv:
            subprocess.run(["uv", "sync"], check=True)
        else:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        
        print("✅ Dependencies installed successfully")
        print()
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)

def setup_environment():
    """Setup environment configuration"""
    print("🔧 Setting up environment configuration...")
    
    env_file = Path(".env")
    env_template = Path(".env.template")
    
    if env_file.exists():
        print("⚠️  .env file already exists")
        response = input("   Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("   Skipping environment setup")
            print()
            return
    
    if env_template.exists():
        shutil.copy(env_template, env_file)
        print("✅ Created .env file from template")
        print("📝 Please edit .env file with your API keys:")
        print("   - GROQ_API_KEY")
        print("   - ELEVENLABS_API_KEY")
        print("   - ELEVENLABS_AGENT_ID")
        print("   - ELEVENLABS_PHONE_NUMBER_ID")
    else:
        print("⚠️  .env.template not found, creating basic .env file")
        create_basic_env_file(env_file)
    
    print()

def create_basic_env_file(env_file):
    """Create a basic .env file"""
    basic_env_content = """# InfluencerFlow AI Platform - Basic Configuration

# Required API Keys (Update these with your actual keys)
GROQ_API_KEY=your_groq_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
ELEVENLABS_AGENT_ID=your_agent_id_here
ELEVENLABS_PHONE_NUMBER_ID=your_phone_number_here

# Basic Configuration
DEBUG=true
DEMO_MODE=true
MOCK_CALLS=false
HOST=0.0.0.0
PORT=8000

# Database (Optional)
DATABASE_URL=postgresql://localhost:5432/influencerflow
"""
    
    with open(env_file, 'w') as f:
        f.write(basic_env_content)

def setup_data_files():
    """Setup data files"""
    print("📊 Setting up data files...")
    
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Check for required data files
    required_files = ["creators.json", "market_data.json"]
    missing_files = []
    
    for file_name in required_files:
        file_path = data_dir / file_name
        if not file_path.exists():
            missing_files.append(file_name)
    
    if missing_files:
        print("⚠️  Missing data files:")
        for file_name in missing_files:
            print(f"   - data/{file_name}")
        print("   Creating sample data files...")
        create_sample_data_files(data_dir)
    else:
        print("✅ All data files present")
    
    print()

def create_sample_data_files(data_dir):
    """Create sample data files"""
    
    # Sample creators.json
    sample_creators = {
        "creators": [
            {
                "id": "sample_creator_1",
                "name": "FitnessInfluencer_Sarah",
                "platform": "Instagram",
                "followers": 250000,
                "niche": "fitness",
                "typical_rate": 3500,
                "engagement_rate": 5.8,
                "average_views": 95000,
                "last_campaign_date": "2024-01-15",
                "availability": "good",
                "location": "Los Angeles, USA",
                "phone_number": "+1234567890",
                "languages": ["English"],
                "specialties": ["workout_routines", "nutrition", "fitness_gear"],
                "audience_demographics": {"age_18_24": 35, "age_25_34": 40, "male": 45, "female": 55},
                "performance_metrics": {"brand_safety_score": 9.2, "collaboration_rating": 4.7},
                "recent_campaigns": [],
                "rate_history": {"2024": 3500},
                "preferred_collaboration_style": "Professional and authentic approach"
            }
        ]
    }
    
    # Sample market_data.json
    sample_market_data = {
        "rate_benchmarks": {
            "fitness": {
                "micro_influencer": {"min": 1800, "max": 3800, "avg": 2800},
                "macro_influencer": {"min": 3800, "max": 6500, "avg": 5000},
                "mega_influencer": {"min": 6500, "max": 12000, "avg": 9000}
            },
            "tech": {
                "micro_influencer": {"min": 2000, "max": 4000, "avg": 3000},
                "macro_influencer": {"min": 4000, "max": 8000, "avg": 6000},
                "mega_influencer": {"min": 8000, "max": 15000, "avg": 12000}
            }
        }
    }
    
    # Write sample files
    import json
    
    with open(data_dir / "creators.json", 'w') as f:
        json.dump(sample_creators, f, indent=2)
    
    with open(data_dir / "market_data.json", 'w') as f:
        json.dump(sample_market_data, f, indent=2)
    
    print("✅ Sample data files created")

def test_installation():
    """Test the installation"""
    print("🧪 Testing installation...")
    
    try:
        # Test imports
        from config.settings import settings
        from models.campaign import CampaignWebhook
        from agents.campaign_orchestrator import CampaignOrchestrator
        
        print("✅ Core imports successful")
        
        # Test configuration
        if settings.demo_mode:
            print("✅ Configuration loaded (demo mode)")
        else:
            print("✅ Configuration loaded (production mode)")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Please check your installation")
        return False
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        print("   Please check your .env file")
        return False
    
    print()
    return True

def print_next_steps():
    """Print next steps for the user"""
    print("🎉 Setup completed successfully!")
    print()
    print("📋 Next Steps:")
    print("1. Edit .env file with your API keys:")
    print("   - Get Groq API key: https://console.groq.com/keys")
    print("   - Get ElevenLabs API key: https://elevenlabs.io/app/settings/api-keys")
    print("   - Configure ElevenLabs agent: https://elevenlabs.io/app/conversational-ai")
    print()
    print("2. Start the server:")
    print("   uvicorn main:app --reload")
    print()
    print("3. Test the installation:")
    print("   curl http://localhost:8000/health")
    print("   curl -X POST http://localhost:8000/api/webhook/test-enhanced-campaign")
    print()
    print("4. Access documentation:")
    print("   http://localhost:8000/docs (API documentation)")
    print("   http://localhost:8000/redoc (Alternative API docs)")
    print()
    print("🔗 For more information, see README.md")
    print("=" * 60)

def main():
    """Main setup function"""
    print_header()
    
    # Check requirements
    check_python_version()
    use_uv = check_uv()
    
    # Install and setup
    install_dependencies(use_uv)
    setup_environment()
    setup_data_files()
    
    # Test installation
    if test_installation():
        print_next_steps()
    else:
        print("❌ Setup completed with errors")
        print("   Please check the error messages above and fix any issues")
        sys.exit(1)

if __name__ == "__main__":
    main()