import re
import os
from pathlib import Path
from flask import current_app

class ValidationError(Exception):
    """Custom validation exception."""
    pass

def validate_hostname(hostname):
    """
    Validate hostname to prevent command injection.
    Allows: alphanumeric, dots, hyphens, underscores.
    """
    if not hostname:
        raise ValidationError("Hostname cannot be empty")
    
    if len(hostname) > 253:
        raise ValidationError("Hostname too long")
    
    # RFC 1123 compliant hostname pattern + IP addresses
    pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$|^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
    
    if not re.match(pattern, hostname):
        raise ValidationError("Invalid hostname format")
    
    # Block suspicious patterns
    dangerous_chars = [';', '|', '&', '`', '$', '(', ')', '<', '>', '\n', '\r']
    if any(char in hostname for char in dangerous_chars):
        raise ValidationError("Hostname contains invalid characters")
    
    return hostname

def validate_playbook(playbook_name):
    """
    Validate playbook name and ensure it exists.
    Prevents directory traversal attacks.
    """
    if not playbook_name:
        raise ValidationError("Playbook name cannot be empty")
    
    # Block directory traversal attempts
    if '..' in playbook_name or '/' in playbook_name or '\\' in playbook_name:
        raise ValidationError("Invalid playbook name")
    
    # Ensure it has valid extension
    allowed_extensions = current_app.config['ALLOWED_PLAYBOOK_EXTENSIONS']
    if not any(playbook_name.endswith(ext) for ext in allowed_extensions):
        raise ValidationError(f"Playbook must have extension: {', '.join(allowed_extensions)}")
    
    # Verify file exists
    playbook_dir = Path(current_app.config['ANSIBLE_PLAYBOOK_DIR'])
    playbook_path = playbook_dir / playbook_name
    
    if not playbook_path.exists():
        raise ValidationError(f"Playbook '{playbook_name}' not found")
    
    # Ensure the resolved path is still within playbook directory (prevent symlink attacks)
    if not str(playbook_path.resolve()).startswith(str(playbook_dir.resolve())):
        raise ValidationError("Invalid playbook path")
    
    return playbook_name
