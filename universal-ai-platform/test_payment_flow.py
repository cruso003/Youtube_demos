#!/usr/bin/env python3
"""
Test the complete payment flow with polling
"""

import requests
import time
import json

def test_payment_flow():
    """Test the complete payment flow"""
    
    print("🔍 Testing Complete Payment Flow (with polling)...")
    print("⚠️  This will initiate a real payment and wait for completion")
    
    # Test data
    test_data = {
        "phone_number": "+231881158457",
        "amount": 0.10,  # $0.10 minimum
        "user_id": "test_user_poll"
    }
    
    print(f"🚀 Initiating payment: ${test_data['amount']} to {test_data['phone_number']}")
    
    # Make payment request
    response = requests.post(
        "http://localhost:8000/api/v1/credits/purchase",
        json=test_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"📱 Response Status: {response.status_code}")
    print(f"📄 Response Body: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            print("✅ Payment completed successfully!")
            print(f"   Credits added: {result.get('credits')}")
            print(f"   Transaction ID: {result.get('transaction_id')}")
        else:
            print("❌ Payment failed:", result.get('error'))
    else:
        print("❌ API request failed")

if __name__ == "__main__":
    print("🚨 LIVE PAYMENT TEST - This will charge real money!")
    confirm = input("Continue with live payment test? (y/N): ")
    
    if confirm.lower() == 'y':
        test_payment_flow()
    else:
        print("Test cancelled")
