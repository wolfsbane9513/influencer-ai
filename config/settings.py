# config/settings.py - Enhanced with Email and Notifications
from typing import Optional, List
from pathlib import Path

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
    """
    🔧 ENHANCED SETTINGS - Complete configuration management
    
    Supports all platform features:
    - Core AI integrations (Groq, ElevenLabs)
    - Email service configuration  
    - Multi-channel notifications
    - Database and monitoring
    - Security and deployment
    """
    
    # ================================
    # CORE API INTEGRATIONS
    # ================================
    
    # AI Services
    groq_api_key: str
    elevenlabs_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None  # Backup LLM
    
    # ElevenLabs Voice Configuration
    elevenlabs_agent_id: Optional[str] = None
    elevenlabs_phone_number_id: Optional[str] = None
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"  # Default voice
    
    # ================================
    # EMAIL SERVICE CONFIGURATION
    # ================================
    
    # SMTP Configuration
    email_username: Optional[str] = None
    email_password: Optional[str] = None
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    
    # Email Branding
    sender_name: str = "InfluencerFlow AI"
    sender_email: Optional[str] = None  # Defaults to email_username if not set
    
    # Email Templates
    email_template_dir: str = "templates/emails"
    
    # Email Security
    smtp_use_tls: bool = True
    smtp_use_ssl: bool = False
    email_timeout: int = 60
    
    # ================================
    # NOTIFICATION SERVICES
    # ================================
    
    # Slack Integration
    slack_webhook_url: Optional[str] = None
    slack_default_channel: str = "#general"
    slack_bot_name: str = "InfluencerFlow AI"
    
    # Discord Integration
    discord_webhook_url: Optional[str] = None
    discord_bot_name: str = "InfluencerFlow AI"
    
    # Microsoft Teams
    teams_webhook_url: Optional[str] = None
    
    # SMS/Twilio (Optional)
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_phone_number: Optional[str] = None
    
    # Webhook Notifications
    webhook_urls: List[str] = []  # Comma-separated in env: WEBHOOK_URLS=url1,url2
    webhook_timeout: int = 30
    webhook_retry_count: int = 3
    
    # Notification Processing
    notification_batch_size: int = 10
    notification_processing_interval: int = 30
    notification_max_retries: int = 3
    notification_retry_delay: int = 60
    
    # ================================
    # DATABASE CONFIGURATION
    # ================================
    
    database_url: str = "postgresql://localhost:5432/influencerflow"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_pool_timeout: int = 30
    
    # Redis (for background tasks and caching)
    redis_url: str = "redis://localhost:6379"
    redis_password: Optional[str] = None
    redis_db: int = 0
    
    # ================================
    # SECURITY CONFIGURATION
    # ================================
    
    # Webhook Security
    webhook_secret: str = "your-webhook-secret-here"
    
    # API Security
    api_key_encryption_secret: Optional[str] = None
    jwt_secret_key: Optional[str] = None
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    
    # CORS
    allowed_origins: List[str] = ["*"]  # Configure for production
    allowed_methods: List[str] = ["GET", "POST", "PUT", "DELETE"]
    allowed_headers: List[str] = ["*"]
    
    # ================================
    # SERVER CONFIGURATION
    # ================================
    
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    log_level: str = "INFO"
    
    # Workers (for production)
    workers: int = 1
    worker_class: str = "uvicorn.workers.UvicornWorker"
    
    # ================================
    # AI CONFIGURATION
    # ================================
    
    # Embedding Service
    max_embedding_length: int = 512
    similarity_threshold: float = 0.6
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # Voice Service
    max_negotiation_duration: int = 300  # 5 minutes
    call_timeout: int = 60
    conversation_monitoring_interval: int = 15  # seconds
    
    # Groq Models
    groq_strategy_model: str = "llama3-70b-8192"
    groq_quick_model: str = "llama3-8b-8192"
    groq_temperature: float = 0.1
    groq_max_tokens: int = 1000
    
    # ================================
    # BUSINESS CONFIGURATION
    # ================================
    
    # Pricing
    base_success_rate: float = 0.7
    max_retry_attempts: int = 2
    
    # Campaign Defaults
    default_campaign_duration_days: int = 30
    default_content_review_hours: int = 48
    default_revision_count: int = 2
    
    # Contract Generation
    contract_template_dir: str = "templates/contracts"
    contract_pdf_watermark: bool = True
    contract_digital_signature: bool = False
    
    # ================================
    # MONITORING & ANALYTICS
    # ================================
    
    # Metrics Collection
    enable_metrics: bool = True
    metrics_port: int = 8001
    
    # Error Tracking
    sentry_dsn: Optional[str] = None
    sentry_environment: str = "development"
    sentry_traces_sample_rate: float = 1.0
    
    # Performance Monitoring
    newrelic_license_key: Optional[str] = None
    datadog_api_key: Optional[str] = None
    
    # Structured Logging
    log_format: str = "json"  # json or text
    log_file: Optional[str] = None
    log_rotation: str = "daily"
    log_retention_days: int = 30
    
    # ================================
    # FEATURE FLAGS
    # ================================
    
    # Demo and Development
    demo_mode: bool = True
    mock_calls: bool = False
    mock_emails: bool = False
    mock_notifications: bool = False
    
    # Feature Toggles
    enable_ai_strategy: bool = True
    enable_voice_negotiations: bool = True
    enable_email_delivery: bool = True
    enable_notifications: bool = True
    enable_conversation_monitoring: bool = True
    enable_real_time_updates: bool = True
    
    # Beta Features
    enable_advanced_analytics: bool = False
    enable_blockchain_payments: bool = False
    enable_mobile_api: bool = False
    
    # ================================
    # FILE STORAGE
    # ================================
    
    # Local File Storage
    data_dir: str = "data"
    upload_dir: str = "uploads"
    temp_dir: str = "temp"
    
    # Cloud Storage (Optional)
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_s3_bucket: Optional[str] = None
    aws_region: str = "us-east-1"
    
    # Google Cloud Storage (Optional)
    gcp_project_id: Optional[str] = None
    gcp_credentials_path: Optional[str] = None
    gcp_bucket_name: Optional[str] = None
    
    # ================================
    # EXTERNAL INTEGRATIONS
    # ================================
    
    # Social Media APIs (for future features)
    instagram_client_id: Optional[str] = None
    instagram_client_secret: Optional[str] = None
    youtube_api_key: Optional[str] = None
    tiktok_client_key: Optional[str] = None
    
    # Payment Processing (for future features)
    stripe_public_key: Optional[str] = None
    stripe_secret_key: Optional[str] = None
    paypal_client_id: Optional[str] = None
    paypal_client_secret: Optional[str] = None
    
    # Analytics (for future features)
    google_analytics_id: Optional[str] = None
    mixpanel_token: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        
        # Environment variable parsing
        @staticmethod
        def parse_webhook_urls(v):
            if isinstance(v, str):
                return [url.strip() for url in v.split(',') if url.strip()]
            return v
        
        @staticmethod
        def parse_allowed_origins(v):
            if isinstance(v, str):
                return [origin.strip() for origin in v.split(',') if origin.strip()]
            return v
    
    # ================================
    # COMPUTED PROPERTIES
    # ================================
    
    @property
    def effective_sender_email(self) -> str:
        """Get effective sender email (falls back to email_username)"""
        return self.sender_email or self.email_username or "noreply@influencerflow.ai"
    
    @property
    def email_configured(self) -> bool:
        """Check if email service is properly configured"""
        return bool(self.email_username and self.email_password)
    
    @property
    def notifications_configured(self) -> bool:
        """Check if any notification channel is configured"""
        return any([
            self.slack_webhook_url,
            self.discord_webhook_url,
            self.teams_webhook_url,
            self.webhook_urls,
            self.email_configured
        ])
    
    @property
    def ai_integrations_configured(self) -> bool:
        """Check if core AI integrations are configured"""
        return bool(self.groq_api_key and self.elevenlabs_api_key)
    
    @property
    def voice_negotiations_ready(self) -> bool:
        """Check if voice negotiations are fully configured"""
        return bool(
            self.elevenlabs_api_key and 
            self.elevenlabs_agent_id and 
            self.elevenlabs_phone_number_id
        )
    
    @property
    def production_ready(self) -> bool:
        """Check if configuration is ready for production"""
        production_checks = [
            not self.debug,
            not self.demo_mode,
            self.ai_integrations_configured,
            self.email_configured,
            bool(self.webhook_secret != "your-webhook-secret-here"),
            bool(self.database_url != "postgresql://localhost:5432/influencerflow")
        ]
        return all(production_checks)
    
    # ================================
    # VALIDATION METHODS
    # ================================
    
    def validate_email_config(self) -> Dict[str, Any]:
        """Validate email configuration"""
        issues = []
        
        if not self.email_username:
            issues.append("EMAIL_USERNAME not configured")
        if not self.email_password:
            issues.append("EMAIL_PASSWORD not configured")
        if self.smtp_port not in [25, 465, 587, 2525]:
            issues.append(f"Unusual SMTP port: {self.smtp_port}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "server": f"{self.smtp_server}:{self.smtp_port}",
            "security": "TLS" if self.smtp_use_tls else ("SSL" if self.smtp_use_ssl else "None")
        }
    
    def validate_ai_config(self) -> Dict[str, Any]:
        """Validate AI service configuration"""
        issues = []
        
        if not self.groq_api_key:
            issues.append("GROQ_API_KEY not configured")
        if not self.elevenlabs_api_key:
            issues.append("ELEVENLABS_API_KEY not configured")
        if not self.elevenlabs_agent_id:
            issues.append("ELEVENLABS_AGENT_ID not configured")
        if not self.elevenlabs_phone_number_id:
            issues.append("ELEVENLABS_PHONE_NUMBER_ID not configured")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "features_available": {
                "ai_strategy": bool(self.groq_api_key),
                "voice_calls": self.voice_negotiations_ready,
                "conversation_monitoring": bool(self.elevenlabs_api_key)
            }
        }
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get comprehensive configuration summary"""
        return {
            "platform": {
                "version": "2.0.0",
                "mode": "demo" if self.demo_mode else "production",
                "debug": self.debug
            },
            "integrations": {
                "ai_services": self.ai_integrations_configured,
                "email_service": self.email_configured,
                "notifications": self.notifications_configured,
                "voice_negotiations": self.voice_negotiations_ready
            },
            "features": {
                "ai_strategy": self.enable_ai_strategy and bool(self.groq_api_key),
                "voice_negotiations": self.enable_voice_negotiations and self.voice_negotiations_ready,
                "email_delivery": self.enable_email_delivery and self.email_configured,
                "notifications": self.enable_notifications and self.notifications_configured,
                "conversation_monitoring": self.enable_conversation_monitoring,
                "real_time_updates": self.enable_real_time_updates
            },
            "security": {
                "cors_configured": len(self.allowed_origins) > 0,
                "rate_limiting": self.rate_limit_enabled,
                "webhook_security": bool(self.webhook_secret),
                "encryption": bool(self.api_key_encryption_secret)
            },
            "monitoring": {
                "metrics": self.enable_metrics,
                "error_tracking": bool(self.sentry_dsn),
                "performance_monitoring": bool(self.newrelic_license_key or self.datadog_api_key),
                "structured_logging": self.log_format == "json"
            },
            "readiness": {
                "production_ready": self.production_ready,
                "demo_ready": True,  # Always ready for demo
                "all_features_available": all([
                    self.ai_integrations_configured,
                    self.email_configured,
                    self.notifications_configured
                ])
            }
        }

# Create global settings instance
settings = Settings()

# Environment validation function
def validate_environment() -> Dict[str, Any]:
    """Comprehensive environment validation"""
    
    validation_results = {
        "overall_status": "valid",
        "email_config": settings.validate_email_config(),
        "ai_config": settings.validate_ai_config(),
        "configuration_summary": settings.get_configuration_summary(),
        "recommendations": []
    }
    
    # Check for common issues
    if not settings.email_configured:
        validation_results["recommendations"].append(
            "Configure email settings for contract delivery: EMAIL_USERNAME, EMAIL_PASSWORD"
        )
    
    if not settings.voice_negotiations_ready:
        validation_results["recommendations"].append(
            "Configure ElevenLabs for voice negotiations: ELEVENLABS_AGENT_ID, ELEVENLABS_PHONE_NUMBER_ID"
        )
    
    if not settings.notifications_configured:
        validation_results["recommendations"].append(
            "Configure notification channels: SLACK_WEBHOOK_URL or WEBHOOK_URLS"
        )
    
    if settings.debug and not settings.demo_mode:
        validation_results["recommendations"].append(
            "Disable DEBUG mode for production deployment"
        )
    
    # Determine overall status
    critical_issues = []
    if not validation_results["email_config"]["valid"]:
        critical_issues.extend(validation_results["email_config"]["issues"])
    if not validation_results["ai_config"]["valid"]:
        critical_issues.extend(validation_results["ai_config"]["issues"])
    
    if critical_issues:
        validation_results["overall_status"] = "issues_found"
        validation_results["critical_issues"] = critical_issues
    
    return validation_results

# Debugging helper
def debug_settings():
    """Debug helper to check configuration status"""
    print("🔍 InfluencerFlow AI Configuration Status:")
    print("=" * 50)
    
    # Core services
    print("🚀 CORE SERVICES:")
    print(f"   Groq AI: {'✅ Configured' if settings.groq_api_key else '❌ Missing GROQ_API_KEY'}")
    print(f"   ElevenLabs: {'✅ Configured' if settings.elevenlabs_api_key else '❌ Missing ELEVENLABS_API_KEY'}")
    print(f"   Voice Ready: {'✅ Ready' if settings.voice_negotiations_ready else '❌ Incomplete'}")
    
    # Email service
    print("\n📧 EMAIL SERVICE:")
    email_status = settings.validate_email_config()
    print(f"   Status: {'✅ Configured' if email_status['valid'] else '❌ Issues found'}")
    print(f"   Server: {email_status['server']}")
    print(f"   Security: {email_status['security']}")
    if email_status['issues']:
        for issue in email_status['issues']:
            print(f"   Issue: {issue}")
    
    # Notifications
    print("\n🔔 NOTIFICATIONS:")
    print(f"   Email: {'✅ Ready' if settings.email_configured else '❌ Not configured'}")
    print(f"   Slack: {'✅ Configured' if settings.slack_webhook_url else '❌ Missing'}")
    print(f"   Webhooks: {'✅ Configured' if settings.webhook_urls else '❌ Missing'}")
    
    # Feature flags
    print("\n🎯 FEATURES:")
    print(f"   Demo Mode: {'✅ Enabled' if settings.demo_mode else '❌ Disabled'}")
    print(f"   Mock Calls: {'✅ Enabled' if settings.mock_calls else '❌ Disabled'}")
    print(f"   Production Ready: {'✅ Yes' if settings.production_ready else '❌ No'}")
    
    print("=" * 50)

# Environment template generator
def generate_env_template() -> str:
    """Generate comprehensive .env template"""
    
    template = """# InfluencerFlow AI Platform - Environment Configuration
# Version 2.0.0 - Complete Configuration Template

# ================================
# CORE API INTEGRATIONS (Required)
# ================================

# Groq AI (Required for AI strategy generation)
GROQ_API_KEY=gsk_your_groq_api_key_here

# ElevenLabs Voice AI (Required for voice negotiations)
ELEVENLABS_API_KEY=sk_your_elevenlabs_api_key_here
ELEVENLABS_AGENT_ID=your_agent_id_here
ELEVENLABS_PHONE_NUMBER_ID=your_phone_number_here
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM

# OpenAI (Optional - backup for Groq)
# OPENAI_API_KEY=sk-your_openai_api_key_here

# ================================
# EMAIL SERVICE (Required for contract delivery)
# ================================

# SMTP Configuration
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password_here
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Email Branding
SENDER_NAME=InfluencerFlow AI
SENDER_EMAIL=partnerships@yourcompany.com

# Email Security
SMTP_USE_TLS=true
EMAIL_TIMEOUT=60

# ================================
# NOTIFICATION SERVICES (Optional but recommended)
# ================================

# Slack Integration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
SLACK_DEFAULT_CHANNEL=#general
SLACK_BOT_NAME=InfluencerFlow AI

# Discord Integration
# DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR/WEBHOOK

# Microsoft Teams
# TEAMS_WEBHOOK_URL=https://your-company.webhook.office.com/webhookb2/YOUR/WEBHOOK

# Webhook Notifications (comma-separated URLs)
WEBHOOK_URLS=https://your-system.com/webhooks/campaigns,https://analytics.yoursite.com/webhook

# SMS/Twilio (Optional)
# TWILIO_ACCOUNT_SID=your_twilio_account_sid
# TWILIO_AUTH_TOKEN=your_twilio_auth_token
# TWILIO_PHONE_NUMBER=+1234567890

# ================================
# DATABASE CONFIGURATION
# ================================

# PostgreSQL Database
DATABASE_URL=postgresql://user:password@localhost:5432/influencerflow

# Redis (for background tasks)
REDIS_URL=redis://localhost:6379
# REDIS_PASSWORD=your_redis_password
REDIS_DB=0

# ================================
# SECURITY CONFIGURATION
# ================================

# Webhook Security
WEBHOOK_SECRET=your_super_secure_webhook_secret_here

# API Security
API_KEY_ENCRYPTION_SECRET=your_encryption_secret_here
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ALGORITHM=HS256

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# CORS (comma-separated origins)
ALLOWED_ORIGINS=*
ALLOWED_METHODS=GET,POST,PUT,DELETE
ALLOWED_HEADERS=*

# ================================
# SERVER CONFIGURATION
# ================================

# Development
HOST=0.0.0.0
PORT=8000
DEBUG=true
LOG_LEVEL=INFO

# Production
WORKERS=4
WORKER_CLASS=uvicorn.workers.UvicornWorker

# ================================
# FEATURE CONFIGURATION
# ================================

# Demo and Development
DEMO_MODE=true
MOCK_CALLS=false
MOCK_EMAILS=false
MOCK_NOTIFICATIONS=false

# Feature Toggles
ENABLE_AI_STRATEGY=true
ENABLE_VOICE_NEGOTIATIONS=true
ENABLE_EMAIL_DELIVERY=true
ENABLE_NOTIFICATIONS=true
ENABLE_CONVERSATION_MONITORING=true

# AI Configuration
SIMILARITY_THRESHOLD=0.6
MAX_NEGOTIATION_DURATION=300
CALL_TIMEOUT=60
GROQ_STRATEGY_MODEL=llama3-70b-8192
GROQ_QUICK_MODEL=llama3-8b-8192

# ================================
# MONITORING & ANALYTICS (Optional)
# ================================

# Error Tracking
# SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
# SENTRY_ENVIRONMENT=production

# Performance Monitoring
# NEWRELIC_LICENSE_KEY=your_newrelic_license_key
# DATADOG_API_KEY=your_datadog_api_key

# Metrics
ENABLE_METRICS=true
METRICS_PORT=8001

# ================================
# FILE STORAGE (Optional)
# ================================

# Local Storage
DATA_DIR=data
UPLOAD_DIR=uploads
TEMP_DIR=temp

# AWS S3 (Optional)
# AWS_ACCESS_KEY_ID=your_aws_access_key
# AWS_SECRET_ACCESS_KEY=your_aws_secret_key
# AWS_S3_BUCKET=your_s3_bucket_name
# AWS_REGION=us-east-1

# Google Cloud Storage (Optional)
# GCP_PROJECT_ID=your_gcp_project_id
# GCP_CREDENTIALS_PATH=path/to/credentials.json
# GCP_BUCKET_NAME=your_gcs_bucket_name

# ================================
# EXTERNAL INTEGRATIONS (Future Features)
# ================================

# Social Media APIs
# INSTAGRAM_CLIENT_ID=your_instagram_client_id
# INSTAGRAM_CLIENT_SECRET=your_instagram_client_secret
# YOUTUBE_API_KEY=your_youtube_api_key
# TIKTOK_CLIENT_KEY=your_tiktok_client_key

# Payment Processing
# STRIPE_PUBLIC_KEY=pk_your_stripe_public_key
# STRIPE_SECRET_KEY=sk_your_stripe_secret_key
# PAYPAL_CLIENT_ID=your_paypal_client_id
# PAYPAL_CLIENT_SECRET=your_paypal_client_secret

# Analytics
# GOOGLE_ANALYTICS_ID=UA-your-analytics-id
# MIXPANEL_TOKEN=your_mixpanel_token

# ================================
# LOGGING CONFIGURATION
# ================================

LOG_FORMAT=json
# LOG_FILE=logs/influencerflow.log
LOG_ROTATION=daily
LOG_RETENTION_DAYS=30

# ================================
# BUSINESS CONFIGURATION
# ================================

# Campaign Defaults
DEFAULT_CAMPAIGN_DURATION_DAYS=30
DEFAULT_CONTENT_REVIEW_HOURS=48
DEFAULT_REVISION_COUNT=2

# Contract Generation
CONTRACT_TEMPLATE_DIR=templates/contracts
CONTRACT_PDF_WATERMARK=true
EMAIL_TEMPLATE_DIR=templates/emails

# Pricing
BASE_SUCCESS_RATE=0.7
MAX_RETRY_ATTEMPTS=2

# ================================
# NOTIFICATIONS PROCESSING
# ================================

NOTIFICATION_BATCH_SIZE=10
NOTIFICATION_PROCESSING_INTERVAL=30
NOTIFICATION_MAX_RETRIES=3
NOTIFICATION_RETRY_DELAY=60
"""
    
    return template

# Configuration health check
def health_check() -> Dict[str, Any]:
    """Comprehensive configuration health check"""
    
    health_status = {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "2.0.0",
        "services": {},
        "features": {},
        "recommendations": []
    }
    
    # Check core services
    health_status["services"]["groq_ai"] = {
        "status": "configured" if settings.groq_api_key else "missing_config",
        "required": True
    }
    
    health_status["services"]["elevenlabs"] = {
        "status": "configured" if settings.voice_negotiations_ready else "partial_config",
        "required": True,
        "details": {
            "api_key": bool(settings.elevenlabs_api_key),
            "agent_id": bool(settings.elevenlabs_agent_id),
            "phone_number": bool(settings.elevenlabs_phone_number_id)
        }
    }
    
    health_status["services"]["email"] = {
        "status": "configured" if settings.email_configured else "missing_config",
        "required": True,
        "details": settings.validate_email_config()
    }
    
    health_status["services"]["notifications"] = {
        "status": "configured" if settings.notifications_configured else "optional",
        "required": False,
        "channels": {
            "slack": bool(settings.slack_webhook_url),
            "webhooks": bool(settings.webhook_urls),
            "email": settings.email_configured
        }
    }
    
    # Check feature readiness
    health_status["features"]["ai_strategy"] = settings.enable_ai_strategy and bool(settings.groq_api_key)
    health_status["features"]["voice_negotiations"] = settings.enable_voice_negotiations and settings.voice_negotiations_ready
    health_status["features"]["email_delivery"] = settings.enable_email_delivery and settings.email_configured
    health_status["features"]["notifications"] = settings.enable_notifications and settings.notifications_configured
    
    # Generate recommendations
    if not settings.email_configured:
        health_status["recommendations"].append("Configure email service for contract delivery")
    
    if not settings.voice_negotiations_ready:
        health_status["recommendations"].append("Complete ElevenLabs setup for voice negotiations")
    
    if not settings.notifications_configured:
        health_status["recommendations"].append("Configure notification channels for better monitoring")
    
    if settings.debug and not settings.demo_mode:
        health_status["recommendations"].append("Disable debug mode for production")
    
    # Determine overall status
    critical_services = ["groq_ai", "elevenlabs", "email"]
    unhealthy_services = [
        name for name, service in health_status["services"].items() 
        if name in critical_services and service["status"] != "configured"
    ]
    
    if unhealthy_services:
        health_status["status"] = "degraded"
        health_status["unhealthy_services"] = unhealthy_services
    
    return health_status

if __name__ == "__main__":
    """
    Run configuration validation and debugging
    
    Usage:
    python config/settings.py
    """
    print("🔧 InfluencerFlow AI Configuration Validator")
    print("=" * 60)
    
    # Run debug
    debug_settings()
    
    # Run validation
    print("\n🔍 VALIDATION RESULTS:")
    validation = validate_environment()
    print(f"Status: {validation['overall_status']}")
    
    if validation['recommendations']:
        print("\n💡 RECOMMENDATIONS:")
        for rec in validation['recommendations']:
            print(f"   • {rec}")
    
    # Health check
    print("\n❤️ HEALTH CHECK:")
    health = health_check()
    print(f"Overall Status: {health['status']}")
    print(f"Features Ready: {sum(health['features'].values())}/{len(health['features'])}")