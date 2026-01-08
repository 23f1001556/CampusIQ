import os
import sys

# Add the current directory to sys.path so we can import 'app'
sys.path.append(os.getcwd())

from app import create_app, db
from sqlalchemy import text

def debug_config():
    print(f"Current Working Directory: {os.getcwd()}")
    
    # Initialize app
    try:
        app = create_app()
    except Exception as e:
        print(f"Failed to create app: {e}")
        return

    with app.app_context():
        print("\n--- Config Debug ---")
        uri = app.config.get("SQLALCHEMY_DATABASE_URI", "NOT SET")
        # Mask the URI for security
        if "@" in uri:
            prefix, output = uri.rsplit("@", 1)
            print(f"Database URI: ...@{output}")
        else:
            print(f"Database URI: {uri}")
            
        print(f"Mail Server: {app.config.get('MAIL_SERVER')}")
        print(f"Mail Username: {app.config.get('MAIL_USERNAME')}")
        print(f"Mail Password Set: {'Yes' if app.config.get('MAIL_PASSWORD') else 'No'}")
        print(f"SECRET_KEY Set: {'Yes' if app.config.get('SECRET_KEY') else 'No'}")
        print(f"CORS Origins: {app.config.get('CORS_ORIGINS')}")

        print("\n--- Environment Variables ---")
        print(f"DEV_ENV: {os.getenv('DEV_ENV')}")
        print(f"DATABASE_URL set: {'Yes' if os.getenv('DATABASE_URL') else 'No'}")
        print(f"POSTGRESDB_URL set: {'Yes' if os.getenv('POSTGRESDB_URL') else 'No'}")

        print("\n--- Database Connection Test ---")
        try:
            with db.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                print("Database Connection: SUCCESS")
                
                print("\n--- Schema Check ---")
                inspector = db.inspect(db.engine)
                tables = inspector.get_table_names()
                print(f"Tables found: {tables}")
                
                if "users" in tables:
                     user_count = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
                     print(f"Users count: {user_count}")
                else:
                    print("CRITICAL: 'users' table NOT found! Migrations might be missing.")

        except Exception as e:
            print(f"Database Connection/Schema Check FAILED")
            import traceback
            print(traceback.format_exc())

if __name__ == "__main__":
    debug_config()
