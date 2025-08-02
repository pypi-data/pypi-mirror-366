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
        """Initialize embeddings for vector operations"""
        if OLLAMA_EMBEDDINGS_AVAILABLE:
            try:
                # Try Ollama first (local)
                self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
                # print("✅ Using Ollama embeddings for vector operations")
            except Exception as e:
                # print(f"⚠️ Ollama embeddings failed: {e}")
                self.embeddings = None
        else:
            print("⚠️ No embeddings available. Install ollama for local embeddings.")
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
    
    def init_user_database(self, user_dir: Path):
        """Initialize SQLite database for user"""
        db_path = user_dir / 'user_data.db'
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create tables for user information
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_info (
                username TEXT PRIMARY KEY,
                created_at TEXT,
                last_login TEXT,
                preferences TEXT
            )
        ''')
        
        # Create table for chat sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_sessions (
                session_id TEXT PRIMARY KEY,
                username TEXT,
                created_at TEXT,
                updated_at TEXT,
                session_data TEXT,
                FOREIGN KEY (username) REFERENCES user_info (username)
            )
        ''')
        
        # Create table for file interactions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                session_id TEXT,
                file_path TEXT,
                action TEXT,
                timestamp TEXT,
                metadata TEXT,
                FOREIGN KEY (username) REFERENCES user_info (username)
            )
        ''')
        
        # Create table for conversation history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                session_id TEXT,
                role TEXT,
                content TEXT,
                timestamp TEXT,
                metadata TEXT,
                FOREIGN KEY (username) REFERENCES user_info (username)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def setup_user(self, username: str, password: str = None) -> bool:
        """Setup user environment with secure caching"""
        try:
            # Get user directory
            self.user_dir = self.get_user_directory(username)
            self.current_user = username
            self.session_id = str(uuid.uuid4())
            self.db_path = self.user_dir / 'user_data.db'
            
            # Store master password for encryption
            self.master_password = password
            
            # Initialize database
            self.init_user_database(self.user_dir)
            
            # Save user info
            self.save_user_info(username)
            
            # Initialize secure cache with user-specific directory
            cache_dir = self.user_dir / "secure_cache"
            cache_dir.mkdir(exist_ok=True)
            
            try:
                self.secure_cache = SecureCacheManager(
                    cache_dir=str(cache_dir),
                    master_password=password
                )
                print("🔒 Secure cache initialized successfully")
            except Exception as e:
                print(f"⚠️ Secure cache initialization failed: {e}")
                print("📍 Continuing without secure caching...")
                self.secure_cache = None
            
            # Initialize vector store if embeddings are available
            if self.embeddings:
                self.init_vector_store()
            
            print(f"✅ User '{username}' initialized successfully")
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
    
    def init_vector_store(self):
        """Initialize vector store for semantic search"""
        if not self.embeddings:
            return
        
        vector_dir = self.user_dir / "vector_store"
        vector_dir.mkdir(exist_ok=True)
        
        try:
            if FAISS_AVAILABLE:
                # Try to load existing FAISS index
                faiss_path = vector_dir / "faiss_index"
                if faiss_path.exists():
                    self.vector_store = LangchainFAISS.load_local(
                        str(faiss_path), 
                        self.embeddings,
                        allow_dangerous_deserialization=True
                    )
                    print("✅ Loaded existing FAISS vector store")
                else:
                    # Create new FAISS index with dummy document
                    from langchain.schema import Document
                    dummy_doc = Document(page_content="Initialization document", metadata={"type": "init"})
                    self.vector_store = LangchainFAISS.from_documents([dummy_doc], self.embeddings)
                    self.vector_store.save_local(str(faiss_path))
                    print("✅ Created new FAISS vector store")
            
            elif CHROMADB_AVAILABLE and Chroma:
                # Use ChromaDB as fallback
                chroma_path = vector_dir / "chroma_db"
                self.vector_store = Chroma(
                    persist_directory=str(chroma_path),
                    embedding_function=self.embeddings
                )
                print("✅ Initialized ChromaDB vector store")
            
        except Exception as e:
            print(f"⚠️ Vector store initialization failed: {e}")
            self.vector_store = None
    
    def add_conversation(self, role: str, content: str, metadata: Dict = None):
        """Add conversation to database and vector store"""
        if not self.current_user or not self.session_id:
            return
        
        try:
            # Add to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO conversations 
                (username, session_id, role, content, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                self.current_user,
                self.session_id, 
                role,
                content,
                datetime.now().isoformat(),
                json.dumps(metadata or {})
            ))
            
            conn.commit()
            conn.close()
            
            # Add to vector store if available
            if self.vector_store and len(content.strip()) > 10:  # Only index meaningful content
                from langchain.schema import Document
                doc = Document(
                    page_content=content,
                    metadata={
                        "role": role,
                        "session_id": self.session_id,
                        "timestamp": datetime.now().isoformat(),
                        **(metadata or {})
                    }
                )
                
                if hasattr(self.vector_store, 'add_documents'):
                    self.vector_store.add_documents([doc])
                    
                    # Save FAISS index if applicable
                    if FAISS_AVAILABLE and isinstance(self.vector_store, LangchainFAISS):
                        vector_dir = self.user_dir / "vector_store" / "faiss_index"
                        self.vector_store.save_local(str(vector_dir))
                        
        except Exception as e:
            print(f"⚠️ Error adding conversation: {e}")
    
    def search_conversations(self, query: str, limit: int = 5) -> List[Dict]:
        """Search conversations using vector similarity"""
        if not self.vector_store:
            return []
        
        try:
            results = self.vector_store.similarity_search(query, k=limit)
            return [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": getattr(doc, 'score', 0.0)
                }
                for doc in results
            ]
        except Exception as e:
            print(f"⚠️ Vector search failed: {e}")
            return []
    
    def get_conversation_history(self, session_id: str = None, limit: int = 50) -> List[Dict]:
        """Get conversation history from database"""
        if not self.current_user:
            return []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if session_id:
                cursor.execute('''
                    SELECT role, content, timestamp, metadata 
                    FROM conversations 
                    WHERE username = ? AND session_id = ?
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (self.current_user, session_id, limit))
            else:
                cursor.execute('''
                    SELECT role, content, timestamp, metadata 
                    FROM conversations 
                    WHERE username = ?
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (self.current_user, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "role": row[0],
                    "content": row[1],
                    "timestamp": row[2],
                    "metadata": json.loads(row[3]) if row[3] else {}
                }
                for row in reversed(rows)  # Reverse to get chronological order
            ]
            
        except Exception as e:
            print(f"⚠️ Error retrieving conversation history: {e}")
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
    
    def get_user_stats(self) -> Dict[str, Any]:
        """Get user statistics"""
        if not self.current_user or not self.db_path:
            return {}
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get conversation count
            cursor.execute('''
                SELECT COUNT(*) FROM conversations WHERE username = ?
            ''', (self.current_user,))
            conversation_count = cursor.fetchone()[0]
            
            # Get session count
            cursor.execute('''
                SELECT COUNT(DISTINCT session_id) FROM conversations WHERE username = ?
            ''', (self.current_user,))
            session_count = cursor.fetchone()[0]
            
            # Get file interaction count
            cursor.execute('''
                SELECT COUNT(*) FROM file_interactions WHERE username = ?
            ''', (self.current_user,))
            file_interaction_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "username": self.current_user,
                "conversations": conversation_count,
                "sessions": session_count,
                "file_interactions": file_interaction_count,
                "vector_store_available": self.vector_store is not None,
                "secure_cache_available": self.secure_cache is not None,
                "user_directory": str(self.user_dir) if self.user_dir else None
            }
            
        except Exception as e:
            return {"error": str(e)}
    
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
            "secure_cache_available": self.secure_cache is not None,
            "vector_store_available": self.vector_store is not None,
            "embeddings_available": self.embeddings is not None
        }
        
        # Add secure cache stats
        if self.secure_cache:
            try:
                cache_stats = self.secure_cache.get_stats()
                stats.update(cache_stats)
            except Exception as e:
                stats["secure_cache_error"] = str(e)
        
        # Add database stats
        if self.db_path and self.db_path.exists():
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM conversations")
                conversation_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(DISTINCT session_id) FROM conversations")
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


# Global user session manager
user_manager = UserSessionManager()
