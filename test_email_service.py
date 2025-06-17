#!/usr/bin/env python3
"""
Test script for the Email Service
Run this to test if your SendGrid integration is working correctly
"""

import asyncio
import logging
from services.email_service import email_service
from services.contract_service import contract_service

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_email_service():
    """Test the email service functionality"""
    
    print("🧪 Testing Email Service...")
    print("=" * 50)
    
    # Test data - UPDATE THIS WITH YOUR REAL EMAIL ADDRESS
    test_email = "your-email@example.com"  # 🚨 CHANGE THIS TO YOUR REAL EMAIL
    test_name = "John Doe"
    
    print(f"📧 Testing with email: {test_email}")
    print("⚠️  Make sure to update test_email with your real email address!")
    
    # Test 1: Simple notification email
    print("\n📧 Test 1: Sending notification email...")
    success = await email_service.send_notification_email(
        to_email=test_email,
        subject="🧪 Test Email from InfluencerFlow AI",
        message="This is a test email to verify your SendGrid integration is working correctly!"
    )
    
    if success:
        print("✅ Notification email test PASSED")
    else:
        print("❌ Notification email test FAILED")
    
    # Test 2: Contract email
    print("\n📋 Test 2: Sending contract email...")
    
    # Sample contract content
    contract_content = """
SAMPLE INFLUENCER COLLABORATION CONTRACT
Contract ID: TEST-12345
Generated: 2024-01-15 10:30:00

═══════════════════════════════════════════════════════════════

PARTIES:
Brand: Test Brand Inc.
Influencer: John Doe (test@example.com)

CAMPAIGN DETAILS:
Campaign Name: Test Product Launch
Campaign Budget: $5,000
Agreed Rate: $1,500

DELIVERABLES:
• 1 Instagram post
• 3 Instagram stories
• 1 TikTok video

TIMELINE:
Start Date: 2024-01-22
End Date: 2024-02-05
Duration: 2 weeks

This is a test contract for demonstration purposes.
    """
    
    campaign_details = {
        "campaign_name": "Test Product Launch",
        "brand_name": "Test Brand Inc.",
        "budget": 5000,
        "deliverables": ["1 Instagram post", "3 Instagram stories", "1 TikTok video"],
        "timeline": "2 weeks"
    }
    
    success = await email_service.send_contract_email(
        to_email=test_email,
        to_name=test_name,
        contract_content=contract_content,
        campaign_details=campaign_details,
        contract_filename="Test_Contract_20240115.txt"
    )
    
    if success:
        print("✅ Contract email test PASSED")
    else:
        print("❌ Contract email test FAILED")
    
    # Test 3: Full contract service workflow
    print("\n🔄 Test 3: Testing full contract service workflow...")
    
    call_data = {
        "agreed_rate": 1500,
        "special_terms": ["Exclusive content", "Usage rights for 1 year"],
        "contract_id": "TEST-WORKFLOW-001"
    }
    
    influencer_data = {
        "name": test_name,
        "email": test_email,
        "id": "test_influencer_123"
    }
    
    campaign_data = {
        "campaign_name": "Test Workflow Campaign",
        "brand_name": "Test Workflow Brand",
        "budget": 3000,
        "deliverables": ["2 Instagram posts", "5 Stories"],
        "timeline": "3 weeks",
        "offered_rate": 1500
    }
    
    success = await contract_service.process_successful_call(
        call_data=call_data,
        influencer_data=influencer_data,
        campaign_data=campaign_data
    )
    
    if success:
        print("✅ Contract service workflow test PASSED")
    else:
        print("❌ Contract service workflow test FAILED")
    
    print("\n" + "=" * 50)
    print("🏁 Email service testing completed!")
    print("\nIf you see ✅ for all tests, your email service is working correctly!")
    print("If you see ❌, check your SendGrid configuration in your .env file.")

def main():
    """Main function to run the tests"""
    print("🚀 Starting Email Service Tests...")
    print("Make sure you have set up your SendGrid API key in your .env file!")
    print("Update the test_email variable in this script to use your email address.")
    
    # Run the async test
    asyncio.run(test_email_service())

if __name__ == "__main__":
    main() 