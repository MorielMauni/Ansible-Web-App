from app.celery_worker import celery
from flask import current_app
from app.api.ansible_runner import AnsibleRunner

@celery.task()
def run_playbook_async(playbook_name, target_host, job_id):
    with current_app.app_context():
        return AnsibleRunner.run_playbook(playbook_name, target_host, job_id)
