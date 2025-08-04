from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass

@dataclass
class DocumentChunk:
    id: str
    content: str
    metadata: dict

class Chunker(ABC):
    @abstractmethod
    def chunk_text(self, text: str) -> List[DocumentChunk]:
        pass
