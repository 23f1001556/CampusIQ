import os
from dotenv import load_dotenv

load_dotenv()

def fix_database_uri(uri):
    if not uri:
        return uri
    # Strip quotes if they were included in the env variable
    uri = uri.strip("'").strip('"')
    # Render provides DATABASE_URL starting with postgres:// but SQLAlchemy requires postgresql://
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    return uri

class BaseConfig:
    SQLALCHEMY_DATABASE_URI = fix_database_uri(os.getenv("POSTGRESDB_URL", os.getenv("DATABASE_URL", "sqlite:///site.db")))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER","sidhant")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # Celery
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    RESULT_BACKEND = os.getenv("RESULT_BACKEND", "redis://localhost:6379/0")
    
    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = fix_database_uri(os.getenv("POSTGRESDB_URL"))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    #mailing
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER","sidhant")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER","sidhant")
    MAIL_DEBUG = False
    
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = fix_database_uri(os.getenv("POSTGRESDB_URL", os.getenv("DATABASE_URL")))
    DEBUG = False
