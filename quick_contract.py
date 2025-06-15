# quick_contract.py - Generate contract from your successful call
import requests
from datetime import datetime

def generate_contract_now():
    """Generate contract from your ElevenLabs call"""
    
    print("📋 GENERATING YOUR CONTRACT")
    print("=" * 50)
    
    # Your successful call ID
    conversation_id = "conv_01jxsbshjpfx5r1t119nexre7j"
    
    print(f"📞 Using call: {conversation_id}")
    
    try:
        # Call the API to generate contract
        response = requests.post(
            "http://127.0.0.1:8000/api/webhook/generate-contract-from-call",
            json={"conversation_id": conversation_id},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ CONTRACT GENERATED SUCCESSFULLY!")
            print(f"   Contract ID: {result['contract_id']}")
            print(f"   Creator: {result['negotiation_summary']['creator']}")
            print(f"   Amount: {result['negotiation_summary']['compensation']}")
            print(f"   Timeline: {result['negotiation_summary']['timeline']}")
            
            # Save contract to file
            contract_text = result['contract_text']
            filename = f"contract_{result['contract_id']}.txt"
            
            with open(filename, 'w') as f:
                f.write(contract_text)
            
            print(f"\n📄 Contract saved to: {filename}")
            
            # Display the contract
            print("\n📋 CONTRACT CONTENT:")
            print("-" * 50)
            print(contract_text)
            print("-" * 50)
            
            print("\n🎯 NEXT STEPS:")
            for step in result['next_steps']:
                print(f"   • {step}")
            
            return True
            
        else:
            print(f"❌ Failed to generate contract: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    generate_contract_now()