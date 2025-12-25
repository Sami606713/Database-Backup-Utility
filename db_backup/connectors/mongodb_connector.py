"""
MongoDB Connector for Database Backup Utility.

This connector uses pymongo for connection testing and mongodump/mongorestore
for backup and restore operations.
"""
from typing import Any, Dict, Optional, List
from pathlib import Path
import subprocess
import shutil
from db_backup.connectors.base import BaseConnector

try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False


class MongoDBConnector(BaseConnector):
    """MongoDB database connector with backup and restore support."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client: Optional[MongoClient] = None
    
    def _get_connection_uri(self) -> str:
        """Build MongoDB connection URI from config."""
        host = self.config.get("host", "localhost")
        port = self.config.get("port", 27017)
        username = self.config.get("username", "")
        password = self.config.get("password", "")
        database = self.config.get("database", "")
        auth_db = self.config.get("auth_database", "admin")
        
        # Build URI
        if username and password:
            uri = f"mongodb://{username}:{password}@{host}:{port}/{database}?authSource={auth_db}"
        else:
            uri = f"mongodb://{host}:{port}/{database}"
        
        return uri
    
    def connect(self):
        """Establish connection to MongoDB."""
        if not PYMONGO_AVAILABLE:
            raise ImportError(
                "pymongo is not installed. Please install it with: pip install pymongo"
            )
        
        uri = self._get_connection_uri()
        self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        # Trigger connection to verify
        self.client.admin.command('ping')
        self.connection = self.client
    
    def disconnect(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            self.client = None
            self.connection = None
    
    def verify_connection(self) -> bool:
        """Verify MongoDB connection is valid."""
        try:
            self.connect()
            # Try to ping the server
            self.client.admin.command('ping')
            return True
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"Connection failed: {e}")
            return False
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
        finally:
            self.disconnect()
    
    def get_databases(self) -> List[str]:
        """List all accessible databases."""
        if not self.client:
            self.connect()
        return self.client.list_database_names()
    
    def get_collections(self, database: str = None) -> List[str]:
        """List collections in a database."""
        if not self.client:
            self.connect()
        db_name = database or self.config.get("database")
        if not db_name:
            raise ValueError("Database name not provided")
        return self.client[db_name].list_collection_names()
    
    def _check_mongodump_available(self) -> bool:
        """Check if mongodump is available in PATH."""
        return shutil.which("mongodump") is not None
    
    def _check_mongorestore_available(self) -> bool:
        """Check if mongorestore is available in PATH."""
        return shutil.which("mongorestore") is not None
    
    def _build_connection_args(self) -> List[str]:
        """Build mongodump/mongorestore connection arguments."""
        args = []
        
        host = self.config.get("host", "localhost")
        port = self.config.get("port", 27017)
        username = self.config.get("username")
        password = self.config.get("password")
        auth_db = self.config.get("auth_database", "admin")
        
        args.extend(["--host", host])
        args.extend(["--port", str(port)])
        
        if username:
            args.extend(["--username", username])
        if password:
            args.extend(["--password", password])
            args.extend(["--authenticationDatabase", auth_db])
        
        return args
    
    def backup(
        self, 
        output_path: Path, 
        collections: Optional[List[str]] = None,
        compress: bool = True
    ) -> Path:
        """
        Create a MongoDB backup using mongodump.
        
        Args:
            output_path: Directory to store the backup
            collections: Optional list of collections to backup (None = all)
            compress: Whether to create gzip compressed archive
            
        Returns:
            Path to the backup file/directory
        """
        if not self._check_mongodump_available():
            raise RuntimeError(
                "mongodump not found. Please install MongoDB Database Tools.\n"
                "Download from: https://www.mongodb.com/try/download/database-tools"
            )
        
        database = self.config.get("database")
        if not database:
            raise ValueError("Database name not provided in config")
        
        # Ensure output directory exists
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Build command
        cmd = ["mongodump"]
        cmd.extend(self._build_connection_args())
        cmd.extend(["--db", database])
        
        # Add specific collections if provided
        if collections:
            for collection in collections:
                cmd.extend(["--collection", collection])
        
        if compress:
            # Create archive with gzip compression
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_name = f"{database}_{timestamp}.archive.gz"
            archive_path = output_path / archive_name
            cmd.extend(["--archive=" + str(archive_path), "--gzip"])
        else:
            # Output to directory
            cmd.extend(["--out", str(output_path)])
        
        # Execute mongodump
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            if compress:
                return archive_path
            else:
                return output_path / database
                
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"mongodump failed: {e.stderr}")
    
    def restore(
        self,
        backup_path: Path,
        target_database: Optional[str] = None,
        collections: Optional[List[str]] = None,
        drop: bool = False
    ) -> bool:
        """
        Restore a MongoDB backup using mongorestore.
        
        Args:
            backup_path: Path to backup archive or directory
            target_database: Optional target database name (None = use original name)
            collections: Optional list of collections to restore (None = all)
            drop: Whether to drop existing collections before restore
            
        Returns:
            True if restore successful
        """
        if not self._check_mongorestore_available():
            raise RuntimeError(
                "mongorestore not found. Please install MongoDB Database Tools.\n"
                "Download from: https://www.mongodb.com/try/download/database-tools"
            )
        
        backup_path = Path(backup_path)
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup path not found: {backup_path}")
        
        # Build command
        cmd = ["mongorestore"]
        cmd.extend(self._build_connection_args())
        
        # Target database
        db_name = target_database or self.config.get("database")
        if db_name:
            cmd.extend(["--db", db_name])
        
        # Drop existing collections
        if drop:
            cmd.append("--drop")
        
        # Restore specific collections
        if collections:
            for collection in collections:
                cmd.extend(["--collection", collection])
        
        # Handle archive vs directory
        if backup_path.suffix == ".gz" or ".archive" in backup_path.name:
            cmd.extend(["--archive=" + str(backup_path), "--gzip"])
        else:
            cmd.append(str(backup_path))
        
        # Execute mongorestore
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return True
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"mongorestore failed: {e.stderr}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        if not self.client:
            self.connect()
        
        database = self.config.get("database")
        if not database:
            raise ValueError("Database name not provided")
        
        db = self.client[database]
        stats = db.command("dbStats")
        
        return {
            "database": database,
            "collections": stats.get("collections", 0),
            "documents": stats.get("objects", 0),
            "data_size_mb": round(stats.get("dataSize", 0) / (1024 * 1024), 2),
            "storage_size_mb": round(stats.get("storageSize", 0) / (1024 * 1024), 2),
            "indexes": stats.get("indexes", 0)
        }
