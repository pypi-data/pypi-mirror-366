"""
ChromaDB ingestion system for chatbot knowledge base

Handles document storage and retrieval with vector embeddings

ChromaDBIngester now requires async instantiation:
    ingester = await ChromaDBIngester.ainit(...)
"""

import chromadb
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import logging
from .config import Config
from .utils import prepare_metadata, KEYWORD_EXTRACTORS, create_document_id
import asyncio

logger = logging.getLogger(__name__)


class ChromaDBAdapter:
    """ChromaDB adapter for chatbot knowledge base"""

    def __init__(self):
        self.client = None
        self.collection = None
        # Initialization is now fully async, so __init__ does nothing.

    async def ainit(self):
        """Asynchronous factory to create and initialize an instance."""
        # Corrected: this should be an instance method that calls the classmethod
        instance = self
        await instance._initialize_client()
        return instance

    # async def _initialize_client(self):
    #     """Initializes the ChromaDB async client and collection."""
    #     try:
    #         self.client = await chromadb.AsyncHttpClient(
    #             host=Config.CHROMA_HOST,
    #             port=Config.CHROMA_PORT,
    #             tenant=Config.CHROMA_TENANT,
    #             database=Config.CHROMA_DATABASE,
    #         )
    #         logger.info(
    #             f"✅ ChromaDB async client initialized for tenant '{Config.CHROMA_TENANT}' and database '{Config.CHROMA_DATABASE}'"
    #         )

    #         # Let's not delete the collection by default, only if needed for a clean slate.
    #         # This avoids data loss on every restart.
    #         collections = await self.client.list_collections()
    #         if Config.COLLECTION not in [c.name for c in collections]:
    #             logger.info(f"Creating new ChromaDB collection '{Config.COLLECTION}'")
    #             self.collection = await self.client.create_collection(
    #                 name=Config.COLLECTION
    #             )
    #             logger.info(f"✅ ChromaDB collection '{Config.COLLECTION}' created.")
    #         else:
    #             logger.info(
    #                 f"✅ ChromaDB collection '{Config.COLLECTION}' already exists."
    #             )
    #             self.collection = await self.client.get_collection(
    #                 name=Config.COLLECTION
    #             )

    #     except Exception as e:
    #         logger.error(f"❌ Failed to initialize ChromaDB collection: {e}")
    #         raise

    async def _initialize_client(self):
        """Initializes the ChromaDB async client and collection with proper configuration."""
        try:
            self.client = await chromadb.AsyncHttpClient(
                host=Config.CHROMA_HOST,
                port=Config.CHROMA_PORT,
                tenant=Config.CHROMA_TENANT,
                database=Config.CHROMA_DATABASE,
            )
            logger.info(
                f"✅ ChromaDB async client initialized for tenant '{Config.CHROMA_TENANT}' and database '{Config.CHROMA_DATABASE}'"
            )

            # Define desired collection configuration
            desired_config = {
                "hnsw": {
                    "space": "cosine",  # Use cosine similarity for semantic search
                    "ef_construction": getattr(Config, "CHROMA_EF_CONSTRUCTION", 100),
                    "ef_search": getattr(Config, "CHROMA_EF_SEARCH", 100),
                    "max_neighbors": getattr(Config, "CHROMA_MAX_NEIGHBORS", 16),
                    "resize_factor": getattr(Config, "CHROMA_RESIZE_FACTOR", 1.2),
                    "sync_threshold": getattr(Config, "CHROMA_SYNC_THRESHOLD", 1000),
                }
            }

            expected_dimension = getattr(Config, "EMBEDDING_DIMENSION", 768)

            collections = await self.client.list_collections()
            existing_collections = [c.name for c in collections]

            if Config.COLLECTION not in existing_collections:
                # Create new collection with proper configuration
                logger.info(
                    f"Creating new ChromaDB collection '{Config.COLLECTION}' with cosine similarity"
                )
                self.collection = await self.client.create_collection(
                    name=Config.COLLECTION,
                    configuration=desired_config,
                    # Note: dimension will be auto-detected on first document insert
                )
                logger.info(
                    f"✅ ChromaDB collection '{Config.COLLECTION}' created with cosine similarity."
                )

            else:
                # Collection exists - validate configuration
                logger.info(
                    f"ChromaDB collection '{Config.COLLECTION}' already exists. Validating configuration..."
                )
                self.collection = await self.client.get_collection(
                    name=Config.COLLECTION
                )

                # Get collection details to check configuration
                collection_info = await self._get_collection_info()
                await self._validate_collection_config(
                    collection_info, desired_config, expected_dimension
                )

        except Exception as e:
            logger.error(f"❌ Failed to initialize ChromaDB collection: {e}")
            raise

    async def _get_collection_info(self):
        """Get collection information including configuration."""
        try:
            # Use the REST API to get detailed collection info
            import aiohttp

            url = f"http://{Config.CHROMA_HOST}:{Config.CHROMA_PORT}/api/v2/tenants/{Config.CHROMA_TENANT}/databases/{Config.CHROMA_DATABASE}/collections/{Config.COLLECTION}"

            async with aiohttp.ClientSession() as session:
                headers = {}
                if hasattr(Config, "CHROMA_TOKEN") and Config.CHROMA_TOKEN:
                    headers["Authorization"] = f"Bearer {Config.CHROMA_TOKEN}"

                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.warning(
                            f"Could not fetch collection info: {response.status}"
                        )
                        return None

        except Exception as e:
            logger.warning(f"Could not fetch collection configuration: {e}")
            return None

    async def _validate_collection_config(
        self, collection_info, desired_config, expected_dimension
    ):
        """Validate existing collection configuration and handle mismatches."""
        if not collection_info:
            logger.warning(
                "⚠️ Could not validate collection configuration - proceeding with existing collection"
            )
            return

        config = collection_info.get("configuration_json", {})
        hnsw_config = config.get("hnsw", {})
        current_space = hnsw_config.get("space", "unknown")
        current_dimension = collection_info.get("dimension")

        # Check distance metric
        if current_space != "cosine":
            logger.error(
                f"❌ Collection '{Config.COLLECTION}' uses '{current_space}' distance, but 'cosine' is required for semantic search!"
            )

            if getattr(Config, "AUTO_RECREATE_COLLECTION", False):
                logger.warning(
                    "🔄 AUTO_RECREATE_COLLECTION=True. Recreating collection with correct configuration..."
                )
                await self._recreate_collection_with_config(desired_config)
            else:
                logger.error(
                    "💡 Set AUTO_RECREATE_COLLECTION=True in config to automatically recreate with correct configuration"
                )
                logger.error(
                    "💡 Or manually recreate the collection with cosine similarity"
                )
                raise ValueError(
                    f"Collection configuration mismatch: expected 'cosine' similarity, got '{current_space}'"
                )

        # Check dimension (if set)
        if current_dimension and current_dimension != expected_dimension:
            logger.error(
                f"❌ Dimension mismatch: collection has {current_dimension}, expected {expected_dimension}"
            )
            raise ValueError(
                f"Collection dimension mismatch: expected {expected_dimension}, got {current_dimension}"
            )

        # Log configuration validation success
        logger.info("✅ Collection configuration validated:")
        logger.info(f"   - Distance metric: {current_space}")
        logger.info(f"   - Dimension: {current_dimension or 'auto-detect'}")
        logger.info(
            f"   - HNSW params: ef_construction={hnsw_config.get('ef_construction')}, ef_search={hnsw_config.get('ef_search')}"
        )

    async def _recreate_collection_with_config(self, desired_config):
        """Recreate collection with proper configuration (destructive operation)."""
        logger.warning(f"🗑️ Deleting existing collection '{Config.COLLECTION}'...")

        try:
            await self.client.delete_collection(name=Config.COLLECTION)
            logger.info(f"✅ Collection '{Config.COLLECTION}' deleted")

            # Create new collection with proper configuration
            logger.info(
                f"🔄 Creating new collection '{Config.COLLECTION}' with cosine similarity..."
            )
            self.collection = await self.client.create_collection(
                name=Config.COLLECTION, configuration=desired_config
            )
            logger.info(
                f"✅ Collection '{Config.COLLECTION}' recreated with proper configuration"
            )

        except Exception as e:
            logger.error(f"❌ Failed to recreate collection: {e}")
            raise

    async def ingest_document(
        self,
        content: str,
        page_title: str,
        solution: str = "zmp",
        page_no: int = None,
        chunk_order: int = None,
        doc_url: str = "",
        manual_keywords: Optional[List[str]] = None,
        embedded_images: Optional[List[str]] = None,
        assets_s3_keys: Optional[List[str]] = None,
        chunk_type: str = "single",
        created_at: str = None,
        updated_at: str = None,
        dense_vector: Optional[List[float]] = None,
        sparse_vector: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Ingest a single document chunk into ChromaDB.
        """
        doc_id = None
        try:
            if dense_vector is None:
                raise ValueError(
                    "dense_vector is required for ingestion into ChromaDB."
                )

            # Prepare metadata for hashing (exclude timestamps)
            metadata_for_hash = prepare_metadata(
                solution=solution,
                page_title=page_title,
                page_no=page_no,
                chunk_order=chunk_order,
                content=content,
                doc_url=doc_url,
                manual_keywords=manual_keywords,
                embedded_images=embedded_images,
                assets_s3_keys=assets_s3_keys,
                chunk_type=chunk_type,
                created_at=None,
                updated_at=None,
                keyword_extractors=KEYWORD_EXTRACTORS,
            )
            doc_id = create_document_id(content, metadata_for_hash)

            # Preserve original created_at if document exists
            existing_doc = await self.get_document_by_id(doc_id)
            if existing_doc and existing_doc.get("created_at"):
                created_at_to_use = existing_doc["created_at"]
            else:
                created_at_to_use = created_at or datetime.now(timezone.utc).isoformat()

            # Prepare final metadata for upsert
            final_metadata = prepare_metadata(
                solution=solution,
                page_title=page_title,
                page_no=page_no,
                chunk_order=chunk_order,
                content=content,
                doc_url=doc_url,
                manual_keywords=manual_keywords,
                embedded_images=embedded_images,
                assets_s3_keys=assets_s3_keys,
                chunk_type=chunk_type,
                created_at=created_at_to_use,
                updated_at=updated_at or datetime.now(timezone.utc).isoformat(),
                keyword_extractors=KEYWORD_EXTRACTORS,
            )

            # Ensure all extra fields in metadata (like doctags_markdown) are included
            metadata_to_store = final_metadata.copy()
            for k, v in final_metadata.items():
                if k not in metadata_to_store:
                    metadata_to_store[k] = v
            await self._add_or_update_document(
                doc_id=doc_id,
                content=content,
                metadata=metadata_to_store,
                dense_vector=dense_vector,
                is_update=bool(existing_doc),
            )
            logger.info(f"✅ Ingested doc_id: {doc_id}")
            return doc_id

        except Exception as e:
            if "dense_vector is required" in str(e):
                logger.error(
                    f"❌ Exception in ingest_document for doc_id {doc_id}: {e}"
                )
                logger.error("❌ dense_vector was None during the failed ingestion.")
            else:
                logger.error(
                    f"❌ Exception in ingest_document for doc_id {doc_id}: {e}"
                )
            raise

    async def _add_or_update_document(
        self,
        doc_id: str,
        content: str,
        metadata: Dict[str, Any],
        dense_vector: List[float],
        is_update: bool = False,
    ):
        """Helper to add or update a document."""
        # ChromaDB's upsert handles both add and update
        await self.collection.upsert(
            ids=[doc_id],
            documents=[content],
            embeddings=[dense_vector],
            metadatas=[metadata],
        )

    async def ingest_batch(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Ingests a batch of documents into ChromaDB."""
        # This is a simplified batch ingest; a more robust version would handle errors per-document
        return await asyncio.gather(*[self.ingest_document(**doc) for doc in documents])

    async def query(
        self,
        dense_vector: List[float],
        sparse_vector: Optional[Dict[str, Any]],
        n_results: int = 5,
        solution_filter: str = None,
    ) -> Dict:
        """
        Queries the ChromaDB collection using a dense vector.
        Sparse vector is ignored as it's not supported in Chroma OSS.
        """
        where_clause = {}
        if solution_filter:
            where_clause["solution"] = solution_filter
        logger.debug(f"[ChromaDB] Query embedding: {dense_vector}")
        logger.info(f"[ChromaDB] Query embedding dimension: {len(dense_vector)}")
        logger.info(f"[ChromaDB] Collection: {self.collection.name}")
        results = await self.collection.query(
            query_embeddings=[dense_vector],
            n_results=n_results,
            where=where_clause if where_clause else None,
            include=["metadatas", "documents", "distances"],
        )
        logger.info(f"[ChromaDB] Raw query results: {results}")
        return results

    async def get_collection_stats(self):
        """Returns stats about the collection."""
        return await self.collection.count()

    async def delete_document(self, doc_id: str):
        """Deletes a document by its ID."""
        await self.collection.delete(ids=[doc_id])

    async def update_document(
        self, doc_id: str, content: str = None, metadata: Dict = None
    ) -> bool:
        """Updates a document's content or metadata."""
        updates = {}
        if content:
            updates["documents"] = [content]
        if metadata:
            updates["metadatas"] = [metadata]

        if not updates:
            return False

        await self.collection.update(ids=[doc_id], **updates)
        return True

    async def get_document(self, doc_id: str) -> Dict[str, Any]:
        """Retrieves a document by its ID."""
        return await self.collection.get(ids=[doc_id])

    async def list_documents(
        self, solution: str = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Lists documents, optionally filtering by solution."""
        where_clause = {}
        if solution:
            where_clause["solution"] = solution

        results = await self.collection.get(
            where=where_clause if where_clause else None,
            limit=limit,
            include=["metadatas", "documents"],
        )
        # The result from ChromaDB is a dict with 'ids', 'documents', 'metadatas'
        # We need to re-format it into a list of dicts.
        output = []
        for i, doc_id in enumerate(results["ids"]):
            output.append(
                {
                    "id": doc_id,
                    "document": results["documents"][i],
                    "metadata": results["metadatas"][i],
                }
            )
        return output

    async def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Fetches a single document by its ID and returns its metadata if found."""
        try:
            result = await self.collection.get(ids=[doc_id], include=["metadatas"])
            if result and result["ids"]:
                return result["metadatas"][0]
            return None
        except Exception as e:
            logger.warning(f"Failed to get document by ID {doc_id}: {e}")
            return None

    async def get_all_document_ids(self) -> List[str]:
        """Retrieves all document IDs from the collection."""
        try:
            # Using get without IDs and a large limit to fetch all items.
            # For very large collections, this might need pagination.
            results = await self.collection.get(limit=await self.collection.count())
            return results["ids"]
        except Exception as e:
            logger.error(f"❌ Failed to get all document IDs: {e}")
            return []
