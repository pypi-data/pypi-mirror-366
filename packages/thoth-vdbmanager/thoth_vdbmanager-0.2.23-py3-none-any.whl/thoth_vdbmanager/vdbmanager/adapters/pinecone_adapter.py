"""Pinecone adapter for Thoth Vector Database."""

import logging
from typing import Any, Dict

from haystack_integrations.document_stores.pinecone import PineconeDocumentStore

from .haystack_adapter import HaystackVectorStoreAdapter

logger = logging.getLogger(__name__)


class PineconeAdapter(HaystackVectorStoreAdapter):
    """Pinecone implementation using Haystack integration."""
    
    _instances: Dict[str, "PineconeAdapter"] = {}
    
    def __new__(
        cls,
        collection: str,
        api_key: str,
        environment: str = "us-west1-gcp-free",
        **kwargs
    ):
        """Singleton pattern for Pinecone adapter."""
        instance_key = f"{collection}:{api_key}:{environment}"
        if instance_key in cls._instances:
            return cls._instances[instance_key]
            
        instance = super().__new__(cls)
        cls._instances[instance_key] = instance
        return instance
    
    def __init__(
        self,
        collection: str,
        api_key: str,
        environment: str = "us-west1-gcp-free",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        embedding_dim: int = 384,
        **kwargs
    ):
        """Initialize Pinecone adapter.
        
        Args:
            collection: Index name
            api_key: Pinecone API key
            environment: Pinecone environment
            embedding_model: Embedding model name
            embedding_dim: Embedding dimension
            **kwargs: Additional Pinecone parameters
        """
        if hasattr(self, '_initialized'):
            return
            
        # Create Pinecone document store
        document_store = PineconeDocumentStore(
            api_key=api_key,
            index=collection,
            dimension=embedding_dim,
            namespace=collection,
            **{k: v for k, v in kwargs.items() if k not in ["index", "dimension", "namespace", "environment"]}
        )
        
        super().__init__(
            document_store=document_store,
            collection_name=collection,
            embedding_model=embedding_model,
            embedding_dim=embedding_dim
        )
        
        self._initialized = True
        self.api_key = api_key
        self.environment = environment
        logger.info(f"Pinecone adapter initialized for index: {collection}")
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get detailed Pinecone collection information."""
        info = super().get_collection_info()
        info["backend"] = "pinecone"
        
        try:
            # Get Pinecone-specific info
            import pinecone
            
            pc = pinecone.Pinecone(api_key=self.api_key, environment=self.environment)
            index = pc.Index(self.collection_name)
            
            # Get index stats
            stats = index.describe_index_stats()
            
            info.update({
                "api_key": "****" + self.api_key[-4:] if self.api_key else None,
                "environment": self.environment,
                "index_name": self.collection_name,
                "total_vector_count": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness,
                "namespaces": list(stats.namespaces.keys()) if stats.namespaces else [],
            })
            
        except Exception as e:
            logger.error(f"Error getting Pinecone collection info: {e}")
            
        return info
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "PineconeAdapter":
        """Create Pinecone adapter from configuration."""
        return cls(**config)
