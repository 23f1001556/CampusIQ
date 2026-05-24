import os
import sys

sys.path.append(os.getcwd())

from app import create_app, db
from sqlalchemy import text

def init_database():
    print("--- Initializing Database ---")
    app = create_app()
    with app.app_context():
        # Print which DB we are using
        uri = app.config.get("SQLALCHEMY_DATABASE_URI", "NOT SET")
        if "@" in uri:
            prefix, output = uri.rsplit("@", 1)
            print(f"Target Database: ...@{output}")
        else:
            print(f"Target Database: {uri}")

        print("Running db.create_all()...")
        try:
            db.create_all()
            print("db.create_all() executed.")
        except Exception as e:
            print(f"Error creating tables: {e}")
            return

        print("--- Verifying Tables ---")
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Tables found: {tables}")
        
        if 'users' in tables:
            print("SUCCESS: 'users' table exists.")
        else:
            print("FAILURE: 'users' table still missing.")

if __name__ == "__main__":
    init_database()
