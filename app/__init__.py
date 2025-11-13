from flask import Flask
from app.extensions import db, migrate
from app.config import config
from dotenv import load_dotenv
import os

def create_app(config_name=None):
    load_dotenv()  # load .env if exists

    app = Flask(__name__)
    
    # Determine configuration
    if not config_name:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    # Load configuration object
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    from app.api import create_api_blueprint
    app.register_blueprint(create_api_blueprint())
    
    # Add root route
    @app.route('/')
    def index():
        return {
            'message': 'Ansible Web API',
            'api_base': '/api',
            'health_check': '/api/health',
            'documentation': '/api/'
        }
    
    # Initialize Celery
    from app.celery_worker import make_celery
    make_celery(app)
    
    return app
