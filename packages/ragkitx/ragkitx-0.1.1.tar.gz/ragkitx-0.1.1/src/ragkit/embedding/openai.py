import uuid
from typing import List
from openai import OpenAI
from .base import Embedder, EmbeddingResult

class OpenAIEmbedder(Embedder):
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def embed(self, texts: List[str]) -> List[EmbeddingResult]:
        response = self.client.embeddings.create(
            model=self.model,
            input=texts,
        )
        return [
            EmbeddingResult(
                id=str(uuid.uuid4()),
                embedding=item.embedding,
                metadata={"index": i}
            )
            for i, item in enumerate(response.data)
        ]
