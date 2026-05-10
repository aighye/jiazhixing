import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'

    # MySQL 数据库配置（必须通过环境变量或 .env 文件配置）
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_HOST = os.environ.get('DB_HOST')
    DB_PORT = os.environ.get('DB_PORT') or '3306'
    DB_NAME = os.environ.get('DB_NAME')

    if not all([DB_USER, DB_HOST, DB_NAME]):
        raise RuntimeError(
            'MySQL 数据库配置缺失！请确保 .env 文件或环境变量中设置了 '
            'DB_USER、DB_HOST、DB_NAME（以及 DB_PASSWORD）。\n'
            '示例:\n'
            '  DB_USER=4srepair\n'
            '  DB_PASSWORD=4srepair2024\n'
            '  DB_HOST=127.0.0.1\n'
            '  DB_PORT=3306\n'
            '  DB_NAME=4s_repair_db'
        )

    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }

    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    BACKUP_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backups')

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:4srepair2024@127.0.0.1:3306/4s_repair_test?charset=utf8mb4'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
