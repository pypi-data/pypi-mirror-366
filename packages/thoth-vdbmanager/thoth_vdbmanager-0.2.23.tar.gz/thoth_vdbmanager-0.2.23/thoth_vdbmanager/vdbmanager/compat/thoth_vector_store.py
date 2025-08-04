"""Compatibility layer for ThothVectorStore API."""

import warnings
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from haystack.document_stores.types import DuplicatePolicy

from ..core.base import (
    BaseThothDocument,
    ColumnNameDocument,
    HintDocument,
    SqlDocument,
    ThothType,
)
from ..factory import VectorStoreFactory


class ThothVectorStore:
    """Compatibility wrapper maintaining the original ThothVectorStore API."""
    
    def __init__(
        self,
        backend: str = "qdrant",
        collection: str = "thoth_documents",
        **kwargs
    ):
        """Initialize compatibility wrapper.
        
        Args:
            backend: Backend type (qdrant, weaviate, chroma, pgvector, milvus, pinecone)
            collection: Collection name
            **kwargs: Backend-specific parameters
        """
        self._backend = VectorStoreFactory.create(
            backend=backend,
            collection=collection,
            **kwargs
        )
        self._backend_name = backend
        
        # Issue deprecation warning
        warnings.warn(
            "ThothVectorStore is deprecated. Use VectorStoreFactory.create() instead.",
            DeprecationWarning,
            stacklevel=2
        )
    
    def add_column_description(self, doc: ColumnNameDocument) -> str:
        """Add a column description document."""
        return self._backend.add_column_description(doc)
    
    def add_sql(self, doc: SqlDocument) -> str:
        """Add an SQL document."""
        return self._backend.add_sql(doc)
    
    def add_hint(self, doc: HintDocument) -> str:
        """Add a hint document."""
        return self._backend.add_hint(doc)
    
    def _add_document(self, doc: BaseThothDocument) -> str:
        """Add a document (internal method)."""
        if isinstance(doc, ColumnNameDocument):
            return self.add_column_description(doc)
        elif isinstance(doc, SqlDocument):
            return self.add_sql(doc)
        elif isinstance(doc, HintDocument):
            return self.add_hint(doc)
        else:
            raise ValueError(f"Unsupported document type: {type(doc)}")
    
    def _enrich_column_content(self, doc: ColumnNameDocument) -> str:
        """Enrich column content for embedding."""
        return (
            f"{doc.table_name}, {doc.column_name}, {doc.original_column_name}, "
            f"{doc.column_description}, {doc.value_description}"
        )
    
    def _enrich_sql_content(self, doc: SqlDocument) -> str:
        """Enrich SQL content for embedding."""
        return f"{doc.question.lower()} {doc.hint.lower()}"
    
    def search_similar(
        self,
        query: str,
        doc_type: ThothType,
        top_k: int = 5,
        score_threshold: float = 0.7
    ) -> List[BaseThothDocument]:
        """Search for similar documents."""
        return self._backend.search_similar(
            query=query,
            doc_type=doc_type,
            top_k=top_k,
            score_threshold=score_threshold
        )
    
    def get_document(self, doc_id: str) -> Optional[BaseThothDocument]:
        """Get a document by ID."""
        return self._backend.get_document(doc_id)
    
    def get_all_column_documents(self) -> List[ColumnNameDocument]:
        """Get all column documents."""
        return self._backend.get_all_column_documents()
    
    def get_all_sql_documents(self) -> List[SqlDocument]:
        """Get all SQL documents."""
        return self._backend.get_all_sql_documents()
    
    def get_all_hint_documents(self) -> List[HintDocument]:
        """Get all hint documents."""
        return self._backend.get_all_hint_documents()
    
    def get_columns_document_by_id(self, doc_id: str) -> Optional[ColumnNameDocument]:
        """Get a column document by ID."""
        return self._backend.get_columns_document_by_id(doc_id)
    
    def get_sql_document_by_id(self, doc_id: str) -> Optional[SqlDocument]:
        """Get an SQL document by ID."""
        return self._backend.get_sql_document_by_id(doc_id)
    
    def get_hint_document_by_id(self, doc_id: str) -> Optional[HintDocument]:
        """Get a hint document by ID."""
        return self._backend.get_hint_document_by_id(doc_id)
    
    def get_all_documents(self, doc_type: ThothType) -> List[BaseThothDocument]:
        """Get all documents of a specific type."""
        if doc_type == ThothType.COLUMN_NAME:
            return self.get_all_column_documents()
        elif doc_type == ThothType.SQL:
            return self.get_all_sql_documents()
        elif doc_type == ThothType.HINT:
            return self.get_all_hint_documents()
        else:
            return []
    
    def bulk_add_documents(self, documents: List[BaseThothDocument], policy: Optional['DuplicatePolicy'] = None) -> List[str]:
        """Add multiple documents in batch."""
        return self._backend.bulk_add_documents(documents, policy)
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get collection information."""
        info = self._backend.get_collection_info()
        info["backend"] = self._backend_name
        return info
    
    @property
    def backend(self):
        """Access to underlying backend for advanced usage."""
        return self._backend


# Legacy QdrantHaystackStore for backward compatibility
class QdrantHaystackStore(ThothVectorStore):
    """Legacy QdrantHaystackStore for backward compatibility."""
    
    def __init__(
        self,
        collection: str,
        host: str = "localhost",
        port: int = 6333,
        api_key: Optional[str] = None,
        **kwargs
    ):
        """Initialize legacy Qdrant store."""
        super().__init__(
            backend="qdrant",
            collection=collection,
            host=host,
            port=port,
            api_key=api_key,
            **kwargs
        )
        
        warnings.warn(
            "QdrantHaystackStore is deprecated. Use QdrantAdapter instead.",
            DeprecationWarning,
            stacklevel=2
        )
