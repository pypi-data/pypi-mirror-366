"""
Google Cloud Platform implementation of cloud services.
"""
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta

try:
    from google.cloud import storage, firestore, pubsub_v1
    from google.cloud.exceptions import NotFound
    GCP_AVAILABLE = True
except ImportError:
    GCP_AVAILABLE = False

from ..interfaces import CloudStorageInterface, CloudDatabaseInterface, CloudMessagingInterface
from ..cloud_factory import CloudConfig, CloudServiceFactory, CloudProvider

class GCPStorage(CloudStorageInterface):
    """Google Cloud Storage implementation."""
    
    def __init__(self, config: CloudConfig):
        if not GCP_AVAILABLE:
            raise ImportError("GCP dependencies not installed. Install with: pip install mmmlabs-common[gcp]")
        
        self.config = config
        self.client = storage.Client(project=config.config.get('project_id'))
        self.bucket_name = config.config.get('storage_bucket')
        self.bucket = self.client.bucket(self.bucket_name)
    
    async def upload_file(self, local_path: Union[str, Path], remote_path: str, **kwargs) -> bool:
        """Upload a file to GCS."""
        try:
            blob = self.bucket.blob(remote_path)
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, blob.upload_from_filename, str(local_path))
            
            return True
        except Exception as e:
            print(f"Error uploading file: {e}")
            return False
    
    async def download_file(self, remote_path: str, local_path: Union[str, Path], **kwargs) -> bool:
        """Download a file from GCS."""
        try:
            blob = self.bucket.blob(remote_path)
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, blob.download_to_filename, str(local_path))
            
            return True
        except Exception as e:
            print(f"Error downloading file: {e}")
            return False
    
    async def delete_file(self, remote_path: str, **kwargs) -> bool:
        """Delete a file from GCS."""
        try:
            blob = self.bucket.blob(remote_path)
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, blob.delete)
            
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    async def list_files(self, prefix: str = "", **kwargs) -> List[str]:
        """List files in GCS bucket."""
        try:
            loop = asyncio.get_event_loop()
            blobs = await loop.run_in_executor(None, list, self.client.list_blobs(self.bucket_name, prefix=prefix))
            
            return [blob.name for blob in blobs]
        except Exception as e:
            print(f"Error listing files: {e}")
            return []
    
    async def file_exists(self, remote_path: str, **kwargs) -> bool:
        """Check if a file exists in GCS."""
        try:
            blob = self.bucket.blob(remote_path)
            
            loop = asyncio.get_event_loop()
            exists = await loop.run_in_executor(None, blob.exists)
            
            return exists
        except Exception as e:
            print(f"Error checking file existence: {e}")
            return False
    
    async def get_file_metadata(self, remote_path: str, **kwargs) -> Dict[str, Any]:
        """Get metadata for a file."""
        try:
            blob = self.bucket.blob(remote_path)
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, blob.reload)
            
            return {
                'name': blob.name,
                'size': blob.size,
                'created': blob.time_created,
                'updated': blob.updated,
                'content_type': blob.content_type,
                'etag': blob.etag,
            }
        except Exception as e:
            print(f"Error getting file metadata: {e}")
            return {}
    
    async def generate_signed_url(self, remote_path: str, expiry_hours: int = 1, **kwargs) -> str:
        """Generate a signed URL for temporary access."""
        try:
            blob = self.bucket.blob(remote_path)
            
            expiration = datetime.utcnow() + timedelta(hours=expiry_hours)
            
            loop = asyncio.get_event_loop()
            url = await loop.run_in_executor(
                None, 
                blob.generate_signed_url,
                expiration,
                method='GET'
            )
            
            return url
        except Exception as e:
            print(f"Error generating signed URL: {e}")
            return ""

class GCPDatabase(CloudDatabaseInterface):
    """Google Firestore implementation."""
    
    def __init__(self, config: CloudConfig):
        if not GCP_AVAILABLE:
            raise ImportError("GCP dependencies not installed. Install with: pip install mmmlabs-common[gcp]")
        
        self.config = config
        self.client = firestore.Client(
            project=config.config.get('project_id'),
            database=config.config.get('firestore_database', '(default)')
        )
    
    async def create_document(self, collection: str, document_id: str, data: Dict[str, Any], **kwargs) -> bool:
        """Create a new document in Firestore."""
        try:
            doc_ref = self.client.collection(collection).document(document_id)
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, doc_ref.set, data)
            
            return True
        except Exception as e:
            print(f"Error creating document: {e}")
            return False
    
    async def get_document(self, collection: str, document_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Get a document from Firestore."""
        try:
            doc_ref = self.client.collection(collection).document(document_id)
            
            loop = asyncio.get_event_loop()
            doc = await loop.run_in_executor(None, doc_ref.get)
            
            if doc.exists:
                data = doc.to_dict()
                data['_id'] = doc.id
                return data
            
            return None
        except Exception as e:
            print(f"Error getting document: {e}")
            return None
    
    async def update_document(self, collection: str, document_id: str, data: Dict[str, Any], **kwargs) -> bool:
        """Update a document in Firestore."""
        try:
            doc_ref = self.client.collection(collection).document(document_id)
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, doc_ref.update, data)
            
            return True
        except Exception as e:
            print(f"Error updating document: {e}")
            return False
    
    async def delete_document(self, collection: str, document_id: str, **kwargs) -> bool:
        """Delete a document from Firestore."""
        try:
            doc_ref = self.client.collection(collection).document(document_id)
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, doc_ref.delete)
            
            return True
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
    
    async def query_documents(self, collection: str, filters: Dict[str, Any], **kwargs) -> List[Dict[str, Any]]:
        """Query documents from Firestore."""
        try:
            query = self.client.collection(collection)
            
            # Apply filters
            for field, value in filters.items():
                if isinstance(value, dict):
                    # Handle operators like {'>=': 10}
                    for op, val in value.items():
                        query = query.where(field, op, val)
                else:
                    query = query.where(field, '==', value)
            
            loop = asyncio.get_event_loop()
            docs = await loop.run_in_executor(None, list, query.stream())
            
            results = []
            for doc in docs:
                data = doc.to_dict()
                data['_id'] = doc.id
                results.append(data)
            
            return results
        except Exception as e:
            print(f"Error querying documents: {e}")
            return []
    
    async def batch_write(self, operations: List[Dict[str, Any]], **kwargs) -> bool:
        """Perform batch operations in Firestore."""
        try:
            batch = self.client.batch()
            
            for op in operations:
                op_type = op['type']  # 'create', 'update', 'delete'
                collection = op['collection']
                doc_id = op['document_id']
                
                doc_ref = self.client.collection(collection).document(doc_id)
                
                if op_type == 'create':
                    batch.set(doc_ref, op['data'])
                elif op_type == 'update':
                    batch.update(doc_ref, op['data'])
                elif op_type == 'delete':
                    batch.delete(doc_ref)
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, batch.commit)
            
            return True
        except Exception as e:
            print(f"Error in batch write: {e}")
            return False

class GCPMessaging(CloudMessagingInterface):
    """Google Cloud Pub/Sub implementation."""
    
    def __init__(self, config: CloudConfig):
        if not GCP_AVAILABLE:
            raise ImportError("GCP dependencies not installed. Install with: pip install mmmlabs-common[gcp]")
        
        self.config = config
        self.project_id = config.config.get('project_id')
        self.publisher = pubsub_v1.PublisherClient()
        self.subscriber = pubsub_v1.SubscriberClient()
    
    async def publish_message(self, topic: str, message: Dict[str, Any], **kwargs) -> str:
        """Publish a message to Pub/Sub topic."""
        try:
            topic_path = self.publisher.topic_path(self.project_id, topic)
            
            # Convert message to JSON string
            import json
            message_data = json.dumps(message).encode('utf-8')
            
            loop = asyncio.get_event_loop()
            future = await loop.run_in_executor(None, self.publisher.publish, topic_path, message_data)
            
            return future.result()
        except Exception as e:
            print(f"Error publishing message: {e}")
            return ""
    
    async def subscribe_to_topic(self, topic: str, callback, **kwargs) -> str:
        """Subscribe to a Pub/Sub topic."""
        try:
            subscription_name = f"{topic}-subscription"
            subscription_path = self.subscriber.subscription_path(self.project_id, subscription_name)
            
            # This would typically run in a separate process/thread
            # For demonstration purposes, we'll just return the subscription path
            return subscription_path
        except Exception as e:
            print(f"Error subscribing to topic: {e}")
            return ""
    
    async def create_topic(self, topic: str, **kwargs) -> bool:
        """Create a Pub/Sub topic."""
        try:
            topic_path = self.publisher.topic_path(self.project_id, topic)
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.publisher.create_topic, request={"name": topic_path})
            
            return True
        except Exception as e:
            print(f"Error creating topic: {e}")
            return False
    
    async def delete_topic(self, topic: str, **kwargs) -> bool:
        """Delete a Pub/Sub topic."""
        try:
            topic_path = self.publisher.topic_path(self.project_id, topic)
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.publisher.delete_topic, request={"topic": topic_path})
            
            return True
        except Exception as e:
            print(f"Error deleting topic: {e}")
            return False
    
    async def list_topics(self, **kwargs) -> List[str]:
        """List all Pub/Sub topics."""
        try:
            project_path = f"projects/{self.project_id}"
            
            loop = asyncio.get_event_loop()
            topics = await loop.run_in_executor(None, list, self.publisher.list_topics(request={"project": project_path}))
            
            return [topic.name.split('/')[-1] for topic in topics]
        except Exception as e:
            print(f"Error listing topics: {e}")
            return []

# Register GCP implementations
if GCP_AVAILABLE:
    CloudServiceFactory.register_storage(CloudProvider.GCP, GCPStorage)
    CloudServiceFactory.register_database(CloudProvider.GCP, GCPDatabase)
    CloudServiceFactory.register_messaging(CloudProvider.GCP, GCPMessaging)