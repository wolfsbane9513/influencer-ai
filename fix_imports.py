# fix_imports.py - TARGETED IMPORT FIX SCRIPT
"""
🔧 Fix Import Issues in InfluencerFlow AI Platform

This script fixes the specific import and configuration issues identified
by the verification script.

Issues to fix:
1. Change 'models.campaign' imports to 'core.models'
2. Fix old configuration settings (use_mock_services, use_mock_services)
3. Update any remaining legacy imports
4. Clean up legacy directory

Usage:
    python fix_imports.py
"""

import os
import re
import shutil
from pathlib import Path
from typing import List, Dict

class ImportFixer:
    """
    🔧 Import and Configuration Fixer
    
    Fixes specific import issues identified in verification
    """
    
    def __init__(self):
        self.project_root = Path(".")
        self.files_fixed = []
        self.errors = []
        
        # Import mappings to fix
        self.import_mappings = {
            # Old model imports -> new core imports
            "from core.models import": "from core.models import",
            "import core.models": "import core.models",
            "core.models.": "core.models.",
            
            # Old config imports -> new core imports  
            "from core.config import": "from core.config import",
            "from core.config import": "from core.config import",
            "import core.config": "import core.config",
            "core.config.": "core.config.",
            
            # Old enhanced imports -> unified imports
            "from agents.orchestrator import": "from agents.orchestrator import",
            "from services.voice import": "from services.voice import",
            "from api.campaigns import": "from api.campaigns import",
            
            # Class name changes
            "CampaignOrchestrator": "CampaignOrchestrator",
            "VoiceService": "VoiceService",
            "campaigns_router": "campaigns_router"
        }
        
        # Old config settings to remove/replace
        self.config_fixes = {
            "use_mock_services": "use_mock_services",
            "use_mock_services": "use_mock_services",
            "settings.use_mock_services": "settings.use_mock_services",
            "settings.use_mock_services": "settings.use_mock_services"
        }
    
    def fix_all_issues(self):
        """Fix all identified import and config issues"""
        
        print("🔧 FIXING IMPORT AND CONFIGURATION ISSUES")
        print("=" * 50)
        
        # Step 1: Fix imports in Python files
        self.fix_imports_in_files()
        
        # Step 2: Fix configuration issues
        self.fix_config_issues()
        
        # Step 3: Clean up legacy directory
        self.clean_legacy_directory()
        
        # Step 4: Generate report
        self.generate_fix_report()
    
    def fix_imports_in_files(self):
        """Fix import statements in all Python files"""
        
        print("📦 Fixing import statements...")
        
        # Find all Python files (excluding backup directories)
        python_files = []
        for file_path in self.project_root.rglob("*.py"):
            # Skip backup and legacy directories
            if any(part in str(file_path) for part in ['backup_', 'legacy', '__pycache__']):
                continue
            python_files.append(file_path)
        
        print(f"   Found {len(python_files)} Python files to check")
        
        for file_path in python_files:
            try:
                # Read file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Apply import mappings
                for old_import, new_import in self.import_mappings.items():
                    if old_import in content:
                        content = content.replace(old_import, new_import)
                        print(f"   🔄 Fixed import in {file_path}: {old_import} -> {new_import}")
                
                # Apply config fixes
                for old_config, new_config in self.config_fixes.items():
                    if old_config in content:
                        content = content.replace(old_config, new_config)
                        print(f"   🔄 Fixed config in {file_path}: {old_config} -> {new_config}")
                
                # Write back if changed
                if content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.files_fixed.append(str(file_path))
                    
            except Exception as e:
                error_msg = f"Error fixing {file_path}: {e}"
                self.errors.append(error_msg)
                print(f"   ❌ {error_msg}")
    
    def fix_config_issues(self):
        """Fix specific configuration issues in core/config.py"""
        
        print("⚙️ Fixing configuration issues...")
        
        config_file = self.project_root / "core" / "config.py"
        
        if not config_file.exists():
            print("   ⚠️ core/config.py not found - may need to be created")
            return
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Remove old settings that cause validation errors
            old_settings_to_remove = [
                'use_mock_services: bool = False',
                'use_mock_services: bool = False',
                'use_mock_services: Optional[bool] = False',
                'use_mock_services: Optional[bool] = False'
            ]
            
            for old_setting in old_settings_to_remove:
                if old_setting in content:
                    content = content.replace(old_setting, '')
                    print(f"   🗑️ Removed old setting: {old_setting}")
            
            # Ensure use_mock_services exists
            if 'use_mock_services' not in content:
                # Add use_mock_services setting
                if 'class Settings' in content:
                    settings_class_pattern = r'(class Settings.*?:.*?)(class|$)'
                    match = re.search(settings_class_pattern, content, re.DOTALL)
                    if match:
                        settings_content = match.group(1)
                        if 'use_mock_services' not in settings_content:
                            # Add the setting before the class ends
                            insertion_point = settings_content.rfind('\n')
                            new_setting = '\n    use_mock_services: bool = True\n'
                            content = content[:match.start(1) + insertion_point] + new_setting + content[match.start(1) + insertion_point:]
                            print("   ✅ Added use_mock_services setting")
            
            # Write back if changed
            if content != original_content:
                with open(config_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print("   ✅ Configuration file updated")
                
        except Exception as e:
            error_msg = f"Error fixing config: {e}"
            self.errors.append(error_msg)
            print(f"   ❌ {error_msg}")
    
    def clean_legacy_directory(self):
        """Clean up legacy directory"""
        
        print("🧹 Cleaning legacy directory...")
        
        legacy_dir = self.project_root / "legacy"
        
        if legacy_dir.exists():
            try:
                shutil.rmtree(legacy_dir)
                print("   ✅ Removed legacy/ directory")
            except Exception as e:
                error_msg = f"Error removing legacy directory: {e}"
                self.errors.append(error_msg)
                print(f"   ⚠️ {error_msg}")
        else:
            print("   ℹ️ No legacy directory found")
    
    def generate_fix_report(self):
        """Generate report of fixes applied"""
        
        print("\n" + "=" * 50)
        print("📊 FIX REPORT")
        print("=" * 50)
        
        if self.files_fixed:
            print(f"\n✅ FILES FIXED ({len(self.files_fixed)}):")
            for file_path in self.files_fixed:
                print(f"   📄 {file_path}")
        else:
            print("\n✅ No files needed fixing (already clean)")
        
        if self.errors:
            print(f"\n❌ ERRORS ENCOUNTERED ({len(self.errors)}):")
            for error in self.errors:
                print(f"   ❌ {error}")
        
        print(f"\n🎯 NEXT STEPS:")
        print("   1. Run verification again: python verify_current_structure.py")
        print("   2. Test the application: python main.py")
        print("   3. Check health endpoint: curl http://localhost:8000/health")
        
        if not self.errors:
            print("\n🎉 All import issues should now be resolved!")
        else:
            print(f"\n⚠️ {len(self.errors)} errors encountered - manual review may be needed")

def main():
    """Main fix function"""
    
    fixer = ImportFixer()
    fixer.fix_all_issues()

if __name__ == "__main__":
    main()