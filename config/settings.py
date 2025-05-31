# config/settings.py
import os
from typing import Optional

# Handle pydantic BaseSettings import correctly
try:
    from pydantic_settings import BaseSettings
except ImportError:
    try:
        from pydantic.v1 import BaseSettings
    except ImportError:
        # Fallback for very old pydantic versions
        from pydantic import BaseSettings

class Settings(BaseSettings):
    # API Keys
    groq_api_key: str
    elevenlabs_api_key: str
    openai_api_key: Optional[str] = None  # Backup LLM
    
    # Database
    database_url: str = "postgresql://localhost:5432/influencerflow"
    
    # Webhook Security
    webhook_secret: str = "your-webhook-secret-here"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # AI Configuration
    max_embedding_length: int = 512
    similarity_threshold: float = 0.6
    max_negotiation_duration: int = 45  # seconds for demo
    
    # Voice Configuration
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"  # Default voice
    call_timeout: int = 30  # seconds
    
    # Pricing Configuration
    base_success_rate: float = 0.7
    max_retry_attempts: int = 1
    
    # Demo Configuration
    demo_mode: bool = True
    mock_calls: bool = False  # Set to True if you want to simulate calls
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create global settings instance
settings = Settings()

# Environment variables template for .env file
ENV_TEMPLATE = """
# API Keys (Required)
GROQ_API_KEY=your_groq_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# Database (Optional - uses default if not provided)
DATABASE_URL=postgresql://localhost:5432/influencerflow

# Webhook Security
WEBHOOK_SECRET=your_super_secret_webhook_key

# Demo Configuration
DEMO_MODE=true
MOCK_CALLS=false

# Voice Configuration
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
"""