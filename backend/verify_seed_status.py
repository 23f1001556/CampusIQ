import os
import sys

sys.path.append(os.getcwd())

from app import create_app
from app.models.users import User

def verify_seed():
    app = create_app()
    with app.app_context():
        email = "sidhantsksk@gmail.com"
        print(f"--- Checking status for {email} ---")
        
        # 1. Check Config
        uri = app.config.get("SQLALCHEMY_DATABASE_URI", "NOT SET")
        if "@" in uri:
            _, output = uri.rsplit("@", 1)
            print(f"Connected to DB: ...@{output}")
        else:
            print(f"Connected to DB: {uri}")

        # 2. Query User
        user = User.query.filter_by(email=email).first()
        
        if user:
            print(f"SUCCESS: User found!")
            print(f"  ID: {user.id}")
            print(f"  Username: {user.user_name}")
            print(f"  Role: {user.role}")
            print(f"  Is Verified: {user.is_verified}")
            print(f"  Is Blocked: {user.is_blocked}")
            
            # 3. Check Password
            password_to_check = "Sidhant2001@N_P"
            is_valid = user.check_password(password_to_check)
            print(f"  Password '{password_to_check}' valid? {is_valid}")
        else:
            print("FAILURE: User NOT found in this database.")
        
        print("-------------------------------------")

        # Check generic user too
        manager_email = "manager@example.com"
        m_user = User.query.filter_by(email=manager_email).first()
        if m_user:
             print(f"Manager user found: {m_user.email} (Verified: {m_user.is_verified})")
        else:
             print(f"Manager user {manager_email} NOT found.")

if __name__ == "__main__":
    verify_seed()
