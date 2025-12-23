# Database Backup Utility - Build Guide

**For**: 3-Member Development Team | **Duration**: 6 Weeks

---

## Quick Reference: Who Does What?

| Developer | Focus | First Task |
|-----------|-------|------------|
| **Dev 1** | Backend (DB connectors, backup logic) | `db_backup/core/config.py` |
| **Dev 2** | Infrastructure (storage, cloud, scheduler) | `db_backup/storage/base.py` |
| **Dev 3** | CLI & Testing (Typer, pytest, CI/CD) | Project setup, `db_backup/cli/app.py` |

---

## Week-by-Week Build Order

### Week 1: Setup & Core

```
Day 1 (All): Project Setup
├── Dev 3: Create folder structure (see below)
├── Dev 1: Start db_backup/core/config.py
└── Dev 2: Start db_backup/storage/base.py

Day 2-3: Core Abstractions
├── Dev 1: Finish config.py, start connectors/base.py
├── Dev 2: Finish base.py, start local_storage.py
└── Dev 3: Create logger.py, exceptions.py

Day 4-5: First Working Feature
├── Dev 1: Build sqlite_connector.py
├── Dev 2: Complete local_storage.py, compression.py
└── Dev 3: Build CLI structure, backup_commands.py
```

### Week 2: Integration

```
Day 1-2: Connect Components
├── All: Integrate SQLite + Local Storage + CLI
├── Dev 3: Write first integration test
└── Test: db-backup backup --type sqlite --database test.db

Day 3-5: Polish Sprint 1
├── Dev 1: Error handling in connectors
├── Dev 2: Error handling in storage
└── Dev 3: Help commands, basic documentation
```

**✅ Sprint 1 Checkpoint**: SQLite backup/restore works end-to-end

---

### Week 3-4: Core Features

```
Week 3:
├── Dev 1: MySQL connector (3 days), PostgreSQL connector (2 days)
├── Dev 2: AWS S3 storage (3 days), start GCS (2 days)
└── Dev 3: Restore commands, improve CLI output

Week 4:
├── Dev 1: MongoDB connector, unit tests
├── Dev 2: Azure storage, compression improvements
└── Dev 3: Integration tests for all DB types
```

**✅ Sprint 2 Checkpoint**: All 4 DB types + 3 cloud storage backends work

---

### Week 5-6: Production Features

```
Week 5:
├── Dev 1: Incremental backup, selective restore
├── Dev 2: APScheduler integration, scheduler commands
└── Dev 3: YAML config file support, validation

Week 6:
├── Dev 1: Code review, bug fixes
├── Dev 2: Slack notifications, Docker image
└── Dev 3: CI/CD, PyPI packaging, final docs
```

**✅ Sprint 3 Checkpoint**: Production-ready product

---

## Commands to Create Folder Structure

```bash
# Dev 3 runs this on Day 1
cd d:/products/Database-Backup-Utility

# Create package structure
mkdir -p db_backup/cli
mkdir -p db_backup/core
mkdir -p db_backup/connectors
mkdir -p db_backup/backup/strategies
mkdir -p db_backup/restore
mkdir -p db_backup/storage
mkdir -p db_backup/scheduler
mkdir -p db_backup/notifications

# Create test structure
mkdir -p tests/unit
mkdir -p tests/integration

# Create config examples
mkdir -p configs

# Create __init__.py files
touch db_backup/__init__.py
touch db_backup/cli/__init__.py
touch db_backup/core/__init__.py
touch db_backup/connectors/__init__.py
touch db_backup/backup/__init__.py
touch db_backup/backup/strategies/__init__.py
touch db_backup/restore/__init__.py
touch db_backup/storage/__init__.py
touch db_backup/scheduler/__init__.py
touch db_backup/notifications/__init__.py
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/integration/__init__.py
```

---

## Dependencies to Add (pyproject.toml)

```toml
dependencies = [
    # CLI
    "typer>=0.20.1",
    "rich>=13.0.0",
    
    # Config
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "pyyaml>=6.0",
    
    # Cloud Storage
    "boto3>=1.34.0",           # AWS S3
    "google-cloud-storage>=2.14.0",  # GCS
    "azure-storage-blob>=12.19.0",   # Azure
    
    # Scheduling
    "apscheduler>=3.10.0",
    
    # Notifications
    "slack-sdk>=3.26.0",
    
    # Database (optional, for pymysql/psycopg2 approach)
    # We'll use native dump tools instead
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=24.0.0",
    "ruff>=0.1.0",
    "mypy>=1.8.0",
]

[project.scripts]
db-backup = "db_backup.cli.app:app"
```

---

## Git Branch Strategy

```bash
# Initial setup
git checkout -b develop
git push -u origin develop

# Each developer creates feature branch
git checkout -b feature/sqlite-connector  # Dev 1
git checkout -b feature/local-storage     # Dev 2
git checkout -b feature/cli-structure     # Dev 3

# After completion, PR to develop
# Weekly release from develop → main
```

---

## Daily Standup Template

```
What I did yesterday:
- [Task completed]

What I'm doing today:
- [Current task]

Blockers:
- [Any issues]
```

---

## Definition of "Done" Checklist

Before merging any feature:

- [ ] Code has type hints
- [ ] Docstrings on public functions
- [ ] Unit tests written (aim for >80% coverage)
- [ ] No linting errors (`uv run ruff check .`)
- [ ] Formatted with Black (`uv run black .`)
- [ ] Tested manually
- [ ] PR reviewed by 1 teammate
