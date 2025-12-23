# Database Backup Utility

A production-ready CLI tool for backing up and restoring databases with support for multiple DBMS, cloud storage, scheduling, and notifications.

## Features

- **Multi-Database Support**: MySQL, PostgreSQL, MongoDB, SQLite
- **Backup Types**: Full, Incremental, Differential
- **Compression**: gzip/zip with configurable compression levels
- **Cloud Storage**: AWS S3, Google Cloud Storage, Azure Blob Storage
- **Local Storage**: Filesystem backups with directory management
- **Scheduling**: Cron-like backup scheduling with APScheduler
- **Notifications**: Slack and Email notifications
- **Logging**: Structured logging with rotation

## Quick Start

```bash
# Install dependencies
uv sync

# SQLite backup (simplest example)
uv run python main.py backup --type sqlite --database ./myapp.db --output ./backups/

# MySQL backup
uv run python main.py backup \
    --type mysql \
    --host localhost \
    --user root \
    --password secret \
    --database myapp \
    --compress \
    --output ./backups/

# Restore from backup
uv run python main.py restore --type mysql --file ./backups/myapp.sql.gz --database myapp
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md) - System design and component overview
- [Folder Structure](docs/FOLDER_STRUCTURE.md) - Project structure explanation
- [User Guide](docs/USER_GUIDE.md) - Installation and usage instructions
- [API Reference](docs/API_REFERENCE.md) - Programmatic usage
- [Contributing](docs/CONTRIBUTING.md) - Development guidelines

## Project Structure

```
db_backup/
├── cli/           # CLI commands (Typer)
├── core/          # Config, logging, exceptions
├── connectors/    # Database connectors (MySQL, PostgreSQL, MongoDB, SQLite)
├── backup/        # Backup strategies and compression
├── restore/       # Restore operations
├── storage/       # Storage backends (Local, S3, GCS, Azure)
├── scheduler/     # Backup scheduling
└── notifications/ # Slack/Email notifications
```

## Development

```bash
# Install dev dependencies
uv sync --dev

# Run tests
uv run pytest

# Format code
uv run black .
uv run ruff check .
```

## License

MIT License
