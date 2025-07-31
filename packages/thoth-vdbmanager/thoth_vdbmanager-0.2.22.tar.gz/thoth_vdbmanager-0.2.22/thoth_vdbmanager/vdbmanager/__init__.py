"""Thoth Vector Database Manager - Haystack-based implementation."""

from .core.base import (
    BaseThothDocument,
    ColumnNameDocument,
    HintDocument,
    SqlDocument,
    DocumentationDocument,
    ThothType,
    VectorStoreInterface,
)
from .factory import VectorStoreFactory
from .compat.thoth_vector_store import ThothVectorStore, QdrantHaystackStore

# Adapters are loaded dynamically by VectorStoreFactory to handle missing dependencies

__version__ = "2.0.0"
__all__ = [
    # Core classes
    "BaseThothDocument",
    "ColumnNameDocument",
    "HintDocument",
    "SqlDocument",
    "DocumentationDocument",
    "ThothType",
    "VectorStoreInterface",
    
    # Factory
    "VectorStoreFactory",
    
    # Compatibility
    "ThothVectorStore",
    "QdrantHaystackStore",
]

# Backward compatibility aliases
ThothHaystackVectorStore = ThothVectorStore
