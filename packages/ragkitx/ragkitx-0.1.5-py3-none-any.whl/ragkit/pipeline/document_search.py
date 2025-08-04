from typing import List, Optional
from ragkit.embedding.base import Embedder, EmbeddingResult
from ragkit.vectorstore.base import VectorStore


class DocumentSearchService:
    def __init__(self, embedder: Embedder, store: VectorStore):
        self.embedder = embedder
        self.store = store

    def search(
        self,
        query: str,
        top_k: int = 5,
        keywords: Optional[List[str]] = None,
    ) -> List[EmbeddingResult]:
        # Embed the query string
        embedding = self.embedder.embed([query])[0].embedding

        if not keywords:
            return self.store.query(query_vector=embedding, top_k=top_k)

        results = []
        for keyword in keywords:
            results.extend(
                self.store.query(query_vector=embedding, top_k=top_k, keywords=[keyword])
            )

        # Optional deduplication
        seen_ids = set()
        deduped_results = []
        for r in results:
            if r.id not in seen_ids:
                deduped_results.append(r)
                seen_ids.add(r.id)

        return deduped_results
