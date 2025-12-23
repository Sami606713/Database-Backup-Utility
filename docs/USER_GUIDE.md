# Database Backup Utility - User Guide

## Installation

```bash
# Clone the repository
git clone https://github.com/your-repo/database-backup-utility.git
cd database-backup-utility

# Install dependencies (using uv)
uv sync

# Or using pip
pip install -e .
```

---

## Quick Start

### 1. SQLite Backup (Simplest)
```bash
# Backup a SQLite database
db-backup backup --type sqlite --database ./myapp.db --output ./backups/

# Restore from backup
db-backup restore --type sqlite --file ./backups/myapp_20231215.db.gz --database ./restored.db
```

### 2. MySQL Backup
```bash
# Full backup with compression
db-backup backup \
    --type mysql \
    --host localhost \
    --port 3306 \
    --user root \
    --password secret \
    --database myapp \
    --backup-type full \
    --compress \
    --output ./backups/
```

### 3. Using Config File
```bash
# Generate config template
db-backup config init --output backup-config.yaml

# Run backup with config
db-backup backup --config backup-config.yaml
```

---

## CLI Commands

### `db-backup backup`
Create database backup.

| Option | Description | Required |
|--------|-------------|----------|
| `--type` | Database type (mysql/postgres/mongodb/sqlite) | Yes |
| `--host` | Database host | For remote DBs |
| `--port` | Database port | No (uses default) |
| `--user` | Database username | For auth DBs |
| `--password` | Database password | For auth DBs |
| `--database` | Database name or path | Yes |
| `--backup-type` | full/incremental/differential | No (default: full) |
| `--compress` | Enable gzip compression | No |
| `--output` | Output directory | Yes |
| `--storage` | Storage type (local/s3/gcs/azure) | No (default: local) |
| `--config` | Path to YAML config file | No |

### `db-backup restore`
Restore database from backup.

| Option | Description | Required |
|--------|-------------|----------|
| `--file` | Path to backup file | Yes |
| `--type` | Database type | Yes |
| `--host` | Target database host | For remote DBs |
| `--database` | Target database name | Yes |
| `--tables` | Specific tables to restore (comma-separated) | No |

### `db-backup schedule`
Manage backup schedules.

| Subcommand | Description |
|------------|-------------|
| `add` | Add new scheduled backup |
| `list` | List all scheduled jobs |
| `remove` | Remove scheduled job |
| `start` | Start scheduler daemon |
| `stop` | Stop scheduler daemon |

---

## Configuration File

Example `backup-config.yaml`:

```yaml
database:
  type: mysql
  host: localhost
  port: 3306
  user: backup_user
  password: ${DB_PASSWORD}  # Environment variable
  database: production_db

backup:
  type: full
  compress: true
  compression_level: 6

storage:
  type: s3
  bucket: my-backups
  prefix: mysql/production/
  region: us-east-1

notifications:
  slack:
    enabled: true
    webhook_url: ${SLACK_WEBHOOK_URL}
    channel: "#backups"

schedule:
  cron: "0 2 * * *"  # Daily at 2 AM
```

---

## Cloud Storage Setup

### AWS S3
```bash
# Set environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_REGION=us-east-1

# Backup to S3
db-backup backup --storage s3 --s3-bucket my-backups ...
```

### Google Cloud Storage
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
db-backup backup --storage gcs --gcs-bucket my-backups ...
```

### Azure Blob Storage
```bash
export AZURE_STORAGE_CONNECTION_STRING=your_connection_string
db-backup backup --storage azure --azure-container my-backups ...
```

---

## Logging

Logs are stored in `~/.db-backup/logs/` by default:
- `backup.log` - All backup/restore activities
- `error.log` - Errors only

Log format:
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "operation": "backup",
  "database": "myapp",
  "status": "success",
  "duration_seconds": 45,
  "file_size_mb": 128
}
```

---

## Troubleshooting

| Error | Solution |
|-------|----------|
| Connection refused | Check host/port, ensure DB is running |
| Access denied | Verify username/password, check DB permissions |
| mysqldump not found | Install MySQL client tools |
| Insufficient space | Check disk space, use compression |
