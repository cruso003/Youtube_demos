"""
End-to-End Testing Script for NexusAI Credit System
Tests: Credit Purchase → API Usage → Credit Deduction
"""

import requests
import json
import time
import sys

# Configuration
DASHBOARD_URL = "http://localhost:3000"
PAYMENT_SERVICE_URL = "http://localhost:8000"
AI_SERVICE_URL = "http://localhost:8001"  # Assuming AI service runs on 8001

def test_payment_service():
    """Test if payment service is running"""
    print("🔍 Testing Payment Service...")
    try:
        response = requests.get(f"{PAYMENT_SERVICE_URL}/health")
        if response.status_code == 200:
            print("✅ Payment service is healthy")
            return True
        else:
            print("❌ Payment service is not responding correctly")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Payment service is not running")
        return False

def test_dashboard_api():
    """Test if dashboard API is accessible"""
    print("🔍 Testing Dashboard API...")
    try:
        response = requests.get(f"{DASHBOARD_URL}/api/health")
        if response.status_code == 200:
            print("✅ Dashboard API is accessible")
            return True
        else:
            print("❌ Dashboard API not responding")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Dashboard is not running")
        return False

def simulate_credit_purchase():
    """Simulate a credit purchase flow"""
    print("💳 Simulating Credit Purchase...")
    
    # This would normally require authentication
    # For testing, we'll simulate the payment webhook directly
    
    webhook_data = {
        "transaction_id": "mtn_test_12345",
        "reference_id": "tx_test_123",
        "status": "completed",
        "amount": 9.00,
        "currency": "USD",
        "message": "Payment successful"
    }
    
    try:
        response = requests.post(f"{DASHBOARD_URL}/api/webhooks/mtn", json=webhook_data)
        if response.status_code == 200:
            print("✅ Credit purchase webhook processed successfully")
            return True
        else:
            print(f"❌ Webhook failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Webhook error: {str(e)}")
        return False

def test_api_key_usage(api_key):
    """Test API usage with credit deduction"""
    print(f"🔑 Testing API Key Usage: {api_key[:12]}...")
    
    usage_data = {
        "api_key": api_key,
        "endpoint": "/v1/chat/completions",
        "tokens_used": 150,
        "requests_count": 1,
        "model": "gpt-3.5-turbo",
        "cost": 0.003
    }
    
    try:
        response = requests.post(f"{DASHBOARD_URL}/api/usage", json=usage_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Usage recorded successfully")
            print(f"   Credits used: {result.get('credits_used', 0)}")
            print(f"   Credits remaining: {result.get('credits_remaining', 0)}")
            return True
        elif response.status_code == 402:
            print("❌ Insufficient credits!")
            return False
        elif response.status_code == 401:
            print("❌ Invalid API key!")
            return False
        else:
            print(f"❌ Usage tracking failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Usage tracking error: {str(e)}")
        return False

def test_credit_insufficient(api_key):
    """Test behavior when credits are insufficient"""
    print("💸 Testing Insufficient Credits Scenario...")
    
    # Try to use way more tokens than available credits
    usage_data = {
        "api_key": api_key,
        "endpoint": "/v1/chat/completions",
        "tokens_used": 1000000,  # 1M tokens = 1000 credits
        "requests_count": 1,
        "model": "gpt-4",
        "cost": 30.0
    }
    
    try:
        response = requests.post(f"{DASHBOARD_URL}/api/usage", json=usage_data)
        
        if response.status_code == 402:
            result = response.json()
            print("✅ Correctly blocked due to insufficient credits")
            print(f"   Credits available: {result.get('credits_available', 0)}")
            print(f"   Credits needed: {result.get('credits_needed', 0)}")
            return True
        else:
            print(f"❌ Should have been blocked: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing insufficient credits: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting NexusAI End-to-End Testing")
    print("=" * 50)
    
    # Test services
    payment_ok = test_payment_service()
    dashboard_ok = test_dashboard_api()
    
    if not dashboard_ok:
        print("\n❌ Dashboard must be running to continue tests")
        print("Run: cd nexus-landing && npm run dev")
        sys.exit(1)
    
    # For testing, we'll use a demo API key
    # In real testing, you'd get this from logging into the dashboard
    demo_api_key = "nx_admin_demo_key"  # This should exist from seeding
    
    print(f"\n🧪 Testing with demo API key: {demo_api_key[:12]}...")
    
    # Test scenarios
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Credit purchase simulation
    total_tests += 1
    if simulate_credit_purchase():
        tests_passed += 1
    
    # Test 2: Normal API usage
    total_tests += 1
    if test_api_key_usage(demo_api_key):
        tests_passed += 1
    
    # Test 3: Insufficient credits
    total_tests += 1
    if test_credit_insufficient(demo_api_key):
        tests_passed += 1
    
    # Results
    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! System is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the issues above.")
    
    print("\n💡 Next Steps:")
    print("1. Start the payment service: python payment_service.py")
    print("2. Test real MTN payment in the dashboard")
    print("3. Monitor credit balances and usage")

if __name__ == "__main__":
    main()
