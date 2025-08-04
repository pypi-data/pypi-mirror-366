"""Base classes and interfaces for Thoth Vector Database."""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, TypeVar, Generic, TYPE_CHECKING
from uuid import uuid4

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from haystack.document_stores.types import DuplicatePolicy

T = TypeVar('T', bound='BaseThothDocument')


class ThothType(Enum):
    """Supported document types in Thoth."""
    COLUMN_NAME = "column_name"
    HINT = "hint"
    SQL = "sql"
    DOCUMENTATION = "documentation"


class BaseThothDocument(BaseModel):
    """Base class for all Thoth documents."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    thoth_type: ThothType
    text: str = ""

    class Config:
        """Pydantic configuration."""
        use_enum_values = True


class ColumnNameDocument(BaseThothDocument):
    """Document for column descriptions."""
    table_name: str
    column_name: str
    original_column_name: str
    column_description: str
    value_description: str
    thoth_type: ThothType = ThothType.COLUMN_NAME


class SqlDocument(BaseThothDocument):
    """Document for SQL examples."""
    question: str
    sql: str
    hint: str = ""
    thoth_type: ThothType = ThothType.SQL


class HintDocument(BaseThothDocument):
    """Document for hints."""
    hint: str
    thoth_type: ThothType = ThothType.HINT


class DocumentationDocument(BaseThothDocument):
    """Document for documentation."""
    content: str
    thoth_type: ThothType = ThothType.DOCUMENTATION


class VectorStoreInterface(ABC, Generic[T]):
    """Interface for vector store implementations."""
    
    @abstractmethod
    def add_column_description(self, doc: ColumnNameDocument) -> str:
        """Add a column description document."""
        pass

    @abstractmethod
    def add_sql(self, doc: SqlDocument) -> str:
        """Add an SQL document."""
        pass

    @abstractmethod
    def add_hint(self, doc: HintDocument) -> str:
        """Add a hint document."""
        pass


    @abstractmethod
    def search_similar(
        self,
        query: str,
        doc_type: ThothType,
        top_k: int = 5,
        score_threshold: float = 0.7
    ) -> List[BaseThothDocument]:
        """Search for similar documents."""
        pass

    @abstractmethod
    def get_document(self, doc_id: str) -> Optional[BaseThothDocument]:
        """Get a document by ID."""
        pass

    @abstractmethod
    def delete_document(self, doc_id: str) -> None:
        """Delete a document by ID."""
        pass

    @abstractmethod
    def get_collection_info(self) -> Dict[str, Any]:
        """Get collection information."""
        pass

    @abstractmethod
    def bulk_add_documents(self, documents: List[BaseThothDocument], policy: Optional['DuplicatePolicy'] = None) -> List[str]:
        """Add multiple documents in batch."""
        pass

    @abstractmethod
    def delete_collection(self, thoth_type: ThothType) -> None:
        """Delete all documents of a specific type."""
        pass

    def get_all_column_documents(self) -> List[ColumnNameDocument]:
        """Get all column documents."""
        return [
            doc for doc in self._get_all_documents()
            if isinstance(doc, ColumnNameDocument)
        ]

    def get_all_sql_documents(self) -> List[SqlDocument]:
        """Get all SQL documents."""
        return [
            doc for doc in self._get_all_documents()
            if isinstance(doc, SqlDocument)
        ]

    def get_all_hint_documents(self) -> List[HintDocument]:
        """Get all hint documents."""
        return [
            doc for doc in self._get_all_documents()
            if isinstance(doc, HintDocument)
        ]

    def get_all_documentation_documents(self) -> List[DocumentationDocument]:
        """Get all documentation documents."""
        return [
            doc for doc in self._get_all_documents()
            if isinstance(doc, DocumentationDocument)
        ]

    def get_columns_document_by_id(self, doc_id: str) -> Optional[ColumnNameDocument]:
        """Get a column document by ID."""
        doc = self.get_document(doc_id)
        return doc if isinstance(doc, ColumnNameDocument) else None

    def get_sql_document_by_id(self, doc_id: str) -> Optional[SqlDocument]:
        """Get an SQL document by ID."""
        doc = self.get_document(doc_id)
        return doc if isinstance(doc, SqlDocument) else None

    def get_hint_document_by_id(self, doc_id: str) -> Optional[HintDocument]:
        """Get a hint document by ID."""
        doc = self.get_document(doc_id)
        return doc if isinstance(doc, HintDocument) else None

    def get_documentation_document_by_id(self, doc_id: str) -> Optional[DocumentationDocument]:
        """Get a documentation document by ID."""
        doc = self.get_document(doc_id)
        return doc if isinstance(doc, DocumentationDocument) else None

    @abstractmethod
    def _get_all_documents(self) -> List[BaseThothDocument]:
        """Get all documents (internal method)."""
        pass
