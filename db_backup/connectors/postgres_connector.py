from typing import Any, Dict
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
