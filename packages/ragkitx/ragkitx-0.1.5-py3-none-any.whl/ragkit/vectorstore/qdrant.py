from typing import List, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import (
    PointStruct,
    VectorParams,
    Distance,
    Filter,
    SearchParams,
)
from ragkit.embedding.base import EmbeddingResult
from .base import VectorStore
from qdrant_client.models import FieldCondition, MatchValue
from qdrant_client.http.models import MatchText

class QdrantVectorStore(VectorStore):
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        collection_name: str = "ragkit_collection",
        vector_size: int = 1536,
    ):
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = collection_name

        # Ensure collection exists
        if not self.client.collection_exists(self.collection_name):
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )

    def upsert(self, embeddings: List[EmbeddingResult]) -> None:
        points = [
            PointStruct(id=e.id, vector=e.embedding, payload=e.metadata)
            for e in embeddings
        ]
        self.client.upsert(collection_name=self.collection_name, points=points)

    def query(
            self,
            query_vector: List[float],
            top_k: int = 5,
            keywords: Optional[List[str]] = None,
            score_threshold: Optional[float] = None,
    ) -> List[EmbeddingResult]:
        payload_filter = None
        if keywords:
            payload_filter = Filter(
                should=[
                    FieldCondition(key="text", match=MatchText(text=kw)) for kw in keywords
                ]
            )

        result = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=payload_filter,
            limit=top_k,
            search_params=SearchParams(hnsw_ef=128),
            with_payload=True,
            with_vectors=False,
            score_threshold=score_threshold,
        )

        return [
            EmbeddingResult(
                id=point.id,
                embedding=query_vector,
                metadata=point.payload or {},
            )
            for point in result.points
        ]

