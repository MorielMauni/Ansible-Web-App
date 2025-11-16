import os
from pathlib import Path

basedir = Path(__file__).resolve().parent.parent

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Ansible paths
    ANSIBLE_PLAYBOOK_DIR = os.environ.get('ANSIBLE_PLAYBOOK_DIR', str(basedir / 'playbooks'))
    ANSIBLE_INVENTORY_PATH = os.environ.get('ANSIBLE_INVENTORY_PATH', str(basedir / 'inventory' / 'hosts'))
    ANSIBLE_CONFIG_PATH = os.environ.get('ANSIBLE_CONFIG_PATH', str(basedir / 'ansible.cfg'))
    
    # Logging
    LOG_DIR = basedir / 'logs'
    LOG_FILE = LOG_DIR / 'ansible_api.log'
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Security
    MAX_CONTENT_LENGTH = 16 * 1024  # 16KB max request size
    ALLOWED_PLAYBOOK_EXTENSIONS = ['.yml', '.yaml']
    
    @classmethod
    def init_app(cls, app):
        # Create logs directory if it doesn't exist
        cls.LOG_DIR.mkdir(exist_ok=True)

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URI') or \
        f'sqlite:///{basedir}/instance/ansible_dev.db'

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or \
        f'sqlite:///{basedir}/instance/ansible_prod.db'

    @staticmethod
    def init_app(app):
        Config.init_app(app)
        # Production-specific initialization

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
