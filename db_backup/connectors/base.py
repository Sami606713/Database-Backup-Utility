from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseConnector(ABC):
    """Abstract base class for database connectors."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connection = None

    @abstractmethod
    def connect(self):
        """Establish a connection to the database."""
        pass

    @abstractmethod
    def disconnect(self):
        """Close the database connection."""
        pass

    @abstractmethod
    def verify_connection(self) -> bool:
        """Verify that the connection is valid."""
        pass
