import subprocess
import os
from pathlib import Path
from datetime import datetime
from flask import current_app
from app.extensions import db
from app.models import Job

class AnsibleRunner:
    """Handles secure Ansible playbook execution."""

    @staticmethod
    def run_playbook(playbook_name, target_host, job_id):
        playbook_path = Path(current_app.config['ANSIBLE_PLAYBOOK_DIR']) / playbook_name
        inventory_path = current_app.config['ANSIBLE_INVENTORY_PATH']

        cmd = [
            'ansible-playbook',
            str(playbook_path),
            '-i', inventory_path,
            '--limit', target_host,
            '-v'
        ]

        env = {
            'ANSIBLE_CONFIG': current_app.config['ANSIBLE_CONFIG_PATH'],
            'PATH': os.environ.get('PATH', '/usr/bin:/bin'),
            'HOME': os.environ.get('HOME', '/root')
        }

        current_app.logger.info(f"Executing: {' '.join(cmd)}")
        job = db.session.get(Job, job_id)
        job.status = 'running'
        db.session.commit()

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=1800,
                env=env,
                shell=False,
                check=False
            )

            job.status = 'success' if result.returncode == 0 else 'failed'
            job.exit_code = result.returncode
            job.stdout = result.stdout
            job.stderr = result.stderr
            job.completed_at = datetime.utcnow()
            current_app.logger.info(f"Job {job_id} completed with exit code {result.returncode}")

        except subprocess.TimeoutExpired:
            job.status = 'failed'
            job.stderr = "Execution timed out after 30 minutes"
            job.completed_at = datetime.utcnow()
            current_app.logger.error(f"Job {job_id} timed out")

        except Exception as e:
            job.status = 'failed'
            job.stderr = f"Execution error: {str(e)}"
            job.completed_at = datetime.utcnow()
            current_app.logger.error(f"Job {job_id} failed: {str(e)}")

        finally:
            db.session.commit()

        return job

    @staticmethod
    def list_playbooks():
        playbook_dir = Path(current_app.config['ANSIBLE_PLAYBOOK_DIR'])
        if not playbook_dir.exists():
            return []
        allowed_extensions = current_app.config['ALLOWED_PLAYBOOK_EXTENSIONS']
        playbooks = []
        for file in playbook_dir.iterdir():
            if file.is_file() and any(file.name.endswith(ext) for ext in allowed_extensions):
                playbooks.append({
                    'name': file.name,
                    'size': file.stat().st_size,
                    'modified': datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                })
        return sorted(playbooks, key=lambda x: x['name'])
