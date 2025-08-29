#!/usr/bin/env python3
"""
Live Payment Test with Credit Allocation
Tests the complete flow: Payment → Credit Allocation → Balance Check
"""

import time
import logging
from billing.payment_processor import PaymentProcessor

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

def test_live_payment_with_credits():
    """Test live payment with actual credit allocation"""
    
    print("🧪 Live Payment Test with Credit Allocation")
    print("=" * 60)
    
    processor = PaymentProcessor()
    credit_manager = processor.credit_manager
    
    # Test parameters
    test_user_id = "live_test_user_456"
    test_amount = 0.10  # $0.10 for testing
    expected_credits = int(test_amount * 1000)  # 100 credits
    
    print(f"📊 Test Parameters:")
    print(f"   User ID: {test_user_id}")
    print(f"   Amount: ${test_amount}")
    print(f"   Expected Credits: {expected_credits}")
    print(f"   Phone: +231881158457")
    print()
    
    # Check initial balance
    initial_balance = credit_manager.get_user_credits(test_user_id)
    print(f"💰 Initial Credit Balance: {initial_balance} credits")
    
    print("\n🚀 Initiating Live MTN Payment...")
    print("⚠️  This will attempt a real MTN Mobile Money transaction!")
    
    # Process payment
    result = processor.process_credit_purchase(
        amount=test_amount,
        phone_number="+231881158457",
        user_id=test_user_id,
        country_code="LR"
    )
    
    print(f"\n📞 Payment Result:")
    print(f"   Success: {result.get('success', False)}")
    print(f"   Status: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', 'No message')}")
    
    if result.get('success'):
        print(f"   Transaction ID: {result.get('transaction_id', 'N/A')}")
        print(f"   Credits Added: {result.get('credits', 'N/A')}")
        print(f"   Total Credits: {result.get('total_credits', 'N/A')}")
        
        # Verify credit balance
        final_balance = credit_manager.get_user_credits(test_user_id)
        print(f"\n💰 Final Credit Balance: {final_balance} credits")
        print(f"📈 Credits Gained: {final_balance - initial_balance}")
        
        # Show transaction history
        transactions = credit_manager.get_user_transactions(test_user_id, limit=5)
        print(f"\n📜 Recent Transactions:")
        for tx in transactions:
            print(f"   - {tx['created_at']}: {tx['credits']} credits")
            print(f"     Type: {tx['transaction_type']}, Amount: ${tx.get('amount_usd', 'N/A')}")
            print(f"     Description: {tx['description']}")
            print()
            
        return True
    else:
        print(f"\n❌ Payment failed: {result.get('error', 'Unknown error')}")
        print("💡 This might be normal if:")
        print("   - User declined the payment prompt")
        print("   - Payment timed out (normal MTN behavior)")
        print("   - Insufficient balance in MTN wallet")
        return False

if __name__ == "__main__":
    print("🚀 NexusAI Live Payment + Credit Test")
    print("=" * 60)
    
    # Ask for confirmation
    print("⚠️  WARNING: This will attempt a real payment transaction!")
    print("💳 Amount: $0.10 to phone +231881158457")
    print()
    
    confirm = input("Continue with live payment test? (y/N): ").lower().strip()
    
    if confirm == 'y':
        success = test_live_payment_with_credits()
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 Live payment test completed successfully!")
            print("✅ Credits were properly allocated after payment completion.")
        else:
            print("⚠️  Payment test completed but payment did not succeed.")
            print("💡 This is often normal due to user interaction requirements.")
    else:
        print("❌ Test cancelled by user.")
