import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Database
    DATABASE_HOST = os.getenv('DATABASE_HOST', 'localhost')
    DATABASE_PORT = os.getenv('DATABASE_PORT', '3306')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'flaskstarter')
    DATABASE_USER = os.getenv('DATABASE_USER', 'root')
    DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', '')

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DATABASE_USER}:{DATABASE_PASSWORD}@"
        f"{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # App settings
    APP_NAME = os.getenv('APP_NAME', 'FlaskStarter')
    APP_URL = os.getenv('APP_URL', 'http://localhost:5000')

    # Session
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    WTF_CSRF_ENABLED = False
    
    # Fast bcrypt for testing (4 rounds instead of default 12)
    BCRYPT_LOG_ROUNDS = 4

    # Use test database
    DATABASE_NAME = os.getenv('TEST_DATABASE_NAME', 'flaskstarter_test')
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{Config.DATABASE_USER}:{Config.DATABASE_PASSWORD}@"
        f"{Config.DATABASE_HOST}:{Config.DATABASE_PORT}/"
        f"{os.getenv('TEST_DATABASE_NAME', 'flaskstarter_test')}?charset=utf8mb4"
    )


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
