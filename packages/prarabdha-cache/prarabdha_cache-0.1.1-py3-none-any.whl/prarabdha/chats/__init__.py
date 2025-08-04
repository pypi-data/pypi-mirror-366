# Chat caching module for Prarabdha cache system

from .core import SegmentCacheManager, SegmentCacheManagerFactory, CacheStrategy, DefaultChatStrategy

# Main classes for direct import
__all__ = [
    "SegmentCacheManager",
    "SegmentCacheManagerFactory", 
    "CacheStrategy",
    "DefaultChatStrategy",
    "ChatCache"  # Alias for backward compatibility
]

# Create an alias for easier import
ChatCache = SegmentCacheManager
