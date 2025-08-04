from typing import List
import uuid
import nltk
import tiktoken
from .base import Chunker, DocumentChunk

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

class RecursiveChunker(Chunker):
    def __init__(self, max_tokens: int = 300, model_name: str = "gpt-3.5-turbo"):
        self.max_tokens = max_tokens
        self.encoding = tiktoken.encoding_for_model(model_name)

    def count_tokens(self, text: str) -> int:
        return len(self.encoding.encode(text))

    def chunk_text(self, text: str) -> List[DocumentChunk]:
        sentences = nltk.sent_tokenize(text)
        chunks = []
        current_chunk = ""
        token_count = 0

        for sentence in sentences:
            sentence_token_count = self.count_tokens(sentence)
            if token_count + sentence_token_count > self.max_tokens:
                chunks.append(
                    DocumentChunk(
                        id=str(uuid.uuid4()),
                        content=current_chunk.strip(),
                        metadata={"tokens": token_count},
                    )
                )
                current_chunk = sentence
                token_count = sentence_token_count
            else:
                current_chunk += " " + sentence
                token_count += sentence_token_count

        if current_chunk:
            chunks.append(
                DocumentChunk(
                    id=str(uuid.uuid4()),
                    content=current_chunk.strip(),
                    metadata={"tokens": token_count},
                )
            )

        return chunks
