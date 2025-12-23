# Database Backup Utility - Folder Structure

This document explains the production-ready folder structure for the Database Backup Utility CLI tool.

## Root Structure

```
Database-Backup-Utility/
├── main.py                 # CLI entry point
├── pyproject.toml          # Dependencies & project config
├── README.md               # Quick start guide
├── .env.example            # Environment template
├── db_backup/              # Main package
├── docs/                   # Documentation
├── tests/                  # Test suite
├── configs/                # YAML config files
└── scripts/                # Utility scripts
```

---

## Main Package: `db_backup/`

### CLI Layer (`cli/`)
| File | Purpose |
|------|---------|
| `app.py` | Main Typer app, registers all sub-commands |
| `backup_commands.py` | `backup` command with all options |
| `restore_commands.py` | `restore` command with selective restore |
| `schedule_commands.py` | Scheduling commands (start, stop, list) |
| `config_commands.py` | Config management (init, validate, show) |

### Core Layer (`core/`)
| File | Purpose |
|------|---------|
| `config.py` | Pydantic config from YAML/env vars |
| `logger.py` | Structured logging with rotation |
| `exceptions.py` | Custom exception hierarchy |
| `constants.py` | Enums: BackupType, DBType, StorageType |

### Connectors Layer (`connectors/`)
| File | Purpose |
|------|---------|
| `base.py` | Abstract `BaseConnector` class |
| `mysql_connector.py` | MySQL/MariaDB using `mysqldump` |
| `postgres_connector.py` | PostgreSQL using `pg_dump` |
| `mongodb_connector.py` | MongoDB using `mongodump` |
| `sqlite_connector.py` | SQLite via file operations |

### Backup Layer (`backup/`)
| File | Purpose |
|------|---------|
| `backup_manager.py` | Orchestrates backup flow |
| `strategies/full_backup.py` | Full database dump |
| `strategies/incremental_backup.py` | Changes since last backup |
| `strategies/differential_backup.py` | Changes since last full |
| `compression.py` | gzip/zip compression utilities |

### Storage Layer (`storage/`)
| File | Purpose |
|------|---------|
| `base.py` | Abstract `BaseStorage` class |
| `local_storage.py` | Local filesystem storage |
| `s3_storage.py` | AWS S3 via boto3 |
| `gcs_storage.py` | Google Cloud Storage |
| `azure_storage.py` | Azure Blob Storage |

### Restore Layer (`restore/`)
| File | Purpose |
|------|---------|
| `restore_manager.py` | Orchestrates restore flow |
| `validators.py` | Pre-restore validation checks |

### Scheduler Layer (`scheduler/`)
| File | Purpose |
|------|---------|
| `scheduler.py` | APScheduler-based scheduling |
| `jobs.py` | Job definitions and handlers |

### Notifications Layer (`notifications/`)
| File | Purpose |
|------|---------|
| `base.py` | Abstract `BaseNotifier` class |
| `slack_notifier.py` | Slack webhook integration |
| `email_notifier.py` | SMTP email notifications |

---

## Why This Structure?

1. **Separation of Concerns**: Each layer handles one responsibility
2. **Plugin Architecture**: Easy to add new DB connectors or storage backends
3. **Testability**: Each component can be tested in isolation
4. **Maintainability**: Clear boundaries between components
5. **Scalability**: New features fit naturally into existing structure
