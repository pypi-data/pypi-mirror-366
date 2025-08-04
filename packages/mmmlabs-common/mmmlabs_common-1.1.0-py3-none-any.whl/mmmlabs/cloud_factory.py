"""
Cloud provider factory for creating cloud-specific implementations.
"""
import os
from enum import Enum
from typing import Optional, Dict, Any, Type
from abc import ABC, abstractmethod

class CloudProvider(Enum):
    GCP = "gcp"
    AZURE = "azure"
    AWS = "aws"

class CloudConfig:
    """Base configuration for cloud providers."""
    
    def __init__(self, provider: CloudProvider, **kwargs):
        self.provider = provider
        self.config = kwargs
    
    @classmethod
    def from_env(cls, provider: Optional[CloudProvider] = None) -> 'CloudConfig':
        """Create config from environment variables."""
        if provider is None:
            provider_str = os.getenv('CLOUD_PROVIDER', 'gcp').lower()
            provider = CloudProvider(provider_str)
        
        config = {}
        
        if provider == CloudProvider.GCP:
            config.update({
                'project_id': os.getenv('GCP_PROJECT_ID'),
                'storage_bucket': os.getenv('GCP_STORAGE_BUCKET'),
                'pubsub_topic': os.getenv('GCP_PUBSUB_TOPIC'),
                'firestore_database': os.getenv('GCP_FIRESTORE_DATABASE', '(default)'),
                'region': os.getenv('GCP_REGION', 'us-central1'),
            })
        
        elif provider == CloudProvider.AZURE:
            config.update({
                'subscription_id': os.getenv('AZURE_SUBSCRIPTION_ID'),
                'resource_group': os.getenv('AZURE_RESOURCE_GROUP'),
                'storage_account': os.getenv('AZURE_STORAGE_ACCOUNT'),
                'servicebus_namespace': os.getenv('AZURE_SERVICEBUS_NAMESPACE'),
                'cosmos_db_account': os.getenv('AZURE_COSMOS_DB_ACCOUNT'),
                'region': os.getenv('AZURE_REGION', 'eastus'),
            })
        
        elif provider == CloudProvider.AWS:
            config.update({
                'region': os.getenv('AWS_REGION', 'us-east-1'),
                's3_bucket': os.getenv('AWS_S3_BUCKET'),
                'sqs_queue': os.getenv('AWS_SQS_QUEUE'),
                'dynamodb_table': os.getenv('AWS_DYNAMODB_TABLE'),
            })
        
        return cls(provider, **config)

class CloudServiceFactory:
    """Factory for creating cloud-specific service implementations."""
    
    _storage_classes: Dict[CloudProvider, Type] = {}
    _database_classes: Dict[CloudProvider, Type] = {}
    _messaging_classes: Dict[CloudProvider, Type] = {}
    
    @classmethod
    def register_storage(cls, provider: CloudProvider, storage_class: Type):
        """Register a storage implementation for a provider."""
        cls._storage_classes[provider] = storage_class
    
    @classmethod
    def register_database(cls, provider: CloudProvider, database_class: Type):
        """Register a database implementation for a provider."""
        cls._database_classes[provider] = database_class
    
    @classmethod
    def register_messaging(cls, provider: CloudProvider, messaging_class: Type):
        """Register a messaging implementation for a provider."""
        cls._messaging_classes[provider] = messaging_class
    
    @classmethod
    def create_storage(cls, config: CloudConfig):
        """Create a storage service instance."""
        if config.provider not in cls._storage_classes:
            raise ValueError(f"Storage not supported for provider: {config.provider}")
        
        storage_class = cls._storage_classes[config.provider]
        return storage_class(config)
    
    @classmethod
    def create_database(cls, config: CloudConfig):
        """Create a database service instance."""
        if config.provider not in cls._database_classes:
            raise ValueError(f"Database not supported for provider: {config.provider}")
        
        database_class = cls._database_classes[config.provider]
        return database_class(config)
    
    @classmethod
    def create_messaging(cls, config: CloudConfig):
        """Create a messaging service instance."""
        if config.provider not in cls._messaging_classes:
            raise ValueError(f"Messaging not supported for provider: {config.provider}")
        
        messaging_class = cls._messaging_classes[config.provider]
        return messaging_class(config)

# Convenience function for easy setup
def setup_cloud_services(provider: Optional[CloudProvider] = None) -> Dict[str, Any]:
    """Setup all cloud services for the specified provider."""
    config = CloudConfig.from_env(provider)
    
    services = {}
    
    try:
        services['storage'] = CloudServiceFactory.create_storage(config)
    except (ValueError, ImportError) as e:
        print(f"Storage service not available: {e}")
    
    try:
        services['database'] = CloudServiceFactory.create_database(config)
    except (ValueError, ImportError) as e:
        print(f"Database service not available: {e}")
    
    try:
        services['messaging'] = CloudServiceFactory.create_messaging(config)
    except (ValueError, ImportError) as e:
        print(f"Messaging service not available: {e}")
    
    return services