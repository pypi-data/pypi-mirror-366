from ragkit.chunking.recursive import RecursiveChunker

def test_chunking_short_text():
    text = "This is sentence one. This is sentence two. This is sentence three."
    chunker = RecursiveChunker(max_tokens=5)
    chunks = chunker.chunk_text(text)
    for chunk in chunks:
        print("== CHUNK ==")
        print(chunk.content)
        print("Token count:", chunk.metadata["tokens"])

if __name__ == "__main__":
    test_chunking_short_text()
