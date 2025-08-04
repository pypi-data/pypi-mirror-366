import sqlite3
import json
import threading
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import os


class MetadataStore:
    """Persistent metadata store using SQLite for cache metadata and TTL tracking."""
    
    def __init__(self, db_path: str = "prarabdha_metadata.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_database()
    
    def _init_database(self):
        """Initialize the SQLite database with required tables."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Cache metadata table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cache_metadata (
                    key TEXT PRIMARY KEY,
                    cache_type TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Vector mappings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vector_mappings (
                    vector_id TEXT PRIMARY KEY,
                    cache_key TEXT NOT NULL,
                    vector_type TEXT NOT NULL,
                    dimension INTEGER,
                    index_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (cache_key) REFERENCES cache_metadata (key)
                )
            ''')
            
            # RAG document mappings
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rag_mappings (
                    chunk_id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    chunk_index INTEGER,
                    content_hash TEXT,
                    vector_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (vector_id) REFERENCES vector_mappings (vector_id)
                )
            ''')
            
            # Create indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_expires_at ON cache_metadata (expires_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_cache_type ON cache_metadata (cache_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_document_id ON rag_mappings (document_id)')
            
            conn.commit()
            conn.close()
    
    def set_metadata(self, key: str, cache_type: str, metadata: Dict[str, Any], 
                    ttl_seconds: Optional[int] = None) -> None:
        """Store metadata for a cache entry."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            expires_at = None
            if ttl_seconds:
                expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
            
            cursor.execute('''
                INSERT OR REPLACE INTO cache_metadata 
                (key, cache_type, metadata, expires_at) 
                VALUES (?, ?, ?, ?)
            ''', (key, cache_type, json.dumps(metadata), expires_at))
            
            conn.commit()
            conn.close()
    
    def get_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve metadata for a cache entry."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT metadata, expires_at, access_count, last_accessed
                FROM cache_metadata WHERE key = ?
            ''', (key,))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return None
            
            metadata_str, expires_at, access_count, last_accessed = result
            
            # Check if expired
            if expires_at and datetime.fromisoformat(expires_at) < datetime.now():
                self.delete_metadata(key)
                return None
            
            # Update access statistics
            self._update_access_stats(key, access_count + 1)
            
            return {
                'metadata': json.loads(metadata_str) if metadata_str else {},
                'expires_at': expires_at,
                'access_count': access_count + 1,
                'last_accessed': last_accessed
            }
    
    def _update_access_stats(self, key: str, new_count: int) -> None:
        """Update access statistics for a cache entry."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE cache_metadata 
                SET access_count = ?, last_accessed = CURRENT_TIMESTAMP
                WHERE key = ?
            ''', (new_count, key))
            
            conn.commit()
            conn.close()
    
    def delete_metadata(self, key: str) -> None:
        """Delete metadata for a cache entry."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM cache_metadata WHERE key = ?', (key,))
            cursor.execute('DELETE FROM vector_mappings WHERE cache_key = ?', (key,))
            
            conn.commit()
            conn.close()
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count of cleaned entries."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM cache_metadata 
                WHERE expires_at IS NOT NULL AND expires_at < CURRENT_TIMESTAMP
            ''')
            
            cleaned_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            return cleaned_count
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive metadata statistics."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total entries by type
            cursor.execute('''
                SELECT cache_type, COUNT(*) 
                FROM cache_metadata 
                GROUP BY cache_type
            ''')
            type_counts = dict(cursor.fetchall())
            
            # Expired entries
            cursor.execute('''
                SELECT COUNT(*) 
                FROM cache_metadata 
                WHERE expires_at IS NOT NULL AND expires_at < CURRENT_TIMESTAMP
            ''')
            expired_count = cursor.fetchone()[0]
            
            # Total entries
            cursor.execute('SELECT COUNT(*) FROM cache_metadata')
            total_entries = cursor.fetchone()[0]
            
            # Vector mappings count
            cursor.execute('SELECT COUNT(*) FROM vector_mappings')
            vector_count = cursor.fetchone()[0]
            
            # RAG mappings count
            cursor.execute('SELECT COUNT(*) FROM rag_mappings')
            rag_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_entries': total_entries,
                'expired_entries': expired_count,
                'type_counts': type_counts,
                'vector_mappings': vector_count,
                'rag_mappings': rag_count
            }
    
    def export_metadata(self, export_path: str) -> None:
        """Export all metadata to JSON file."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all metadata
            cursor.execute('''
                SELECT key, cache_type, metadata, created_at, expires_at, 
                       access_count, last_accessed
                FROM cache_metadata
            ''')
            
            metadata_entries = []
            for row in cursor.fetchall():
                key, cache_type, metadata_str, created_at, expires_at, access_count, last_accessed = row
                metadata_entries.append({
                    'key': key,
                    'cache_type': cache_type,
                    'metadata': json.loads(metadata_str) if metadata_str else {},
                    'created_at': created_at,
                    'expires_at': expires_at,
                    'access_count': access_count,
                    'last_accessed': last_accessed
                })
            
            # Get vector mappings
            cursor.execute('''
                SELECT vector_id, cache_key, vector_type, dimension, index_type, created_at
                FROM vector_mappings
            ''')
            
            vector_mappings = []
            for row in cursor.fetchall():
                vector_id, cache_key, vector_type, dimension, index_type, created_at = row
                vector_mappings.append({
                    'vector_id': vector_id,
                    'cache_key': cache_key,
                    'vector_type': vector_type,
                    'dimension': dimension,
                    'index_type': index_type,
                    'created_at': created_at
                })
            
            conn.close()
            
            # Export to JSON
            export_data = {
                'metadata_entries': metadata_entries,
                'vector_mappings': vector_mappings,
                'export_timestamp': datetime.now().isoformat()
            }
            
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2)
    
    def import_metadata(self, import_path: str) -> int:
        """Import metadata from JSON file."""
        with open(import_path, 'r') as f:
            import_data = json.load(f)
        
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            imported_count = 0
            
            # Import metadata entries
            for entry in import_data.get('metadata_entries', []):
                cursor.execute('''
                    INSERT OR REPLACE INTO cache_metadata 
                    (key, cache_type, metadata, created_at, expires_at, access_count, last_accessed)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    entry['key'], entry['cache_type'], json.dumps(entry['metadata']),
                    entry['created_at'], entry['expires_at'], entry['access_count'], 
                    entry['last_accessed']
                ))
                imported_count += 1
            
            # Import vector mappings
            for mapping in import_data.get('vector_mappings', []):
                cursor.execute('''
                    INSERT OR REPLACE INTO vector_mappings 
                    (vector_id, cache_key, vector_type, dimension, index_type, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    mapping['vector_id'], mapping['cache_key'], mapping['vector_type'],
                    mapping['dimension'], mapping['index_type'], mapping['created_at']
                ))
            
            conn.commit()
            conn.close()
            
            return imported_count 