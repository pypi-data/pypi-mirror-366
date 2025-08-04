import logging
from typing import Any, Dict, List, Optional

from haystack import Pipeline
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack_integrations.components.retrievers.qdrant import QdrantEmbeddingRetriever
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore
from haystack.document_stores.types import DuplicatePolicy
from qdrant_client import QdrantClient

from ..ThothHaystackVectorStore import ThothHaystackVectorStore
from ..ThothVectorStore import (
     BaseThothDocument,
     ThothType,
)

logger = logging.getLogger(__name__) # Added logger initialization

class QdrantHaystackStore(ThothHaystackVectorStore):
    _instances: Dict[tuple, "QdrantHaystackStore"] = {}

    def __new__(cls,
                collection: str,
                host: str = "localhost",
                port: int = 6333,
                api_key: Optional[str] = None):
        instance_key = (collection, host, port, api_key)
        if instance_key in cls._instances:
            return cls._instances[instance_key]
        
        instance = super().__new__(cls)
        cls._instances[instance_key] = instance
        return instance

    def __init__(self,
                 collection: str,
                 host: str = "localhost",
                 port: int = 6333,
                 api_key: Optional[str] = None):
        logging.info(f"Initializing QdrantHaystackStore with host: {host}, port: {port}, collection: {collection}")
        if hasattr(self, '_initialized') and self._initialized:
            return

        # Store connection details for later use
        self._host = host
        self._port = port
        self._api_key = api_key

        store = QdrantDocumentStore(
            index=collection,
            host=host,
            port=port,
            api_key=api_key,
            embedding_dim=384,
            hnsw_config={
                "m": 16,
                "ef_construct": 100
            }
        )
        super().__init__(store=store, collection_name=collection)

        # Initialize components for the search pipeline
        logger.info("Initializing search pipeline components for QdrantHaystackStore...")
        self._search_text_embedder = SentenceTransformersTextEmbedder(
            model="sentence-transformers/all-MiniLM-L6-v2"
        )
        logger.info("Warming up search text embedder...")
        self._search_text_embedder.warm_up()
        
        self._search_retriever = QdrantEmbeddingRetriever(
            document_store=self.store, # Use the initialized QdrantDocumentStore
            scale_score=True
            # filters and top_k will be provided at runtime
        )
        
        self.search_pipeline = Pipeline()
        self.search_pipeline.add_component("embedder", self._search_text_embedder)
        self.search_pipeline.add_component("retriever", self._search_retriever)
        self.search_pipeline.connect("embedder.embedding", "retriever.query_embedding")
        logger.info("Search pipeline initialized and connected for QdrantHaystackStore.")
        
        self._initialized = True

    # Removed _get_text_embedder method as it's replaced by components in __init__

    def get_collection_info(self, doc_type: ThothType) -> Dict[str, Any]:
        try:
            # Create direct client connection using stored connection details
            client = QdrantClient(host=self._host, port=self._port, api_key=self._api_key)
            collection_info = client.get_collection(self.collection_name)
            points_count = collection_info.points_count
            vectors_config = collection_info.config.params.vectors

            return {
                "doc_type": doc_type.value,
                "collection_name": self.collection_name,
                "total_docs": points_count,
                "embedding_dim": vectors_config.size
            }
        except Exception as e:
            logger.error(f"Collection info retrieval failed: {e}")
            return {
                "doc_type": doc_type.value,
                "collection_name": self.collection_name,
                "total_docs": 0,
                "embedding_dim": 384
            }

    def search_similar(self,
                       query: str,
                       doc_type: ThothType,
                       top_k: int = 5,
                       score_threshold: float = 0.7) -> List[BaseThothDocument]:
        if not query:
            return []

        try:
            filters = { # Define filters for the search
                "field": "meta.thoth_type",
                "operator": "==",
                "value": doc_type.value
            }

            # Run the pre-initialized pipeline
            pipeline_input = {
                "embedder": {"text": query},
                "retriever": {"filters": filters, "top_k": top_k}
            }

            results = self.search_pipeline.run(pipeline_input)

            thoth_docs = []
            if "retriever" in results and "documents" in results["retriever"]:
                for doc in results["retriever"]["documents"]:
                    # Ensure score exists and is a float before comparison
                    current_score = getattr(doc, 'score', 0.0)
                    if current_score is None: # Handle None score explicitly
                        current_score = 0.0

                    thoth_doc = self._convert_from_haystack_document(doc)
                    if thoth_doc and current_score >= score_threshold:
                        # CRITICAL FIX: Validate that the returned document type matches the requested type
                        if thoth_doc.thoth_type == doc_type:
                            thoth_docs.append(thoth_doc)
                        else:
                            logger.error(f"CRITICAL: Document type mismatch! Requested {doc_type.value}, got {thoth_doc.thoth_type.value} for document {thoth_doc.id}")
                            logger.error("This indicates a serious issue with the vector database filtering mechanism.")
            else:
                logger.warning("Retriever results missing or not in expected format.")

            logger.debug(f"Search for {doc_type.value} returned {len(thoth_docs)} documents after filtering")
            return thoth_docs

        except Exception as e:
            logger.error(f"Similarity search failed: {e}", exc_info=True) # Added exc_info for more details
            return []

    # --- Implementation of abstract methods from ThothVectorStore ---

    def _add_document(self, doc: BaseThothDocument) -> str:
        return super()._add_document_internal(doc, policy=DuplicatePolicy.OVERWRITE)

    def get_document(self, doc_id: str) -> Optional[BaseThothDocument]:
        return super().get_document_by_id(doc_id=doc_id, output_type=BaseThothDocument)

