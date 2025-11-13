import os
from flask import Flask
from app.extensions import db

def create_app():
    app = Flask(__name__)
    # This line ensures config is loaded:
    app.config.from_pyfile(os.environ.get("FLASK_CONFIG_FILE", "config.py"), silent=True)
    app.config.from_envvar("FLASK_CONFIG", silent=True)  # Optional: for more env-based config
    db.init_app(app)
    
    from app.api import create_api_blueprint
    app.register_blueprint(create_api_blueprint())
    return app
