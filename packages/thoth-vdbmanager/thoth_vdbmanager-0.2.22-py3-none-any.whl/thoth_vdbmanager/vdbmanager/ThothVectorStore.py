from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, cast, TYPE_CHECKING
from uuid import uuid4

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from haystack.document_stores.types import DuplicatePolicy


class ThothType(Enum):
    """Tipi di documenti supportati da Thoth"""
    COLUMN_NAME = "column_name"
    HINT = "hint"
    SQL = "sql"

class BaseThothDocument(BaseModel):
    """Classe base per tutti i documenti Thoth"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    thoth_type: ThothType
    text: str = ""

class ColumnNameDocument(BaseThothDocument):
    """Documento per la descrizione di una colonna"""
    table_name: str
    column_name: str
    original_column_name: str
    column_description: str
    value_description: str
    thoth_type: ThothType = ThothType.COLUMN_NAME

class SqlDocument(BaseThothDocument):
    """Documento per esempi SQL"""
    question: str
    sql: str
    hint: str = ""
    thoth_type: ThothType = ThothType.SQL

class HintDocument(BaseThothDocument):
    """Documento per suggerimenti"""
    hint: str
    thoth_type: ThothType = ThothType.HINT

class ThothVectorStore(ABC):
    @abstractmethod
    def add_column_description(self, doc: ColumnNameDocument) -> str:
        pass

    @abstractmethod
    def add_sql(self, doc: SqlDocument) -> str:
        pass

    @abstractmethod
    def add_hint(self, doc: HintDocument) -> str:
        pass

    @abstractmethod
    def _add_document(self, doc: BaseThothDocument) -> str:
        pass

    def _enrich_column_content(self, doc: ColumnNameDocument) -> str:
        return f"{doc.table_name}, {doc.column_name}, {doc.original_column_name}, {doc.column_description}, {doc.value_description}"

    def _enrich_sql_content(self, doc: SqlDocument) -> str:
        return f"{doc.question.lower()} {doc.hint.lower()}"

    @abstractmethod
    def search_similar(self,
                       query: str,
                       doc_type: ThothType,
                       top_k: int = 5,
                       score_threshold: float = 0.7) -> List[BaseThothDocument]:
        pass

    @abstractmethod
    def get_document(self, doc_id: str) -> Optional[BaseThothDocument]:
        pass

    def get_all_column_documents(self) -> List[ColumnNameDocument]:
        return cast(List[ColumnNameDocument], self.get_all_documents(ThothType.COLUMN_NAME))

    def get_all_sql_documents(self) -> List[SqlDocument]:
        return cast(List[SqlDocument], self.get_all_documents(ThothType.SQL))

    def get_all_hint_documents(self) -> List[HintDocument]:
        return cast(List[HintDocument], self.get_all_documents(ThothType.HINT))

    def get_columns_document_by_id(self, doc_id: str) -> Optional[ColumnNameDocument]:
        doc = self.get_document(doc_id)
        if isinstance(doc, ColumnNameDocument):
            return doc
        return None

    def get_sql_document_by_id(self, doc_id: str) -> Optional[SqlDocument]:
        doc = self.get_document(doc_id)
        if isinstance(doc, SqlDocument):
            return doc
        return None

    def get_hint_document_by_id(self, doc_id: str) -> Optional[HintDocument]:
        """
        Recupera un documento hint specifico per ID.

        Args:
            doc_id: ID del documento

        Returns:
            Optional[HintDocument]: Documento trovato o None
        """
        doc = self.get_document(doc_id)
        if isinstance(doc, HintDocument):
            return doc
        return None

    def get_all_documents(self, doc_type: ThothType) -> List[BaseThothDocument]:
        """
        Recupera tutti i documenti di un tipo specifico.

        Args:
            doc_type: Tipo di documenti da recuperare

        Returns:
            List[BaseThothDocument]: Lista di tutti i documenti del tipo specificato
        """
        if doc_type == ThothType.COLUMN_NAME:
            return self.get_all_column_documents()
        elif doc_type == ThothType.SQL:
            return self.get_all_sql_documents()
        elif doc_type == ThothType.HINT:
            return self.get_all_hint_documents()
        else:
            return []

    def bulk_add_documents(self, documents: List[BaseThothDocument], policy: Optional['DuplicatePolicy'] = None) -> List[str]:
        """
        Aggiunge più documenti in batch.

        Args:
            documents: Lista di documenti da aggiungere
            policy: Policy for handling duplicate documents (ignored in base implementation)

        Returns:
            List[str]: Lista degli ID dei documenti creati
        """
        return [self._add_document(doc) for doc in documents]

    @abstractmethod
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Recupera le informazioni sulla collezione.

        Returns:
            Dict[str, Any]: Informazioni sulla collezione
        """
        pass
