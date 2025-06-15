# verify_current_structure.py - QUICK STRUCTURE VERIFICATION
"""
🔍 Quick verification script to check if your codebase is already unified

This script tests whether your codebase is already aligned with our 
refactoring plan or if cleanup is still needed.

Usage:
    python verify_current_structure.py

Results:
- ✅ UNIFIED: Your codebase is already clean!
- ⚠️ MIXED: Some cleanup needed
- ❌ NEEDS REFACTORING: Major work required
"""

import sys
import os
from pathlib import Path

class StructureVerifier:
    """
    🔍 Codebase Structure Verifier
    
    Checks if the current structure matches our unified design
    """
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.successes = []
        
    def verify_all(self):
        """Run complete verification"""
        
        print("🔍 VERIFYING CURRENT CODEBASE STRUCTURE")
        print("=" * 50)
        
        # Test imports
        self.test_core_imports()
        self.test_agent_imports() 
        self.test_service_imports()
        self.test_api_imports()
        
        # Test file structure
        self.test_file_structure()
        
        # Test for legacy pollution
        self.test_legacy_pollution()
        
        # Generate report
        self.generate_report()
    
    def test_core_imports(self):
        """Test core module imports"""
        
        print("\n📦 Testing Core Module...")
        
        try:
            # Test basic core import
            sys.path.insert(0, '.')
            
            # Test config import
            try:
                from core.config import settings
                self.successes.append("✅ core.config imports successfully")
            except ImportError as e:
                self.issues.append(f"❌ core.config import failed: {e}")
            
            # Test models import
            try:
                from core.models import CampaignData
                self.successes.append("✅ core.models imports successfully")
            except ImportError as e:
                self.issues.append(f"❌ core.models import failed: {e}")
                
        except Exception as e:
            self.issues.append(f"❌ Core module completely broken: {e}")
    
    def test_agent_imports(self):
        """Test agent module imports"""
        
        print("🤖 Testing Agent Module...")
        
        try:
            # Test unified orchestrator
            try:
                from agents.orchestrator import CampaignOrchestrator
                self.successes.append("✅ agents.orchestrator imports successfully")
            except ImportError as e:
                self.issues.append(f"❌ agents.orchestrator import failed: {e}")
            
            # Test other agents
            agent_files = ['discovery', 'negotiation', 'contracts']
            for agent in agent_files:
                try:
                    module = __import__(f'agents.{agent}', fromlist=[''])
                    self.successes.append(f"✅ agents.{agent} imports successfully")
                except ImportError as e:
                    self.warnings.append(f"⚠️ agents.{agent} import failed: {e}")
                    
        except Exception as e:
            self.issues.append(f"❌ Agent module completely broken: {e}")
    
    def test_service_imports(self):
        """Test service module imports"""
        
        print("🔧 Testing Service Module...")
        
        try:
            # Test unified voice service
            try:
                from services.voice import VoiceService
                self.successes.append("✅ services.voice imports successfully")
            except ImportError as e:
                self.issues.append(f"❌ services.voice import failed: {e}")
            
            # Test other services
            service_files = ['database', 'embeddings', 'pricing']
            for service in service_files:
                try:
                    module = __import__(f'services.{service}', fromlist=[''])
                    self.successes.append(f"✅ services.{service} imports successfully")
                except ImportError as e:
                    self.warnings.append(f"⚠️ services.{service} import failed: {e}")
                    
        except Exception as e:
            self.issues.append(f"❌ Service module completely broken: {e}")
    
    def test_api_imports(self):
        """Test API module imports"""
        
        print("🌐 Testing API Module...")
        
        try:
            # Test unified campaigns API
            try:
                from api.campaigns import router
                self.successes.append("✅ api.campaigns imports successfully")
            except ImportError as e:
                self.issues.append(f"❌ api.campaigns import failed: {e}")
                
        except Exception as e:
            self.issues.append(f"❌ API module completely broken: {e}")
    
    def test_file_structure(self):
        """Test file structure matches unified design"""
        
        print("📁 Testing File Structure...")
        
        # Expected unified structure
        expected_structure = {
            'core': ['__init__.py', 'models.py', 'config.py'],
            'agents': ['__init__.py', 'orchestrator.py', 'discovery.py', 'negotiation.py', 'contracts.py'],
            'services': ['__init__.py', 'voice.py', 'database.py', 'embeddings.py', 'pricing.py'],
            'api': ['__init__.py', 'campaigns.py'],
            '.': ['main.py', 'pyproject.toml']
        }
        
        for directory, files in expected_structure.items():
            dir_path = Path(directory) if directory != '.' else Path('.')
            
            if not dir_path.exists() and directory != '.':
                self.issues.append(f"❌ Missing directory: {directory}/")
                continue
                
            for file_name in files:
                file_path = dir_path / file_name
                if file_path.exists():
                    self.successes.append(f"✅ Found: {directory}/{file_name}")
                else:
                    self.warnings.append(f"⚠️ Missing: {directory}/{file_name}")
    
    def test_legacy_pollution(self):
        """Test for legacy/duplicate files that should be removed"""
        
        print("🧹 Testing for Legacy Pollution...")
        
        # Files that should NOT exist in unified architecture
        legacy_patterns = [
            'agents/enhanced_*.py',
            'services/enhanced_*.py', 
            'api/enhanced_*.py',
            'config/simple_settings.py',
            'config/settings.py',  # Should be core/config.py
            'models/campaign.py',  # Should be core/models.py
            'test_setup.py',
            'simple_test.py',
            'setup.py'
        ]
        
        # Directories that should NOT exist
        legacy_dirs = [
            'backup_*',
            'cleanup_backup_*',
            'legacy',
            'archive'
        ]
        
        # Check for legacy files
        for pattern in legacy_patterns:
            matching_files = list(Path('.').glob(pattern))
            for file_path in matching_files:
                self.warnings.append(f"⚠️ Legacy file found: {file_path}")
        
        # Check for legacy directories
        for pattern in legacy_dirs:
            matching_dirs = list(Path('.').glob(pattern))
            for dir_path in matching_dirs:
                if dir_path.is_dir():
                    self.warnings.append(f"⚠️ Legacy directory found: {dir_path}/")
    
    def generate_report(self):
        """Generate final verification report"""
        
        print("\n" + "=" * 50)
        print("📊 VERIFICATION REPORT")
        print("=" * 50)
        
        # Show successes
        if self.successes:
            print(f"\n✅ SUCCESSES ({len(self.successes)}):")
            for success in self.successes[:5]:  # Show first 5
                print(f"   {success}")
            if len(self.successes) > 5:
                print(f"   ... and {len(self.successes) - 5} more")
        
        # Show warnings
        if self.warnings:
            print(f"\n⚠️ WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   {warning}")
        
        # Show critical issues
        if self.issues:
            print(f"\n❌ CRITICAL ISSUES ({len(self.issues)}):")
            for issue in self.issues:
                print(f"   {issue}")
        
        # Overall status
        print(f"\n🎯 OVERALL STATUS:")
        
        if not self.issues and not self.warnings:
            print("   🎉 PERFECTLY UNIFIED! Your codebase is clean.")
            print("   💡 Action: Just remove any backup directories")
            
        elif not self.issues and self.warnings:
            print("   ✅ MOSTLY UNIFIED with minor cleanup needed")
            print("   💡 Action: Run cleanup script to remove legacy files")
            
        elif len(self.issues) <= 2:
            print("   ⚠️ PARTIALLY UNIFIED with some missing files")
            print("   💡 Action: Create missing unified files")
            
        else:
            print("   ❌ NEEDS MAJOR REFACTORING")
            print("   💡 Action: Run complete refactoring process")
        
        # Quick fix commands
        print(f"\n🚀 QUICK FIXES:")
        
        if any("backup_" in w or "cleanup_backup_" in w for w in self.warnings):
            print("   # Remove backup pollution:")
            print("   rm -rf backup_* cleanup_backup_*")
        
        if any("enhanced_" in w for w in self.warnings):
            print("   # Remove enhanced/legacy files:")
            print("   python cleanup_project.py --all")
        
        if not self.issues:
            print("   # Verify everything works:")
            print("   python main.py")

def main():
    """Main verification function"""
    
    verifier = StructureVerifier()
    verifier.verify_all()

if __name__ == "__main__":
    main()