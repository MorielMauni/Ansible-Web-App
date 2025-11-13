from datetime import datetime
from app.extensions import db

class Job(db.Model):
    """Model for tracking Ansible job executions."""
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    playbook_name = db.Column(db.String(255), nullable=False)
    target_host = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, running, success, failed
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    stdout = db.Column(db.Text, nullable=True)
    stderr = db.Column(db.Text, nullable=True)
    exit_code = db.Column(db.Integer, nullable=True)
    
    def __repr__(self):
        return f'<Job {self.id}: {self.playbook_name} -> {self.target_host}>'
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'playbook_name': self.playbook_name,
            'target_host': self.target_host,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'exit_code': self.exit_code
        }
    
    def to_dict_with_output(self):
        """Include output logs in dictionary."""
        data = self.to_dict()
        data.update({
            'stdout': self.stdout,
            'stderr': self.stderr
        })
        return data
