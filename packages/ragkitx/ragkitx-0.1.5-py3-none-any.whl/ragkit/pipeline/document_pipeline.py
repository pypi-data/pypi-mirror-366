from typing import List
from ragkit.chunking.base import Chunker
from ragkit.embedding.base import Embedder, EmbeddingResult
from ragkit.vectorstore.base import VectorStore


class DocumentPipelineService:
    def __init__(self, chunker: Chunker, embedder: Embedder, store: VectorStore):
        self.chunker = chunker
        self.embedder = embedder
        self.store = store

    def index_text(self, text: str) -> List[EmbeddingResult]:
        chunks = self.chunker.chunk_text(text)
        texts = [c.content for c in chunks]
        embeddings = self.embedder.embed(texts)

        # Optional: attach metadata from chunks to embeddings
        for emb, chunk in zip(embeddings, chunks):
            emb.metadata.update(chunk.metadata)
            emb.metadata["text"] = chunk.content

        self.store.upsert(embeddings)
        return embeddings
