import sqlite3
from pathlib import Path
from typing import Any, Dict
from db_backup.connectors.base import BaseConnector

class SQLiteConnector(BaseConnector):
    def connect(self):
        db_path = self.config.get("database")
        if not db_path:
            raise ValueError("Database path not provided in config")
        
        # Ensure directory exists if it's a new file, though usually for connect it should exist or be created
        # user might provide a path relative to CWD
        self.connection = sqlite3.connect(db_path)

    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def verify_connection(self) -> bool:
        try:
            self.connect()
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
        finally:
            self.disconnect()
