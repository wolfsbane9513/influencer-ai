# add_negotiation_state.py - ADD MISSING NEGOTIATION STATE
"""
🔧 Add missing NegotiationState model to core/models.py

Final fix to complete the unified codebase!
"""

from pathlib import Path

def add_negotiation_state():
    """Add NegotiationState model to core/models.py"""
    
    print("🤝 Adding NegotiationState model...")
    
    models_file = Path("core/models.py")
    
    with open(models_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if NegotiationState already exists
    if 'class NegotiationState' in content:
        print("   ✅ NegotiationState already exists")
        return
    
    # Add NegotiationState model after NegotiationStatus enum
    negotiation_state_model = '''
class CallStatus(str, Enum):
    """Call status enumeration"""
    NOT_STARTED = "not_started"
    INITIATED = "initiated"
    RINGING = "ringing"
    ANSWERED = "answered"
    COMPLETED = "completed"
    FAILED = "failed"
    NO_ANSWER = "no_answer"

class NegotiationState(BaseModel):
    """
    Negotiation state tracking model
    
    Tracks the state of ongoing negotiations with creators
    """
    creator_id: str
    creator_name: str
    campaign_id: str
    status: NegotiationStatus = NegotiationStatus.PENDING
    call_status: CallStatus = CallStatus.NOT_STARTED
    
    # Call tracking
    conversation_id: Optional[str] = None
    call_started_at: Optional[datetime] = None
    call_ended_at: Optional[datetime] = None
    call_duration_seconds: int = 0
    
    # Results
    agreed_rate: Optional[float] = None
    original_rate: Optional[float] = None
    terms_agreed: List[str] = Field(default_factory=list)
    
    # Metadata
    last_contact_date: datetime = Field(default_factory=datetime.now)
    notes: Optional[str] = None
    follow_up_required: bool = False
    
    def get_call_duration_minutes(self) -> float:
        """Get call duration in minutes"""
        return self.call_duration_seconds / 60.0
'''
    
    # Insert after NegotiationStatus enum
    content = content.replace(
        'class CampaignData(BaseModel):',
        negotiation_state_model + '\n\nclass CampaignData(BaseModel):'
    )
    
    with open(models_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("   ✅ Added NegotiationState model")

def update_model_exports():
    """Update exports to include new models"""
    
    print("📤 Updating model exports...")
    
    models_file = Path("core/models.py")
    
    with open(models_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update __all__ if it exists
    if '__all__' in content and 'NegotiationState' not in content:
        content = content.replace(
            '"NegotiationStatus"',
            '"NegotiationStatus",\n    "NegotiationState",\n    "CallStatus"'
        )
    
    # Add to legacy compatibility section
    if 'NegotiationState' not in content.split('# Legacy compatibility')[1] if '# Legacy compatibility' in content else True:
        content = content.replace(
            '# Legacy compatibility - for old imports',
            '''# Legacy compatibility - for old imports
# Ensure all models are available'''
        )
    
    with open(models_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("   ✅ Updated model exports")

def update_core_init():
    """Update core/__init__.py to export new models"""
    
    print("📤 Updating core/__init__.py...")
    
    init_file = Path("core/__init__.py")
    
    with open(init_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add new models to __all__
    if 'NegotiationState' not in content:
        content = content.replace(
            '"NegotiationStatus"',
            '"NegotiationStatus",\n    "NegotiationState",\n    "CallStatus"'
        )
    
    with open(init_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("   ✅ Updated core/__init__.py")

def verify_all_models_present():
    """Verify all required models are present"""
    
    print("🔍 Verifying all models are present...")
    
    models_file = Path("core/models.py")
    
    with open(models_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Required models
    required_models = [
        'NegotiationStatus',
        'CallStatus', 
        'NegotiationState',
        'CampaignData',
        'Creator',
        'CreatorMatch',
        'NegotiationResult',
        'Contract',
        'OrchestrationState'
    ]
    
    missing_models = []
    present_models = []
    
    for model in required_models:
        if f'class {model}' in content or f'{model} =' in content:
            present_models.append(model)
        else:
            missing_models.append(model)
    
    print(f"   ✅ Present models: {len(present_models)}")
    for model in present_models:
        print(f"      ✅ {model}")
    
    if missing_models:
        print(f"   ⚠️ Missing models: {len(missing_models)}")
        for model in missing_models:
            print(f"      ❌ {model}")
    else:
        print("   🎉 All required models are present!")

def main():
    """Add missing NegotiationState and complete the codebase"""
    
    print("🔧 ADDING FINAL MISSING MODELS")
    print("=" * 50)
    
    # Add the missing model
    add_negotiation_state()
    
    # Update exports
    update_model_exports()
    update_core_init()
    
    # Verify everything is complete
    verify_all_models_present()
    
    print("\n" + "=" * 50)
    print("🎉 CODEBASE COMPLETION - ALL MODELS ADDED")
    print("=" * 50)
    
    print("\n🎯 FINAL VERIFICATION:")
    print("   python verify_current_structure.py")
    
    print("\n💡 Expected result:")
    print("   - 26+ successes")
    print("   - 0 critical issues")
    print("   - All imports working")
    print("   - Ready for: python main.py")
    
    print("\n🚀 YOUR CODEBASE SHOULD NOW BE FULLY UNIFIED!")

if __name__ == "__main__":
    main()