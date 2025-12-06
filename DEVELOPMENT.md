# EVOL Development Guide

This document provides guidance for developers working on EVOL.

## Development Environment Setup

### Prerequisites

- Python 3.10 or higher
- Git
- Docker and Docker Compose (for Grafana)
- Optional: Poetry for dependency management

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/capybara-works/EVOL.git
cd EVOL

# Run automated setup
./quickstart.sh

# Or manual setup
pip install -e .
cp .env.example .env
# Edit .env to add your GITHUB_TOKEN
alembic upgrade head
```

## Project Structure

```
EVOL/
├── evol/                   # Main package
│   ├── api/               # FastAPI application
│   │   └── main.py       # API endpoints
│   ├── collector/         # Data collection modules
│   │   ├── github.py     # GitHub API integration
│   │   ├── device.py     # Hardware telemetry
│   │   ├── disasm.py     # Binary disassembly
│   │   └── sync.py       # CLI entrypoint
│   ├── db/               # Database layer
│   │   ├── models.py     # SQLAlchemy models
│   │   └── database.py   # DB configuration
│   └── ui/               # WebUI (v1.1+)
│       ├── app.py        # FastAPI Control Panel
│       ├── templates/    # Jinja2 HTML
│       └── static/       # CSS, JavaScript
├── alembic/              # Database migrations
├── dashboards/           # Grafana dashboards
├── grafana/              # Grafana provisioning
├── *.sh                  # Automation scripts
├── pyproject.toml        # Dependencies
├── ARCHITECTURE.md       # Technical documentation
├── OPERATIONS_GUIDE.md   # Operations manual
└── CHANGELOG.md          # Version history
```

## Development Workflow

### Making Changes

1. **Create a branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Follow existing code style
   - Update documentation if needed
   - Add type hints to Python code

3. **Test manually**:
   ```bash
   # Run collectors
   python -m evol.collector.sync --project owner/repo
   
   # Start API
   uvicorn evol.api.main:app --reload
   
   # Start WebUI
   ./start-ui.sh
   ```

4. **Create database migration** (if schema changed):
   ```bash
   alembic revision --autogenerate -m "Description of change"
   alembic upgrade head
   ```

5. **Commit changes**:
   ```bash
   git add .
   git commit -m "type: description"
   ```

### Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `test:` Adding tests
- `chore:` Maintenance tasks

Examples:
```
feat: Add WebSocket support for real-time logs
fix: Correct SQLite threading issue in WebUI
docs: Update OPERATIONS_GUIDE with new examples
```

## Adding New Features

### Adding a New Collector

1. Create file in `evol/collector/`:
   ```python
   # evol/collector/my_source.py
   from evol.db.models import Run
   from evol.db.database import SessionLocal
   
   def collect_my_data(params):
       session = SessionLocal()
       try:
           # Collection logic
           run = Run(...)
           session.add(run)
           session.commit()
       finally:
           session.close()
   ```

2. Add CLI command to `sync.py`
3. Update documentation

### Adding API Endpoints

1. Edit `evol/api/main.py`:
   ```python
   @app.get("/api/v1/my-endpoint")
   async def get_my_data(db: Session = Depends(get_db)):
       # Implementation
       return JSONResponse(...)
   ```

2. Update API documentation in `ARCHITECTURE.md`

### Adding WebUI Features

1. **Backend** (`evol/ui/app.py`):
   ```python
   @app.post("/api/my-action")
   async def my_action(background_tasks: BackgroundTasks):
       # Implementation
       return JSONResponse({"status": "started"})
   ```

2. **Frontend** (`evol/ui/static/app.js`):
   ```javascript
   async function myAction() {
       const response = await fetch('/api/my-action', {method: 'POST'});
       // Handle response
   }
   ```

3. **UI** (`evol/ui/templates/index.html`):
   ```html
   <button onclick="myAction()">My Action</button>
   ```

## Database Changes

### Creating Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add new table"

# Review the generated file in alembic/versions/

# Apply migration
alembic upgrade head

# Rollback (if needed)
alembic downgrade -1
```

### Model Guidelines

- Use UUIDs for primary keys (`run_id`, `artifact_id`, etc.)
- Add appropriate indexes for query performance
- Include timestamps (`created_at`, `started_at`)
- Use enums for status fields
- Add foreign key constraints

## Testing

### Manual Testing Checklist

- [ ] Data collection works (GitHub, device, disasm)
- [ ] API endpoints return correct data
- [ ] WebUI loads and displays information
- [ ] Database migrations apply cleanly
- [ ] Automation scripts execute successfully

### Future: Automated Testing

V1.2+ will include:
- Unit tests with pytest
- Integration tests for collectors
- API endpoint tests
- WebUI component tests

## Troubleshooting

### Common Issues

**"ModuleNotFoundError"**:
```bash
pip install -e .
```

**"no such table: runs"**:
```bash
alembic upgrade head
```

**"GITHUB_TOKEN not set"**:
```bash
echo "GITHUB_TOKEN=your_token" >> .env
```

**"database is locked"**:
```bash
# Stop all EVOL processes
pkill -f "evol.collector"
pkill -f "uvicorn"
```

## Code Style

- **Python**: Follow PEP 8
- **Type Hints**: Use for all function signatures
- **Docstrings**: Use for public functions
- **Line Length**: Max 100 characters
- **Imports**: Group stdlib, third-party, local

Example:
```python
from typing import Optional
from sqlalchemy.orm import Session
from evol.db.models import Run

def get_run_by_id(session: Session, run_id: str) -> Optional[Run]:
    """Get a run by its ID.
    
    Args:
        session: Database session
        run_id: UUID of the run
        
    Returns:
        Run object if found, None otherwise
    """
    return session.query(Run).filter(Run.run_id == run_id).first()
```

## Performance Considerations

### Database

- Use indexes for frequently queried columns
- Batch inserts when possible
- Close sessions promptly
- Use pagination for large result sets

### API

- Implement caching for expensive queries
- Use async/await for I/O operations
- Set appropriate rate limits

### WebUI

- Minimize JavaScript bundle size
- Use CSS efficiently
- Implement lazy loading for large lists

## Deployment

### Local Development

```bash
# API only
uvicorn evol.api.main:app --reload

# WebUI only
./start-ui.sh

# Grafana
docker-compose up -d

# All-in-one (future)
docker-compose -f docker-compose.full.yml up
```

### Production Considerations

- Use proper PostgreSQL instead of SQLite
- Add authentication to WebUI
- Set up reverse proxy (nginx)
- Configure SSL/TLS
- Implement logging and monitoring
- Set up automated backups

## Contributing

1. Fork the repository
2. Create your feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

See [PUBLISHING.md](PUBLISHING.md) for detailed contribution guidelines.

## Resources

- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Operations**: [OPERATIONS_GUIDE.md](OPERATIONS_ GUIDE.md)
- **API Docs**: http://localhost:8000/docs (when running)
- **Issues**: https://github.com/capybara-works/EVOL/issues

## License

This project is part of the EVOL observability system.

---

**Note**: This guide is a living document. Please keep it updated as the project evolves.
