import os
import json
from pathlib import Path

class Config:
    BASEDIR = Path(__file__).resolve().parent

    SECRET_KEY = os.environ.get('SECRET_KEY')

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///rayeva.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')

    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

    ENABLE_WHATSAPP = os.environ.get('ENABLE_WHATSAPP', 'false').lower() == 'true'
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 1048576))
    REQUEST_TIMEOUT_SECONDS = int(os.environ.get('REQUEST_TIMEOUT_SECONDS', 20))
    AI_RETRY_COUNT = int(os.environ.get('AI_RETRY_COUNT', 3))
    AI_TIMEOUT_SECONDS = int(os.environ.get('AI_TIMEOUT_SECONDS', 15))

    AUTH_TOKEN_MAP = json.loads(os.environ.get('AUTH_TOKEN_MAP', '{}'))
    WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', '')
    WEBHOOK_REPLAY_WINDOW_SECONDS = int(os.environ.get('WEBHOOK_REPLAY_WINDOW_SECONDS', 300))

    RATE_LIMIT_PER_MINUTE = int(os.environ.get('RATE_LIMIT_PER_MINUTE', 30))
    WHATSAPP_MESSAGE_MAX_LENGTH = int(os.environ.get('WHATSAPP_MESSAGE_MAX_LENGTH', 1000))

    ENV_NAME = os.environ.get('APP_ENV', 'development')

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class StagingConfig(Config):
    DEBUG = False
    TESTING = False
    ENV_NAME = 'staging'

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    ENV_NAME = 'production'

class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def validate_runtime_config(config_obj):
    env_name = config_obj.get('ENV_NAME', 'development')
    secret_key = config_obj.get('SECRET_KEY')
    if env_name in {'production', 'staging'} and not secret_key:
        raise RuntimeError('SECRET_KEY is required for staging/production environments')
