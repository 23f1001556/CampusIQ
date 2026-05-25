from app import create_app
from app.configs.extensions import db
from sqlalchemy import text

app = create_app()
with app.app_context():
    try:
        db.session.execute(text("ALTER TABLE users ADD COLUMN bio VARCHAR(500);"))
        print("Added bio")
    except Exception as e:
        print(f"Bio error: {e}")
        db.session.rollback()

    try:
        db.session.execute(text("ALTER TABLE users ADD COLUMN profile_picture VARCHAR(255);"))
        print("Added profile_picture")
    except Exception as e:
        print(f"profile_picture error: {e}")
        db.session.rollback()

    try:
        db.session.execute(text("ALTER TABLE users ADD COLUMN social_github VARCHAR(255);"))
        print("Added social_github")
    except Exception as e:
        print(f"social_github error: {e}")
        db.session.rollback()

    try:
        db.session.execute(text("ALTER TABLE users ADD COLUMN social_linkedin VARCHAR(255);"))
        print("Added social_linkedin")
    except Exception as e:
        print(f"social_linkedin error: {e}")
        db.session.rollback()

    try:
        db.session.execute(text("ALTER TABLE users ADD COLUMN social_instagram VARCHAR(255);"))
        print("Added social_instagram")
    except Exception as e:
        print(f"social_instagram error: {e}")
        db.session.rollback()

    db.session.commit()
    print("Done!")
