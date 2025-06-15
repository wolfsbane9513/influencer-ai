# core/config.py - UNIFIED CONFIGURATION
import os
import logging
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import validator

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """
    Unified application settings
    
    Centralizes all configuration with proper validation and environment support.
    Replaces multiple settings files with single, clean implementation.
    """
    
    # Core Application Settings
    app_name: str = "InfluencerFlow AI Platform"
    app_version: str = "3.0.0"
    debug: bool = False
    environment: str = "development"  # development, staging, production
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    
    # ElevenLabs Voice Service Configuration
    elevenlabs_api_key: Optional[str] = None
    elevenlabs_agent_id: Optional[str] = None
    elevenlabs_phone_number_id: Optional[str] = None
    elevenlabs_base_url: str = "https://api.elevenlabs.io/v1"
    
    # AI Configuration
    groq_api_key: Optional[str] = None
    groq_model: str = "llama-3.1-70b-versatile"
    
    # Database Configuration
    database_url: Optional[str] = None
    database_pool_size: int = 10
    database_timeout: int = 30
    
    # Development and Testing Settings
    use_mock_services: bool = True
    mock_call_duration: int = 180  # seconds
    mock_success_rate: float = 0.8  # 80% success rate for mock calls
    
    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Campaign Default Settings
    default_max_creators: int = 10
    default_timeline_days: int = 30
    default_engagement_threshold: float = 3.0
    max_concurrent_calls: int = 5
    call_timeout_seconds: int = 300
    
    # Security Settings
    allowed_origins: List[str] = ["*"]
    api_key_header: str = "X-API-Key"
    rate_limit_per_minute: int = 60
    
    # Performance Settings
    max_campaigns_in_memory: int = 100
    cleanup_completed_campaigns_hours: int = 24
    
    @validator('environment')
    def validate_environment(cls, v):
        valid_environments = ['development', 'staging', 'production']
        if v not in valid_environments:
            raise ValueError(f'Environment must be one of: {", ".join(valid_environments)}')
        return v
    
    @validator('log_level')
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of: {", ".join(valid_levels)}')
        return v.upper()
    
    @validator('mock_success_rate')
    def validate_success_rate(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Mock success rate must be between 0.0 and 1.0')
        return v
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment == "production"
    
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment == "development"
    
    def get_log_level_int(self) -> int:
        """Get numeric log level for logging configuration"""
        return getattr(logging, self.log_level)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        # Allow environment variables to override settings
        env_prefix = ""

class ProductionSettings(Settings):
    """
    Production-specific settings with security hardening
    """
    
    debug: bool = False
    api_reload: bool = False
    
    log_level: str = "WARNING"
    allowed_origins: List[str] = []  # Must be explicitly set in production
    rate_limit_per_minute: int = 30  # More restrictive in production
    
    @validator('elevenlabs_api_key')
    def validate_elevenlabs_key_required(cls, v):
        if not v:
            raise ValueError('ElevenLabs API key is required in production')
        return v

class DevelopmentSettings(Settings):
    """
    Development-specific settings with relaxed validation
    """
    
    debug: bool = True
    api_reload: bool = True
    use_mock_services: bool = True
    log_level: str = "DEBUG"

def get_settings() -> Settings:
    """
    Factory function to get appropriate settings based on environment
    
    Returns:
        Settings instance configured for current environment
    """
    
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    if environment == "production":
        return ProductionSettings()
    elif environment == "development":
        return DevelopmentSettings()
    else:
        return Settings(environment=environment)

def setup_logging(settings: Settings):
    """
    Configure logging based on settings
    
    Args:
        settings: Application settings instance
    """
    
    logging.basicConfig(
        level=settings.get_log_level_int(),
        format=settings.log_format,
        handlers=[
            logging.StreamHandler(),
            # Add file handler in production
            logging.FileHandler('app.log') if settings.is_production() else logging.NullHandler()
        ]
    )
    
    # Reduce noise from external libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    
    logger.info(f"🔧 Logging configured for {settings.environment} environment")

def validate_production_settings(settings: Settings):
    """
    Validate that all required settings are present for production
    
    Args:
        settings: Settings to validate
        
    Raises:
        ValueError: If required production settings are missing
    """
    
    if not settings.is_production():
        return
    
    required_production_settings = [
        ("elevenlabs_api_key", "ElevenLabs API key"),
        ("elevenlabs_agent_id", "ElevenLabs Agent ID"),
        ("elevenlabs_phone_number_id", "ElevenLabs Phone Number ID")
    ]
    
    missing_settings = []
    
    for setting_name, description in required_production_settings:
        value = getattr(settings, setting_name)
        if not value:
            missing_settings.append(description)
    
    if missing_settings:
        raise ValueError(
            f"Missing required production settings: {', '.join(missing_settings)}. "
            f"Please set these environment variables before running in production."
        )
    
    # Validate security settings
    if settings.allowed_origins == ["*"]:
        logger.warning("⚠️ CORS is set to allow all origins in production - this is insecure!")
    
    logger.info("✅ Production settings validation passed")

def print_settings_summary(settings: Settings):
    """
    Print a summary of current settings (excluding sensitive data)
    
    Args:
        settings: Settings to summarize
    """
    
    print(f"""
🔧 {settings.app_name} v{settings.app_version}
Environment: {settings.environment}
Debug Mode: {settings.debug}
Mock Services: {settings.use_mock_services}
Log Level: {settings.log_level}
API: {settings.api_host}:{settings.api_port}
ElevenLabs Configured: {'✅' if settings.elevenlabs_api_key else '❌'}
Groq AI Configured: {'✅' if settings.groq_api_key else '❌'}
Database Configured: {'✅' if settings.database_url else '❌'}
""")

# Global settings instance
settings = get_settings()

# Setup logging immediately
setup_logging(settings)

# Validate production settings if needed
try:
    validate_production_settings(settings)
except ValueError as e:
    if settings.is_production():
        logger.error(f"❌ Production validation failed: {e}")
        raise
    else:
        logger.warning(f"⚠️ Production validation would fail: {e}")

# Print settings summary
if settings.is_development():
    print_settings_summary(settings)

# Export commonly used settings for convenience
API_HOST = settings.api_host
API_PORT = settings.api_port
DEBUG = settings.debug
USE_MOCK_SERVICES = settings.use_mock_services