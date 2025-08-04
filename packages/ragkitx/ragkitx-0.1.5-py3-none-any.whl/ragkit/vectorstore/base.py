from abc import ABC, abstractmethod
from typing import List, Optional
from ragkit.embedding.base import EmbeddingResult


class VectorStore(ABC):
    @abstractmethod
    def upsert(self, embeddings: List[EmbeddingResult]) -> None:
        """Store embeddings into the vector DB"""
        pass

    @abstractmethod
    def query(
        self,
        query_vector: List[float],
        top_k: int = 5,
        keywords: Optional[List[str]] = None,
        score_threshold: Optional[float] = None,
    ) -> List[EmbeddingResult]:
        """Find nearest vectors to the query with optional filtering"""
        pass
