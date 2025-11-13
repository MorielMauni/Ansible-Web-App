from flask import Blueprint, request, jsonify, current_app
from app.extensions import db
from app.models import Job
from app.api.validators import validate_hostname, validate_playbook, ValidationError
from app.api.ansible_runner import AnsibleRunner

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/', methods=['GET'])
def api_info():
    return jsonify({
        'service': 'Ansible Web API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/api/health',
            'playbooks': '/api/playbooks',
            'execute': '/api/execute (POST)',
            'jobs': '/api/jobs',
            'job_status': '/api/jobs/<job_id>',
            'job_logs': '/api/jobs/<job_id>/logs'
        }
    }), 200

@api.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'ansible-api'}), 200

@api.route('/playbooks', methods=['GET'])
def list_playbooks():
    try:
        playbooks = AnsibleRunner.list_playbooks()
        return jsonify({'count': len(playbooks), 'playbooks': playbooks}), 200
    except Exception as e:
        current_app.logger.error(f"Error listing playbooks: {str(e)}")
        return jsonify({'error': 'Failed to list playbooks'}), 500

@api.route('/execute', methods=['POST'])
def execute_playbook():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400

    playbook_name = data.get('playbook')
    target_host   = data.get('hostname')

    try:
        playbook_name = validate_playbook(playbook_name)
        target_host = validate_hostname(target_host)
    except ValidationError as e:
        current_app.logger.warning(f"Validation failed: {str(e)}")
        return jsonify({'error': str(e)}), 400

    job = Job(
        playbook_name=playbook_name,
        target_host=target_host,
        status='pending'
    )
    db.session.add(job)
    db.session.commit()
    current_app.logger.info(f"Created job {job.id}: {playbook_name} -> {target_host}")

    # Use Celery for async execution
    from app.tasks import run_playbook_async
    run_playbook_async.apply_async(args=(playbook_name, target_host, job.id))

    return jsonify({
        'job_id': job.id,
        'message': 'Job started',
        'status': 'pending'
    }), 202

@api.route('/jobs/<int:job_id>', methods=['GET'])
def get_job_status(job_id):
    job = db.session.get(Job, job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify(job.to_dict()), 200

@api.route('/jobs/<int:job_id>/logs', methods=['GET'])
def get_job_logs(job_id):
    job = db.session.get(Job, job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify(job.to_dict_with_output()), 200

@api.route('/jobs', methods=['GET'])
def list_jobs():
    limit = request.args.get('limit', 50, type=int)
    status = request.args.get('status', None)
    query = Job.query
    if status:
        query = query.filter_by(status=status)
    jobs = query.order_by(Job.started_at.desc()).limit(limit).all()
    return jsonify({
        'count': len(jobs),
        'jobs': [job.to_dict() for job in jobs]
    }), 200

@api.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@api.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    current_app.logger.error(f"Internal error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500
