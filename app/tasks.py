from app.celery_worker import celery
from app import create_app
from app.api.ansible_runner import AnsibleRunner
from app.extensions import db
from app.models import Job
from datetime import datetime

@celery.task()
def run_playbook_async(playbook_name, target_host, job_id):
    app = create_app()
    with app.app_context():
        try:
            app.logger.info(f"Starting async task for job {job_id}")
            job = db.session.get(Job, job_id)
            if not job:
                app.logger.error(f"Job {job_id} not found")
                return None

            job.status = 'running'
            db.session.commit()

            # Run the playbook
            result = AnsibleRunner.run_playbook(playbook_name, target_host, job_id)
            app.logger.info(f"Task completed for job {job_id}")
            return result
        except Exception as e:
            app.logger.error(f"Task failed for job {job_id}: {str(e)}")
            job = db.session.get(Job, job_id)
            if job:
                job.status = 'failed'
                job.stderr = f"Task error: {str(e)}"
                job.completed_at = datetime.utcnow()
                db.session.commit()
            return None
