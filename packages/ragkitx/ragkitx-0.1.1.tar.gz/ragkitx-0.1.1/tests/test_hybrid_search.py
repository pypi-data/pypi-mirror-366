import os
import uuid
import pytest
from ragkit.chunking.recursive import RecursiveChunker
from ragkit.embedding.openai import OpenAIEmbedder
from ragkit.vectorstore.qdrant import QdrantVectorStore
from ragkit.pipeline.document_pipeline import DocumentPipelineService
from ragkit.embedding.base import EmbeddingResult
import os
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="Requires OPENAI_API_KEY in .env"
)
def test_hybrid_search_with_keyword_filtering():
    api_key = os.getenv("OPENAI_API_KEY")

    chunker = RecursiveChunker(max_tokens=50)
    embedder = OpenAIEmbedder(api_key=api_key)
    store = QdrantVectorStore(vector_size=1536)

    # Prepare raw texts
    text1 = "Qdrant is a vector database. It supports hybrid search."  # contains keyword 'vector'
    text2 = "Cats are cute animals. They like to sleep all day."       # contains keyword 'cats'

    # Embed manually so we can attach the "text" payload
    embedded1 = embedder.embed([text1])[0]
    embedded2 = embedder.embed([text2])[0]

    store.upsert([
        EmbeddingResult(
            id=str(uuid.uuid4()),  # ✅ valid UUID string
            embedding=embedded1.embedding,
            metadata={"text": text1}
        ),
        EmbeddingResult(
            id=str(uuid.uuid4()),  # ✅ valid UUID string
            embedding=embedded2.embedding,
            metadata={"text": text2}
        )
    ])

    # Query with hybrid search: vector + keyword filter
    search_vector = embedder.embed(["Tell me Qdrant"])[0].embedding
    results = store.query(query_vector=search_vector, top_k=3, keywords=["vector", "search"],
    score_threshold=0.3)

    assert len(results) > 0, "Expected at least one result for keyword 'vector'"
    assert "vector" in results[0].metadata.get("text", ""), "Expected result to contain 'vector' in text"
