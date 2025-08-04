import hashlib
import json
import time
import numpy as np
from typing import Dict, Any, Optional, List, Tuple, Callable
from abc import ABC, abstractmethod
import threading

from ..core.kv_store import MultiLayerKVStore
from ..core.vector_index import SemanticVectorIndex, VectorIndexManager

class CacheStrategy(ABC):
    """Abstract base class for cache strategies"""
    
    @abstractmethod
    def should_cache(self, segment: Dict[str, Any]) -> bool:
        """Determine if a segment should be cached"""
        pass
    
    @abstractmethod
    def generate_key(self, segment: Dict[str, Any]) -> str:
        """Generate cache key for a segment"""
        pass
    
    @abstractmethod
    def extract_features(self, segment: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features for vector indexing"""
        pass

class DefaultChatStrategy(CacheStrategy):
    """Default strategy for chat segment caching"""
    
    def __init__(self, 
                 cache_by_content: bool = True,
                 cache_by_metadata: bool = True,
                 similarity_threshold: float = 0.8):
        self.cache_by_content = cache_by_content
        self.cache_by_metadata = cache_by_metadata
        self.similarity_threshold = similarity_threshold
    
    def should_cache(self, segment: Dict[str, Any]) -> bool:
        """Determine if segment should be cached"""
        # Cache if it has meaningful content
        content = segment.get('content', '')
        if not content or len(content.strip()) < 10:
            return False
        
        # Cache if it has required metadata
        if self.cache_by_metadata:
            required_fields = ['user_id', 'session_id', 'timestamp']
            if not all(field in segment for field in required_fields):
                return False
        
        return True
    
    def generate_key(self, segment: Dict[str, Any]) -> str:
        """Generate cache key based on content and metadata"""
        key_parts = []
        
        if self.cache_by_content:
            content = segment.get('content', '')
            content_hash = hashlib.md5(content.encode()).hexdigest()
            key_parts.append(content_hash)
        
        if self.cache_by_metadata:
            metadata = {
                'user_id': segment.get('user_id', ''),
                'session_id': segment.get('session_id', ''),
                'model': segment.get('model', ''),
                'timestamp': segment.get('timestamp', '')
            }
            metadata_str = json.dumps(metadata, sort_keys=True)
            metadata_hash = hashlib.md5(metadata_str.encode()).hexdigest()
            key_parts.append(metadata_hash)
        
        return ':'.join(key_parts)
    
    def extract_features(self, segment: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features for vector indexing"""
        features = {
            'content': segment.get('content', ''),
            'user_id': segment.get('user_id', ''),
            'session_id': segment.get('session_id', ''),
            'model': segment.get('model', ''),
            'timestamp': segment.get('timestamp', ''),
            'length': len(segment.get('content', '')),
            'type': segment.get('type', 'chat')
        }
        return features

class SegmentCacheManager:
    """Segment-level cache manager with RAG integration"""
    
    def __init__(self,
                 kv_store: Optional[MultiLayerKVStore] = None,
                 vector_index: Optional[SemanticVectorIndex] = None,
                 strategy: Optional[CacheStrategy] = None,
                 enable_rag: bool = True,
                 rag_similarity_threshold: float = 0.8):
        
        # Initialize KV store
        self.kv_store = kv_store or MultiLayerKVStore()
        
        # Initialize vector index
        self.vector_index = vector_index or SemanticVectorIndex(
            similarity_threshold=rag_similarity_threshold
        )
        
        # Initialize strategy
        self.strategy = strategy or DefaultChatStrategy()
        
        # RAG settings
        self.enable_rag = enable_rag
        self.rag_similarity_threshold = rag_similarity_threshold
        
        # Statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'total_requests': 0,
            'cache_size': 0
        }
        self.stats_lock = threading.RLock()
    
    def _update_stats(self, hit: bool):
        """Update cache statistics"""
        with self.stats_lock:
            self.stats['total_requests'] += 1
            if hit:
                self.stats['hits'] += 1
            else:
                self.stats['misses'] += 1
    
    def _get_cache_key(self, segment: Dict[str, Any]) -> str:
        """Generate cache key for segment"""
        return self.strategy.generate_key(segment)
    
    def _should_cache(self, segment: Dict[str, Any]) -> bool:
        """Check if segment should be cached"""
        return self.strategy.should_cache(segment)
    
    def _extract_features(self, segment: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features for vector indexing"""
        return self.strategy.extract_features(segment)
    
    def _create_vector_embedding(self, features: Dict[str, Any]) -> np.ndarray:
        """Create vector embedding from features"""
        # Simple feature vector based on content length and metadata
        # In a real implementation, you'd use a proper embedding model
        embedding = []
        
        # Content length feature (normalized)
        content_length = features.get('length', 0)
        embedding.append(min(content_length / 1000.0, 1.0))  # Normalize to 0-1
        
        # User ID hash feature
        user_id = features.get('user_id', '')
        user_hash = hash(user_id) % 1000 / 1000.0
        embedding.append(user_hash)
        
        # Session ID hash feature
        session_id = features.get('session_id', '')
        session_hash = hash(session_id) % 1000 / 1000.0
        embedding.append(session_hash)
        
        # Timestamp feature (normalized to 0-1)
        timestamp = features.get('timestamp', 0)
        if timestamp:
            # Normalize timestamp to 0-1 (assuming 24-hour range)
            normalized_time = (timestamp % 86400) / 86400.0
            embedding.append(normalized_time)
        else:
            embedding.append(0.0)
        
        # Pad to 768 dimensions (simple repetition for demo)
        while len(embedding) < 768:
            embedding.extend(embedding[:min(len(embedding), 768 - len(embedding))])
        
        return np.array(embedding[:768], dtype=np.float32)
    
    def cache_segment(self, segment: Dict[str, Any]) -> Optional[str]:
        """Cache a chat segment"""
        if not self._should_cache(segment):
            return None
        
        cache_key = self._get_cache_key(segment)
        
        # Store in KV cache
        self.kv_store.set(cache_key, segment)
        
        # Store in vector index for semantic search
        if self.enable_rag:
            features = self._extract_features(segment)
            embedding = self._create_vector_embedding(features)
            
            metadata = {
                'cache_key': cache_key,
                'segment_type': 'chat',
                'features': features
            }
            
            self.vector_index.add_vector(
                vector=embedding,
                metadata=metadata,
                vector_id=cache_key
            )
        
        # Update stats
        with self.stats_lock:
            self.stats['cache_size'] = self.kv_store.get_stats()['memory_size']
        
        return cache_key
    
    def get_segment(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get segment by cache key"""
        segment = self.kv_store.get(cache_key)
        hit = segment is not None
        self._update_stats(hit)
        return segment
    
    def find_similar_segments(self, 
                             query_segment: Dict[str, Any], 
                             k: int = 5) -> List[Tuple[str, float, Dict[str, Any]]]:
        """Find similar segments using vector search"""
        if not self.enable_rag:
            return []
        
        features = self._extract_features(query_segment)
        embedding = self._create_vector_embedding(features)
        
        similar_segments = self.vector_index.search_similar(
            query_vector=embedding,
            k=k,
            threshold=self.rag_similarity_threshold
        )
        
        return similar_segments
    
    def get_segment_with_rag_fallback(self, 
                                     query_segment: Dict[str, Any],
                                     k: int = 3) -> Optional[Dict[str, Any]]:
        """Get segment with RAG fallback for similar content"""
        
        # First try exact match
        cache_key = self._get_cache_key(query_segment)
        exact_match = self.get_segment(cache_key)
        if exact_match:
            return exact_match
        
        # Try RAG fallback
        if self.enable_rag:
            similar_segments = self.find_similar_segments(query_segment, k)
            
            for vector_id, similarity, metadata in similar_segments:
                cache_key = metadata.get('cache_key')
                if cache_key:
                    segment = self.get_segment(cache_key)
                    if segment:
                        return segment
        
        return None
    
    def flush(self):
        """Clear all caches"""
        self.kv_store.flush()
        if self.enable_rag:
            self.vector_index.flush()
        
        # Reset stats
        with self.stats_lock:
            self.stats = {
                'hits': 0,
                'misses': 0,
                'total_requests': 0,
                'cache_size': 0
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.stats_lock:
            stats = self.stats.copy()
            
            # Add hit rate
            if stats['total_requests'] > 0:
                stats['hit_rate'] = stats['hits'] / stats['total_requests']
            else:
                stats['hit_rate'] = 0.0
            
            # Add KV store stats
            kv_stats = self.kv_store.get_stats()
            stats.update(kv_stats)
            
            # Add vector index stats
            if self.enable_rag:
                vector_stats = self.vector_index.get_stats()
                stats['vector_index'] = vector_stats
            
            return stats
    
    def export_cache(self, output_file: str):
        """Export cache data"""
        export_data = {
            'stats': self.get_stats(),
            'vector_index_stats': self.vector_index.get_stats() if self.enable_rag else None
        }
        
        try:
            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Could not export cache: {e}")

class SegmentCacheManagerFactory:
    """Factory for creating segment cache managers with different configurations"""
    
    @staticmethod
    def create_default_manager() -> SegmentCacheManager:
        """Create default cache manager"""
        return SegmentCacheManager()
    
    @staticmethod
    def create_redis_manager(redis_config: Dict[str, Any]) -> SegmentCacheManager:
        """Create cache manager with Redis backend"""
        kv_store = MultiLayerKVStore(
            redis_config=redis_config,
            memory_cache_type="lru",
            memory_max_size=1000
        )
        return SegmentCacheManager(kv_store=kv_store)
    
    @staticmethod
    def create_high_performance_manager() -> SegmentCacheManager:
        """Create high-performance cache manager"""
        kv_store = MultiLayerKVStore(
            memory_cache_type="lfu",
            memory_max_size=5000,
            memory_ttl=3600  # 1 hour
        )
        return SegmentCacheManager(
            kv_store=kv_store,
            enable_rag=True,
            rag_similarity_threshold=0.7
        )
    
    @staticmethod
    def create_custom_manager(strategy: CacheStrategy,
                            kv_store: Optional[MultiLayerKVStore] = None,
                            vector_index: Optional[SemanticVectorIndex] = None) -> SegmentCacheManager:
        """Create custom cache manager"""
        return SegmentCacheManager(
            kv_store=kv_store,
            vector_index=vector_index,
            strategy=strategy
        )
