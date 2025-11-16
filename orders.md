## 1. Setup and Ensure Environment

- Activate the Python virtual environment: `source venv/bin/activate`
- Confirm Python 3.10+ is installed.
- Install all required packages (if not done): `pip install -r requirements.txt`
- Confirm Redis is installed (`sudo apt install redis-server`) and running (`sudo systemctl start redis`).

## 2. Repository Structure

Confirm that the project directory contains at least:
- `app/` - Flask backend
    - `__init__.py`
    - `config.py`
    - `api/`
        - `routes.py`
        - `ansible_runner.py`
        - `validators.py`
        - `__init__.py`
    - `models.py`
    - `extensions.py`
    - `tasks.py`
    - `celery_worker.py`
- `frontend/` - Static HTML+JS frontend (index.html, app.js, style.css)
- `.env` (optional)
- `requirements.txt`
- `wsgi.py`

## 3. Database and Config Setup

- Ensure `app/config.py` exists and includes:
    ```
    SQLALCHEMY_DATABASE_URI = "sqlite:////<absolute_path>/ansible_dev.db"
    SECRET_KEY = "<your-secret-key>"
    ```
  Replace `<absolute_path>` with the real (absolute) path, e.g. `/home/debian/ansible_web_api/ansible_dev.db`.

- If you use environment variables or `.env`, ensure `from dotenv import load_dotenv; load_dotenv()` is called at the top of `app/__init__.py`.

## 4. Flask App Factory

- `app/__init__.py` must contain:
    ```
    from flask import Flask
    from app.extensions import db
    from dotenv import load_dotenv
    import os

    def create_app(config_name=None):
        load_dotenv()
        app = Flask(__name__)
        config_path = os.path.join(os.path.dirname(__file__), "config.py")
        app.config.from_pyfile(config_path, silent=False)
        db.init_app(app)
        from app.api import create_api_blueprint
        app.register_blueprint(create_api_blueprint())
        return app
    ```

## 5. Celery Integration

- `app/celery_worker.py` should have:
    ```
    from celery import Celery
    from app import create_app

    def make_celery(app):
        celery = Celery(
            "ansible_web_api",
            broker="redis://localhost:6379/0",
            backend="redis://localhost:6379/0"
        )
        celery.conf.update(app.config)
        class ContextTask(celery.Task):
            abstract = True
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return super().__call__(*args, **kwargs)
        celery.Task = ContextTask
        return celery

    flask_app = create_app()
    celery = make_celery(flask_app)
    import app.tasks
    ```

- `app/tasks.py` should have:
    ```
    from app.celery_worker import celery
    from flask import current_app
    from app.api.ansible_runner import AnsibleRunner

    @celery.task()
    def run_playbook_async(playbook_name, target_host, job_id):
        with current_app.app_context():
            return AnsibleRunner.run_playbook(playbook_name, target_host, job_id)
    ```

## 6. API Blueprint

- `app/api/routes.py` should use:
    ```
    from flask import Blueprint, request, jsonify, current_app
    from app.extensions import db
    from app.models import Job
    from app.api.validators import validate_hostname, validate_playbook, ValidationError
    from app.api.ansible_runner import AnsibleRunner
    from app.tasks import run_playbook_async

    api = Blueprint('api', __name__, url_prefix='/api')
    # All API route definitions follow...
    # Make sure the /execute endpoint calls run_playbook_async.apply_async
    ```

## 7. Models and Database

- Ensure `app/models.py` defines Job and all required models, with fields for job status, stdout, stderr, timestamps, etc.
- Migrate or initialize the database using Flask migration commands if needed.

## 8. Frontend

- `frontend/index.html`, `frontend/app.js`, and `frontend/style.css` should enable:
    - Playbook selection
    - Host entry
    - Job submission
    - Listing jobs
    - Viewing logs of completed jobs

- Server frontend using a simple static server (e.g. `python3 -m http.server 8080` in /frontend), or from Flask as static files.

## 9. Running and Testing

- Start Redis: `sudo systemctl start redis`
- Start the Flask API: `flask run --host=0.0.0.0 --port=5000`
- Start the Celery worker: `celery -A app.celery_worker.celery worker --loglevel=INFO`
- Open `/api/health`, `/api/playbooks`, `/api/jobs` in browser or via curl to verify service
- Use the frontend UI to check functionality

## 10. Documentation

- Write a full README explaining:
    - How to install dependencies and set up config
    - How to run Flask, Celery, Redis, and the frontend
    - How to test and submit jobs
    - Troubleshooting steps
    - How to extend or deploy the app

## 11. Error Handling and Logging

- Ensure all exceptions are logged, API errors are clear, and failed jobs have tracebacks in their logs.
- Validate input everywhere; handle edge cases.

## 12. Optional Production Improvements

- Add CORS support if needed.
- Add basic authentication if exposing to public users.
- Add deployment steps for running under Gunicorn + Nginx.

---

**Follow each step exactly, verify each component before moving on, and document every issue and fix. Push all changes to the repository.*