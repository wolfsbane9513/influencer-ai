# core/__init__.py
"""
InfluencerFlow AI Platform - Core Module

Unified core components for the platform:
- models: Data models and schemas
- config: Application configuration
- exceptions: Custom exception classes
- utils: Utility functions
"""

from .models import *
from .config import settings

__all__ = [
    "settings",
    "CampaignData",
    "Creator", 
    "NegotiationResult",
    "Contract",
    "OrchestrationState",
    "CampaignOrchestrationState"
]
