import os
import sys

sys.path.append(os.getcwd())

from app import create_app, db
from app.models.users import User
from sqlalchemy import text

def verify_app_model():
    print("--- Verifying App Context and Model Access ---")
    app = create_app()
    with app.app_context():
        # 1. Print DB URL
        uri = app.config.get("SQLALCHEMY_DATABASE_URI", "NOT SET")
        if "@" in uri:
            _, output = uri.rsplit("@", 1)
            print(f"App Config DB: ...@{output}")
        else:
            print(f"App Config DB: {uri}")

        # 2. Check Search Path
        try:
            # properly use session context for raw sql
            result = db.session.execute(text("SHOW search_path"))
            print(f"Current search_path: {result.scalar()}")
            
            # 3. Check current schema of 'users' table
            result = db.session.execute(text("SELECT schemaname FROM pg_tables WHERE tablename = 'users'"))
            schemas = [row[0] for row in result]
            print(f"Schemas containing 'users' table: {schemas}")

        except Exception as e:
            print(f"Error checking search_path/schemas: {e}")
            import traceback
            traceback.print_exc()

        # 4. Try ORM Query
        print("\nAttempting User.query.first()...")
        try:
            user = User.query.first()
            print("SUCCESS: User.query.first() executed without error.")
            print(f"Result: {user}")
        except Exception as e:
            print(f"FAILURE: User.query.first() raised exception.")
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    verify_app_model()
