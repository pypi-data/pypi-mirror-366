"""
AI Helper Agent - Secure Local File and Session Caching System
Requirement #6: Enhanced encrypted user history, FAISS cache, and secret management
"""

import os
import json
import hashlib
import sqlite3
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import gzip
import pickle
import struct

try:
    import faiss
    import numpy as np
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    np = None

try:
    from langchain_community.vectorstores import FAISS as LangchainFAISS
    from langchain_ollama import OllamaEmbeddings
    OLLAMA_EMBEDDINGS_AVAILABLE = True
except ImportError:
    try:
        from langchain_community.embeddings import OllamaEmbeddings
        from langchain_community.vectorstores import FAISS as LangchainFAISS
        OLLAMA_EMBEDDINGS_AVAILABLE = True
    except ImportError:
        OllamaEmbeddings = None
        LangchainFAISS = None
        OLLAMA_EMBEDDINGS_AVAILABLE = False

import structlog

# Configure logger to not show debug messages in CLI
logger = structlog.get_logger()
# Set logger level to WARNING to hide debug messages
logger = logger.bind(level="WARNING")


class SecretManager:
    """Enhanced secret management with multiple encryption layers"""
    
    def __init__(self, user_dir: Path):
        self.user_dir = user_dir
        self.secrets_dir = user_dir / ".secrets"
        self.secrets_dir.mkdir(mode=0o700, exist_ok=True)
        self.master_key_file = self.secrets_dir / ".master_key"
        self.salt_file = self.secrets_dir / ".salt"
        self._master_key = None
        self._lock = threading.Lock()
    
    def _generate_salt(self) -> bytes:
        """Generate or load salt for key derivation"""
        if self.salt_file.exists():
            with open(self.salt_file, 'rb') as f:
                return f.read()
        else:
            salt = os.urandom(32)
            with open(self.salt_file, 'wb') as f:
                f.write(salt)
            if os.name == 'nt':  # Windows
                try:
                    import ctypes
                    ctypes.windll.kernel32.SetFileAttributesW(str(self.salt_file), 2)
                except:
                    pass
            else:  # Unix-like
                self.salt_file.chmod(0o600)
            return salt
    
    def _derive_key(self, password: bytes, salt: bytes) -> bytes:
        """Derive encryption key from password and salt"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password))
    
    def get_master_key(self, password: str = None) -> bytes:
        """Get or create master encryption key"""
        with self._lock:
            if self._master_key:
                return self._master_key
            
            if self.master_key_file.exists():
                # Load existing key
                if password:
                    salt = self._generate_salt()
                    key = self._derive_key(password.encode(), salt)
                    try:
                        with open(self.master_key_file, 'rb') as f:
                            encrypted_key = f.read()
                        f = Fernet(key)
                        self._master_key = f.decrypt(encrypted_key)
                        return self._master_key
                    except Exception:
                        logger.error("Invalid password for master key")
                        raise ValueError("Invalid password")
                else:
                    # Use default key (for backward compatibility)
                    with open(self.master_key_file, 'rb') as f:
                        self._master_key = f.read()
                    return self._master_key
            else:
                # Generate new key
                self._master_key = Fernet.generate_key()
                
                if password:
                    # Encrypt with password
                    salt = self._generate_salt()
                    key = self._derive_key(password.encode(), salt)
                    f = Fernet(key)
                    encrypted_key = f.encrypt(self._master_key)
                    with open(self.master_key_file, 'wb') as f:
                        f.write(encrypted_key)
                else:
                    # Store unencrypted (for backward compatibility)
                    with open(self.master_key_file, 'wb') as f:
                        f.write(self._master_key)
                
                # Set strict permissions
                if os.name == 'nt':  # Windows
                    try:
                        import ctypes
                        ctypes.windll.kernel32.SetFileAttributesW(str(self.master_key_file), 2)
                    except:
                        pass
                else:  # Unix-like
                    self.master_key_file.chmod(0o600)
                
                return self._master_key
    
    def encrypt_data(self, data: Union[str, bytes, Dict, List], compression: bool = True) -> bytes:
        """Encrypt any type of data with optional compression"""
        try:
            # Convert to bytes
            if isinstance(data, (dict, list)):
                data_bytes = json.dumps(data).encode('utf-8')
            elif isinstance(data, str):
                data_bytes = data.encode('utf-8')
            else:
                data_bytes = data
            
            # Compress if requested
            if compression:
                data_bytes = gzip.compress(data_bytes)
                prefix = b'GZIP'
            else:
                prefix = b'RAW '
            
            # Encrypt
            fernet = Fernet(self.get_master_key())
            encrypted_data = fernet.encrypt(data_bytes)
            
            # Add prefix to indicate compression
            return prefix + encrypted_data
            
        except Exception as e:
            logger.error("Encryption failed", error=str(e))
            raise
    
    def decrypt_data(self, encrypted_data: bytes, return_type: str = 'auto') -> Any:
        """Decrypt data and return in specified format"""
        try:
            # Check prefix
            prefix = encrypted_data[:4]
            compressed = prefix == b'GZIP'
            encrypted_bytes = encrypted_data[4:]
            
            # Decrypt
            fernet = Fernet(self.get_master_key())
            data_bytes = fernet.decrypt(encrypted_bytes)
            
            # Decompress if needed
            if compressed:
                data_bytes = gzip.decompress(data_bytes)
            
            # Convert to requested type
            if return_type == 'bytes':
                return data_bytes
            elif return_type == 'str':
                return data_bytes.decode('utf-8')
            elif return_type == 'json':
                return json.loads(data_bytes.decode('utf-8'))
            else:  # auto
                try:
                    # Try JSON first
                    return json.loads(data_bytes.decode('utf-8'))
                except:
                    # Fall back to string
                    return data_bytes.decode('utf-8')
                    
        except Exception as e:
            logger.error("Decryption failed", error=str(e))
            raise


class EncryptedCache:
    """High-performance encrypted cache with TTL support"""
    
    def __init__(self, cache_dir: Path, secret_manager: SecretManager):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.secret_manager = secret_manager
        self.db_path = cache_dir / "cache.db"
        self._init_database()
        self._lock = threading.Lock()
    
    def _init_database(self):
        """Initialize cache database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache_entries (
                key TEXT PRIMARY KEY,
                value BLOB,
                created_at TIMESTAMP,
                expires_at TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                last_accessed TIMESTAMP,
                data_type TEXT,
                compressed BOOLEAN DEFAULT 1
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_expires_at ON cache_entries(expires_at)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_last_accessed ON cache_entries(last_accessed)
        ''')
        
        conn.commit()
        conn.close()
    
    def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> bool:
        """Set cached value with TTL"""
        try:
            with self._lock:
                # Encrypt value
                encrypted_value = self.secret_manager.encrypt_data(value)
                
                # Calculate expiration
                now = datetime.now()
                expires_at = now + timedelta(seconds=ttl_seconds)
                
                # Store in database
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO cache_entries
                    (key, value, created_at, expires_at, last_accessed, data_type, compressed)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    key,
                    encrypted_value,
                    now.isoformat(),
                    expires_at.isoformat(),
                    now.isoformat(),
                    type(value).__name__,
                    True
                ))
                
                conn.commit()
                conn.close()
                
                logger.debug("Cache entry set", key=key, expires_at=expires_at.isoformat())
                # Suppress debug messages in CLI
                # print(f"🔒 Cache entry set: {key}")
                return True
                
        except Exception as e:
            logger.error("Failed to set cache entry", key=key, error=str(e))
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT value, expires_at, access_count
                    FROM cache_entries
                    WHERE key = ?
                ''', (key,))
                
                result = cursor.fetchone()
                if not result:
                    conn.close()
                    return None
                
                encrypted_value, expires_at_str, access_count = result
                
                # Check expiration
                expires_at = datetime.fromisoformat(expires_at_str)
                if datetime.now() > expires_at:
                    # Remove expired entry
                    cursor.execute('DELETE FROM cache_entries WHERE key = ?', (key,))
                    conn.commit()
                    conn.close()
                    logger.debug("Cache entry expired", key=key)
                    return None
                
                # Update access statistics
                cursor.execute('''
                    UPDATE cache_entries 
                    SET access_count = ?, last_accessed = ?
                    WHERE key = ?
                ''', (access_count + 1, datetime.now().isoformat(), key))
                
                conn.commit()
                conn.close()
                
                # Decrypt and return
                value = self.secret_manager.decrypt_data(encrypted_value)
                logger.debug("Cache hit", key=key)
                return value
                
        except Exception as e:
            logger.error("Failed to get cache entry", key=key, error=str(e))
            return None
    
    def delete(self, key: str) -> bool:
        """Delete cached value"""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM cache_entries WHERE key = ?', (key,))
                deleted = cursor.rowcount > 0
                
                conn.commit()
                conn.close()
                
                if deleted:
                    logger.debug("Cache entry deleted", key=key)
                
                return deleted
                
        except Exception as e:
            logger.error("Failed to delete cache entry", key=key, error=str(e))
            return False
    
    def cleanup_expired(self) -> int:
        """Remove expired entries"""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    DELETE FROM cache_entries 
                    WHERE expires_at < ?
                ''', (datetime.now().isoformat(),))
                
                deleted_count = cursor.rowcount
                conn.commit()
                conn.close()
                
                if deleted_count > 0:
                    logger.info("Expired cache entries cleaned up", count=deleted_count)
                
                return deleted_count
                
        except Exception as e:
            logger.error("Failed to cleanup expired cache entries", error=str(e))
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM cache_entries')
            total_entries = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM cache_entries WHERE expires_at < ?', 
                         (datetime.now().isoformat(),))
            expired_entries = cursor.fetchone()[0]
            
            cursor.execute('SELECT SUM(access_count) FROM cache_entries')
            total_accesses = cursor.fetchone()[0] or 0
            
            cursor.execute('SELECT AVG(access_count) FROM cache_entries')
            avg_accesses = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                'total_entries': total_entries,
                'expired_entries': expired_entries,
                'active_entries': total_entries - expired_entries,
                'total_accesses': total_accesses,
                'average_accesses': round(avg_accesses, 2)
            }
            
        except Exception as e:
            logger.error("Failed to get cache stats", error=str(e))
            return {}


class SecureVectorStore:
    """Encrypted FAISS vector store with secure persistence"""
    
    def __init__(self, vector_dir: Path, secret_manager: SecretManager, 
                 embeddings_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.vector_dir = vector_dir
        self.vector_dir.mkdir(parents=True, exist_ok=True)
        self.secret_manager = secret_manager
        self.embeddings_model = embeddings_model
        
        # FAST STARTUP: Skip embeddings initialization for better performance
        print("⚡ SecureVectorStore: Skipping embeddings for faster startup")
        self.embeddings = None
        
        # FAISS paths
        self.faiss_index_path = vector_dir / "faiss_index.encrypted"
        self.faiss_metadata_path = vector_dir / "faiss_metadata.encrypted"
        
        self.vector_store = None
        self.metadata_store = []
        self._lock = threading.Lock()
        
        # Skip loading existing index for performance
        print("⚡ SecureVectorStore: Skipping index loading for faster startup")
    
    def _load_encrypted_index(self):
        """Load encrypted FAISS index"""
        if not FAISS_AVAILABLE or not self.embeddings:
            logger.warning("FAISS or embeddings not available")
            return
        
        try:
            if self.faiss_index_path.exists() and self.faiss_metadata_path.exists():
                with self._lock:
                    # Load encrypted index
                    with open(self.faiss_index_path, 'rb') as f:
                        encrypted_index = f.read()
                    
                    index_bytes = self.secret_manager.decrypt_data(encrypted_index, 'bytes')
                    
                    # Load encrypted metadata
                    with open(self.faiss_metadata_path, 'rb') as f:
                        encrypted_metadata = f.read()
                    
                    self.metadata_store = self.secret_manager.decrypt_data(encrypted_metadata, 'json')
                    
                    # Recreate FAISS index
                    if index_bytes:
                        # Create temporary file for FAISS
                        temp_index_path = self.vector_dir / "temp_index"
                        with open(temp_index_path, 'wb') as f:
                            f.write(index_bytes)
                        
                        # Load FAISS index
                        index = faiss.read_index(str(temp_index_path))
                        
                        # Create LangChain FAISS wrapper
                        if self.metadata_store:
                            texts = [meta.get('text', '') for meta in self.metadata_store]
                            metadatas = [meta.get('metadata', {}) for meta in self.metadata_store]
                            
                            self.vector_store = LangchainFAISS.from_texts(
                                texts, self.embeddings, metadatas=metadatas
                            )
                            # Replace index
                            self.vector_store.index = index
                        
                        # Clean up temp file
                        temp_index_path.unlink()
                        
                        logger.info("Encrypted FAISS index loaded successfully")
            
            else:
                # Create new index
                self._create_empty_index()
                
        except Exception as e:
            logger.error("Failed to load encrypted FAISS index", error=str(e))
            self._create_empty_index()
    
    def _create_empty_index(self):
        """Create empty FAISS index"""
        if not FAISS_AVAILABLE or not self.embeddings:
            return
        
        try:
            with self._lock:
                # Create empty index with initial text
                texts = ["Initial setup"]
                metadatas = [{"type": "setup", "timestamp": datetime.now().isoformat()}]
                
                self.vector_store = LangchainFAISS.from_texts(
                    texts, self.embeddings, metadatas=metadatas
                )
                
                self.metadata_store = [{
                    'text': texts[0],
                    'metadata': metadatas[0]
                }]
                
                # Save immediately
                self._save_encrypted_index()
                
                logger.info("Empty encrypted FAISS index created")
                
        except Exception as e:
            logger.error("Failed to create empty FAISS index", error=str(e))
    
    def _save_encrypted_index(self):
        """Save encrypted FAISS index"""
        if not self.vector_store:
            return
        
        try:
            with self._lock:
                # Save FAISS index to temporary file
                temp_index_path = self.vector_dir / "temp_save"
                faiss.write_index(self.vector_store.index, str(temp_index_path))
                
                # Read and encrypt index
                with open(temp_index_path, 'rb') as f:
                    index_bytes = f.read()
                
                encrypted_index = self.secret_manager.encrypt_data(index_bytes)
                
                # Save encrypted index
                with open(self.faiss_index_path, 'wb') as f:
                    f.write(encrypted_index)
                
                # Encrypt and save metadata
                encrypted_metadata = self.secret_manager.encrypt_data(self.metadata_store)
                
                with open(self.faiss_metadata_path, 'wb') as f:
                    f.write(encrypted_metadata)
                
                # Clean up temp file
                temp_index_path.unlink()
                
                logger.debug("Encrypted FAISS index saved")
                
        except Exception as e:
            logger.error("Failed to save encrypted FAISS index", error=str(e))
    
    def add_texts(self, texts: List[str], metadatas: List[Dict] = None) -> bool:
        """Add texts to encrypted vector store"""
        if not self.vector_store or not texts:
            return False
        
        try:
            with self._lock:
                if metadatas is None:
                    metadatas = [{}] * len(texts)
                
                # Add to vector store
                self.vector_store.add_texts(texts, metadatas=metadatas)
                
                # Update metadata store
                for text, metadata in zip(texts, metadatas):
                    self.metadata_store.append({
                        'text': text,
                        'metadata': {
                            **metadata,
                            'timestamp': datetime.now().isoformat()
                        }
                    })
                
                # Save encrypted index
                self._save_encrypted_index()
                
                logger.debug("Texts added to encrypted vector store", count=len(texts))
                return True
                
        except Exception as e:
            logger.error("Failed to add texts to vector store", error=str(e))
            return False
    
    def similarity_search(self, query: str, k: int = 5) -> List[Dict]:
        """Search similar texts in encrypted vector store"""
        if not self.vector_store:
            return []
        
        try:
            with self._lock:
                results = self.vector_store.similarity_search_with_score(query, k=k)
                
                search_results = []
                for doc, score in results:
                    search_results.append({
                        'text': doc.page_content,
                        'metadata': doc.metadata,
                        'similarity_score': float(score)
                    })
                
                logger.debug("Vector similarity search completed", 
                           query_length=len(query), results_count=len(search_results))
                
                return search_results
                
        except Exception as e:
            logger.error("Vector similarity search failed", error=str(e))
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        try:
            stats = {
                'total_vectors': len(self.metadata_store) if self.metadata_store else 0,
                'index_exists': self.vector_store is not None,
                'embeddings_model': self.embeddings_model,
                'encrypted': True
            }
            
            if self.vector_store and hasattr(self.vector_store, 'index'):
                stats['index_size'] = self.vector_store.index.ntotal
            
            return stats
            
        except Exception as e:
            logger.error("Failed to get vector store stats", error=str(e))
            return {}


class SecureCacheManager:
    """Main secure cache management system"""
    
    def __init__(self, user_dir: Path, password: str = None):
        self.user_dir = user_dir
        self.cache_dir = user_dir / ".cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.secret_manager = SecretManager(user_dir)
        if password:
            self.secret_manager.get_master_key(password)
        
        self.cache = EncryptedCache(self.cache_dir, self.secret_manager)
        self.vector_store = SecureVectorStore(
            self.cache_dir / "vectors", self.secret_manager
        )
        
        logger.info("Secure cache manager initialized", user_dir=str(user_dir))
    
    def cache_conversation(self, session_id: str, role: str, content: str, 
                          metadata: Dict = None) -> bool:
        """Cache conversation with encryption and vector indexing"""
        try:
            # Cache in encrypted storage
            cache_key = f"conversation:{session_id}:{datetime.now().isoformat()}"
            conversation_data = {
                'session_id': session_id,
                'role': role,
                'content': content,
                'metadata': metadata or {},
                'timestamp': datetime.now().isoformat()
            }
            
            # Cache with 30-day TTL
            self.cache.set(cache_key, conversation_data, ttl_seconds=30*24*3600)
            
            # Add to vector store for semantic search
            if len(content.strip()) > 10:
                vector_metadata = {
                    'session_id': session_id,
                    'role': role,
                    'cache_key': cache_key,
                    **(metadata or {})
                }
                
                self.vector_store.add_texts([content], [vector_metadata])
            
            logger.debug("Conversation cached securely", 
                       session_id=session_id, role=role)
            # Suppress debug output in CLI
            # print(f"🔒 Conversation cached: {session_id}")
            return True
            
        except Exception as e:
            logger.error("Failed to cache conversation", error=str(e))
            return False
    
    def search_conversations(self, query: str, session_id: str = None, 
                           limit: int = 5) -> List[Dict]:
        """Search cached conversations"""
        try:
            # Vector-based semantic search
            results = self.vector_store.similarity_search(query, k=limit*2)
            
            # Filter by session if specified
            if session_id:
                results = [r for r in results 
                          if r.get('metadata', {}).get('session_id') == session_id]
            
            # Limit results
            results = results[:limit]
            
            # Enrich with full conversation data from cache
            enriched_results = []
            for result in results:
                cache_key = result.get('metadata', {}).get('cache_key')
                if cache_key:
                    full_data = self.cache.get(cache_key)
                    if full_data:
                        enriched_results.append({
                            **result,
                            'full_conversation': full_data
                        })
                    else:
                        enriched_results.append(result)
                else:
                    enriched_results.append(result)
            
            logger.debug("Conversation search completed", 
                       query_length=len(query), results_count=len(enriched_results))
            
            return enriched_results
            
        except Exception as e:
            logger.error("Conversation search failed", error=str(e))
            return []
    
    def cache_file_content(self, file_path: str, content: Union[str, bytes], 
                          ttl_seconds: int = 24*3600) -> bool:
        """Cache file content with encryption"""
        try:
            cache_key = f"file:{hashlib.sha256(file_path.encode()).hexdigest()}"
            
            file_data = {
                'file_path': file_path,
                'content': content,
                'cached_at': datetime.now().isoformat(),
                'file_size': len(content) if isinstance(content, (str, bytes)) else 0
            }
            
            return self.cache.set(cache_key, file_data, ttl_seconds)
            
        except Exception as e:
            logger.error("Failed to cache file content", file_path=file_path, error=str(e))
            return False
    
    def get_cached_file(self, file_path: str) -> Optional[Dict]:
        """Get cached file content"""
        try:
            cache_key = f"file:{hashlib.sha256(file_path.encode()).hexdigest()}"
            return self.cache.get(cache_key)
            
        except Exception as e:
            logger.error("Failed to get cached file", file_path=file_path, error=str(e))
            return None
    
    def cleanup(self) -> Dict[str, int]:
        """Cleanup expired cache entries"""
        try:
            cache_cleaned = self.cache.cleanup_expired()
            
            return {
                'cache_entries_cleaned': cache_cleaned,
                'total_cleaned': cache_cleaned
            }
            
        except Exception as e:
            logger.error("Cache cleanup failed", error=str(e))
            return {'error': str(e)}
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        try:
            cache_stats = self.cache.get_stats()
            vector_stats = self.vector_store.get_stats()
            
            return {
                'cache': cache_stats,
                'vector_store': vector_stats,
                'security': {
                    'encryption_enabled': True,
                    'master_key_protected': self.secret_manager._master_key is not None,
                    'cache_directory': str(self.cache_dir)
                }
            }
            
        except Exception as e:
            logger.error("Failed to get system stats", error=str(e))
            return {'error': str(e)}


# Factory function for easy integration
def create_secure_cache(user_dir: Union[str, Path], password: str = None) -> SecureCacheManager:
    """Create secure cache manager for a user"""
    if isinstance(user_dir, str):
        user_dir = Path(user_dir)
    
    return SecureCacheManager(user_dir, password)
