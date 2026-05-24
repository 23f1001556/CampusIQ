import os
from flask import Flask, jsonify
from flask_cors import CORS
from app.configs.extensions import db, mail
from app.configs.config import DevelopmentConfig, ProductionConfig
from app.models import User, Scores, Quiz, Chapter, Subject, Question, InstituteCourse, InstitutePaper, InstituteLecture, AIGeneratedContent, UserResponse
from app.models.Ai.history import AIHistory
from app.models.study_material import StudyMaterial
from app.models.mock_quiz import MockQuiz, MockQuestion, MockAttempt

from app.auth.routes import auth_bp
from app.route.users.routes import users_bp
from app.route.subjects.routes import subjects_bp
from app.route.chapters.routes import chapters_bp
from app.route.quiz.routes import quiz_bp


def create_app(test_config=None):
    app = Flask(__name__)
    # CORS(app) moved down after config loading

    env = os.getenv("DEV_ENV","development")

    if test_config:
        app.config.update(test_config)
    elif env == "production":
        app.config.from_object("app.configs.config.ProductionConfig")
    elif env == "development":
        app.config.from_object("app.configs.config.DevelopmentConfig")
    elif env == "testing":
        app.config.from_object("app.configs.config.BaseConfig")
    else:
        raise ValueError(f"Unknown environment: {env}")

    # Log the database URI for debugging (safely masked)
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
    if db_uri:
        from urllib.parse import urlparse
        try:
            parsed = urlparse(db_uri)
            masked_uri = f"{parsed.scheme}://****:****@{parsed.hostname}:{parsed.port}{parsed.path}"
            # Using print as well because it's more reliable in some Render log views
            print(f"DEBUG: Using database: {masked_uri}")
            app.logger.info(f"Using database: {masked_uri}")
        except Exception:
            print("DEBUG: Using database: [malformed URI]")
            app.logger.info("Using database: [malformed URI]")

    @app.route("/")
    def index():
        return jsonify({
            "status": "online",
            "message": "Quizzy API is live",
            "environment": env
        }), 200

    @app.route("/health")
    def health():
        return jsonify({"status": "healthy"}), 200

    db.init_app(app)
    mail.init_app(app)
    
    # Init CORS with config
    CORS(app, resources={r"/*": {"origins": app.config.get("CORS_ORIGINS")}}, supports_credentials=True)
    
    from app.celery.config import celery_init_app
    celery_init_app(app)
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(subjects_bp)
    app.register_blueprint(chapters_bp)
    app.register_blueprint(quiz_bp)
    
    from app.route.test_paper.routes import test_paper_bp
    app.register_blueprint(test_paper_bp)

    from app.route.ai.routes import ai_bp
    app.register_blueprint(ai_bp)

    from app.route.mock.routes import mock_bp
    app.register_blueprint(mock_bp)

    from app.route.institute.routes import institute_bp
    app.register_blueprint(institute_bp, url_prefix='/institute')

    from app.route.admin.routes import admin_bp
    app.register_blueprint(admin_bp)
    
    # Register Lectures Blueprint (Now consolidated into AI/Study Material)
    # from app.route.lectures.routes import lectures_bp
    # app.register_blueprint(lectures_bp)

    with app.app_context():
        db.create_all() 

    return app