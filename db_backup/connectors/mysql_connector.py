from typing import Any, Dict
from db_backup.connectors.base import BaseConnector

try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

class MySQLConnector(BaseConnector):
    def connect(self):
        if not MYSQL_AVAILABLE:
            raise ImportError("mysql-connector-python is not installed. Please install it to use MySQL.")
        
        self.connection = mysql.connector.connect(
            host=self.config.get("host"),
            port=self.config.get("port", 3306),
            user=self.config.get("username"),
            password=self.config.get("password"),
            database=self.config.get("database")
        )

    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def verify_connection(self) -> bool:
        try:
            self.connect()
            if self.connection and self.connection.is_connected():
                cursor = self.connection.cursor()
                cursor.execute("SELECT 1")
                return True
            return False
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
        finally:
            self.disconnect()
