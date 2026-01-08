import os
import sys

# Add the parent directory to sys.path to allow importing 'app'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.configs.extensions import db
from app.models.users import User

def seed_accounts():
    app = create_app()
    with app.app_context():
        accounts = [
            {
                "email": "sidhantsksk@gmail.com",
                "user_name": "ADMIN",
                "password": "Sidhant@2001",
                "role": "admin",
                "fullname": "System Administrator"
            },
            {
                "email": "manager@example.com",
                "user_name": "MANAGER",
                "password": "Manager@2001",
                "role": "manager",
                "fullname": "Project Manager"
            },
            {
                "email": "user@example.com",
                "user_name": "USER",
                "password": "User@2001",
                "role": "user",
                "fullname": "Standard User"
            },
            {
                "email": "student@alpha.edu",
                "user_name": "student_alpha",
                "password": "Test@123",
                "role": "user",
                "fullname": "Alpha Student"
            },
            {
                "email": "student2@alpha.edu",
                "user_name": "student_alpha_2",
                "password": "Test@123",
                "role": "user",
                "fullname": "Alpha Student 2"
            }
        ]

        for acc in accounts:
            user = User.query.filter_by(email=acc["email"]).first()
            if not user:
                print(f"Creating {acc['role']} user: {acc['email']}...")
                user = User(
                    user_name=acc["user_name"],
                    email=acc["email"],
                    isadmin=(acc["role"] == "admin"),
                    role=acc["role"],
                    is_verified=True,
                    fullname=acc["fullname"]
                )
                try:
                    user.password = acc["password"]
                    db.session.add(user)
                    db.session.commit()
                    print(f"{acc['role'].capitalize()} user {acc['email']} created successfully.")
                except Exception as e:
                    db.session.rollback()
                    print(f"Error creating {acc['role']}: {e}")
            else:
                print(f"{acc['role'].capitalize()} user {acc['email']} already exists.")
                # Sync roles and flags if they already exist
                user.role = acc["role"]
                user.isadmin = (acc["role"] == "admin")
                user.is_verified = True
                user.password = acc["password"] # Ensure password is synced
                db.session.commit()

if __name__ == "__main__":
    seed_accounts()
