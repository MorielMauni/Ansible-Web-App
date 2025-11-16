from flask import Flask
from flask_cors import CORS
from app.extensions import db, migrate
from app.config import config
from dotenv import load_dotenv
import os

def create_app(config_name=None):
    load_dotenv()  # load .env if exists

    app = Flask(__name__,
                static_folder='../frontend',
                static_url_path='')

    # Determine configuration
    if not config_name:
        config_name = os.environ.get('FLASK_CONFIG', 'default')

    # Load configuration object
    app.config.from_object(config[config_name])

    # Initialize CORS
    CORS(app)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    from app.api import create_api_blueprint
    app.register_blueprint(create_api_blueprint())

    # Add root route - serve frontend
    @app.route('/')
    def index():
        return app.send_static_file('index.html')

    @app.route('/<path:filename>')
    def serve_static(filename):
        return app.send_static_file(filename)
    
    # Initialize Celery
    from app.celery_worker import make_celery
    make_celery(app)
    
    return app
