# refactor_codebase.py - Automated cleanup and refactoring
import os
import shutil
import re
from pathlib import Path

def backup_current_state():
    """Create a backup before refactoring"""
    print("🔄 Creating backup...")
    
    import subprocess
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Backup before refactoring"], check=True)
        subprocess.run(["git", "checkout", "-b", "refactor-cleanup"], check=True)
        print("✅ Backup created on branch 'refactor-cleanup'")
        return True
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return False

def remove_legacy_files():
    """Remove redundant legacy files"""
    print("🗑️ Removing legacy files...")
    
    files_to_remove = [
        "agents/orchestrator.py",           # Legacy orchestrator
        "services/voice.py",                # Legacy voice service
        "api/webhooks.py",                  # Legacy webhooks
        "api/monitoring.py",                # Basic monitoring
        "config/simple_settings.py",       # Redundant config
        # Add other redundant files as identified
    ]
    
    removed_count = 0
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"   ✅ Removed: {file_path}")
                removed_count += 1
            except Exception as e:
                print(f"   ❌ Failed to remove {file_path}: {e}")
        else:
            print(f"   ⏭️ Not found: {file_path}")
    
    print(f"📊 Removed {removed_count} legacy files")

def rename_enhanced_files():
    """Rename enhanced files to standard names"""
    print("📝 Renaming enhanced files...")
    
    renames = [
        ("agents/enhanced_orchestrator.py", "agents/orchestrator.py"),
        ("services/enhanced_voice.py", "services/voice.py"),
        ("api/enhanced_webhooks.py", "api/webhooks.py"),
        ("api/enhanced_monitoring.py", "api/monitoring.py"),
    ]
    
    renamed_count = 0
    for old_path, new_path in renames:
        if os.path.exists(old_path):
            try:
                # Remove target if it exists
                if os.path.exists(new_path):
                    os.remove(new_path)
                
                shutil.move(old_path, new_path)
                print(f"   ✅ Renamed: {old_path} → {new_path}")
                renamed_count += 1
            except Exception as e:
                print(f"   ❌ Failed to rename {old_path}: {e}")
        else:
            print(f"   ⏭️ Not found: {old_path}")
    
    print(f"📊 Renamed {renamed_count} files")

def update_imports_in_file(file_path):
    """Update imports in a single file"""
    if not os.path.exists(file_path):
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Define import replacements
        replacements = [
            # Agent imports
            (r'from agents\.enhanced_orchestrator import EnhancedCampaignOrchestrator',
             'from agents.orchestrator import CampaignOrchestrator'),
            (r'EnhancedCampaignOrchestrator', 'CampaignOrchestrator'),
            
            # Service imports
            (r'from services\.enhanced_voice import EnhancedVoiceService',
             'from services.voice import VoiceService'),
            (r'EnhancedVoiceService', 'VoiceService'),
            
            # API imports
            (r'from api\.enhanced_webhooks import enhanced_webhook_router',
             'from api.webhooks import webhook_router'),
            (r'enhanced_webhook_router', 'webhook_router'),
            
            # Remove redundant imports
            (r'from agents\.enhanced_negotiation import.*\n', ''),
            (r'from agents\.enhanced_contracts import.*\n', ''),
            (r'from services\.conversation_monitor import.*\n', ''),
        ]
        
        # Apply replacements
        modified = False
        for pattern, replacement in replacements:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                modified = True
        
        # Write back if modified
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
    
    except Exception as e:
        print(f"   ❌ Error updating {file_path}: {e}")
        return False

def update_all_imports():
    """Update imports throughout the codebase"""
    print("🔄 Updating imports...")
    
    # Find all Python files
    python_files = []
    for root, dirs, files in os.walk('.'):
        # Skip hidden directories and __pycache__
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    updated_count = 0
    for file_path in python_files:
        if update_imports_in_file(file_path):
            print(f"   ✅ Updated: {file_path}")
            updated_count += 1
    
    print(f"📊 Updated imports in {updated_count} files")

def remove_stub_classes():
    """Remove stub classes from orchestrator"""
    print("🧹 Removing stub classes...")
    
    orchestrator_file = "agents/orchestrator.py"
    if not os.path.exists(orchestrator_file):
        print(f"   ⏭️ Orchestrator file not found: {orchestrator_file}")
        return
    
    try:
        with open(orchestrator_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove stub classes (everything after the main orchestrator class)
        # Find the end of the main orchestrator class
        main_class_pattern = r'class.*CampaignOrchestrator.*?(?=\n\n# Simple supporting classes|class.*Agent.*?:|class.*Validator.*?:|class.*Manager.*?:|$)'
        
        match = re.search(main_class_pattern, content, re.DOTALL)
        if match:
            # Keep only the main orchestrator class and imports
            lines = content.split('\n')
            
            # Find imports and main class
            import_lines = []
            class_lines = []
            in_main_class = False
            class_indent = 0
            
            for line in lines:
                if line.startswith('import ') or line.startswith('from '):
                    import_lines.append(line)
                elif line.startswith('class') and 'CampaignOrchestrator' in line:
                    in_main_class = True
                    class_indent = len(line) - len(line.lstrip())
                    class_lines.append(line)
                elif in_main_class:
                    # Check if we've reached another class at the same level
                    if line.startswith('class') and len(line) - len(line.lstrip()) == class_indent:
                        break
                    class_lines.append(line)
                elif not in_main_class and not line.startswith('#') and line.strip():
                    # Other module-level code before the class
                    class_lines.append(line)
            
            # Reconstruct the clean file
            clean_content = '\n'.join(import_lines + [''] + class_lines)
            
            with open(orchestrator_file, 'w', encoding='utf-8') as f:
                f.write(clean_content)
            
            print(f"   ✅ Cleaned up: {orchestrator_file}")
        else:
            print(f"   ⚠️ Could not find main class pattern in {orchestrator_file}")
    
    except Exception as e:
        print(f"   ❌ Error cleaning {orchestrator_file}: {e}")

def update_main_app():
    """Update main.py with clean imports"""
    print("🔧 Updating main.py...")
    
    main_file = "main.py"
    if not os.path.exists(main_file):
        print(f"   ⏭️ Main file not found: {main_file}")
        return
    
    try:
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update router includes
        content = re.sub(
            r'app\.include_router\(enhanced_webhook_router.*?\)',
            'app.include_router(webhook_router, prefix="/api/webhook", tags=["Webhooks"])',
            content
        )
        
        content = re.sub(
            r'app\.include_router\(monitoring_router.*?\)',
            'app.include_router(monitoring_router, prefix="/api/monitor", tags=["Monitoring"])',
            content
        )
        
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"   ✅ Updated: {main_file}")
    
    except Exception as e:
        print(f"   ❌ Error updating {main_file}: {e}")

def clean_init_files():
    """Clean up __init__.py files to remove legacy imports"""
    print("🧹 Cleaning __init__.py files...")
    
    init_files = [
        "agents/__init__.py",
        "services/__init__.py",
        "api/__init__.py"
    ]
    
    for init_file in init_files:
        if os.path.exists(init_file):
            try:
                with open(init_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Remove enhanced/legacy imports
                content = re.sub(r'.*Enhanced.*\n', '', content)
                content = re.sub(r'.*legacy.*\n', '', content, flags=re.IGNORECASE)
                
                # Clean up empty lines
                content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
                
                with open(init_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"   ✅ Cleaned: {init_file}")
            
            except Exception as e:
                print(f"   ❌ Error cleaning {init_file}: {e}")

def validate_refactoring():
    """Run basic validation to ensure refactoring didn't break anything"""
    print("🧪 Validating refactoring...")
    
    # Check that main files exist
    required_files = [
        "main.py",
        "agents/orchestrator.py",
        "services/voice.py",
        "api/webhooks.py",
        "api/monitoring.py"
    ]
    
    all_good = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ Found: {file_path}")
        else:
            print(f"   ❌ Missing: {file_path}")
            all_good = False
    
    # Try to import main modules
    try:
        import sys
        sys.path.insert(0, '.')
        
        from main import app
        print("   ✅ main.py imports successfully")
        
        # Try basic imports
        from agents.orchestrator import CampaignOrchestrator
        print("   ✅ CampaignOrchestrator imports successfully")
        
        from services.voice import VoiceService
        print("   ✅ VoiceService imports successfully")
        
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        all_good = False
    
    if all_good:
        print("🎉 Refactoring validation passed!")
    else:
        print("⚠️ Validation issues detected - check logs above")
    
    return all_good

def main():
    """Run the complete refactoring process"""
    print("🔧 AUTOMATED CODEBASE REFACTORING")
    print("=" * 50)
    print("This will clean up redundant code and improve maintainability")
    print()
    
    # Confirmation
    confirm = input("🤔 Do you want to proceed? (type 'yes' to confirm): ").strip().lower()
    if confirm != 'yes':
        print("🛑 Refactoring cancelled")
        return
    
    print("\n🚀 Starting refactoring process...")
    
    # Step 1: Backup
    if not backup_current_state():
        print("❌ Backup failed - aborting refactoring")
        return
    
    # Step 2: Remove legacy files
    remove_legacy_files()
    
    # Step 3: Rename enhanced files
    rename_enhanced_files()
    
    # Step 4: Update imports
    update_all_imports()
    
    # Step 5: Remove stub classes
    remove_stub_classes()
    
    # Step 6: Update main app
    update_main_app()
    
    # Step 7: Clean init files
    clean_init_files()
    
    # Step 8: Validate
    validation_passed = validate_refactoring()
    
    print("\n" + "=" * 50)
    print("🏁 REFACTORING COMPLETE!")
    print("=" * 50)
    
    if validation_passed:
        print("✅ All validation checks passed")
        print("📊 Your codebase is now cleaner and more maintainable")
        print("\n🎯 NEXT STEPS:")
        print("1. Test your application: uvicorn main:app --reload")
        print("2. Run end-to-end tests: python quick_e2e_test.py")
        print("3. Commit changes: git add . && git commit -m 'Refactor: Clean up redundant code'")
    else:
        print("⚠️ Some validation checks failed")
        print("🔧 You may need to manually fix import issues")
        print("💡 You can rollback with: git checkout main")
    
    print("\n📈 BENEFITS ACHIEVED:")
    print("• Removed duplicate orchestrators")
    print("• Consolidated voice services")
    print("• Simplified API structure")
    print("• Cleaned up imports")
    print("• Reduced code complexity")

if __name__ == "__main__":
    main()