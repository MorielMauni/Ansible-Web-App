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

# ONLY import Celery tasks HERE! This ensures the app, blueprints, and everything else are ready.
import app.tasks
