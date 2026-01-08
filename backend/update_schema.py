from app.configs.extensions import db
from app import create_app
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("Updating schema for StudyMaterial...")
    with db.engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE study_materials ADD COLUMN material_type VARCHAR(50) DEFAULT 'text'"))
            print("Added material_type")
        except Exception as e:
            print(f"material_type exists or error: {e}")

        try:
            conn.execute(text("ALTER TABLE study_materials ADD COLUMN file_path VARCHAR(500)"))
            print("Added file_path")
        except Exception as e:
            print(f"file_path exists or error: {e}")
            
        try:
            conn.execute(text("ALTER TABLE study_materials ADD COLUMN link_url VARCHAR(500)"))
            print("Added link_url")
        except Exception as e:
            print(f"link_url exists or error: {e}")
            
    print("Schema update complete.")
