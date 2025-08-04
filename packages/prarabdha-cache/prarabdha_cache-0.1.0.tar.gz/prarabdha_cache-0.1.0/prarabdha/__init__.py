"""
Prarabdha - Modular AI Cache System

A futuristic modular caching system for AI applications supporting:
- Multi-layer caching (RAM, disk, Redis)
- Vector similarity search with FAISS
- RAG-aware chunk indexing
- Audio and video feature caching
- Async ingestion APIs
- CLI tools for management
"""

__version__ = "0.1.0"
__author__ = "Prarabdha Soni"

# Core components
from .core.kv_store import MultiLayerKVStore, LRUCache, LFUCache, DiskKVStore
from .core.redis_store import RedisKVStore
from .core.vector_index import SemanticVectorIndex, VectorIndexManager

# Chat components
from .chats.core import SegmentCacheManager, SegmentCacheManagerFactory, CacheStrategy, DefaultChatStrategy
from .chats import ChatCache

# RAG components
from .rag.chunk_index import ChunkIndex, ChunkIndexManager, DocumentChunk
from .rag import RAGCache

# Audio components
from .audio.audio_cache import AudioCache, AudioCacheManager, AudioFeature
from .audio import audioCache

# Video components
from .video.video_cache import VideoCache, VideoCacheManager, VideoSegment, VideoFrame
from .video import videoCache

# CLI and API
from .cli.cli import app as cli_app
from .api.app import app as api_app

__all__ = [
    # Core
    "MultiLayerKVStore",
    "LRUCache", 
    "LFUCache",
    "DiskKVStore",
    "RedisKVStore",
    "SemanticVectorIndex",
    "VectorIndexManager",
    
    # Chat
    "SegmentCacheManager",
    "SegmentCacheManagerFactory", 
    "CacheStrategy",
    "DefaultChatStrategy",
    "ChatCache",
    
    # RAG
    "ChunkIndex",
    "ChunkIndexManager",
    "DocumentChunk",
    "RAGCache",
    
    # Audio
    "AudioCache",
    "AudioCacheManager",
    "AudioFeature",
    "audioCache",
    
    # Video
    "VideoCache",
    "VideoCacheManager",
    "VideoSegment",
    "VideoFrame",
    "videoCache",
    
    # CLI and API
    "cli_app",
    "api_app",
]
