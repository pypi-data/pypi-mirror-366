import os
import pytest
from dotenv import load_dotenv

from ragkit.chunking.recursive import RecursiveChunker
from ragkit.embedding.openai import OpenAIEmbedder
from ragkit.vectorstore.qdrant import QdrantVectorStore

load_dotenv()

@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="Requires OPENAI_API_KEY in .env"
)
def test_qdrant_vectorstore_workflow():
    api_key = os.getenv("OPENAI_API_KEY")

    # Step 1: Prepare text and chunk it
    text = (
        "Qdrant is a vector search engine. It helps with semantic search. "
        "You can use it with LLMs to build RAG pipelines. "
        "This test verifies upsert and search integration."
    )
    chunker = RecursiveChunker(max_tokens=50)
    chunks = chunker.chunk_text(text)
    texts = [chunk.content for chunk in chunks]

    # Step 2: Embed chunks
    embedder = OpenAIEmbedder(api_key=api_key)
    embeddings = embedder.embed(texts)

    # Step 3: Upsert to Qdrant
    store = QdrantVectorStore(vector_size=len(embeddings[0].embedding))
    store.upsert(embeddings)

    # Step 4: Query with the first vector
    results = store.query(embeddings[0].embedding, top_k=2)

    assert len(results) >= 1
    for r in results:
        assert isinstance(r.id, str)
        assert isinstance(r.metadata, dict)
