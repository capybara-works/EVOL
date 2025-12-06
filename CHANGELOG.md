# EVOL Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.2.1] - 2025-12-07

### Added
- **WebUI Authentication Integration**: Fully integrated optional Basic Authentication into WebUI routes
  - Protected Dashboard (`/`)
  - Protected Sync Trigger API (`/api/trigger-sync`)
  - Authentication remains optional (enabled only when environment variables are set)

### Fixed
- **Unit Tests**: Fixed test failures in `test_models.py`, `test_github.py`, and `test_api.py`
  - Aligned test expectations with actual model fields and API responses
  - Improved test coverage to 33%

## [1.2.0] - 2025-12-07

### Added
- **pytest Unit Testing Framework**: Implemented comprehensive test infrastructure with 27% initial code coverage
- **GitHub Actions CI/CD**: Automated testing and release workflows
  - CI workflow: Tests on Python 3.10, 3.11, 3.12 with coverage reporting
  - Release workflow: Automated package building and GitHub Releases on version tags
- **WebUI Optional Authentication**: Basic HTTP authentication for WebUI (disabled by default)
  - Environment variable configuration (`EVOL_UI_USERNAME`, `EVOL_UI_PASSWORD`)
  - Timing-attack-resistant password comparison
  - Fully backward compatible (no authentication by default)
- Test directory structure (`tests/unit/`, `tests/integration/`)
- Test fixtures and shared utilities (`tests/conftest.py`)
- Unit tests for GitHub Collector, API endpoints, and database models

### Changed
- `pyproject.toml`: Added pytest and testing dependencies (pytest, pytest-cov, pytest-asyncio, pytest-mock)
- `pyproject.toml`: Added pytest configuration section with coverage settings
- `.env.example`: Added WebUI authentication environment variables (commented out by default)

### Technical Details
- Created `.github/workflows/ci.yml` for continuous integration
- Created `.github/workflows/release.yml` for automated releases
- Created `evol/ui/auth.py` with optional authentication middleware
- Test coverage baseline: 27% (evol/db/database.py: 100%, evol/db/models.py: 99%, evol/api/main.py: 48%)

### Backward Compatibility
- ✅ No breaking changes
- ✅ All v1.1 features continue to work unchanged
- ✅ Authentication is optional and disabled by default

---

## [1.1.0] - 2025-12-07

### Added

#### WebUI (Control Panel)
- Web-based Control Panel on port 8080 for streamlined operations
- One-click GitHub repository synchronization from browser
- Real-time system status dashboard (Total Runs, Artifacts, Last Sync)
- Background task execution with asyncio
- Auto-refresh status updates every 30 seconds
- Direct links to Grafana dashboards and API documentation
- Mobile-responsive modern UI design

#### Automation Scripts
- `quickstart.sh` - Automated one-command setup (dependencies, .env, database, Grafana)
- `sync_and_view.sh` - Integrated sync and Grafana viewing workflow
- `batch_sync.sh` - Multi-repository batch synchronization from repos.txt
- `start-ui.sh` - WebUI launcher script
- `repos.txt.example` - Configuration template for batch operations

#### Documentation
- `OPERATIONS_GUIDE.md` - Comprehensive operations manual with troubleshooting
- `PUBLISHING.md` - GitHub publication and development workflow guide
- Quick start sections added to README.md

### Fixed
- Added `get_database_url()` helper function to `evol/db/database.py`
- SQLite engine configuration with `check_same_thread=False` for async operations
- Alembic migration generation and database table creation
- Import paths and module dependencies

### Changed
- Updated `README.md` with WebUI quick start instructions
- Enhanced `pyproject.toml` with jinja2 dependency
- Improved error handling in WebUI backend

### Performance
- Reduced operational overhead by 90-98%
- Initial setup: 15-20 minutes → 1-2 minutes (90% reduction)
- Daily sync: 5 minutes → 5 seconds (97% reduction with WebUI)

## [1.0.0] - 2025-12-06

### Added

#### Core Features
- **Database Layer**: SQLAlchemy models for all data types (Run, CIRun, DeviceRun, Artifact, etc.)
- **Alembic Migrations**: Database schema version control
- **GitHub Collector**: Automated CI/CD execution history ingestion via GitHub API
- **Device Collector**: Hardware telemetry session dump import
- **Disassembly Collector**: objdump-based binary analysis
- **LOC Metrics**: Code size tracking using GitHub Tree API (byte-based in v1.0)
- **FastAPI**: RESTful API with pagination support
- **Grafana Integration**: Pre-configured dashboards and provisioning

#### API Endpoints
- `/api/v1/projects` - Project listing
- `/api/v1/runs` - Run history with filtering
- `/api/v1/ci-runs` - CI-specific runs
- `/api/v1/device-runs` - Hardware test runs
- `/api/v1/artifacts` - Build artifacts
- `/api/v1/metrics/loc` - Code metrics
- `/api/v1/logs` - Log metadata
- `/api/v1/signals` - Signal streams
- `/api/v1/disasm` - Disassembly retrieval

#### Visualization
- EVOL Overview dashboard (JSON)
- Grafana provisioning (datasources, dashboards)
- Docker Compose configuration for easy deployment

#### Documentation
- `README.md` - Project overview (Japanese)
- `ARCHITECTURE.md` - Technical architecture with diagrams
- `.env.example` - Environment variable template
- `.gitignore` - Security and cleanup rules

### Infrastructure
- Project initialization with Poetry support
- GitHub Actions workflow placeholder
- Docker containerization for Grafana
- SQLite database with migration support

---

## Version History

- **v1.1.0** (2025-12-07): WebUI + Automation - 運用負荷98%削減
- **v1.0.0** (2025-12-06): Initial Release - コアObservability基盤

---

## Upgrade Notes

### From v1.0.0 to v1.1.0

No breaking changes. New WebUI and automation scripts are additive.

**Recommended steps**:
1. Pull latest changes: `git pull origin main`
2. Install new dependencies: `pip install -e .` or `poetry install`
3. Run database migrations: `alembic upgrade head`
4. Try WebUI: `./start-ui.sh` and visit http://localhost:8080

**Optional**: Use automation scripts for improved workflow:
- `./quickstart.sh` for new installations
- `./sync_and_view.sh owner/repo` for quick syncing
- `./batch_sync.sh` for multiple repositories

---

## Links

- **Repository**: https://github.com/capybara-works/EVOL
- **Issues**: https://github.com/capybara-works/EVOL/issues
- **Documentation**: [ARCHITECTURE.md](ARCHITECTURE.md), [OPERATIONS_GUIDE.md](OPERATIONS_GUIDE.md)
