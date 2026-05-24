import os
from dotenv import load_dotenv

load_dotenv()

class BaseConfig:
    SQLALCHEMY_DATABASE_URI = os.getenv("POSTGRESDB_URL", os.getenv("DATABASE_URL", "sqlite:///site.db"))
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
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://161.118.163.147:6379/0")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "https://quizv2-tau.vercel.app,http://161.118.163.147,http://localhost:5173,http://localhost:3000").split(",")

class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv("POSTGRESDB_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    #mailing
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER","sidhant")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER","sidhant")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "https://quizv2-tau.vercel.app,http://161.118.163.147,http://localhost:5173,http://localhost:3000").split(",")

class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv("POSTGRESDB_URL", os.getenv("DATABASE_URL"))
    DEBUG = False
