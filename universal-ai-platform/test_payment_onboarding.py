
import requests
import uuid

API_URL = "http://localhost:8000/api/v1/credits/purchase"

# Use a valid UUID for user_id
test_user_id = str(uuid.uuid4())
test_phone = "+231881158457"

import requests
from billing.db import SessionLocal
from billing.models import User

API_URL = "http://localhost:8000/api/v1/credits/purchase"

def get_user_id_by_email(email):
    db = SessionLocal()
    user = db.query(User).filter_by(email=email).first()
    db.close()
    return str(user.id) if user else None

def main():
    # Use seeded test user
    test_email = "john@example.com"
    test_user_id = get_user_id_by_email(test_email)
    if not test_user_id:
        print(f"User {test_email} not found. Please seed users first.")
        return
    test_phone = "+231881158457"
    country_code = "LR"

    # 1. First purchase (should create API key and give bonus)
    first_purchase = {
        "amount": 0.10,
        "phone_number": test_phone,
        "user_id": test_user_id,
        "country_code": country_code
    }
    resp1 = requests.post(API_URL, json=first_purchase)
    print("First purchase response:", resp1.status_code, resp1.json())

    # 2. Second purchase (should not create new API key or bonus)
    second_purchase = {
        "amount": 0.10,
        "phone_number": test_phone,
        "user_id": test_user_id,
        "country_code": country_code
    }
    resp2 = requests.post(API_URL, json=second_purchase)
    print("Second purchase response:", resp2.status_code, resp2.json())

    # 3. Invalid (below minimum)
    invalid_purchase = {
        "amount": 0.01,
        "phone_number": test_phone,
        "user_id": test_user_id,
        "country_code": country_code
    }
    resp3 = requests.post(API_URL, json=invalid_purchase)
    print("Invalid purchase response:", resp3.status_code, resp3.json())

    # 4. Missing required field
    missing_field = {
        "amount": 0.10,
        "user_id": test_user_id,
        "country_code": country_code
    }
    resp4 = requests.post(API_URL, json=missing_field)
    print("Missing field response:", resp4.status_code, resp4.json())

if __name__ == "__main__":
    main()
