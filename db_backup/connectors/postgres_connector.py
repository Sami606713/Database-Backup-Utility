from typing import Any, Dict
import os
from db_backup.connectors.base import BaseConnector

try:
    import psycopg2
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

class PostgresConnector(BaseConnector):
    def connect(self):
        if not PSYCOPG2_AVAILABLE:
            raise ImportError("psycopg2 is not installed. Please install it to use PostgreSQL.")
        
        self.connection = psycopg2.connect(
            host=self.config.get("host"),
            port=self.config.get("port", 5432),
            user=self.config.get("username"),
            password=self.config.get("password"),
            dbname=self.config.get("database")
        )

    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def verify_connection(self) -> bool:
        try:
            self.connect()
            if self.connection:
                with self.connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                return True
            return False
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
        finally:
            self.disconnect()

    def _get_env(self) -> Dict[str, str]:
        env = os.environ.copy()
        password = self.config.get("password")
        if password:
            env["PGPASSWORD"] = password
        return env

    def backup_database(self, timestamp: str) -> str:
        """
        Creates a backup of the PostgreSQL database.
        Returns the path to the backup ZIP file.
        """
        import subprocess
        import os
        import zipfile
        from pathlib import Path

        db_name = self.config.get("database")
        host = self.config.get("host")
        port = str(self.config.get("port", 5432))
        user = self.config.get("username")

        backup_dir = Path(".backup/postgres")
        backup_dir.mkdir(parents=True, exist_ok=True)

        backup_zip_path = backup_dir / f"{db_name}_{timestamp}.zip"
        temp_sql_path = backup_dir / f"{db_name}_{timestamp}.sql"

        cmd = [
            "pg_dump",
            "-h", host,
            "-p", port,
            "-U", user,
            "-F", "p",  # Plain text format
            "-f", str(temp_sql_path),
            db_name
        ]

        try:
            subprocess.run(
                cmd, 
                check=True, 
                env=self._get_env(), 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            
            # Compress to ZIP
            with zipfile.ZipFile(backup_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(temp_sql_path, arcname=f"{db_name}_{timestamp}.sql")
            
            return str(backup_zip_path.absolute())

        except subprocess.CalledProcessError as e:
            # Clean up if failed
            if temp_sql_path.exists():
                temp_sql_path.unlink()
            raise Exception(f"Backup failed: {e.stderr.decode()}")
        finally:
            # Always clean up temp sql file
            if temp_sql_path.exists():
                temp_sql_path.unlink()

    def list_backups(self) -> list[str]:
        """Returns a list of available backup files, sorted by newest first."""
        import os
        from pathlib import Path
        
        backup_dir = Path(".backup/postgres")
        if not backup_dir.exists():
            return []
            
        files = [f.name for f in backup_dir.glob("*.zip")]
        # Sort by modification time, newest first
        files.sort(key=lambda x: (backup_dir / x).stat().st_mtime, reverse=True)
        return files

    def restore_database(self, backup_filename: str):
        """
        Restores the database from a given backup ZIP file.
        """
        import subprocess
        import os
        import zipfile
        from pathlib import Path

        backup_dir = Path(".backup/postgres")
        backup_path = backup_dir / backup_filename
        
        if not backup_path.exists():
             raise FileNotFoundError(f"Backup file not found: {backup_path}")

        db_name = self.config.get("database")
        host = self.config.get("host")
        port = str(self.config.get("port", 5432))
        user = self.config.get("username")
        
        # Extract path
        extracted_sql_path = None

        try:
            # Extract SQL
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                # We assume there's one SQL file inside matching the pattern or we check contents
                # For simplicity, let's take the first file that ends with .sql
                sql_files = [f for f in zipf.namelist() if f.endswith('.sql')]
                if not sql_files:
                     raise Exception("No SQL file found in the backup archive.")
                
                # Extract specifically that file using its original name
                extracted_sql_filename = sql_files[0]
                extracted_sql_path = backup_dir / extracted_sql_filename

                with zipf.open(extracted_sql_filename) as source, open(extracted_sql_path, "wb") as target:
                    import shutil
                    shutil.copyfileobj(source, target)
            
            print(f"Extracted backup file to: {extracted_sql_path}")

            # Restore using psql
            cmd = [
                "psql",
                "-h", host,
                "-p", port,
                "-U", user,
                "-d", db_name,
                "-f", str(extracted_sql_path)
            ]
            
            subprocess.run(
                cmd,
                check=True,
                env=self._get_env(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
        except subprocess.CalledProcessError as e:
             raise Exception(f"Restore failed: {e.stderr.decode()}")
