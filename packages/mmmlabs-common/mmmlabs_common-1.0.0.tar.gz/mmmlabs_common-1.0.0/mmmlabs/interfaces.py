"""
Abstract interfaces for cloud services to ensure consistent API across providers.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, AsyncIterator, Union
from pathlib import Path
import asyncio

class CloudStorageInterface(ABC):
    """Abstract interface for cloud storage operations."""
    
    @abstractmethod
    async def upload_file(self, local_path: Union[str, Path], remote_path: str, **kwargs) -> bool:
        """Upload a file to cloud storage."""
        pass
    
    @abstractmethod
    async def download_file(self, remote_path: str, local_path: Union[str, Path], **kwargs) -> bool:
        """Download a file from cloud storage."""
        pass
    
    @abstractmethod
    async def delete_file(self, remote_path: str, **kwargs) -> bool:
        """Delete a file from cloud storage."""
        pass
    
    @abstractmethod
    async def list_files(self, prefix: str = "", **kwargs) -> List[str]:
        """List files in cloud storage."""
        pass
    
    @abstractmethod
    async def file_exists(self, remote_path: str, **kwargs) -> bool:
        """Check if a file exists in cloud storage."""
        pass
    
    @abstractmethod
    async def get_file_metadata(self, remote_path: str, **kwargs) -> Dict[str, Any]:
        """Get metadata for a file."""
        pass
    
    @abstractmethod
    async def generate_signed_url(self, remote_path: str, expiry_hours: int = 1, **kwargs) -> str:
        """Generate a signed URL for temporary access."""
        pass

class CloudDatabaseInterface(ABC):
    """Abstract interface for cloud database operations."""
    
    @abstractmethod
    async def create_document(self, collection: str, document_id: str, data: Dict[str, Any], **kwargs) -> bool:
        """Create a new document."""
        pass
    
    @abstractmethod
    async def get_document(self, collection: str, document_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Get a document by ID."""
        pass
    
    @abstractmethod
    async def update_document(self, collection: str, document_id: str, data: Dict[str, Any], **kwargs) -> bool:
        """Update an existing document."""
        pass
    
    @abstractmethod
    async def delete_document(self, collection: str, document_id: str, **kwargs) -> bool:
        """Delete a document."""
        pass
    
    @abstractmethod
    async def query_documents(self, collection: str, filters: Dict[str, Any], **kwargs) -> List[Dict[str, Any]]:
        """Query documents with filters."""
        pass
    
    @abstractmethod
    async def batch_write(self, operations: List[Dict[str, Any]], **kwargs) -> bool:
        """Perform batch write operations."""
        pass

class CloudMessagingInterface(ABC):
    """Abstract interface for cloud messaging operations."""
    
    @abstractmethod
    async def publish_message(self, topic: str, message: Dict[str, Any], **kwargs) -> str:
        """Publish a message to a topic."""
        pass
    
    @abstractmethod
    async def subscribe_to_topic(self, topic: str, callback, **kwargs) -> str:
        """Subscribe to a topic with a callback function."""
        pass
    
    @abstractmethod
    async def create_topic(self, topic: str, **kwargs) -> bool:
        """Create a new topic."""
        pass
    
    @abstractmethod
    async def delete_topic(self, topic: str, **kwargs) -> bool:
        """Delete a topic."""
        pass
    
    @abstractmethod
    async def list_topics(self, **kwargs) -> List[str]:
        """List all topics."""
        pass

class CloudSecretsInterface(ABC):
    """Abstract interface for cloud secrets management."""
    
    @abstractmethod
    async def get_secret(self, secret_name: str, **kwargs) -> Optional[str]:
        """Get a secret value."""
        pass
    
    @abstractmethod
    async def set_secret(self, secret_name: str, secret_value: str, **kwargs) -> bool:
        """Set a secret value."""
        pass
    
    @abstractmethod
    async def delete_secret(self, secret_name: str, **kwargs) -> bool:
        """Delete a secret."""
        pass
    
    @abstractmethod
    async def list_secrets(self, **kwargs) -> List[str]:
        """List all secrets."""
        pass

class CloudMonitoringInterface(ABC):
    """Abstract interface for cloud monitoring operations."""
    
    @abstractmethod
    async def log_metric(self, metric_name: str, value: float, labels: Dict[str, str] = None, **kwargs) -> bool:
        """Log a custom metric."""
        pass
    
    @abstractmethod
    async def log_event(self, event_name: str, data: Dict[str, Any], severity: str = "INFO", **kwargs) -> bool:
        """Log an event."""
        pass
    
    @abstractmethod
    async def create_alert(self, alert_name: str, condition: Dict[str, Any], **kwargs) -> str:
        """Create a monitoring alert."""
        pass