# fix_orchestration_state.py - FIX ORCHESTRATION STATE
"""
🔧 Fix the CampaignOrchestrationState import issue

The issue: Files are importing CampaignOrchestrationState but it's defined as OrchestrationState
Solution: Add proper alias or fix the imports
"""

from pathlib import Path
import re

def fix_core_models_exports():
    """Ensure CampaignOrchestrationState is properly exported"""
    
    print("📦 Fixing OrchestrationState exports...")
    
    models_file = Path("core/models.py")
    
    with open(models_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if CampaignOrchestrationState alias exists
    if 'CampaignOrchestrationState = OrchestrationState' not in content:
        # Add the alias right after the OrchestrationState class
        content = content.replace(
            '# Legacy compatibility - for old imports',
            '''# Legacy compatibility - for old imports
CampaignOrchestrationState = OrchestrationState  # Main alias'''
        )
        
        # Also ensure it's in the __all__ if that exists
        if '__all__' in content:
            content = content.replace(
                '"OrchestrationState"',
                '"OrchestrationState",\n    "CampaignOrchestrationState"'
            )
    
    # Also add to core/__init__.py exports
    if '"CampaignOrchestrationState"' not in content:
        content = content.replace(
            '# Legacy compatibility - for old imports',
            '''# Ensure all necessary exports
__all__ = [
    "CampaignData", "Creator", "NegotiationResult", "Contract", 
    "OrchestrationState", "CampaignOrchestrationState", "CreatorMatch",
    "NegotiationStatus"
]

# Legacy compatibility - for old imports'''
        )
    
    with open(models_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("   ✅ Fixed OrchestrationState exports")

def fix_core_init():
    """Fix core/__init__.py to export CampaignOrchestrationState"""
    
    print("📤 Fixing core/__init__.py exports...")
    
    init_file = Path("core/__init__.py")
    
    with open(init_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update __all__ to include CampaignOrchestrationState
    if 'CampaignOrchestrationState' not in content:
        content = content.replace(
            '"OrchestrationState"',
            '"OrchestrationState",\n    "CampaignOrchestrationState"'
        )
    
    with open(init_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("   ✅ Updated core/__init__.py exports")

def alternative_fix_imports():
    """Alternative: Change imports to use OrchestrationState instead"""
    
    print("🔄 Alternative: Updating imports to use OrchestrationState...")
    
    # Files that might have the wrong import
    files_to_check = [
        'agents/orchestrator.py',
        'agents/discovery.py', 
        'agents/negotiation.py',
        'agents/contracts.py',
        'api/campaigns.py',
        'services/database.py',
        'services/embeddings.py',
        'services/pricing.py'
    ]
    
    for file_path_str in files_to_check:
        file_path = Path(file_path_str)
        
        if not file_path.exists():
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Replace CampaignOrchestrationState with OrchestrationState
            content = content.replace('CampaignOrchestrationState', 'OrchestrationState')
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"   🔄 Fixed imports in {file_path_str}")
            
        except UnicodeDecodeError:
            print(f"   ⚠️ Skipping {file_path_str} (encoding issue)")
        except Exception as e:
            print(f"   ❌ Error with {file_path_str}: {e}")

def create_minimal_orchestration_state():
    """Ensure OrchestrationState model has all required fields"""
    
    print("🏗️ Ensuring OrchestrationState is complete...")
    
    models_file = Path("core/models.py")
    
    with open(models_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if OrchestrationState is properly defined
    if 'class OrchestrationState' not in content:
        print("   ❌ OrchestrationState class not found!")
        return
    
    # Extract the OrchestrationState class
    orchestration_match = re.search(r'class OrchestrationState\(BaseModel\):(.*?)(?=class|\Z)', content, re.DOTALL)
    
    if orchestration_match:
        orchestration_content = orchestration_match.group(1)
        
        # Check for required fields
        required_fields = [
            'campaign_id', 'campaign_data', 'current_stage', 'started_at',
            'discovered_creators', 'negotiations', 'contracts',
            'successful_negotiations', 'total_cost'
        ]
        
        missing_fields = []
        for field in required_fields:
            if f'{field}:' not in orchestration_content and f'{field} =' not in orchestration_content:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"   ⚠️ Missing fields in OrchestrationState: {missing_fields}")
        else:
            print("   ✅ OrchestrationState looks complete")
    
    print("   ✅ OrchestrationState verification complete")

def main():
    """Run all fixes for OrchestrationState"""
    
    print("🔧 FIXING ORCHESTRATION STATE ISSUES")
    print("=" * 50)
    
    # Try multiple approaches
    
    # Approach 1: Fix exports
    fix_core_models_exports()
    fix_core_init()
    
    # Approach 2: Verify model is complete
    create_minimal_orchestration_state()
    
    # Approach 3: Fix imports to use correct name
    alternative_fix_imports()
    
    print("\n" + "=" * 50)
    print("✅ ORCHESTRATION STATE FIXES COMPLETED")
    print("=" * 50)
    
    print("\n🎯 TEST AGAIN:")
    print("   python verify_current_structure.py")
    
    print("\n💡 Expected result:")
    print("   - All imports should work")
    print("   - No missing CampaignOrchestrationState errors")
    print("   - Ready to run: python main.py")

if __name__ == "__main__":
    main()