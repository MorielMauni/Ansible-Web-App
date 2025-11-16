from celery import Celery

celery = Celery(
    "ansible_web_api",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

def make_celery(app):
    celery.conf.update(app.config)
    class ContextTask(celery.Task):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return super().__call__(*args, **kwargs)
    celery.Task = ContextTask
    return celery

# Import tasks to register them with Celery
import app.tasks
