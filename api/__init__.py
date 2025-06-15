# api/__init__.py
"""
InfluencerFlow AI API - Unified Implementation
"""

from .campaigns import router as campaigns_router

__all__ = [
    "campaigns_router"
]
