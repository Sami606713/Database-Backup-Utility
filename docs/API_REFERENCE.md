# Database Backup Utility - API Reference

## Core Classes

### `BaseConnector` (Abstract)
Base class for all database connectors.

```python
from db_backup.connectors.base import BaseConnector

class BaseConnector(ABC):
    def __init__(self, config: DatabaseConfig): ...
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test database connection and credentials."""
        
    @abstractmethod
    def get_databases(self) -> List[str]:
        """List all accessible databases."""
        
    @abstractmethod
    def get_tables(self, database: str) -> List[str]:
        """List tables/collections in a database."""
        
    @abstractmethod
    def dump(self, output_path: Path, tables: List[str] = None) -> Path:
        """Create backup dump. Returns path to dump file."""
        
    @abstractmethod
    def restore(self, backup_path: Path, tables: List[str] = None) -> bool:
        """Restore from backup file. Returns success status."""
```

---

### `BaseStorage` (Abstract)
Base class for storage backends.

```python
from db_backup.storage.base import BaseStorage

class BaseStorage(ABC):
    def __init__(self, config: StorageConfig): ...
    
    @abstractmethod
    def upload(self, local_path: Path, remote_key: str) -> str:
        """Upload file. Returns remote URL/path."""
        
    @abstractmethod
    def download(self, remote_key: str, local_path: Path) -> Path:
        """Download file. Returns local path."""
        
    @abstractmethod
    def list_backups(self, prefix: str = "") -> List[BackupInfo]:
        """List available backups."""
        
    @abstractmethod
    def delete(self, remote_key: str) -> bool:
        """Delete backup file."""
```

---

### `BackupManager`
Orchestrates backup operations.

```python
from db_backup.backup.backup_manager import BackupManager

manager = BackupManager(
    connector=MySQLConnector(db_config),
    storage=S3Storage(storage_config),
    compress=True
)

# Run backup
result = manager.backup(backup_type=BackupType.FULL)
# Returns: BackupResult(path, size, duration, status)
```

---

### `RestoreManager`
Orchestrates restore operations.

```python
from db_backup.restore.restore_manager import RestoreManager

manager = RestoreManager(
    connector=MySQLConnector(db_config),
    storage=S3Storage(storage_config)
)

# Full restore
result = manager.restore(backup_path="s3://bucket/backup.sql.gz")

# Selective restore
result = manager.restore(
    backup_path="./backup.sql.gz",
    tables=["users", "orders"]
)
```

---

## Configuration Models

### `DatabaseConfig`
```python
from db_backup.core.config import DatabaseConfig

config = DatabaseConfig(
    type="mysql",           # mysql | postgres | mongodb | sqlite
    host="localhost",
    port=3306,
    user="root",
    password="secret",
    database="myapp"
)
```

### `StorageConfig`
```python
from db_backup.core.config import StorageConfig

# Local storage
local_config = StorageConfig(type="local", path="./backups")

# S3 storage
s3_config = StorageConfig(
    type="s3",
    bucket="my-backups",
    prefix="mysql/",
    region="us-east-1"
)
```

### `BackupConfig`
```python
from db_backup.core.config import BackupConfig

config = BackupConfig(
    type=BackupType.FULL,
    compress=True,
    compression_level=6
)
```

---

## Enums

### `BackupType`
```python
from db_backup.core.constants import BackupType

BackupType.FULL         # Complete backup
BackupType.INCREMENTAL  # Changes since last backup
BackupType.DIFFERENTIAL # Changes since last full
```

### `DBType`
```python
from db_backup.core.constants import DBType

DBType.MYSQL
DBType.POSTGRES
DBType.MONGODB
DBType.SQLITE
```

### `StorageType`
```python
from db_backup.core.constants import StorageType

StorageType.LOCAL
StorageType.S3
StorageType.GCS
StorageType.AZURE
```

---

## Exceptions

```python
from db_backup.core.exceptions import (
    BackupError,           # Base exception
    ConnectionError,       # DB connection failed
    AuthenticationError,   # Invalid credentials
    BackupOperationError,  # Backup failed
    RestoreOperationError, # Restore failed
    StorageError,          # Storage operation failed
    CompressionError,      # Compression failed
)
```

---

## Extending with Custom Connectors

```python
from db_backup.connectors.base import BaseConnector

class CustomDBConnector(BaseConnector):
    def test_connection(self) -> bool:
        # Implement connection test
        pass
    
    def dump(self, output_path: Path, tables: List[str] = None) -> Path:
        # Implement backup logic
        pass
    
    def restore(self, backup_path: Path, tables: List[str] = None) -> bool:
        # Implement restore logic
        pass
```
