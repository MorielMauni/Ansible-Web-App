# Ansible Web API - Agent Guidelines

## Commands
- **Run development server**: `python -m flask run --host=0.0.0.0 --port=5000`
- **Database migrations**: `flask db migrate -m "description"` and `flask db upgrade`
- **Install dependencies**: `pip install -r requirements.txt`
- **Run tests**: `python -m pytest` (no test framework currently configured)

## Code Style Guidelines

### Imports & Structure
- Use absolute imports: `from app.extensions import db`
- Group imports: standard library, third-party, local app imports
- Use `pathlib.Path` for file operations instead of `os.path`

### Naming Conventions
- Classes: PascalCase (`AnsibleRunner`, `ValidationError`)
- Functions/variables: snake_case (`validate_hostname`, `playbook_name`)
- Constants: UPPER_SNAKE_CASE (`ALLOWED_PLAYBOOK_EXTENSIONS`)
- Database models: singular PascalCase (`Job`, not `Jobs`)

### Error Handling
- Use custom exceptions for validation (`ValidationError`)
- Log errors with appropriate levels using `current_app.logger`
- Always rollback database sessions on errors: `db.session.rollback()`
- Return JSON error responses with proper HTTP status codes

### Security
- Validate all user inputs against injection attacks
- Use subprocess with `shell=False` and explicit argument lists
- Implement path traversal protection for file operations
- Never expose secrets or sensitive data in logs/responses

### Database
- Use Flask-SQLAlchemy ORM models with `to_dict()` methods
- Always commit database transactions in try/except blocks
- Use `db.session.get()` for primary key lookups

### API Design
- Use Flask blueprints for route organization
- Return consistent JSON responses with proper status codes
- Implement proper HTTP methods (GET, POST, etc.)
- Add comprehensive error handlers for common HTTP errors