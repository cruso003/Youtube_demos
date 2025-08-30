"""
Seed test users for onboarding/bonus payment tests (Python, SQLAlchemy, Postgres)
Run: python3 seed_test_users.py
"""

import uuid
from billing.db import SessionLocal
from billing.models import User
from datetime import datetime
import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def seed_user(user_id, email, name, password, role="USER", is_active=True):
    db = SessionLocal()
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        user = User(
            id=user_id,
            email=email,
            name=name,
            password=hash_password(password),
            role=role,
            is_active=is_active,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        print(f"Seeded user: {email} ({user_id}) [{role}]")
    else:
        print(f"User already exists: {email} ({user_id}) [{user.role}]")
    db.close()

if __name__ == "__main__":
    # Super Admin
    super_admin_id = str(uuid.uuid4())
    seed_user(
        user_id=super_admin_id,
        email="admin@nexusai.africa",
        name="Super Administrator",
        password="SuperAdmin123!",
        role="SUPER_ADMIN",
        is_active=True
    )

    # Demo Users
    demo_users = [
        {
            "user_id": str(uuid.uuid4()),
            "email": "john@example.com",
            "name": "John Developer",
            "password": "Demo123!",
            "role": "USER",
            "is_active": True
        },
        {
            "user_id": str(uuid.uuid4()),
            "email": "sarah@nexusai.africa",
            "name": "Sarah Admin",
            "password": "Demo123!",
            "role": "ADMIN",
            "is_active": True
        }
    ]
    for user in demo_users:
        seed_user(**user)
    print("Done.")
