import gzip
import lzma
import zlib
import pickle
import json
from typing import Any, Dict, Optional, Union
from enum import Enum
import base64


class CompressionType(Enum):
    """Supported compression types."""
    NONE = "none"
    GZIP = "gzip"
    LZMA = "lzma"
    ZLIB = "zlib"
    BASE64 = "base64"


class CompressionManager:
    """Manages compression and decompression of cache values."""
    
    def __init__(self, default_compression: CompressionType = CompressionType.GZIP):
        self.default_compression = default_compression
    
    def compress(self, data: Any, compression_type: Optional[CompressionType] = None) -> Dict[str, Any]:
        """Compress data using specified compression type."""
        compression_type = compression_type or self.default_compression
        
        if compression_type == CompressionType.NONE:
            return {
                'data': data,
                'compression': 'none',
                'compressed': False
            }
        
        # Serialize data first
        if isinstance(data, (dict, list, str, int, float, bool)) or data is None:
            serialized = json.dumps(data, default=str)
        else:
            serialized = pickle.dumps(data)
        
        compressed_data = None
        compression_method = None
        
        if compression_type == CompressionType.GZIP:
            compressed_data = gzip.compress(serialized.encode('utf-8'))
            compression_method = 'gzip'
        elif compression_type == CompressionType.LZMA:
            compressed_data = lzma.compress(serialized.encode('utf-8'))
            compression_method = 'lzma'
        elif compression_type == CompressionType.ZLIB:
            compressed_data = zlib.compress(serialized.encode('utf-8'))
            compression_method = 'zlib'
        elif compression_type == CompressionType.BASE64:
            compressed_data = base64.b64encode(serialized.encode('utf-8'))
            compression_method = 'base64'
        
        return {
            'data': base64.b64encode(compressed_data).decode('utf-8'),
            'compression': compression_method,
            'compressed': True,
            'original_size': len(serialized),
            'compressed_size': len(compressed_data)
        }
    
    def decompress(self, compressed_data: Dict[str, Any]) -> Any:
        """Decompress data from compressed format."""
        if not compressed_data.get('compressed', False):
            return compressed_data['data']
        
        compression_method = compressed_data['compression']
        data_bytes = base64.b64decode(compressed_data['data'])
        
        if compression_method == 'gzip':
            decompressed = gzip.decompress(data_bytes)
        elif compression_method == 'lzma':
            decompressed = lzma.decompress(data_bytes)
        elif compression_method == 'zlib':
            decompressed = zlib.decompress(data_bytes)
        elif compression_method == 'base64':
            decompressed = data_bytes
        else:
            raise ValueError(f"Unsupported compression method: {compression_method}")
        
        # Try to deserialize as JSON first, then pickle
        try:
            return json.loads(decompressed.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            try:
                return pickle.loads(decompressed)
            except:
                return decompressed.decode('utf-8')
    
    def get_compression_ratio(self, original_size: int, compressed_size: int) -> float:
        """Calculate compression ratio (0.0 = no compression, 1.0 = maximum compression)."""
        if original_size == 0:
            return 0.0
        return 1.0 - (compressed_size / original_size)
    
    def estimate_compression_savings(self, data: Any) -> Dict[str, Union[int, float]]:
        """Estimate compression savings for different methods."""
        serialized = json.dumps(data, default=str).encode('utf-8')
        original_size = len(serialized)
        
        results = {}
        
        for compression_type in CompressionType:
            if compression_type == CompressionType.NONE:
                results[compression_type.value] = {
                    'size': original_size,
                    'ratio': 0.0
                }
                continue
            
            try:
                compressed = self.compress(data, compression_type)
                compressed_size = compressed['compressed_size']
                ratio = self.get_compression_ratio(original_size, compressed_size)
                
                results[compression_type.value] = {
                    'size': compressed_size,
                    'ratio': ratio
                }
            except Exception:
                results[compression_type.value] = {
                    'size': original_size,
                    'ratio': 0.0
                }
        
        return results


class CompressedKVStore:
    """KV store wrapper that automatically compresses values."""
    
    def __init__(self, kv_store, compression_type: CompressionType = CompressionType.GZIP):
        self.kv_store = kv_store
        self.compression_manager = CompressionManager(compression_type)
    
    def set(self, key: str, value: Any, **kwargs) -> None:
        """Set compressed value in underlying KV store."""
        compressed_data = self.compression_manager.compress(value)
        self.kv_store.set(key, compressed_data, **kwargs)
    
    def get(self, key: str) -> Any:
        """Get and decompress value from underlying KV store."""
        compressed_data = self.kv_store.get(key)
        if compressed_data is None:
            return None
        
        return self.compression_manager.decompress(compressed_data)
    
    def exists(self, key: str) -> bool:
        """Check if key exists in underlying KV store."""
        return self.kv_store.exists(key)
    
    def delete(self, key: str) -> None:
        """Delete key from underlying KV store."""
        self.kv_store.delete(key)
    
    def flush(self) -> None:
        """Flush underlying KV store."""
        self.kv_store.flush()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics including compression info."""
        stats = self.kv_store.get_stats() if hasattr(self.kv_store, 'get_stats') else {}
        stats['compression_type'] = self.compression_manager.default_compression.value
        return stats 