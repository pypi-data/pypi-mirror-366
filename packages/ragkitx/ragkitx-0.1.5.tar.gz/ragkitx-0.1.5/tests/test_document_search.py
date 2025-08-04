import os
import pytest
from dotenv import load_dotenv

from ragkit.chunking.recursive import RecursiveChunker
from ragkit.embedding.openai import OpenAIEmbedder
from ragkit.vectorstore.qdrant import QdrantVectorStore
from ragkit.pipeline.document_pipeline import DocumentPipelineService
from ragkit.pipeline.document_search import DocumentSearchService

load_dotenv()

@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="Requires OPENAI_API_KEY in .env"
)
def test_document_search_end_to_end():
    api_key = os.getenv("OPENAI_API_KEY")

    # Shared components
    chunker = RecursiveChunker(max_tokens=50)
    embedder = OpenAIEmbedder(api_key=api_key)
    store = QdrantVectorStore(vector_size=1536)

    # Step 1: Index content
    pipeline = DocumentPipelineService(chunker, embedder, store)
    source_text = (
        "Vector databases like Qdrant are useful for storing high-dimensional embeddings. "
        "They are often used in semantic search and retrieval-augmented generation (RAG) systems."
    )
    pipeline.index_text(source_text)

    # Step 2: Search
    search_service = DocumentSearchService(embedder, store)
    query = "How do I store embeddings for semantic search?"
    results = search_service.search(query, top_k=3)

    assert len(results) > 0
    for result in results:
        assert isinstance(result.id, str)
        assert isinstance(result.metadata, dict)
