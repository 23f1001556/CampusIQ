from app import create_app, db
from sqlalchemy import text

app = create_app()

def add_profile_columns():
    with app.app_context():
        with db.engine.connect() as conn:
            # Check and add columns one by one
            columns = [
                ("bio", "VARCHAR(500)"),
                ("profile_picture", "VARCHAR(255)"),
                ("social_github", "VARCHAR(255)"),
                ("social_linkedin", "VARCHAR(255)"),
                ("social_instagram", "VARCHAR(255)")
            ]
            
            for col_name, col_type in columns:
                try:
                    conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"))
                    print(f"Added column: {col_name}")
                except Exception as e:
                    # Column might already exist
                    print(f"Skipped {col_name}: {str(e)}")
            
            conn.commit()
            print("Profile schema update completed.")

if __name__ == "__main__":
    add_profile_columns()
