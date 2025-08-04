import logging
from typing import List, Optional
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    PointStruct,
    SparseVector,
    VectorParams,
    Distance,
    SparseVectorParams,
    QueryRequest,  # Use QueryRequest instead of SearchRequest
)
from .utils import prepare_metadata, KEYWORD_EXTRACTORS, create_document_id
import torch
from ranx import Run, fuse
import numpy as np
from zmp_knowledge_store.config import Config
from sklearn.cluster import DBSCAN

logger = logging.getLogger(__name__)


class QdrantAdapter:
    """
    Qdrant adapter for chatbot knowledge base with hybrid (dense + sparse) support.
    Metadata is prepared using the same logic as ChromaDBIngester for consistency.
    """

    def __init__(self):
        self.client: Optional[AsyncQdrantClient] = None
        self.collection_name = Config.DOCUMENT_COLLECTION

    async def ainit(self):
        """Asynchronously initializes the Qdrant client."""
        await self._ainitialize_client()

    async def _acreate_collection_if_not_exists(
        self, collection_name, vectors_config, sparse_vectors_config=None
    ):
        """Creates the specified collection if it doesn't already exist, with given vector configs."""
        if not self.client:
            logger.error("Qdrant client not initialized. Cannot create collection.")
            return
        try:
            collections = (await self.client.get_collections()).collections
            if collection_name not in [c.name for c in collections]:
                logger.info(f"Collection '{collection_name}' not found. Creating...")
                await self.client.recreate_collection(
                    collection_name=collection_name,
                    vectors_config=vectors_config,
                    sparse_vectors_config=sparse_vectors_config,
                )
                logger.info(f"✅ Collection '{collection_name}' created.")
            else:
                logger.info(f"✅ Collection '{collection_name}' already exists.")
        except Exception as e:
            logger.error(
                f"❌ Failed to create or check collection '{collection_name}': {e}"
            )

    async def _ainitialize_client(self):
        """Initializes the Qdrant client and ensures the collection exists."""
        try:
            self.client = AsyncQdrantClient(
                host=Config.QDRANT_HOST,
                port=Config.QDRANT_PORT,
                api_key=Config.QDRANT_API_KEY,
                https=False,
            )
            logger.info("✅ Qdrant async client initialized.")
            await self._acreate_collection_if_not_exists(
                collection_name=self.collection_name,
                vectors_config={
                    "dense": VectorParams(size=768, distance=Distance.COSINE)
                },
                sparse_vectors_config={"sparse": SparseVectorParams()},
            )
        except Exception as e:
            logger.error(f"❌ Failed to initialize Qdrant async client: {e}")
            self.client = None

    async def ensure_chat_history_collection_exists(self):
        """Ensure the chat history collection exists with dense and sparse vectors."""
        if not self.client:
            await self._ainitialize_client()
        await self._acreate_collection_if_not_exists(
            collection_name=Config.CHAT_HISTORY_COLLECTION,
            vectors_config={"dense": VectorParams(size=768, distance=Distance.COSINE)},
            sparse_vectors_config={"sparse": SparseVectorParams()},
        )

    async def log_chat_history(
        self,
        query,
        response,
        timestamp,
        user_id=None,
        session_id=None,
        dense_vector=None,
        sparse_vector=None,
    ):
        """Insert a chat history record into the chat history collection with dense and sparse vectors, using a deterministic hash for deduplication."""
        await self.ensure_chat_history_collection_exists()
        payload = {
            "query": query,
            "response": response,
            "timestamp": timestamp,
        }
        if user_id is not None:
            payload["user_id"] = user_id
        if session_id is not None:
            payload["session_id"] = session_id
        # Prepare vector dict as in ingest_document
        vector_dict = {"dense": dense_vector}
        # --- Consistent sparse vector handling ---
        if sparse_vector is not None:
            from qdrant_client.models import SparseVector

            if isinstance(sparse_vector, dict):
                indices = list(sparse_vector.keys())
                values = list(sparse_vector.values())
                sparse_vector = SparseVector(indices=indices, values=values)
            if (
                getattr(sparse_vector, "indices", None)
                and len(sparse_vector.indices) > 0
            ):
                vector_dict["sparse"] = sparse_vector
        # --- Deterministic ID for deduplication ---
        from zmp_knowledge_store.utils import create_document_id

        # Build a minimal metadata dict for hashing
        hash_metadata = {"query": query}
        if user_id is not None:
            hash_metadata["user_id"] = user_id
        point_id = create_document_id("chat_history", hash_metadata)
        await self.client.upsert(
            collection_name=Config.CHAT_HISTORY_COLLECTION,
            points=[
                PointStruct(
                    id=point_id,
                    payload=payload,
                    vector=vector_dict,
                )
            ],
        )
        logger.info(f"✅ Logged chat history: {point_id}")
        return point_id

    async def ingest_document(
        self,
        content: str,
        page_title: str = None,
        solution: str = "zmp",
        page_no: int = None,
        chunk_order: int = None,
        doc_url: str = "",
        manual_keywords: list = None,
        embedded_images: list = None,
        assets_s3_keys: list = None,
        chunk_type: str = "single",
        dense_vector: list = None,
        sparse_vector: dict = None,
        created_at: str = None,
        updated_at: str = None,
        original_created_at: str = None,
    ) -> str:
        """
        Ingest a single document with both dense and sparse vectors.
        Metadata is prepared using the shared prepare_metadata utility.
        """
        # Convert sparse_vector to Qdrant SparseVector if needed
        if sparse_vector is not None:
            if isinstance(sparse_vector, dict):
                indices = list(sparse_vector.keys())
                values = list(sparse_vector.values())
                sparse_vector = SparseVector(indices=indices, values=values)
            elif isinstance(sparse_vector, torch.Tensor):
                nonzero = sparse_vector.nonzero(as_tuple=True)[0]
                values = sparse_vector[nonzero]
                indices = nonzero.tolist()
                values = values.tolist()
                sparse_vector = SparseVector(indices=indices, values=values)
        # Build vector dict for Qdrant
        vector_dict = {"dense": dense_vector}
        if sparse_vector is not None and getattr(sparse_vector, "indices", None):
            if len(sparse_vector.indices) > 0:
                vector_dict["sparse"] = sparse_vector
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
        import json as _json

        logger.info(f"[DEBUG][Qdrant] create_document_id content: {repr(content)}")
        logger.info(
            f"[DEBUG][Qdrant] create_document_id metadata: {_json.dumps(metadata_for_hash, sort_keys=True, ensure_ascii=False)}"
        )
        doc_id = create_document_id(content, metadata_for_hash)

        # The payload for Qdrant should include the content.
        payload = metadata_for_hash.copy()
        payload["content"] = content

        # Preserve original created_at if document exists
        existing = await self.client.retrieve(
            collection_name=self.collection_name, ids=[doc_id], with_payload=True
        )
        if existing and existing[0].payload and existing[0].payload.get("created_at"):
            created_at_to_use = existing[0].payload["created_at"]
        else:
            created_at_to_use = created_at
        payload["created_at"] = created_at_to_use
        payload["updated_at"] = updated_at

        # Add warning if sparse vector is missing or empty
        if (
            sparse_vector is None
            or not getattr(sparse_vector, "indices", None)
            or len(sparse_vector.indices) == 0
        ):
            logger.warning(
                f"[QdrantAdapter] No sparse vector for doc_id {doc_id} (content length: {len(content)})"
            )

        try:
            await self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(
                        id=doc_id,
                        payload=payload,
                        vector=vector_dict,
                    )
                ],
            )
            logger.info(f"✅ Ingested doc_id: {doc_id}")
            return doc_id
        except Exception as e:
            logger.error(f"❌ Failed to ingest doc_id {doc_id}: {e}")
            raise

    @staticmethod
    def _dbsf_normalize(scores_dict):
        """
        Normalize a dict of {doc_id: score} using DBSF (min-max with 3 std from mean).
        """
        if not scores_dict:
            return {}
        values = np.array(list(scores_dict.values()))
        # if values.size == 0:
        #     return {k: 0.0 for k in scores_dict}
        mean = values.mean()
        std = values.std()
        lower = max(values.min(), mean - 3 * std)
        upper = min(values.max(), mean + 3 * std)
        if upper == lower:
            return {k: 0.0 for k in scores_dict}
        return {k: (v - lower) / (upper - lower) for k, v in scores_dict.items()}

    async def query(
        self, dense_vector: List[float], sparse_vector: dict, limit: int = 5
    ):
        """
        Performs a hybrid search in the specified Qdrant collection using search_batch API and fuses results with DBSF normalization + Ranx RRF.
        Returns a list of fused results (dicts with id, score, payload).
        """
        if not self.client:
            await self._ainitialize_client()

        try:
            # Prepare the sparse vector object
            sparse_vec = SparseVector(
                indices=sparse_vector["indices"],
                values=sparse_vector["values"],
            )

            # Prepare the batch query requests (use QueryRequest, not SearchRequest)
            requests = [
                QueryRequest(
                    query=dense_vector,
                    using="dense",  # Specify the vector name for dense
                    limit=limit,
                    with_payload=True,  # Ensure payload is returned
                ),
                QueryRequest(
                    query=sparse_vec,
                    using="sparse",  # Specify the vector name for sparse
                    limit=limit,
                    with_payload=True,  # Ensure payload is returned
                ),
            ]

            # Perform the batch query using query_batch_points (not search_batch)
            results = await self.client.query_batch_points(
                collection_name=self.collection_name, requests=requests
            )

            # Each result is a QueryResponse object with a .points attribute
            dense_hits = results[0].points
            sparse_hits = results[1].points

            # Convert Qdrant hits to dict for normalization
            def hits_to_scores_dict(hits):
                return {str(hit.id): float(hit.score) for hit in hits}

            dense_scores = self._dbsf_normalize(hits_to_scores_dict(dense_hits))
            sparse_scores = self._dbsf_normalize(hits_to_scores_dict(sparse_hits))

            # Convert to Ranx Run format (using dummy query_id 'q0')
            dense_run = Run({"q0": dense_scores}, name="dense")
            sparse_run = Run({"q0": sparse_scores}, name="sparse")

            # Fuse using RRF (Reciprocal Rank Fusion)
            fused_run = fuse(runs=[dense_run, sparse_run], method="rrf", norm=None)

            # Build a lookup for payloads by doc_id for efficient access
            payload_lookup = {str(h.id): h.payload for h in dense_hits + sparse_hits}

            # Get fused results for 'q0', sorted by score descending
            fused_results = [
                {"id": doc_id, "score": score, "payload": payload_lookup.get(doc_id)}
                for doc_id, score in fused_run["q0"].items()
            ]
            fused_results.sort(key=lambda x: x["score"], reverse=True)
            return fused_results[:limit]

        except Exception as e:
            logger.error(f"❌ Hybrid search or fusion failed: {e}")
            # # Fallback: return dense results only
            # try:
            #     results = await self.client.search_batch(
            #         collection_name=self.collection_name,
            #         requests=[
            #             SearchRequest(
            #                 vector=NamedVector(name="dense", vector=dense_vector),
            #                 limit=limit,
            #             )
            #         ]
            #     )
            #     dense_hits = results[0]
            #     out = []
            #     for hit in dense_hits:
            #         payload = hit.payload
            #         if payload is None:
            #             try:
            #                 fetched = await self.client.retrieve(collection_name=self.collection_name, ids=[str(hit.id)], with_payload=True)
            #                 if fetched and fetched[0].payload:
            #                     payload = fetched[0].payload
            #             except Exception as e:
            #                 logger.warning(f"Could not fetch payload for doc_id {hit.id}: {e}")
            #         out.append({"id": str(hit.id), "score": float(hit.score), "payload": payload})
            #     return out
            # except Exception as fallback_error:
            #     logger.error(f"❌ Dense-only fallback failed: {fallback_error}")
            #     return []
            return []

    async def search_chat_history(
        self,
        query: str,
        user_id: str = None,
        n_results: int = 5,
        dense_vector=None,
        sparse_vector=None,
    ):
        """Hybrid search for chat history records using provided dense+sparse vectors and optional user_id filter."""
        # Build filter for user_id if provided
        filter_ = None
        if user_id:
            from qdrant_client.http.models import Filter, FieldCondition, MatchValue

            filter_ = Filter(
                must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]
            )

        # Prepare the sparse vector object
        # from qdrant_client.models import SparseVector
        sparse_vec = (
            SparseVector(
                indices=sparse_vector["indices"],
                values=sparse_vector["values"],
            )
            if sparse_vector and sparse_vector.get("indices")
            else None
        )

        # Prepare the batch query requests (use QueryRequest, not SearchRequest)
        # from qdrant_client.models import QueryRequest
        requests = [
            QueryRequest(
                query=dense_vector,
                using="dense",
                limit=n_results,
                with_payload=True,
                filter=filter_,
            ),
        ]
        if sparse_vec:
            requests.append(
                QueryRequest(
                    query=sparse_vec,
                    using="sparse",
                    limit=n_results,
                    with_payload=True,
                    filter=filter_,
                )
            )

        # Perform the batch query using query_batch_points
        results = await self.client.query_batch_points(
            collection_name=Config.CHAT_HISTORY_COLLECTION, requests=requests
        )

        # Each result is a QueryResponse object with a .points attribute
        dense_hits = results[0].points
        sparse_hits = results[1].points if len(results) > 1 else []

        # Convert Qdrant hits to dict for normalization
        def hits_to_scores_dict(hits):
            return {str(hit.id): float(hit.score) for hit in hits}

        dense_scores = self._dbsf_normalize(hits_to_scores_dict(dense_hits))
        sparse_scores = self._dbsf_normalize(hits_to_scores_dict(sparse_hits))

        # Convert to Ranx Run format (using dummy query_id 'q0')
        from ranx import Run, fuse

        dense_run = Run({"q0": dense_scores}, name="dense")
        sparse_run = Run({"q0": sparse_scores}, name="sparse")

        # Fuse using RRF (Reciprocal Rank Fusion)
        fused_run = fuse(runs=[dense_run, sparse_run], method="rrf", norm=None)

        # Build a lookup for payloads by doc_id for efficient access
        payload_lookup = {str(h.id): h.payload for h in dense_hits + sparse_hits}

        # Get fused results for 'q0', sorted by score descending
        fused_results = [
            {"id": doc_id, "score": score, "payload": payload_lookup.get(doc_id)}
            for doc_id, score in fused_run["q0"].items()
        ]
        fused_results.sort(key=lambda x: x["score"], reverse=True)
        # --- Cluster results by score and only return those in the same cluster as the top result ---
        if fused_results:
            try:
                scores = np.array([[r["score"]] for r in fused_results])
                # eps can be tuned; 0.05 is a reasonable starting point for normalized scores
                clustering = DBSCAN(eps=0.01, min_samples=1).fit(scores)
                labels = clustering.labels_
                top_label = labels[0]
                clustered_results = [
                    r for r, label in zip(fused_results, labels) if label == top_label
                ]
                filtered_out = [
                    r for r, label in zip(fused_results, labels) if label != top_label
                ]
                if filtered_out:
                    logger.info(
                        f"[Clustering] Filtered out {len(filtered_out)} results for query: {query}"
                    )
                    for r in filtered_out:
                        logger.info(
                            f"[Clustering][Filtered] Score: {r['score']:.4f}, Payload: {r['payload']}"
                        )
                # Always return at least the top result
                if not clustered_results:
                    clustered_results = fused_results[:1]
                # Log cluster label for every result
                for r, label in zip(fused_results, labels):
                    logger.info(
                        f"[Clustering][Label] Score: {r['score']:.4f}, Label: {label}, Payload: {r['payload']}"
                    )
                # Return clustered results directly (semantic similarity filtering removed due to circular import)
                return clustered_results[:n_results]
            except Exception as e:
                logger.warning(
                    f"Clustering or semantic similarity filtering failed, falling back to top result only: {e}"
                )
                return fused_results[:1]
        else:
            return []

    async def get_all_document_ids(
        self, collection_name: str = "solution-docs"
    ) -> List[str]:
        if not self.client:
            await self._ainitialize_client()

        try:
            # Scroll API might need to be paginated for very large collections
            points, _ = await self.client.scroll(
                collection_name=collection_name, limit=1000
            )
            return [str(point.id) for point in points]
        except Exception as e:
            logger.error(f"❌ Failed to get all document IDs: {e}")
            return []
