import unittest
import tempfile
import shutil
import time
from pathlib import Path

from ..core.kv_store import LRUCache, LFUCache, DiskKVStore, MultiLayerKVStore

class TestLRUCache(unittest.TestCase):
    """Test LRU cache functionality"""
    
    def setUp(self):
        self.cache = LRUCache(max_size=3, ttl_seconds=1)
    
    def test_basic_operations(self):
        """Test basic get/set operations"""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        
        self.assertEqual(self.cache.get("key1"), "value1")
        self.assertEqual(self.cache.get("key2"), "value2")
        self.assertIsNone(self.cache.get("key3"))
    
    def test_lru_eviction(self):
        """Test LRU eviction policy"""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        self.cache.set("key3", "value3")
        self.cache.set("key4", "value4")  # Should evict key1
        
        self.assertIsNone(self.cache.get("key1"))
        self.assertEqual(self.cache.get("key2"), "value2")
        self.assertEqual(self.cache.get("key3"), "value3")
        self.assertEqual(self.cache.get("key4"), "value4")
    
    def test_ttl_expiration(self):
        """Test TTL expiration"""
        self.cache.set("key1", "value1")
        time.sleep(1.1)  # Wait for TTL to expire
        
        self.assertIsNone(self.cache.get("key1"))
    
    def test_flush(self):
        """Test cache flush"""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        
        self.cache.flush()
        
        self.assertIsNone(self.cache.get("key1"))
        self.assertIsNone(self.cache.get("key2"))
        self.assertEqual(self.cache.size(), 0)

class TestLFUCache(unittest.TestCase):
    """Test LFU cache functionality"""
    
    def setUp(self):
        self.cache = LFUCache(max_size=3, ttl_seconds=1)
    
    def test_lfu_eviction(self):
        """Test LFU eviction policy"""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        self.cache.set("key3", "value3")
        
        # Access key1 multiple times to increase its frequency
        self.cache.get("key1")
        self.cache.get("key1")
        self.cache.get("key1")
        
        # Access key2 once
        self.cache.get("key2")
        
        # Add new key, should evict key3 (least frequently used)
        self.cache.set("key4", "value4")
        
        self.assertIsNone(self.cache.get("key3"))
        self.assertEqual(self.cache.get("key1"), "value1")
        self.assertEqual(self.cache.get("key2"), "value2")
        self.assertEqual(self.cache.get("key4"), "value4")

class TestDiskKVStore(unittest.TestCase):
    """Test disk-based KV store"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.cache = DiskKVStore(cache_dir=self.temp_dir, ttl_seconds=1)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_basic_operations(self):
        """Test basic get/set operations"""
        self.cache.set("key1", "value1")
        self.cache.set("key2", {"nested": "value"})
        
        self.assertEqual(self.cache.get("key1"), "value1")
        self.assertEqual(self.cache.get("key2"), {"nested": "value"})
        self.assertIsNone(self.cache.get("key3"))
    
    def test_ttl_expiration(self):
        """Test TTL expiration"""
        self.cache.set("key1", "value1")
        time.sleep(1.1)  # Wait for TTL to expire
        
        self.assertIsNone(self.cache.get("key1"))
    
    def test_flush(self):
        """Test cache flush"""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        
        self.cache.flush()
        
        self.assertIsNone(self.cache.get("key1"))
        self.assertIsNone(self.cache.get("key2"))

class TestMultiLayerKVStore(unittest.TestCase):
    """Test multi-layer KV store"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.cache = MultiLayerKVStore(
            memory_cache_type="lru",
            memory_max_size=2,
            disk_cache_dir=self.temp_dir
        )
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_multi_layer_operations(self):
        """Test operations across memory and disk layers"""
        # Set values
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        self.cache.set("key3", "value3")  # Should go to disk
        
        # All should be retrievable
        self.assertEqual(self.cache.get("key1"), "value1")
        self.assertEqual(self.cache.get("key2"), "value2")
        self.assertEqual(self.cache.get("key3"), "value3")
    
    def test_promotion(self):
        """Test promotion from disk to memory"""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        self.cache.set("key3", "value3")  # Goes to disk
        
        # Access key3, should promote to memory
        self.assertEqual(self.cache.get("key3"), "value3")
        
        # Check stats
        stats = self.cache.get_stats()
        self.assertGreaterEqual(stats['memory_size'], 1)
        self.assertGreaterEqual(stats['disk_size'], 0)
    
    def test_flush(self):
        """Test flushing all layers"""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        
        self.cache.flush()
        
        self.assertIsNone(self.cache.get("key1"))
        self.assertIsNone(self.cache.get("key2"))

if __name__ == "__main__":
    unittest.main()
