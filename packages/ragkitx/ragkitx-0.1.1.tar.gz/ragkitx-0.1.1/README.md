# ragkit

**Modular RAG toolkit** – A flexible and pluggable framework for Retrieval-Augmented Generation (RAG) workflows.

## Features

- Plug-and-play architecture for embedding models and vector stores
- Support for hybrid search (vector + keyword)
- Extensible design with Pydantic models
- Qdrant vector store support
- OpenAI and SentenceTransformer embedding

## Installation

```bash
pip install ragkit


## Usage

```python
from ragkit.search import DocumentSearchService
from ragkit.embedding import OpenAIEmbedder
from ragkit.vectorstore import QdrantVectorStore

# Initialize components
embedder = OpenAIEmbedder(api_key="your-openai-api-key")
store = QdrantVectorStore(vector_size=1536)

search_service = DocumentSearchService(embedder, store)

# Perform search
results = search_service.search("Tell me about vector databases")
```