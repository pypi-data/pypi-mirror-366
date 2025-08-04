import os
import pytest
from dotenv import load_dotenv

from ragkit.chunking.recursive import RecursiveChunker
from ragkit.embedding.openai import OpenAIEmbedder
from ragkit.vectorstore.qdrant import QdrantVectorStore
from ragkit.pipeline.document_pipeline import DocumentPipelineService

load_dotenv()

@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="Requires OPENAI_API_KEY in .env"
)
def test_document_pipeline_end_to_end():
    api_key = os.getenv("OPENAI_API_KEY")

    # Prepare components
    chunker = RecursiveChunker(max_tokens=50)
    embedder = OpenAIEmbedder(api_key=api_key)
    store = QdrantVectorStore(vector_size=1536)  # adjust if using another model

    pipeline = DocumentPipelineService(chunker, embedder, store)

    # Input text
    text = (
        "This is a document about vector search. "
        "We use chunking and embedding to index the content. "
        "Qdrant stores the vectors and lets us retrieve similar content later."
    )

    # Run indexing pipeline
    embeddings = pipeline.index_text(text)

    assert len(embeddings) > 0
    for emb in embeddings:
        assert isinstance(emb.id, str)
        assert isinstance(emb.embedding, list)
        assert isinstance(emb.metadata, dict)
        assert "tokens" in emb.metadata
