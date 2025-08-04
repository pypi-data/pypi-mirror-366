from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass

@dataclass
class EmbeddingResult:
    id: str
    embedding: List[float]
    metadata: dict

class Embedder(ABC):
    """Abstract base class for embedding strategies."""

    @abstractmethod
    def embed(self, texts: List[str]) -> List[EmbeddingResult]:
        pass
