# ensure_core_files.py - ENSURE CORE FILES EXIST
"""
🏗️ Ensure Core Files Exist

This script ensures that all required core files exist with proper content.
If they're missing or broken, it creates clean versions.

Usage:
    python ensure_core_files.py
"""

from pathlib import Path

def ensure_core_config():
    """Ensure core/config.py exists with proper content"""
    
    config_file = Path("core/config.py")
    
    if config_file.exists():
        print("✅ core/config.py exists")
        return
    
    print("🏗️ Creating core/config.py...")
    
    config_content = '''# core/config.py - UNIFIED CONFIGURATION
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Unified application settings"""
    
    # Core Application Settings
    app_name: str = "InfluencerFlow AI Platform"
    app_version: str = "3.0.0"
    debug: bool = False
    environment: str = "development"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # ElevenLabs Configuration
    elevenlabs_api_key: Optional[str] = None
    elevenlabs_agent_id: Optional[str] = None
    elevenlabs_phone_number_id: Optional[str] = None
    
    # AI Configuration
    groq_api_key: Optional[str] = None
    
    # Development Settings
    use_mock_services: bool = True
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Global settings instance
settings = Settings()
'''
    
    with open(config_file, 'w') as f:
        f.write(config_content)
    
    print("✅ Created core/config.py")

def ensure_core_models():
    """Ensure core/models.py exists with proper content"""
    
    models_file = Path("core/models.py")
    
    if models_file.exists():
        print("✅ core/models.py exists")
        return
    
    print("🏗️ Creating core/models.py...")
    
    models_content = '''# core/models.py - UNIFIED DATA MODELS
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

class NegotiationStatus(str, Enum):
    """Negotiation status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"

class CampaignData(BaseModel):
    """Unified campaign data model"""
    id: str
    product_name: str
    brand_name: str
    product_description: str
    target_audience: str
    campaign_goal: str
    product_niche: str
    total_budget: float
    campaign_code: Optional[str] = None
    
    def generate_campaign_code(self) -> str:
        """Generate campaign code if not provided"""
        if not self.campaign_code:
            self.campaign_code = f"CAMP-{self.id[:8].upper()}"
        return self.campaign_code

class Creator(BaseModel):
    """Creator profile model"""
    id: str
    name: str
    handle: str
    followers: int
    engagement_rate: float
    niche: str
    rate_per_post: float
    contact_email: str
    phone_number: Optional[str] = None

class NegotiationResult(BaseModel):
    """Negotiation outcome model"""
    creator_id: str
    creator_name: str
    status: NegotiationStatus
    agreed_rate: Optional[float] = None
    call_duration_seconds: int = 0
    call_recording_url: Optional[str] = None
    call_transcript: Optional[str] = None
    negotiated_at: datetime = Field(default_factory=datetime.now)

class Contract(BaseModel):
    """Contract model"""
    id: str
    creator_id: str
    campaign_id: str
    rate: float
    deliverables: List[str]
    deadline: datetime
    created_at: datetime = Field(default_factory=datetime.now)

class OrchestrationState(BaseModel):
    """Campaign orchestration state"""
    campaign_id: str
    campaign_data: CampaignData
    current_stage: str = "initialized"
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    # Progress tracking
    discovered_creators: List[Creator] = Field(default_factory=list)
    negotiations: List[NegotiationResult] = Field(default_factory=list)
    contracts: List[Contract] = Field(default_factory=list)
    
    # Metrics
    successful_negotiations: int = 0
    total_cost: float = 0.0
    error_message: Optional[str] = None

# Legacy compatibility - for old imports
CampaignWebhook = CampaignData
CampaignOrchestrationState = OrchestrationState
'''
    
    with open(models_file, 'w') as f:
        f.write(models_content)
    
    print("✅ Created core/models.py")

def ensure_core_init():
    """Ensure core/__init__.py has proper exports"""
    
    init_file = Path("core/__init__.py")
    
    if not init_file.exists():
        print("🏗️ Creating core/__init__.py...")
        
        init_content = '''# core/__init__.py
"""
InfluencerFlow AI Platform - Core Module
"""

from .config import settings
from .models import *

__all__ = [
    "settings",
    "CampaignData",
    "Creator", 
    "NegotiationResult",
    "Contract",
    "OrchestrationState"
]
'''
        
        with open(init_file, 'w') as f:
            f.write(init_content)
        
        print("✅ Created core/__init__.py")
    else:
        print("✅ core/__init__.py exists")

def main():
    """Ensure all core files exist"""
    
    print("🏗️ ENSURING CORE FILES EXIST")
    print("=" * 40)
    
    # Create core directory if it doesn't exist
    core_dir = Path("core")
    core_dir.mkdir(exist_ok=True)
    
    # Ensure all core files exist
    ensure_core_config()
    ensure_core_models()
    ensure_core_init()
    
    print("\n✅ All core files are now in place!")
    print("💡 Next: Run 'python fix_imports.py' to fix import issues")

if __name__ == "__main__":
    main()