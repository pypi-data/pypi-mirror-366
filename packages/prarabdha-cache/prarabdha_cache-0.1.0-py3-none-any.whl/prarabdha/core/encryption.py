import base64
import hashlib
import os
from typing import Any, Dict, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import json
import pickle


class EncryptionManager:
    """Manages encryption and decryption of cache values."""
    
    def __init__(self, password: Optional[str] = None, key_file: Optional[str] = None):
        """
        Initialize encryption manager.
        
        Args:
            password: Password to derive encryption key
            key_file: Path to file containing encryption key
        """
        self.key = self._load_or_generate_key(password, key_file)
        self.cipher = Fernet(self.key)
    
    def _load_or_generate_key(self, password: Optional[str], key_file: Optional[str]) -> bytes:
        """Load existing key or generate new one."""
        if key_file and os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        
        if password:
            # Derive key from password
            salt = b'prarabdha_salt'  # In production, use random salt
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        else:
            # Generate random key
            key = Fernet.generate_key()
        
        # Save key to file if key_file is provided
        if key_file:
            os.makedirs(os.path.dirname(key_file), exist_ok=True)
            with open(key_file, 'wb') as f:
                f.write(key)
        
        return key
    
    def encrypt(self, data: Any) -> Dict[str, Any]:
        """Encrypt data and return encrypted format."""
        # Serialize data first
        if isinstance(data, (dict, list, str, int, float, bool)) or data is None:
            serialized = json.dumps(data, default=str)
        else:
            serialized = pickle.dumps(data)
        
        # Encrypt the serialized data
        encrypted_data = self.cipher.encrypt(serialized.encode('utf-8'))
        
        return {
            'data': base64.b64encode(encrypted_data).decode('utf-8'),
            'encrypted': True,
            'algorithm': 'AES-256',
            'original_size': len(serialized),
            'encrypted_size': len(encrypted_data)
        }
    
    def decrypt(self, encrypted_data: Dict[str, Any]) -> Any:
        """Decrypt data from encrypted format."""
        if not encrypted_data.get('encrypted', False):
            return encrypted_data['data']
        
        # Decrypt the data
        encrypted_bytes = base64.b64decode(encrypted_data['data'])
        decrypted_bytes = self.cipher.decrypt(encrypted_bytes)
        
        # Try to deserialize as JSON first, then pickle
        try:
            return json.loads(decrypted_bytes.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            try:
                return pickle.loads(decrypted_bytes)
            except:
                return decrypted_bytes.decode('utf-8')
    
    def get_key_hash(self) -> str:
        """Get hash of encryption key for verification."""
        return hashlib.sha256(self.key).hexdigest()[:16]
    
    def change_password(self, new_password: str, key_file: Optional[str] = None) -> None:
        """Change encryption password and regenerate key."""
        salt = b'prarabdha_salt'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        new_key = base64.urlsafe_b64encode(kdf.derive(new_password.encode()))
        
        self.key = new_key
        self.cipher = Fernet(self.key)
        
        if key_file:
            with open(key_file, 'wb') as f:
                f.write(self.key)


class EncryptedKVStore:
    """KV store wrapper that automatically encrypts values."""
    
    def __init__(self, kv_store, password: Optional[str] = None, key_file: Optional[str] = None):
        self.kv_store = kv_store
        self.encryption_manager = EncryptionManager(password, key_file)
    
    def set(self, key: str, value: Any, **kwargs) -> None:
        """Set encrypted value in underlying KV store."""
        encrypted_data = self.encryption_manager.encrypt(value)
        self.kv_store.set(key, encrypted_data, **kwargs)
    
    def get(self, key: str) -> Any:
        """Get and decrypt value from underlying KV store."""
        encrypted_data = self.kv_store.get(key)
        if encrypted_data is None:
            return None
        
        return self.encryption_manager.decrypt(encrypted_data)
    
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
        """Get statistics including encryption info."""
        stats = self.kv_store.get_stats() if hasattr(self.kv_store, 'get_stats') else {}
        stats['encrypted'] = True
        stats['key_hash'] = self.encryption_manager.get_key_hash()
        return stats


class SecureMultiLayerKVStore:
    """Multi-layer KV store with encryption and compression."""
    
    def __init__(self, memory_cache, disk_cache, redis_cache=None, 
                 password: Optional[str] = None, key_file: Optional[str] = None,
                 compression_type: str = 'gzip'):
        from .compression import CompressionType, CompressedKVStore
        
        # Create encrypted and compressed stores
        self.memory_cache = CompressedKVStore(
            EncryptedKVStore(memory_cache, password, key_file),
            CompressionType(compression_type)
        )
        
        self.disk_cache = CompressedKVStore(
            EncryptedKVStore(disk_cache, password, key_file),
            CompressionType(compression_type)
        )
        
        if redis_cache:
            self.redis_cache = CompressedKVStore(
                EncryptedKVStore(redis_cache, password, key_file),
                CompressionType(compression_type)
            )
        else:
            self.redis_cache = None
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """Set value in all layers with encryption and compression."""
        self.memory_cache.set(key, value)
        self.disk_cache.set(key, value)
        if self.redis_cache:
            self.redis_cache.set(key, value)
    
    def get(self, key: str) -> Any:
        """Get value from layers with decryption and decompression."""
        # Try memory first
        value = self.memory_cache.get(key)
        if value is not None:
            return value
        
        # Try disk
        value = self.disk_cache.get(key)
        if value is not None:
            self.memory_cache.set(key, value)  # Promote to memory
            return value
        
        # Try Redis
        if self.redis_cache:
            value = self.redis_cache.get(key)
            if value is not None:
                self.memory_cache.set(key, value)  # Promote to memory and disk
                self.disk_cache.set(key, value)
                return value
        
        return None
    
    def exists(self, key: str) -> bool:
        """Check if key exists in any layer."""
        return (self.memory_cache.exists(key) or 
                self.disk_cache.exists(key) or 
                (self.redis_cache and self.redis_cache.exists(key)))
    
    def delete(self, key: str) -> None:
        """Delete key from all layers."""
        self.memory_cache.delete(key)
        self.disk_cache.delete(key)
        if self.redis_cache:
            self.redis_cache.delete(key)
    
    def flush(self) -> None:
        """Flush all layers."""
        self.memory_cache.flush()
        self.disk_cache.flush()
        if self.redis_cache:
            self.redis_cache.flush()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics."""
        stats = {
            'memory': self.memory_cache.get_stats(),
            'disk': self.disk_cache.get_stats(),
        }
        
        if self.redis_cache:
            stats['redis'] = self.redis_cache.get_stats()
        
        return stats 