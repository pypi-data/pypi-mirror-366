"""
MMMLabs Common - Cloud-agnostic utilities for MMMLabs services.
"""

__version__ = "1.1.0"

# Core exports
from .cloud_factory import CloudConfig, CloudServiceFactory, CloudProvider, setup_cloud_services
from .interfaces import (
    CloudStorageInterface,
    CloudDatabaseInterface, 
    CloudMessagingInterface,
    CloudSecretsInterface,
    CloudMonitoringInterface,
)

# Utility exports
from .utils import *
from .config import get_config

# Try to import and register available cloud providers
_registered_providers = []

# GCP Provider
try:
    from .providers.gcp_provider import GCPStorage, GCPDatabase, GCPMessaging
    _registered_providers.append("gcp")
except ImportError:
    pass

# Azure Provider
try:
    from .providers.azure_provider import AzureStorage, AzureDatabase, AzureMessaging
    _registered_providers.append("azure")
except ImportError:
    pass

# AWS Provider
try:
    from .providers.aws_provider import AWSStorage, AWSDatabase, AWSMessaging
    _registered_providers.append("aws")
except ImportError:
    pass

def get_available_providers():
    """Get list of available cloud providers."""
    return _registered_providers.copy()

def create_cloud_client(provider: str = None, **config_kwargs):
    """
    Convenience function to create a cloud client with all services.
    
    Args:
        provider: Cloud provider ('gcp', 'azure', 'aws'). If None, uses environment.
        **config_kwargs: Additional configuration parameters.
    
    Returns:
        Dictionary with available cloud services.
    
    Example:
        # Using environment variables
        client = create_cloud_client()
        
        # Explicit provider with config
        client = create_cloud_client(
            provider='gcp',
            project_id='my-project',
            storage_bucket='my-bucket'
        )
        
        # Access services
        await client['storage'].upload_file('local.txt', 'remote.txt')
        doc = await client['database'].get_document('users', 'user123')
    """
    if provider:
        provider_enum = CloudProvider(provider.lower())
        config = CloudConfig(provider_enum, **config_kwargs)
    else:
        config = CloudConfig.from_env()
    
    return setup_cloud_services(config.provider)

# Backward compatibility exports
from .database import *
from .messaging import *  
from .storage import *

__all__ = [
    # Core classes
    'CloudConfig',
    'CloudServiceFactory', 
    'CloudProvider',
    'setup_cloud_services',
    'create_cloud_client',
    
    # Interfaces
    'CloudStorageInterface',
    'CloudDatabaseInterface',
    'CloudMessagingInterface', 
    'CloudSecretsInterface',
    'CloudMonitoringInterface',
    
    # Utilities
    'get_available_providers',
    'get_config',
]