# Ansible Web API - Commands

## Environment Setup
```bash
# Make sure you're in the project root directory
cd /home/debian/ansible_web_api

# Activate Python virtual environment
. venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Database Operations
```bash
# Initialize/upgrade database
FLASK_APP=app flask db upgrade

# Create new migration (if schema changes)
FLASK_APP=app flask db migrate -m "description"
```

## Important Notes
- **Always run Flask commands from the project root directory** (`/home/debian/ansible_web_api`)
- The `app` module must be importable from the current directory
- If you get "No module named 'app'" errors, check that you're in the right directory

## Running the Application

### Start Redis (if not running)
```bash
sudo systemctl start redis
```

### Start Celery Worker
```bash
celery -A app.celery_worker.celery worker --loglevel=INFO
```

### Start Flask Server (API + Frontend)
```bash
# Make sure you're in the project root directory (/home/debian/ansible_web_api)
python -m flask run --host=0.0.0.0 --port=5000
```
# Everything is served by Flask:
# - API: http://localhost:5000/api/*
# - Frontend: http://localhost:5000/

## Testing
```bash
# Run API health check
curl http://localhost:5000/api/health

# List available playbooks
curl http://localhost:5000/api/playbooks

# List jobs
curl http://localhost:5000/api/jobs

# Submit a job
curl -X POST http://localhost:5000/api/execute \
  -H "Content-Type: application/json" \
  -d '{"playbook":"test-playbook.yaml","hostname":"localhost"}'

# Open web interface
# Visit http://localhost:5000/ in your browser
# - View available playbooks as cards
# - Click "Run Playbook" on any playbook card
# - Enter target hostname and execute
# - Monitor job status and view logs
```

## Development
```bash
# Run with debug mode
FLASK_DEBUG=1 python -m flask run --host=0.0.0.0 --port=5000

# Check Celery tasks
celery -A app.celery_worker.celery inspect active
```