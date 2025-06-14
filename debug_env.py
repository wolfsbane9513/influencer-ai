# debug_env.py - Debug script to check environment setup
import os
from pathlib import Path

def debug_environment():
    """Debug environment variables and .env file"""
    
    print("🔍 Environment Setup Debug")
    print("=" * 50)
    
    # Check .env file exists
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file found")
        
        # Read and check .env contents
        with open(env_file, 'r') as f:
            env_contents = f.read()
        
        print(f"📄 .env file contents ({env_file.absolute()}):")
        print("-" * 30)
        
        # Check specific keys
        keys_to_check = [
            "GROQ_API_KEY",
            "ELEVENLABS_API_KEY", 
            "ELEVENLABS_AGENT_ID",
            "ELEVENLABS_PHONE_NUMBER_ID"
        ]
        
        for line in env_contents.split('\n'):
            if line.strip() and not line.startswith('#'):
                key = line.split('=')[0]
                if key in keys_to_check:
                    value = line.split('=', 1)[1] if '=' in line else ''
                    if value and len(value) > 10:
                        print(f"✅ {key}={value[:10]}...")
                    elif value:
                        print(f"⚠️  {key}={value} (might be incomplete)")
                    else:
                        print(f"❌ {key}= (empty)")
                        
        print("-" * 30)
    else:
        print("❌ .env file not found!")
        print(f"   Expected location: {env_file.absolute()}")
        return
    
    print("\n🔧 Environment Variables (os.getenv):")
    print("-" * 30)
    for key in ["GROQ_API_KEY", "ELEVENLABS_API_KEY", "ELEVENLABS_AGENT_ID", "ELEVENLABS_PHONE_NUMBER_ID"]:
        value = os.getenv(key)
        if value:
            print(f"✅ {key}: {value[:10]}..." if len(value) > 10 else f"✅ {key}: {value}")
        else:
            print(f"❌ {key}: Not set")
    
    print("\n🎯 Pydantic Settings Test:")
    print("-" * 30)
    try:
        from config.settings import settings
        
        # Test settings
        checks = [
            ("groq_api_key", settings.groq_api_key),
            ("elevenlabs_api_key", settings.elevenlabs_api_key),
            ("elevenlabs_agent_id", settings.elevenlabs_agent_id),
            ("elevenlabs_phone_number_id", settings.elevenlabs_phone_number_id)
        ]
        
        for name, value in checks:
            if value:
                display_value = value[:10] + "..." if len(str(value)) > 10 else str(value)
                print(f"✅ settings.{name}: {display_value}")
            else:
                print(f"❌ settings.{name}: None/Empty")
                
    except Exception as e:
        print(f"❌ Settings import failed: {e}")
    
    print("\n📋 Setup Instructions:")
    print("-" * 30)
    print("1. Ensure .env file is in the same directory as main.py")
    print("2. Add these lines to your .env file:")
    print("   GROQ_API_KEY=gsk_your_groq_key_here")
    print("   ELEVENLABS_API_KEY=sk_your_elevenlabs_key_here")
    print("   ELEVENLABS_AGENT_ID=your_agent_id_here")
    print("   ELEVENLABS_PHONE_NUMBER_ID=your_phone_id_here")
    print("3. Restart your server: python main.py")
    print("4. Test with: curl http://localhost:8000/api/webhook/test-elevenlabs")

if __name__ == "__main__":
    debug_environment()
