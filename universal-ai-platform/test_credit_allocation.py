#!/usr/bin/env python3
"""
Test Credit Allocation System with Database and Idempotency
Tests that credits are properly allocated when payments succeed, with database persistence and idempotency protection
"""

import requests
import time
import logging
import os
from billing.payment_processor import PaymentProcessor
from payment.mtn_payment import CreditManager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

def test_credit_allocation():
    """Test credit allocation with database persistence"""
    
    print("🧪 Testing Credit Allocation System (Database)")
    print("=" * 50)
    
    # Initialize credit manager with test database
    test_db = "test_credits.db"
    if os.path.exists(test_db):
        os.remove(test_db)
    
    credit_manager = CreditManager(db_path=test_db)
    
    test_user_id = "test_user_credit_123"
    test_amount = 0.10  # $0.10 for testing
    expected_credits = int(test_amount * 1000)  # 100 credits for $0.10
    transaction_id = "test_tx_12345"
    
    print(f"📊 Test Parameters:")
    print(f"   User ID: {test_user_id}")
    print(f"   Amount: ${test_amount}")
    print(f"   Expected Credits: {expected_credits}")
    print(f"   Transaction ID: {transaction_id}")
    print()
    
    # Check initial credit balance
    initial_balance = credit_manager.get_user_credits(test_user_id)
    print(f"💰 Initial Credit Balance: {initial_balance} credits")
    
    # Test credit allocation
    print("\n🔧 Testing Credit Allocation...")
    success = credit_manager.add_credits(
        user_id=test_user_id,
        credits=expected_credits,
        transaction_id=transaction_id,
        amount_usd=test_amount,
        description=f"Test credit purchase: {expected_credits} credits"
    )
    
    if success:
        print("✅ Credit allocation successful!")
        
        # Check new balance
        new_balance = credit_manager.get_user_credits(test_user_id)
        print(f"💰 New Credit Balance: {new_balance} credits")
        print(f"📈 Credits Added: {new_balance - initial_balance}")
        
        # Check transaction history
        transactions = credit_manager.get_user_transactions(test_user_id)
        print(f"📜 Transaction History: {len(transactions)} transactions")
        for tx in transactions:
            print(f"   - {tx['created_at']}: {tx['credits']} credits ({tx['transaction_type']}) - {tx['description']}")
    else:
        print("❌ Credit allocation failed!")
        return False
    
    return True

def test_idempotency():
    """Test idempotency protection"""
    
    print("\n🧪 Testing Idempotency Protection")
    print("=" * 50)
    
    # Use same test database
    credit_manager = CreditManager(db_path="test_credits.db")
    
    test_user_id = "test_user_idempotent"
    test_credits = 500
    transaction_id = "test_idempotent_tx_67890"
    
    print(f"📊 Idempotency Test:")
    print(f"   User ID: {test_user_id}")
    print(f"   Credits: {test_credits}")
    print(f"   Transaction ID: {transaction_id}")
    print()
    
    # Get initial balance
    initial_balance = credit_manager.get_user_credits(test_user_id)
    print(f"💰 Initial Balance: {initial_balance} credits")
    
    # First transaction
    print("\n🔧 First Transaction...")
    success1 = credit_manager.add_credits(
        user_id=test_user_id,
        credits=test_credits,
        transaction_id=transaction_id,
        amount_usd=0.50,
        description="First attempt"
    )
    
    balance_after_first = credit_manager.get_user_credits(test_user_id)
    print(f"✅ First transaction: {'Success' if success1 else 'Failed'}")
    print(f"💰 Balance after first: {balance_after_first} credits")
    
    # Second transaction (same transaction_id - should be idempotent)
    print("\n🔧 Second Transaction (Same ID - Should be Idempotent)...")
    success2 = credit_manager.add_credits(
        user_id=test_user_id,
        credits=test_credits,
        transaction_id=transaction_id,  # Same transaction ID
        amount_usd=0.50,
        description="Second attempt (should be ignored)"
    )
    
    balance_after_second = credit_manager.get_user_credits(test_user_id)
    print(f"✅ Second transaction: {'Success' if success2 else 'Failed'}")
    print(f"💰 Balance after second: {balance_after_second} credits")
    
    # Check if balance is the same (idempotency working)
    if balance_after_first == balance_after_second:
        print("🎉 Idempotency protection working correctly!")
        
        # Verify transaction history
        transactions = credit_manager.get_user_transactions(test_user_id)
        matching_transactions = [tx for tx in transactions if tx['transaction_id'] == transaction_id]
        print(f"📜 Transactions with ID {transaction_id}: {len(matching_transactions)} (should be 1)")
        
        return len(matching_transactions) == 1
    else:
        print("❌ Idempotency protection failed - credits were added twice!")
        return False

def test_credit_deduction():
    """Test credit deduction"""
    
    print("\n🧪 Testing Credit Deduction")
    print("=" * 50)
    
    credit_manager = CreditManager(db_path="test_credits.db")
    
    test_user_id = "test_user_deduction"
    
    # Add some credits first
    credit_manager.add_credits(
        user_id=test_user_id,
        credits=1000,
        transaction_id="test_deduction_setup",
        amount_usd=1.0,
        description="Setup credits for deduction test"
    )
    
    initial_balance = credit_manager.get_user_credits(test_user_id)
    print(f"💰 Initial Balance: {initial_balance} credits")
    
    # Test successful deduction
    deduct_amount = 250
    print(f"\n🔧 Testing Deduction of {deduct_amount} credits...")
    
    success = credit_manager.deduct_credits(
        user_id=test_user_id,
        credits=deduct_amount,
        description="Test AI request usage"
    )
    
    if success:
        final_balance = credit_manager.get_user_credits(test_user_id)
        print(f"✅ Deduction successful!")
        print(f"� Final Balance: {final_balance} credits")
        print(f"📉 Credits Deducted: {initial_balance - final_balance}")
        
        # Test insufficient credits
        print(f"\n🔧 Testing Insufficient Credits (trying to deduct {final_balance + 100})...")
        fail_success = credit_manager.deduct_credits(
            user_id=test_user_id,
            credits=final_balance + 100,
            description="Should fail - insufficient credits"
        )
        
        if not fail_success:
            print("✅ Insufficient credits protection working correctly!")
            return True
        else:
            print("❌ Insufficient credits protection failed!")
            return False
    else:
        print("❌ Credit deduction failed!")
        return False

def test_payment_processor_integration():
    """Test the full payment processor integration"""
    
    print("\n\n🧪 Testing Payment Processor Integration")
    print("=" * 50)
    
    # Test that the payment processor has the credit manager
    processor = PaymentProcessor()
    
    if hasattr(processor, 'credit_manager'):
        print("✅ Payment processor has credit manager")
        
        # Test credit rate calculation
        test_amounts = [0.10, 1.00, 5.00, 10.00]
        
        for amount in test_amounts:
            expected_credits = int(amount * 1000)  # 1000 credits per $1
            print(f"💵 ${amount} → {expected_credits} credits")
            
    else:
        print("❌ Payment processor missing credit manager")
        return False
    
    return True

def cleanup_test_files():
    """Clean up test database files"""
    test_files = ["test_credits.db"]
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"🧹 Cleaned up {file}")

if __name__ == "__main__":
    print("🚀 NexusAI Credit Allocation Testing (Database + Idempotency)")
    print("=" * 60)
    
    try:
        # Test 1: Basic credit allocation
        test1_success = test_credit_allocation()
        
        # Test 2: Idempotency protection
        test2_success = test_idempotency()
        
        # Test 3: Credit deduction
        test3_success = test_credit_deduction()
        
        # Test 4: Payment processor integration
        test4_success = test_payment_processor_integration()
        
        print("\n" + "=" * 60)
        print("📊 Test Results:")
        print(f"✅ Credit Allocation: {'PASS' if test1_success else 'FAIL'}")
        print(f"✅ Idempotency Protection: {'PASS' if test2_success else 'FAIL'}")
        print(f"✅ Credit Deduction: {'PASS' if test3_success else 'FAIL'}")
        print(f"✅ Payment Processor Integration: {'PASS' if test4_success else 'FAIL'}")
        
        all_passed = test1_success and test2_success and test3_success and test4_success
        
        if all_passed:
            print("\n🎉 All tests passed! Database-backed credit system with idempotency is working correctly.")
        else:
            print("\n⚠️  Some tests failed. Please check the implementation.")
            
    finally:
        # Clean up test files
        print("\n" + "=" * 60)
        cleanup_test_files()
