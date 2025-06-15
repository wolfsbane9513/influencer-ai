# core/config.py - CORRECTED UNIFIED CONFIGURATION
import os
import logging
from typing import Optional, List
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Clean Configuration Management
    
    Unified settings class following OOP principles:
    - Single source of truth for all configuration
    - Environment-based configuration with fallbacks
    - Type validation with Pydantic
    - No legacy configuration retention
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
    elevenlabs_base_url: str = "https://api.elevenlabs.io"
    
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
    rate_limit_per_minute: int = 100
    
    class Config:
        """Pydantic configuration"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        # Environment variable prefixes
        env_prefix = ""
    
    def __init__(self, **kwargs):
        """Initialize settings with validation"""
        super().__init__(**kwargs)
        self._validate_configuration()
        self._configure_services()
    
    def _validate_configuration(self) -> None:
        """Validate configuration and set service flags"""
        
        # Validate ElevenLabs configuration
        elevenlabs_configured = all([
            self.elevenlabs_api_key,
            self.elevenlabs_agent_id,
            self.elevenlabs_phone_number_id
        ])
        
        if not elevenlabs_configured:
            logger.warning("⚠️ ElevenLabs not fully configured - using mock services")
            self.use_mock_services = True
        
        # Validate Groq configuration
        if not self.groq_api_key:
            logger.warning("⚠️ Groq API key not configured - AI features limited")
        
        # Validate database configuration
        if not self.database_url:
            logger.warning("⚠️ Database not configured - using mock database")
    
    def _configure_services(self) -> None:
        """Configure services based on environment"""
        
        # Enable/disable mock services based on environment
        if self.environment == "production":
            # In production, disable mock services if APIs are configured
            if self.is_elevenlabs_configured():
                self.use_mock_services = False
        elif self.environment == "development":
            # In development, default to mock services unless explicitly disabled
            if not self.is_elevenlabs_configured():
                self.use_mock_services = True
    
    def is_elevenlabs_configured(self) -> bool:
        """Check if ElevenLabs is fully configured"""
        return all([
            self.elevenlabs_api_key,
            self.elevenlabs_agent_id,
            self.elevenlabs_phone_number_id
        ])
    
    def is_groq_configured(self) -> bool:
        """Check if Groq AI is configured"""
        return bool(self.groq_api_key)
    
    def is_database_configured(self) -> bool:
        """Check if database is configured"""
        return bool(self.database_url)
    
    def get_service_status(self) -> dict:
        """Get status of all configured services"""
        return {
            "elevenlabs": "✅" if self.is_elevenlabs_configured() else "❌",
            "groq": "✅" if self.is_groq_configured() else "❌",
            "database": "✅" if self.is_database_configured() else "❌",
            "mock_services": self.use_mock_services
        }
    
    def log_configuration_status(self) -> None:
        """Log current configuration status"""
        
        logger.info(f"🔧 {self.app_name} v{self.app_version}")
        logger.info(f"Environment: {self.environment}")
        logger.info(f"Debug Mode: {self.debug}")
        logger.info(f"Mock Services: {self.use_mock_services}")
        logger.info(f"Log Level: {self.log_level}")
        logger.info(f"API: {self.api_host}:{self.api_port}")
        
        service_status = self.get_service_status()
        logger.info(f"ElevenLabs Configured: {service_status['elevenlabs']}")
        logger.info(f"Groq AI Configured: {service_status['groq']}")
        logger.info(f"Database Configured: {service_status['database']}")


# Create global settings instance
settings = Settings()

# Configure logging based on settings
def configure_logging():
    """Configure application logging"""
    
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format=settings.log_format,
        handlers=[
            logging.StreamHandler(),
            # Add file handler if needed
            # logging.FileHandler('app.log')
        ]
    )
    
    # Set specific logger levels
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


# Initialize logging when module is imported
configure_logging()