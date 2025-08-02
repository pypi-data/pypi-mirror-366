"""
Conversation History Manager
Handles conversation memory and context for AI Helper Agent
"""

import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

@dataclass
class ConversationMessage:
    role: MessageRole
    content: str
    timestamp: datetime
    model_used: Optional[str] = None
    provider: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['role'] = self.role.value
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationMessage':
        data['role'] = MessageRole(data['role'])
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)

class ConversationHistoryManager:
    """Manages conversation history with persistence and memory management"""
    
    def __init__(self, max_context_messages: int = 20, max_context_tokens: int = 4000):
        self.config_dir = Path.home() / ".ai_helper_agent"
        self.config_dir.mkdir(exist_ok=True)
        
        self.db_path = self.config_dir / "conversations.db"
        self.max_context_messages = max_context_messages
        self.max_context_tokens = max_context_tokens
        
        # In-memory conversation store for active sessions
        self.active_conversations: Dict[str, List[ConversationMessage]] = {}
        
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for conversation storage"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    model_used TEXT,
                    provider TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_session_timestamp 
                ON conversations(session_id, timestamp)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_created_at 
                ON conversations(created_at)
            """)
            
            conn.commit()
    
    def add_message(self, session_id: str, role: MessageRole, content: str, 
                   model_used: Optional[str] = None, provider: Optional[str] = None,
                   metadata: Optional[Dict[str, Any]] = None):
        """Add a message to the conversation history"""
        message = ConversationMessage(
            role=role,
            content=content,
            timestamp=datetime.now(),
            model_used=model_used,
            provider=provider,
            session_id=session_id,
            metadata=metadata
        )
        
        # Add to active conversation
        if session_id not in self.active_conversations:
            self.active_conversations[session_id] = []
        
        self.active_conversations[session_id].append(message)
        
        # Trim conversation if too long
        self._trim_conversation(session_id)
        
        # Persist to database
        self._save_to_database(message)
    
    def add_user_message(self, session_id: str, content: str):
        """Add a user message"""
        self.add_message(session_id, MessageRole.USER, content)
    
    def add_assistant_message(self, session_id: str, content: str, 
                            model_used: Optional[str] = None, provider: Optional[str] = None):
        """Add an assistant message"""
        self.add_message(session_id, MessageRole.ASSISTANT, content, model_used, provider)
    
    def add_system_message(self, session_id: str, content: str):
        """Add a system message"""
        self.add_message(session_id, MessageRole.SYSTEM, content)
    
    def get_conversation_history(self, session_id: str, 
                               include_system: bool = True,
                               max_messages: Optional[int] = None) -> List[ConversationMessage]:
        """Get conversation history for a session"""
        # Load from database if not in active conversations
        if session_id not in self.active_conversations:
            self._load_from_database(session_id)
        
        messages = self.active_conversations.get(session_id, [])
        
        if not include_system:
            messages = [msg for msg in messages if msg.role != MessageRole.SYSTEM]
        
        if max_messages:
            messages = messages[-max_messages:]
        
        return messages
    
    def get_context_for_llm(self, session_id: str, 
                          include_system: bool = False) -> List[Dict[str, str]]:
        """Get conversation context formatted for LLM consumption"""
        messages = self.get_conversation_history(
            session_id, 
            include_system=include_system,
            max_messages=self.max_context_messages
        )
        
        # Convert to LLM format
        llm_messages = []
        for msg in messages:
            llm_messages.append({
                "role": msg.role.value,
                "content": msg.content
            })
        
        # Trim by token count if necessary
        return self._trim_by_tokens(llm_messages)
    
    def get_conversation_context(self, session_id: str, 
                               include_system: bool = False, 
                               as_string: bool = True) -> str:
        """Get conversation context as a formatted string for prompt inclusion"""
        messages = self.get_conversation_history(
            session_id, 
            include_system=include_system,
            max_messages=self.max_context_messages
        )
        
        if not messages:
            return ""
        
        if as_string:
            # Format as readable conversation string
            context_lines = []
            for msg in messages:
                role_name = "Human" if msg.role == MessageRole.USER else "Assistant"
                if msg.role == MessageRole.SYSTEM:
                    role_name = "System"
                
                context_lines.append(f"{role_name}: {msg.content}")
            
            return "\n".join(context_lines)
        else:
            # Return as list of dictionaries
            return [{"role": msg.role.value, "content": msg.content} for msg in messages]
    
    def _trim_conversation(self, session_id: str):
        """Trim conversation to max_context_messages"""
        if session_id in self.active_conversations:
            messages = self.active_conversations[session_id]
            if len(messages) > self.max_context_messages:
                # Keep system messages and trim user/assistant messages
                system_messages = [msg for msg in messages if msg.role == MessageRole.SYSTEM]
                other_messages = [msg for msg in messages if msg.role != MessageRole.SYSTEM]
                
                # Keep the most recent messages
                recent_messages = other_messages[-(self.max_context_messages - len(system_messages)):]
                
                self.active_conversations[session_id] = system_messages + recent_messages
    
    def _trim_by_tokens(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Trim messages by estimated token count"""
        # Simple token estimation: ~4 characters per token
        total_chars = 0
        max_chars = self.max_context_tokens * 4
        
        trimmed_messages = []
        for message in reversed(messages):
            msg_chars = len(message['content'])
            if total_chars + msg_chars > max_chars and trimmed_messages:
                break
            
            trimmed_messages.insert(0, message)
            total_chars += msg_chars
        
        return trimmed_messages
    
    def _save_to_database(self, message: ConversationMessage):
        """Save message to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO conversations 
                    (session_id, role, content, timestamp, model_used, provider, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    message.session_id,
                    message.role.value,
                    message.content,
                    message.timestamp.isoformat(),
                    message.model_used,
                    message.provider,
                    json.dumps(message.metadata) if message.metadata else None
                ))
                conn.commit()
        except Exception as e:
            print(f"⚠️ Warning: Could not save conversation to database: {e}")
    
    def _load_from_database(self, session_id: str, limit: int = 50):
        """Load conversation from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT role, content, timestamp, model_used, provider, metadata
                    FROM conversations 
                    WHERE session_id = ?
                    ORDER BY timestamp ASC
                    LIMIT ?
                """, (session_id, limit))
                
                messages = []
                for row in cursor.fetchall():
                    role, content, timestamp, model_used, provider, metadata_json = row
                    
                    metadata = None
                    if metadata_json:
                        try:
                            metadata = json.loads(metadata_json)
                        except:
                            pass
                    
                    message = ConversationMessage(
                        role=MessageRole(role),
                        content=content,
                        timestamp=datetime.fromisoformat(timestamp),
                        model_used=model_used,
                        provider=provider,
                        session_id=session_id,
                        metadata=metadata
                    )
                    messages.append(message)
                
                self.active_conversations[session_id] = messages
                
        except Exception as e:
            print(f"⚠️ Warning: Could not load conversation from database: {e}")
            self.active_conversations[session_id] = []
    
    def clear_session(self, session_id: str):
        """Clear conversation history for a session"""
        if session_id in self.active_conversations:
            del self.active_conversations[session_id]
        
        # Also clear from database
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM conversations WHERE session_id = ?", (session_id,))
                conn.commit()
        except Exception as e:
            print(f"⚠️ Warning: Could not clear session from database: {e}")
    
    def get_recent_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get list of recent conversation sessions"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT session_id, COUNT(*) as message_count, 
                           MIN(timestamp) as first_message,
                           MAX(timestamp) as last_message
                    FROM conversations 
                    GROUP BY session_id
                    ORDER BY MAX(timestamp) DESC
                    LIMIT ?
                """, (limit,))
                
                sessions = []
                for row in cursor.fetchall():
                    session_id, message_count, first_message, last_message = row
                    sessions.append({
                        'session_id': session_id,
                        'message_count': message_count,
                        'first_message': first_message,
                        'last_message': last_message
                    })
                
                return sessions
                
        except Exception as e:
            print(f"⚠️ Warning: Could not load recent sessions: {e}")
            return []
    
    def cleanup_old_conversations(self, days_to_keep: int = 30):
        """Clean up conversations older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    DELETE FROM conversations 
                    WHERE created_at < ?
                """, (cutoff_date.isoformat(),))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                if deleted_count > 0:
                    print(f"🧹 Cleaned up {deleted_count} old conversation messages")
                
        except Exception as e:
            print(f"⚠️ Warning: Could not cleanup old conversations: {e}")
    
    def export_conversation(self, session_id: str, format: str = 'json') -> Optional[str]:
        """Export conversation to file"""
        messages = self.get_conversation_history(session_id)
        
        if not messages:
            return None
        
        export_data = {
            'session_id': session_id,
            'exported_at': datetime.now().isoformat(),
            'message_count': len(messages),
            'messages': [msg.to_dict() for msg in messages]
        }
        
        if format.lower() == 'json':
            return json.dumps(export_data, indent=2)
        elif format.lower() == 'txt':
            lines = [f"Conversation Export: {session_id}"]
            lines.append(f"Exported: {export_data['exported_at']}")
            lines.append(f"Messages: {export_data['message_count']}")
            lines.append("=" * 50)
            
            for msg in messages:
                lines.append(f"\n[{msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {msg.role.value.upper()}:")
                lines.append(msg.content)
                if msg.model_used:
                    lines.append(f"(Model: {msg.model_used})")
            
            return "\n".join(lines)
        
        return None

# Global instance
conversation_manager = ConversationHistoryManager()

def get_conversation_manager() -> ConversationHistoryManager:
    """Get the global conversation manager instance"""
    return conversation_manager
