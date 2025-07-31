import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar, cast

from haystack import Document as HaystackDocument
from haystack.document_stores.types import DocumentStore, DuplicatePolicy
# Import SentenceTransformersDocumentEmbedder for embedding Documents
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore # Added for get_store_type

from .ThothVectorStore import (
    BaseThothDocument,
    ColumnNameDocument,
    HintDocument,
    SqlDocument,
    ThothType,
    ThothVectorStore,
)

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseThothDocument)


class ThothHaystackVectorStore(ThothVectorStore, ABC):
    """
    An implementation of ThothVectorStore using a Haystack DocumentStore as the backend.

    This class acts as an adapter, mapping ThothVectorStore operations
    to the underlying Haystack DocumentStore methods.
    """

    def __init__(self, store: DocumentStore, collection_name: str):
        """
        Initializes the ThothHaystackVectorStore.

        Args:
            store: An initialized Haystack DocumentStore instance.
            collection_name: The name of the collection/index within the store.
                             Note: Haystack DocumentStores might handle collections differently.
                             This parameter is kept for consistency but its usage depends
                              on the specific underlying store implementation.
        """
        self.store: DocumentStore = store
        self.collection_name = collection_name  # Usage depends on the specific store
        self._document_embedder: Optional[SentenceTransformersDocumentEmbedder] = None

    def _get_document_embedder(self) -> SentenceTransformersDocumentEmbedder:
        if self._document_embedder is None:
            logger.info("Lazily initializing SentenceTransformersDocumentEmbedder...")
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            try:
                self._document_embedder = SentenceTransformersDocumentEmbedder(
                    model=model_name
                )
                self._document_embedder.warm_up()
                logger.info("SentenceTransformersDocumentEmbedder initialized and warmed up.")
            except Exception as e:
                logger.error(f"Failed to initialize or warm up SentenceTransformersDocumentEmbedder: {e}", exc_info=True)
                raise  # Or handle more gracefully if preferred
        if self._document_embedder is None: # Should not happen if raise is used above
            raise RuntimeError("Document embedder could not be initialized.")
        return self._document_embedder

    # --- Haystack DocumentStore Passthrough Methods ---

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the store configuration to a dictionary."""
        return {
            "type": f"{self.__class__.__module__}.{self.__class__.__name__}",
            "init_parameters": {
                "store": self.store.to_dict(),
                "collection_name": self.collection_name,
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ThothHaystackVectorStore":
        """Deserializes the store from a dictionary."""
        init_params = data.get("init_parameters", {})
        store_data = init_params.get("store")
        if not store_data:
            raise ValueError("Missing 'store' data in dictionary for deserialization.")

        store_type_str = store_data.get("type", "haystack.document_stores.types.DocumentStore")
        try:
            module_path, class_name = store_type_str.rsplit(".", 1)
            module = __import__(module_path, fromlist=[class_name])
            store_class = getattr(module, class_name)
        except (ImportError, AttributeError, ValueError) as e:
            logger.warning(f"Could not dynamically load store type '{store_type_str}'. Defaulting to DocumentStore. Error: {e}")
            store_class = DocumentStore

        # Removed issubclass check due to potential Protocol issues
        # if not issubclass(store_class, DocumentStore):
        #     raise TypeError(f"Deserialized store type '{store_type_str}' is not a subclass of DocumentStore.")

        underlying_store = store_class.from_dict(store_data)
        return cls(store=underlying_store,
                   collection_name=init_params.get("collection_name", "documents"))

    def count_documents(self) -> int:
        """Returns the number of documents in the store."""
        return self.store.count_documents()

    async def count_documents_async(self) -> int:
        """Returns the number of documents in the store asynchronously."""
        if hasattr(self.store, "count_documents_async"):
            return await self.store.count_documents_async()
        else:
            logger.warning("Async count_documents not supported by the underlying store, falling back to sync.")
            return self.count_documents()

    def filter_documents(self, filters: Optional[Dict[str, Any]] = None) -> List[HaystackDocument]:
         """Filters documents based on metadata."""
         return self.store.filter_documents(filters=filters)

    async def filter_documents_async(
            self, filters: Optional[Dict[str, Any]] = None
    ) -> List[HaystackDocument]:
        """Filters documents based on metadata asynchronously."""
        if hasattr(self.store, "filter_documents_async"):
            return await self.store.filter_documents_async(filters=filters)
        else:
            logger.warning("Async filter_documents not supported by the underlying store, falling back to sync.")
            return self.filter_documents(filters=filters)

    def write_documents(self, documents: List[HaystackDocument], policy: DuplicatePolicy = DuplicatePolicy.OVERWRITE) -> int:
        """Writes Haystack documents to the store."""
        return self.store.write_documents(documents=documents, policy=policy)

    async def write_documents_async(self, documents: List[HaystackDocument], policy: DuplicatePolicy = DuplicatePolicy.OVERWRITE) -> int:
        """Writes Haystack documents to the store asynchronously."""
        if hasattr(self.store, "write_documents_async"):
            return await self.store.write_documents_async(documents=documents, policy=policy)
        else:
            logger.warning("Async write_documents not supported by the underlying store, falling back to sync.")
            return self.write_documents(documents=documents, policy=policy)

    def delete_documents(self, document_ids: List[str]) -> None:
        """Deletes documents by their IDs."""
        return self.store.delete_documents(document_ids=document_ids)

    async def delete_documents_async(self, document_ids: List[str]) -> None:
        """Deletes documents by their IDs asynchronously."""
        if hasattr(self.store, "delete_documents_async"):
            return await self.store.delete_documents_async(document_ids=document_ids)
        else:
            logger.warning("Async delete_documents not supported by the underlying store, falling back to sync.")
            return self.delete_documents(document_ids=document_ids)

    # --- ThothVectorStore Implementation ---

    def _enrich_content(self, doc: BaseThothDocument) -> str:
        """Generates the text content for embedding based on the document type."""
        if isinstance(doc, ColumnNameDocument):
            return f"Table: {doc.table_name}, Column: {doc.column_name} (Original: {doc.original_column_name}). Description: {doc.column_description}. Value Info: {doc.value_description}"
        elif isinstance(doc, SqlDocument):
            return f"{doc.question.lower()} {doc.hint.lower()}"
        elif isinstance(doc, HintDocument):
            return doc.hint
        else:
            logger.warning(f"Unsupported document type for content enrichment: {type(doc)}")
            return doc.text # Fallback

    def _convert_to_haystack_document(self, doc: BaseThothDocument) -> HaystackDocument:
        """Converts a BaseThothDocument to a HaystackDocument."""
        if not doc.text:
             doc.text = self._enrich_content(doc)

        metadata = {"thoth_type": str(doc.thoth_type), "thoth_id": doc.id}

        if isinstance(doc, ColumnNameDocument):
            metadata.update({
                "table_name": doc.table_name,
                "column_name": doc.column_name,
                "original_column_name": doc.original_column_name,
                "column_description": doc.column_description,
                "value_description": doc.value_description
            })
        elif isinstance(doc, SqlDocument):
            metadata.update({
                "question": doc.question,
                "sql": doc.sql,
                "hint": doc.hint
            })
        elif isinstance(doc, HintDocument):
            metadata.update({
                "hint": doc.hint
            })

        return HaystackDocument(
            id=doc.id,
            content=doc.text,
            meta=metadata,
        )

    def _convert_from_haystack_document(self, h_doc: HaystackDocument) -> Optional[BaseThothDocument]:
        """Converts a HaystackDocument back to a BaseThothDocument."""
        if not h_doc.meta or "thoth_type" not in h_doc.meta:
            logger.warning(f"Haystack document {h_doc.id} missing 'thoth_type' in metadata. Cannot convert.")
            return None

        thoth_type_str = h_doc.meta["thoth_type"]
        try:
            thoth_type = ThothType(thoth_type_str)
        except ValueError:
            logger.warning(f"Invalid ThothType '{thoth_type_str}' in metadata for document {h_doc.id}.")
            return None

        doc_id = h_doc.meta.get("thoth_id", h_doc.id)
        doc_text = h_doc.content

        try:
            if thoth_type == ThothType.COLUMN_NAME:
                return ColumnNameDocument(
                    id=doc_id, text=doc_text,
                    table_name=h_doc.meta.get("table_name", ""),
                    column_name=h_doc.meta.get("column_name", ""),
                    original_column_name=h_doc.meta.get("original_column_name", ""),
                    column_description=h_doc.meta.get("column_description", ""),
                    value_description=h_doc.meta.get("value_description", "")
                )
            elif thoth_type == ThothType.SQL:
                return SqlDocument(
                    id=doc_id, text=doc_text,
                    question=h_doc.meta.get("question", ""),
                    sql=h_doc.meta.get("sql", ""),
                    hint=h_doc.meta.get("hint", "")
                )
            elif thoth_type == ThothType.HINT:
                return HintDocument(
                    id=doc_id, text=doc_text,
                    hint=h_doc.meta.get("hint", h_doc.content)
                )
            else:
                logger.error(f"Unhandled ThothType '{thoth_type}' during conversion from Haystack.")
                return None
        except Exception as e:
            logger.error(f"Error converting Haystack document {h_doc.id} to Thoth type {thoth_type}: {e}", exc_info=True)
            return None

    def _add_document_internal(self, doc: BaseThothDocument, policy: DuplicatePolicy) -> str:
        """Internal helper to add a single document with embedding."""
        embedder = self._get_document_embedder()
        haystack_doc = self._convert_to_haystack_document(doc)

        try:
            # Use keyword argument format documents=...
            result = embedder.run(documents=[haystack_doc])
            embedded_docs = result.get("documents")

            if not embedded_docs:
                 raise ValueError("Embedder did not return documents.")
            if embedded_docs[0].embedding is None:
                 raise ValueError("Embedder failed to generate an embedding for the document.")

            self.write_documents(embedded_docs, policy=policy)
            return embedded_docs[0].id
        except Exception as e:
            logger.error(f"Failed to add document {doc.id} ({doc.thoth_type}): {e}", exc_info=True)
            raise

    def add_document(self, doc: BaseThothDocument) -> str:
        """Adds a single Thoth document to the store, handling embedding."""
        logger.debug(f"Adding document {doc.id} of type {doc.thoth_type}")
        return self._add_document_internal(doc, policy=DuplicatePolicy.OVERWRITE)

    def add_column_description(self, doc: ColumnNameDocument) -> str:
        return self.add_document(doc)

    def add_sql(self, doc: SqlDocument) -> str:
        return self.add_document(doc)

    def add_hint(self, doc: HintDocument) -> str:
        return self.add_document(doc)

    def bulk_add_documents(self, documents: List[BaseThothDocument], policy: DuplicatePolicy = DuplicatePolicy.OVERWRITE) -> List[str]:
        """Adds multiple Thoth documents to the store in a batch, handling embedding."""
        if not documents:
            return []

        embedder = self._get_document_embedder()
        haystack_docs = [self._convert_to_haystack_document(doc) for doc in documents]

        try:
            logger.info(f"Embedding {len(haystack_docs)} documents...")
            # Use keyword argument format documents=...
            result = embedder.run(documents=haystack_docs)
            embedded_docs = result.get("documents")

            if not embedded_docs or len(embedded_docs) != len(haystack_docs):
                 raise ValueError("Embedder did not return the expected number of documents.")

            logger.info(f"Writing {len(embedded_docs)} documents to store...")
            self.write_documents(embedded_docs, policy=policy)
            logger.info("Documents written successfully.")
            return [doc.id for doc in embedded_docs]
        except Exception as e:
            logger.error(f"Failed to bulk add {len(documents)} documents: {e}", exc_info=True)
            raise

    def get_document_by_id(self, doc_id: str, output_type: Type[T] = BaseThothDocument) -> Optional[T]:
        """Retrieves a single document by its ID and optionally casts it."""
        logger.debug(f"Attempting to retrieve document with ID: {doc_id}")
        try:
            filters = {"operator": "OR", "conditions": [
                 {"field": "meta.thoth_id", "operator": "==", "value": doc_id},
                 {"field": "id", "operator": "==", "value": doc_id}
            ]}
            haystack_docs = self.filter_documents(filters=filters)

            if not haystack_docs:
                logger.debug(f"Document with ID {doc_id} not found.")
                return None

            if len(haystack_docs) > 1:
                 logger.warning(f"Multiple documents found for ID {doc_id}. Returning the first one.")

            thoth_doc = self._convert_from_haystack_document(haystack_docs[0])

            if thoth_doc and isinstance(thoth_doc, output_type):
                return thoth_doc
            elif thoth_doc:
                logger.warning(f"Document {doc_id} found, but type mismatch: expected {output_type.__name__}, got {type(thoth_doc).__name__}.")
                return None
            else:
                return None

        except Exception as e:
            logger.error(f"Failed to retrieve document {doc_id}: {e}", exc_info=True)
            return None

    def get_columns_document_by_id(self, doc_id: str) -> Optional[ColumnNameDocument]:
        return self.get_document_by_id(doc_id, output_type=ColumnNameDocument)

    def get_sql_document_by_id(self, doc_id: str) -> Optional[SqlDocument]:
        return self.get_document_by_id(doc_id, output_type=SqlDocument)

    def get_hint_document_by_id(self, doc_id: str) -> Optional[HintDocument]:
        return self.get_document_by_id(doc_id, output_type=HintDocument)

    def get_documents_by_type(self, doc_type: ThothType, output_type: Type[T]) -> List[T]:
        """Retrieves all documents of a specific ThothType, cast to the specified output type."""
        logger.debug(f"Retrieving all documents of type: {str(doc_type)}")
        filters = {"field": "meta.thoth_type", "operator": "==", "value": str(doc_type)}
        try:
            haystack_docs = self.filter_documents(filters=filters)
            thoth_docs: List[T] = []
            for h_doc in haystack_docs:
                converted_doc = self._convert_from_haystack_document(h_doc)
                if converted_doc and isinstance(converted_doc, output_type):
                    thoth_docs.append(converted_doc)
                elif converted_doc:
                     logger.warning(f"Document {h_doc.id} has type {str(doc_type)} but conversion resulted in unexpected type {type(converted_doc).__name__}. Skipping.")

            logger.debug(f"Retrieved {len(thoth_docs)} documents of type {str(doc_type)}")
            return thoth_docs
        except Exception as e:
            logger.error(f"Failed to retrieve documents of type {str(doc_type)}: {e}", exc_info=True)
            return []

    def get_all_column_documents(self) -> List[ColumnNameDocument]:
        return self.get_documents_by_type(ThothType.COLUMN_NAME, ColumnNameDocument)

    def get_all_sql_documents(self) -> List[SqlDocument]:
        return self.get_documents_by_type(ThothType.SQL, SqlDocument)

    def get_all_hint_documents(self) -> List[HintDocument]:
        return self.get_documents_by_type(ThothType.HINT, HintDocument)

    def get_all_documents(self, doc_type: ThothType) -> List[BaseThothDocument]:
         """Deprecated: Use get_documents_by_type for type safety."""
         logger.warning("get_all_documents is deprecated. Use get_documents_by_type instead.")
         type_map = {
             ThothType.COLUMN_NAME: ColumnNameDocument,
             ThothType.SQL: SqlDocument,
             ThothType.HINT: HintDocument,
         }
         target_type = type_map.get(doc_type, BaseThothDocument)
         return cast(List[BaseThothDocument], self.get_documents_by_type(doc_type, target_type))

    def update_document(self, doc: BaseThothDocument) -> None:
        """Updates an existing document in the store."""
        logger.debug(f"Updating document {doc.id} of type {doc.thoth_type}")
        try:
            self._add_document_internal(doc, policy=DuplicatePolicy.OVERWRITE)
            logger.info(f"Document {doc.id} updated successfully.")
        except Exception as e:
             logger.error(f"Failed to update document {doc.id}: {e}", exc_info=True)
             raise

    def delete_document(self, doc_id: str) -> None:
        """Deletes a single document by its ID."""
        logger.debug(f"Deleting document with ID: {doc_id}")
        try:
            self.delete_documents(document_ids=[doc_id])
            logger.info(f"Document {doc_id} deleted successfully.")
        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}: {e}", exc_info=True)
            # raise

    def delete_collection(self, thoth_type: Optional[ThothType] = None) -> None:
        """Deletes documents from the store, optionally filtered by ThothType."""
        if thoth_type:
            logger.info(f"Deleting all documents of type: {str(thoth_type)}")
            docs_to_delete = self.get_documents_by_type(thoth_type, BaseThothDocument)
            if not docs_to_delete:
                logger.info(f"No documents of type {str(thoth_type)} found to delete.")
                return
            doc_ids = [doc.id for doc in docs_to_delete]
            logger.debug(f"Found {len(doc_ids)} documents of type {str(thoth_type)} to delete.")
        else:
            logger.warning("Deleting ALL documents in the collection.") # Message change was correct
            try:
                # Fetch all document IDs first, then delete by ID
                # This avoids potentially problematic filters like '!= None'
                all_docs_haystack = self.filter_documents(filters=None) # Get all docs - This line was correct
                if not all_docs_haystack:
                     logger.info("No documents found in the collection to delete.") # This line was correct
                     return # This line was correct
                # Ensure using the correct variable name from the line above
                doc_ids = [h_doc.id for h_doc in all_docs_haystack] # Corrected variable name
                logger.debug(f"Found {len(doc_ids)} documents to delete.") # Corrected log message

            except Exception as e:
                 logger.error(f"Failed to retrieve all Thoth document IDs for deletion: {e}. Aborting delete_collection(None).", exc_info=True)
                 return

        if not doc_ids:
             logger.info("No document IDs identified for deletion.")
             return

        try:
            logger.info(f"Deleting {len(doc_ids)} documents...")
            self.delete_documents(document_ids=doc_ids)
            logger.info(f"Successfully deleted {len(doc_ids)} documents.")
        except Exception as e:
            logger.error(f"Failed during bulk deletion of {len(doc_ids)} documents: {e}", exc_info=True)

    @abstractmethod
    def search_similar(self, query: str, doc_type: ThothType, top_k: int = 5, score_threshold: float = 0.7) -> List[BaseThothDocument]:
        """Searches for documents similar to a given query, filtered by type."""
        pass

    def get_store_type(self) -> str:
        """
        Identifies the type of the underlying Haystack DocumentStore.

        Returns:
            A string representing the type of the store (e.g., "Qdrant").
        """
        if isinstance(self.store, QdrantDocumentStore):
            return "Qdrant"
        # Future implementations for other vector databases can be added here:
        # elif isinstance(self.store, ChromaDocumentStore):  # Replace with actual Chroma class
        #     return "Chroma"
        # elif isinstance(self.store, PineconeDocumentStore): # Replace with actual Pinecone class
        #     return "Pinecone"
        # elif isinstance(self.store, WeaviateDocumentStore): # Replace with actual Weaviate class
        #     return "Weaviate"
        else:
            # Fallback to the class name if no specific type is matched
            return self.store.__class__.__name__
