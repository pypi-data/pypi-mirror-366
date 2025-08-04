# RAG chunk indexing module for Prarabdha cache system

from .chunk_index import ChunkIndex, ChunkIndexManager, DocumentChunk

# Main classes for direct import
__all__ = [
    "ChunkIndex",
    "ChunkIndexManager",
    "DocumentChunk",
    "RAGCache"  # Alias for backward compatibility
]

# Create an alias for easier import
RAGCache = ChunkIndex
