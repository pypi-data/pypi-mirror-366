"""Weaviate adapter for Thoth Vector Database."""

import logging
import time
from typing import Any, Dict, List, Optional

from haystack import Document as HaystackDocument
from haystack.document_stores.types import DuplicatePolicy
from haystack_integrations.document_stores.weaviate import WeaviateDocumentStore

from ..core.base import BaseThothDocument
from .haystack_adapter import HaystackVectorStoreAdapter

logger = logging.getLogger(__name__)


class WeaviateAdapter(HaystackVectorStoreAdapter):
    """Weaviate implementation using Haystack integration."""
    
    _instances: Dict[str, "WeaviateAdapter"] = {}
    
    def __new__(
        cls,
        collection: str,
        url: str = "http://localhost:8080",
        api_key: Optional[str] = None,
        **kwargs
    ):
        """Singleton pattern for Weaviate adapter."""
        instance_key = f"{collection}:{url}:{api_key}"
        if instance_key in cls._instances:
            return cls._instances[instance_key]
            
        instance = super().__new__(cls)
        cls._instances[instance_key] = instance
        return instance
    
    def __init__(
        self,
        collection: str,
        url: str = "http://localhost:8080",
        api_key: Optional[str] = None,
        timeout: int = 30,
        skip_init_checks: bool = False,
        grpc_port: Optional[int] = None,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        embedding_dim: int = 384,
        **kwargs
    ):
        """Initialize Weaviate adapter.

        Args:
            collection: Collection/class name
            url: Weaviate URL
            api_key: API key for authentication
            timeout: Connection timeout in seconds
            skip_init_checks: Skip gRPC initialization checks
            grpc_port: gRPC port (for health checks)
            embedding_model: Embedding model name
            embedding_dim: Embedding dimension
            **kwargs: Additional Weaviate parameters
        """
        if hasattr(self, '_initialized'):
            return
            
        # Create Weaviate document store with enhanced connection handling
        try:
            # Prepare connection parameters
            connection_params = {
                "url": url,
                "collection_settings": {
                    "class": collection,
                    "vectorizer_config": {
                        "vectorizer": "none"  # We'll handle embeddings
                    },
                    "properties": [
                        # Note: Weaviate handles document IDs internally, no need for explicit id property
                        {"name": "content", "dataType": ["text"]},
                        {"name": "thoth_type", "dataType": ["text"]},
                        {"name": "thoth_id", "dataType": ["text"]},
                        {"name": "table_name", "dataType": ["text"]},
                        {"name": "column_name", "dataType": ["text"]},
                        {"name": "original_column_name", "dataType": ["text"]},
                        {"name": "column_description", "dataType": ["text"]},
                        {"name": "value_description", "dataType": ["text"]},
                        {"name": "question", "dataType": ["text"]},
                        {"name": "sql", "dataType": ["text"]},
                        {"name": "hint", "dataType": ["text"]},
                    ],
                    **kwargs.get("collection_settings", {})
                }
            }

            # Add authentication if provided
            if api_key:
                connection_params["auth_client_secret"] = api_key

            # Note: timeout and skip_init_checks are handled at the adapter level
            # WeaviateDocumentStore doesn't support these parameters directly
            if skip_init_checks:
                logger.info("Weaviate adapter configured to skip initialization checks")

            # Add other parameters
            connection_params.update({
                k: v for k, v in kwargs.items()
                if k not in ["collection_settings", "timeout", "skip_init_checks", "grpc_port"]
            })

            document_store = WeaviateDocumentStore(**connection_params)

        except Exception as e:
            logger.error(f"Failed to create Weaviate document store: {e}")
            raise
        
        super().__init__(
            document_store=document_store,
            collection_name=collection,
            embedding_model=embedding_model,
            embedding_dim=embedding_dim
        )
        
        self._initialized = True
        self.url = url
        self.timeout = timeout
        self.skip_init_checks = skip_init_checks
        self.grpc_port = grpc_port
        logger.info(f"Weaviate adapter initialized for collection: {collection} (URL: {url})")

    def _execute_with_retry(self, operation, *args, **kwargs):
        """Execute an operation with retry logic for connection issues."""
        max_retries = 3
        retry_delay = 1

        for attempt in range(max_retries):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                error_msg = str(e).lower()

                # Check if it's a connection-related error
                if any(keyword in error_msg for keyword in [
                    'connection refused', 'connection error', 'unavailable',
                    'closed client', 'grpc', 'timeout'
                ]):
                    if attempt < max_retries - 1:
                        logger.warning(f"Weaviate connection error (attempt {attempt + 1}/{max_retries}): {e}")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff

                        # Try to reconnect the client
                        try:
                            if hasattr(self.document_store, '_client'):
                                if hasattr(self.document_store._client, 'connect'):
                                    self.document_store._client.connect()
                                elif hasattr(self.document_store._client, 'is_connected') and not self.document_store._client.is_connected():
                                    # Force reconnection by accessing the client property
                                    _ = self.document_store.client
                        except Exception as reconnect_error:
                            logger.debug(f"Reconnection attempt failed: {reconnect_error}")

                        continue

                # If it's not a connection error or we've exhausted retries, re-raise
                raise

        # This should never be reached, but just in case
        raise RuntimeError(f"Operation failed after {max_retries} attempts")

    def _add_document_with_embedding(self, doc: BaseThothDocument) -> str:
        """Add a single document with embedding (Weaviate-specific implementation with retry)."""
        def _add_operation():
            return super(WeaviateAdapter, self)._add_document_with_embedding(doc)

        return self._execute_with_retry(_add_operation)

    def bulk_add_documents(self, documents: List[BaseThothDocument], policy: Optional[DuplicatePolicy] = None) -> List[str]:
        """Add multiple documents in batch (Weaviate-specific implementation with retry)."""
        def _bulk_add_operation():
            return super(WeaviateAdapter, self).bulk_add_documents(documents, policy)

        return self._execute_with_retry(_bulk_add_operation)

    def get_document(self, doc_id: str) -> Optional[BaseThothDocument]:
        """Get a document by ID (Weaviate-specific implementation with retry)."""
        def _get_operation():
            try:
                # Weaviate-specific: Use thoth_id field instead of id field
                filters = {
                    "field": "meta.thoth_id",
                    "operator": "==",
                    "value": doc_id
                }

                documents = self.document_store.filter_documents(filters=filters)
                if documents:
                    return self._convert_from_haystack_document(documents[0])

                # Fallback: try to get by Weaviate's internal ID
                try:
                    documents = self.document_store.filter_documents(filters={"field": "meta.id", "operator": "==", "value": doc_id})
                    if documents:
                        return self._convert_from_haystack_document(documents[0])
                except Exception as e:
                    logger.debug(f"Fallback document retrieval failed: {e}")
                    pass

            except Exception as e:
                logger.error(f"Error getting document {doc_id}: {e}")

            return None

        return self._execute_with_retry(_get_operation)

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document by ID (Weaviate-specific implementation with retry)."""
        def _delete_operation():
            return super(WeaviateAdapter, self).delete_document(doc_id)

        return self._execute_with_retry(_delete_operation)

    def search_similar(self, query: str, doc_type, top_k: int = 5, score_threshold: float = 0.7):
        """Search for similar documents (Weaviate-specific implementation with retry)."""
        def _search_operation():
            return super(WeaviateAdapter, self).search_similar(query, doc_type, top_k, score_threshold)

        return self._execute_with_retry(_search_operation)

    def get_all_documents_by_type(self, doc_type):
        """Get all documents of a specific type (Weaviate-specific implementation with retry)."""
        def _get_all_operation():
            return super(WeaviateAdapter, self).get_all_documents_by_type(doc_type)

        return self._execute_with_retry(_get_all_operation)
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get detailed Weaviate collection information."""
        info = super().get_collection_info()
        info["backend"] = "weaviate"
        
        try:
            # Get Weaviate-specific info
            client = self.document_store._client
            schema = client.collections.get(self.collection_name)
            
            info.update({
                "class_name": schema.name,
                "properties_count": len(schema.config.properties),
                "vector_index_config": {
                    "distance": str(schema.config.vector_index_config.distance),
                    "ef_construction": schema.config.vector_index_config.ef_construction,
                    "max_connections": schema.config.vector_index_config.max_connections,
                }
            })
        except Exception as e:
            logger.error(f"Error getting Weaviate collection info: {e}")
            
        return info
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "WeaviateAdapter":
        """Create Weaviate adapter from configuration."""
        return cls(**config)

    @classmethod
    def clear_all_instances(cls):
        """Clear all singleton instances (useful for testing)."""
        cls._instances.clear()
        logger.debug("Cleared all Weaviate adapter instances")
