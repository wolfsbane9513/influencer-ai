# config/simple_settings.py
"""
Simplified settings that work without pydantic-settings
Use this as a fallback if pydantic-settings installation fails
"""

import os
from typing import Optional

class SimpleSettings:
    """Simple settings class without pydantic dependencies"""
    
    def __init__(self):
        # Load from environment variables
        self.groq_api_key = os.getenv("GROQ_API_KEY", "")
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY", "")
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        
        # Database
        self.database_url = os.getenv("DATABASE_URL", "postgresql://localhost:5432/influencerflow")
        
        # Webhook Security
        self.webhook_secret = os.getenv("WEBHOOK_SECRET", "your-webhook-secret-here")
        
        # Server Configuration
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", "8000"))
        self.debug = os.getenv("DEBUG", "true").lower() == "true"
        
        # AI Configuration
        self.max_embedding_length = int(os.getenv("MAX_EMBEDDING_LENGTH", "512"))
        self.similarity_threshold = float(os.getenv("SIMILARITY_THRESHOLD", "0.6"))
        self.max_negotiation_duration = int(os.getenv("MAX_NEGOTIATION_DURATION", "45"))
        
        # Voice Configuration
        self.elevenlabs_voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
        self.call_timeout = int(os.getenv("CALL_TIMEOUT", "30"))
        
        # Pricing Configuration
        self.base_success_rate = float(os.getenv("BASE_SUCCESS_RATE", "0.7"))
        self.max_retry_attempts = int(os.getenv("MAX_RETRY_ATTEMPTS", "1"))
        
        # Demo Configuration
        self.demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"
        self.mock_calls = os.getenv("MOCK_CALLS", "false").lower() == "true"
    
    def load_env_file(self, env_file=".env"):
        """Load environment variables from file"""
        try:
            if os.path.exists(env_file):
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip()
                
                # Reload settings
                self.__init__()
                print(f"✅ Loaded environment from {env_file}")
        except Exception as e:
            print(f"⚠️  Could not load {env_file}: {e}")

# Try to use pydantic settings first, fallback to simple
try:
    from config.settings import Settings
    settings = Settings()
    print("✅ Using pydantic Settings")
except ImportError as e:
    print(f"⚠️  Pydantic settings failed: {e}")
    print("🔄 Using SimpleSettings fallback")
    settings = SimpleSettings()
    settings.load_env_file()

# Export settings
__all__ = ["settings"]