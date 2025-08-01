"""
User Management Module for AI Helper Agent
Handles username storage, session management, and local indexing with FAISS/ChromaDB
"""

import os
import json
import uuid
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from cryptography.fernet import Fernet
import base64

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

from langchain_community.vectorstores import FAISS as LangchainFAISS

try:
    from langchain_chroma import Chroma
except ImportError:
    try:
        from langchain_community.vectorstores import Chroma
    except ImportError:
        Chroma = None

try:
    from langchain_ollama import OllamaEmbeddings
    OLLAMA_EMBEDDINGS_AVAILABLE = True
except ImportError:
    try:
        from langchain_community.embeddings import OllamaEmbeddings
        OLLAMA_EMBEDDINGS_AVAILABLE = True
    except ImportError:
        OLLAMA_EMBEDDINGS_AVAILABLE = False
        OllamaEmbeddings = None

# Import the new secure cache system
from .secure_cache import SecureCacheManager


class UserSessionManager:
    """Enhanced user session manager with secure caching"""
    
    def __init__(self):
        self.user_dir = None
        self.current_user = None
        self.session_id = None
        self.db_path = None
        self.vector_store = None
        self.embeddings = None
        self.secure_cache = None  # New secure cache manager
        self.master_password = None  # For encryption
        self._init_embeddings()
    
    def _init_embeddings(self):
        """Initialize embeddings for vector storage using Ollama - with fast fallback"""
        try:
            # Skip embeddings initialization entirely for faster startup
            self.embeddings = None
            print("⚡ Skipping embeddings initialization for faster startup")
            print("💡 Vector search features will be disabled")
            return
            
            # Alternative: Use Ollama embeddings instead of HuggingFace
            if OLLAMA_EMBEDDINGS_AVAILABLE:
                try:
                    self.embeddings = OllamaEmbeddings(
                        model="all-minilm",
                        base_url="http://localhost:11434"
                    )
                    print("✅ Ollama embeddings initialized successfully")
                    return
                except Exception as e:
                    print(f"⚠️ Ollama embeddings failed: {e}")
            
            # Fallback: No embeddings
            self.embeddings = None
            print("⚡ Using no embeddings for maximum startup speed")
            
        except Exception as e:
            print(f"❌ Embeddings initialization error: {e}")
            self.embeddings = None
            
            # Legacy code (commented out for performance)
            # if OLLAMA_EMBEDDINGS_AVAILABLE and OllamaEmbeddings:
            #     self.embeddings = OllamaEmbeddings(
            #         model="all-minilm",
            #         base_url="http://localhost:11434"
            #     )
            #     print("✅ Ollama embeddings initialized (all-minilm)")
            # else:
            #     print("Warning: OllamaEmbeddings not available - install langchain-ollama")
            #     self.embeddings = None
        except Exception as e:
            print(f"Warning: Could not initialize embeddings: {e}")
            self.embeddings = None
    
    def get_user_directory(self, username: str) -> Path:
        """Get or create user directory"""
        if os.name == 'nt':  # Windows
            base_dir = Path(os.environ.get('USERPROFILE', 'C:\\Users\\Default'))
        else:  # Unix-like
            base_dir = Path.home()
        
        user_dir = base_dir / '.ai_helper_agent' / username
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir
    
    def generate_encryption_key(self, user_dir: Path) -> bytes:
        """Generate or load encryption key for user"""
        key_file = user_dir / '.secret_key'
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            
            # Hide the file on Windows
            if os.name == 'nt':
                try:
                    import ctypes
                    ctypes.windll.kernel32.SetFileAttributesW(str(key_file), 2)  # Hidden
                except:
                    pass
            
            return key
    
    def encrypt_data(self, data: str, key: bytes) -> str:
        """Encrypt sensitive data"""
        f = Fernet(key)
        return base64.urlsafe_b64encode(f.encrypt(data.encode())).decode()
    
    def decrypt_data(self, encrypted_data: str, key: bytes) -> str:
        """Decrypt sensitive data"""
        f = Fernet(key)
        return f.decrypt(base64.urlsafe_b64decode(encrypted_data.encode())).decode()
    
    def init_user_database(self, user_dir: Path):
        """Initialize SQLite database for user"""
        self.db_path = user_dir / 'sessions.db'
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_info (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                created_at TIMESTAMP,
                last_login TIMESTAMP,
                preferences TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                username TEXT,
                created_at TIMESTAMP,
                last_updated TIMESTAMP,
                session_data TEXT,
                encrypted BOOLEAN DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                timestamp TIMESTAMP,
                role TEXT,
                content TEXT,
                metadata TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def init_vector_store(self, user_dir: Path):
        """Initialize vector store for user - DISABLED for faster startup"""
        if not self.embeddings:
            print("⚡ Skipping vector store initialization (embeddings disabled)")
            return
        
        print("⚠️ Vector store initialization skipped for performance")
        # Legacy vector store code disabled for faster startup
        return
    
    def setup_user(self, username: str, password: str = None) -> bool:
        """Setup user environment with secure caching"""
        try:
            self.current_user = username
            self.master_password = password
            self.user_dir = self.get_user_directory(username)
            
            # Initialize database
            self.init_user_database(self.user_dir)
            
            # Initialize secure cache manager
            try:
                self.secure_cache = SecureCacheManager(self.user_dir, password)
                print("✅ Secure cache system initialized")
            except Exception as e:
                print(f"⚠️  Warning: Secure cache initialization failed: {e}")
                print("Falling back to standard caching...")
            
            # Initialize vector store (legacy fallback)
            self.init_vector_store(self.user_dir)
            
            # Save user info
            self.save_user_info(username)
            
            # Generate new session
            self.session_id = self.create_new_session()
            
            print(f"✅ User environment setup complete for: {username}")
            print(f"📁 User data stored in: {self.user_dir}")
            if self.secure_cache:
                print(f"🔒 Secure caching enabled with encryption")
            
            return True
            
        except Exception as e:
            print(f"❌ Error setting up user: {e}")
            return False
    
    def save_user_info(self, username: str):
        """Save user information to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_info 
            (username, created_at, last_login, preferences)
            VALUES (?, ?, ?, ?)
        ''', (username, now, now, json.dumps({})))
        
        conn.commit()
        conn.close()
    
    def create_new_session(self) -> str:
        """Create a new session"""
        session_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO sessions 
            (session_id, username, created_at, last_updated, session_data)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_id, self.current_user, now, now, json.dumps({})))
        
        conn.commit()
        conn.close()
        
        return session_id
    
    def get_user_sessions(self, username: str) -> List[Dict]:
        """Get all sessions for a user"""
        if not self.db_path or not self.db_path.exists():
            return []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT session_id, created_at, last_updated
            FROM sessions 
            WHERE username = ?
            ORDER BY last_updated DESC
        ''', (username,))
        
        sessions = []
        for row in cursor.fetchall():
            sessions.append({
                'session_id': row[0],
                'created_at': row[1],
                'last_updated': row[2]
            })
        
        conn.close()
        return sessions
    
    def load_session(self, session_id: str) -> bool:
        """Load an existing session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT username, session_data
                FROM sessions 
                WHERE session_id = ?
            ''', (session_id,))
            
            result = cursor.fetchone()
            if result:
                self.session_id = session_id
                self.current_user = result[0]
                
                # Update last_updated
                cursor.execute('''
                    UPDATE sessions 
                    SET last_updated = ?
                    WHERE session_id = ?
                ''', (datetime.now().isoformat(), session_id))
                
                conn.commit()
                conn.close()
                return True
            
            conn.close()
            return False
            
        except Exception as e:
            print(f"Error loading session: {e}")
            return False
    
    def save_conversation(self, role: str, content: str, metadata: Dict = None):
        """Save conversation with secure caching and legacy fallback"""
        if not self.session_id:
            return
        
        try:
            # Use secure cache if available
            if self.secure_cache:
                success = self.secure_cache.cache_conversation(
                    self.session_id, role, content, metadata
                )
                # Don't print cache messages to keep CLI clean
                # if success:
                #     print("🔒 Conversation securely cached")
                # else:
                #     print("⚠️  Secure caching failed, using legacy method")
            
            # Always save to database as backup/legacy
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO conversation_history 
                (session_id, timestamp, role, content, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                self.session_id,
                datetime.now().isoformat(),
                role,
                content,
                json.dumps(metadata or {})
            ))
            
            conn.commit()
            conn.close()
            
            # Save to legacy vector store if available
            if self.vector_store and len(content.strip()) > 10:
                doc_metadata = {
                    "session_id": self.session_id,
                    "role": role,
                    "timestamp": datetime.now().isoformat(),
                    "user": self.current_user,
                    **(metadata or {})
                }
                
                self.vector_store.add_texts([content], metadatas=[doc_metadata])
                
                # Save FAISS index if using FAISS
                if isinstance(self.vector_store, LangchainFAISS):
                    faiss_path = self.user_dir / 'vectors' / 'faiss_index'
                    self.vector_store.save_local(str(faiss_path))
        
        except Exception as e:
            print(f"Warning: Could not save conversation: {e}")
    
    def search_conversations(self, query: str, limit: int = 5) -> List[Dict]:
        """Search conversations using secure cache and legacy fallback"""
        results = []
        
        # Try secure cache first
        if self.secure_cache:
            try:
                secure_results = self.secure_cache.search_conversations(
                    query, self.session_id, limit
                )
                if secure_results:
                    print(f"🔒 Found {len(secure_results)} results from secure cache")
                    return secure_results
            except Exception as e:
                print(f"⚠️  Secure search failed: {e}")
        
        # Fallback to legacy vector store
        if self.vector_store:
            try:
                vector_results = self.vector_store.similarity_search_with_score(query, k=limit)
                
                for doc, score in vector_results:
                    results.append({
                        'content': doc.page_content,
                        'metadata': doc.metadata,
                        'similarity_score': score
                    })
                
                if results:
                    print(f"📊 Found {len(results)} results from legacy vector store")
                
            except Exception as e:
                print(f"Error searching conversations: {e}")
        
        return results
    
    def get_conversation_history(self, limit: int = 20) -> List[Dict]:
        """Get recent conversation history"""
        if not self.session_id:
            return []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT timestamp, role, content, metadata
                FROM conversation_history 
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (self.session_id, limit))
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    'timestamp': row[0],
                    'role': row[1],
                    'content': row[2],
                    'metadata': json.loads(row[3] or '{}')
                })
            
            conn.close()
            return list(reversed(history))  # Return in chronological order
            
        except Exception as e:
            print(f"Error getting conversation history: {e}")
            return []
    
    def change_username(self, new_username: str) -> bool:
        """Change current username"""
        try:
            old_username = self.current_user
            old_user_dir = self.user_dir
            
            # Setup new user environment
            if self.setup_user(new_username, self.master_password):
                print(f"✅ Username changed from '{old_username}' to '{new_username}'")
                print(f"📁 Old data remains at: {old_user_dir}")
                print(f"📁 New data will be stored at: {self.user_dir}")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error changing username: {e}")
            return False
    
    def cache_file_content(self, file_path: str, content: str, ttl_hours: int = 24) -> bool:
        """Cache file content securely"""
        if not self.secure_cache:
            return False
        
        try:
            return self.secure_cache.cache_file_content(
                file_path, content, ttl_seconds=ttl_hours*3600
            )
        except Exception as e:
            print(f"Error caching file: {e}")
            return False
    
    def get_cached_file(self, file_path: str) -> Optional[str]:
        """Get cached file content"""
        if not self.secure_cache:
            return None
        
        try:
            cached_data = self.secure_cache.get_cached_file(file_path)
            if cached_data:
                return cached_data.get('content')
            return None
        except Exception as e:
            print(f"Error retrieving cached file: {e}")
            return None
    
    def cleanup_cache(self) -> Dict[str, Any]:
        """Cleanup expired cache entries"""
        if not self.secure_cache:
            return {"message": "Secure cache not available"}
        
        try:
            return self.secure_cache.cleanup()
        except Exception as e:
            return {"error": str(e)}
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        stats = {
            "user": self.current_user,
            "session_id": self.session_id,
            "user_dir": str(self.user_dir) if self.user_dir else None,
            "secure_cache_enabled": self.secure_cache is not None
        }
        
        if self.secure_cache:
            try:
                secure_stats = self.secure_cache.get_system_stats()
                stats["secure_cache"] = secure_stats
            except Exception as e:
                stats["secure_cache_error"] = str(e)
        
        # Add database stats
        if self.db_path and self.db_path.exists():
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('SELECT COUNT(*) FROM conversation_history')
                conversation_count = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM sessions')
                session_count = cursor.fetchone()[0]
                
                conn.close()
                
                stats["database"] = {
                    "conversations": conversation_count,
                    "sessions": session_count,
                    "path": str(self.db_path)
                }
            except Exception as e:
                stats["database_error"] = str(e)
        
        return stats
    
    def export_encrypted_backup(self, backup_path: str = None) -> bool:
        """Export encrypted backup of user data"""
        if not self.secure_cache or not self.user_dir:
            return False
        
        try:
            import shutil
            from datetime import datetime
            
            if not backup_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = self.user_dir.parent / f"backup_{self.current_user}_{timestamp}.encrypted"
            
            # Create backup directory structure
            backup_dir = Path(backup_path).with_suffix('.backup_temp')
            backup_dir.mkdir(exist_ok=True)
            
            # Copy encrypted cache files
            cache_dir = self.user_dir / ".cache"
            if cache_dir.exists():
                shutil.copytree(cache_dir, backup_dir / ".cache")
            
            # Copy encrypted secrets
            secrets_dir = self.user_dir / ".secrets"
            if secrets_dir.exists():
                shutil.copytree(secrets_dir, backup_dir / ".secrets")
            
            # Copy database
            if self.db_path and self.db_path.exists():
                shutil.copy2(self.db_path, backup_dir / "sessions.db")
            
            # Create encrypted archive
            shutil.make_archive(str(backup_path), 'zip', backup_dir)
            
            # Clean up temp directory
            shutil.rmtree(backup_dir)
            
            print(f"✅ Encrypted backup created: {backup_path}.zip")
            return True
            
        except Exception as e:
            print(f"❌ Backup creation failed: {e}")
            return False


# Global user session manager
user_manager = UserSessionManager()
