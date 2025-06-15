# fix_discovery_agent.py - FIX MISSING DISCOVERY AGENT
"""
🔧 Add missing DiscoveryAgent class to agents/discovery.py

The issue: Files are trying to import DiscoveryAgent but it's not defined
Solution: Create a minimal DiscoveryAgent class or fix the class name
"""

from pathlib import Path

def fix_discovery_agent():
    """Fix the DiscoveryAgent class in agents/discovery.py"""
    
    print("🔍 Fixing DiscoveryAgent...")
    
    discovery_file = Path("agents/discovery.py")
    
    if not discovery_file.exists():
        print("   ❌ agents/discovery.py not found - creating it...")
        create_discovery_file()
        return
    
    try:
        with open(discovery_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        print("   ⚠️ Encoding issue - creating new file...")
        create_discovery_file()
        return
    
    # Check if DiscoveryAgent class exists
    if 'class DiscoveryAgent' in content:
        print("   ✅ DiscoveryAgent class already exists")
        return
    
    # Check if there's a different class name we need to fix
    if 'class InfluencerDiscoveryAgent' in content:
        print("   🔄 Found InfluencerDiscoveryAgent - adding DiscoveryAgent alias...")
        content += '\n\n# Legacy compatibility\nDiscoveryAgent = InfluencerDiscoveryAgent\n'
        
        with open(discovery_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("   ✅ Added DiscoveryAgent alias")
        return
    
    # If no agent class exists, add a minimal one
    print("   🏗️ Adding DiscoveryAgent class...")
    
    discovery_class = '''

class DiscoveryAgent:
    """
    🔍 Creator Discovery Agent
    
    Finds and matches creators for campaigns
    """
    
    def __init__(self):
        logger.info("🔍 Discovery Agent initialized")
    
    async def find_creators(
        self, 
        product_niche: str,
        target_audience: str, 
        budget: float,
        max_creators: int = 10
    ) -> List[Creator]:
        """
        Find creators matching campaign criteria
        
        Args:
            product_niche: Product niche (fitness, beauty, etc.)
            target_audience: Target audience description
            budget: Total campaign budget
            max_creators: Maximum number of creators to return
            
        Returns:
            List of matching creators
        """
        logger.info(f"🔍 Searching for {product_niche} creators...")
        
        # TODO: Implement actual creator discovery logic
        # For now, return empty list
        return []
'''
    
    content += discovery_class
    
    with open(discovery_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("   ✅ Added DiscoveryAgent class")

def create_discovery_file():
    """Create a complete agents/discovery.py file"""
    
    print("   🏗️ Creating complete agents/discovery.py...")
    
    discovery_content = '''# agents/discovery.py - CREATOR DISCOVERY AGENT
import logging
from typing import List, Dict, Any, Optional
from core.models import Creator, CampaignData
from core.config import settings

logger = logging.getLogger(__name__)

class DiscoveryAgent:
    """
    🔍 Creator Discovery Agent
    
    Finds and matches creators for campaigns using AI-powered matching
    """
    
    def __init__(self):
        self.initialized = True
        logger.info("🔍 Discovery Agent initialized")
    
    async def find_creators(
        self, 
        product_niche: str,
        target_audience: str, 
        budget: float,
        max_creators: int = 10
    ) -> List[Creator]:
        """
        Find creators matching campaign criteria
        
        Args:
            product_niche: Product niche (fitness, beauty, etc.)
            target_audience: Target audience description
            budget: Total campaign budget
            max_creators: Maximum number of creators to return
            
        Returns:
            List of matching creators
        """
        logger.info(f"🔍 Searching for {product_niche} creators...")
        logger.info(f"📊 Budget: ${budget}, Max creators: {max_creators}")
        
        # TODO: Implement actual creator discovery logic
        # This would typically:
        # 1. Load creator database
        # 2. Filter by niche and engagement
        # 3. Calculate match scores
        # 4. Return top matches within budget
        
        # For now, return sample creators for testing
        sample_creators = self._get_sample_creators(product_niche, max_creators)
        
        logger.info(f"✅ Found {len(sample_creators)} matching creators")
        return sample_creators
    
    def _get_sample_creators(self, niche: str, max_creators: int) -> List[Creator]:
        """Get sample creators for testing"""
        
        sample_creators = [
            Creator(
                id="creator_001",
                name="Sample Creator 1",
                handle="@sample_creator_1",
                followers=50000,
                engagement_rate=4.2,
                niche=niche,
                rate_per_post=800.0,
                contact_email="creator1@example.com",
                phone_number="+1-555-0001"
            ),
            Creator(
                id="creator_002", 
                name="Sample Creator 2",
                handle="@sample_creator_2",
                followers=75000,
                engagement_rate=3.8,
                niche=niche,
                rate_per_post=1200.0,
                contact_email="creator2@example.com",
                phone_number="+1-555-0002"
            ),
            Creator(
                id="creator_003",
                name="Sample Creator 3", 
                handle="@sample_creator_3",
                followers=30000,
                engagement_rate=5.1,
                niche=niche,
                rate_per_post=600.0,
                contact_email="creator3@example.com",
                phone_number="+1-555-0003"
            )
        ]
        
        return sample_creators[:max_creators]

# Legacy compatibility
InfluencerDiscoveryAgent = DiscoveryAgent
'''
    
    discovery_file = Path("agents/discovery.py")
    
    with open(discovery_file, 'w', encoding='utf-8') as f:
        f.write(discovery_content)
    
    print("   ✅ Created complete agents/discovery.py")

def update_agents_init():
    """Update agents/__init__.py to export DiscoveryAgent"""
    
    print("📤 Updating agents/__init__.py...")
    
    init_file = Path("agents/__init__.py")
    
    if not init_file.exists():
        print("   ❌ agents/__init__.py not found")
        return
    
    with open(init_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if DiscoveryAgent is already imported
    if 'from .discovery import DiscoveryAgent' in content:
        print("   ✅ DiscoveryAgent already in __init__.py")
        return
    
    # Add DiscoveryAgent import if missing
    if 'DiscoveryAgent' not in content:
        content = content.replace(
            'from .orchestrator import CampaignOrchestrator',
            '''from .orchestrator import CampaignOrchestrator
from .discovery import DiscoveryAgent'''
        )
        
        content = content.replace(
            '"CampaignOrchestrator",',
            '''    "CampaignOrchestrator",
    "DiscoveryAgent",'''
        )
        
        with open(init_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("   ✅ Added DiscoveryAgent to agents/__init__.py")

def main():
    """Fix DiscoveryAgent issues"""
    
    print("🔧 FIXING DISCOVERY AGENT ISSUES")
    print("=" * 50)
    
    # Fix the discovery agent
    fix_discovery_agent()
    
    # Update exports
    update_agents_init()
    
    print("\n" + "=" * 50)
    print("✅ DISCOVERY AGENT FIXES COMPLETED")
    print("=" * 50)
    
    print("\n🎯 TEST AGAIN:")
    print("   python verify_current_structure.py")
    
    print("\n💡 Expected result:")
    print("   - All DiscoveryAgent imports should work")
    print("   - Should see 26+ successes")
    print("   - Ready to run: python main.py")

if __name__ == "__main__":
    main()