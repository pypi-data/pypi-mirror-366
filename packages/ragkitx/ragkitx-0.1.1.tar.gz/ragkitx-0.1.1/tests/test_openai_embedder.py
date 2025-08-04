import os
import pytest
from dotenv import load_dotenv
from ragkit.embedding.openai import OpenAIEmbedder

load_dotenv()  # ⬅️ this loads .env file

@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="Requires OPENAI_API_KEY environment variable"
)
def test_openai_embedder_embedding():
    api_key = os.getenv("OPENAI_API_KEY")
    embedder = OpenAIEmbedder(api_key=api_key)

    texts = ["ragkit is awesome", "open source AI utilities"]
    results = embedder.embed(texts)

    assert len(results) == len(texts)
    for res in results:
        assert isinstance(res.id, str)
        assert isinstance(res.embedding, list)
        assert all(isinstance(val, float) for val in res.embedding)
        assert "index" in res.metadata
