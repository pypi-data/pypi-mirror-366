from typing import Any, Dict, Optional
import uuid
import json
from datetime import datetime
from bssagent.database.db_connection import get_db_connection_context


class AgentSessionManager:
    """Manages user sessions for agents with database persistence."""
    
    def __init__(self):
        self.user_sessions: Dict[str, Dict[str, Any]] = {}
        self._init_session_table()
    
    def _init_session_table(self):
        """Initialize the user sessions table in the database."""
        try:
            with get_db_connection_context() as db:
                # Check if this is a database connection that supports SQL operations
                if hasattr(db, 'cursor') and callable(getattr(db, 'cursor', None)):
                    cursor = db.cursor()
                    
                    # Create sessions table if it doesn't exist
                    create_table_sql = """
                    CREATE TABLE IF NOT EXISTS user_sessions (
                        id SERIAL PRIMARY KEY,
                        user_id VARCHAR(255) NOT NULL,
                        thread_id VARCHAR(255) UNIQUE NOT NULL,
                        title VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE
                    );
                    """
                    cursor.execute(create_table_sql)
                    
                    # Create indexes for better performance
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_sessions_thread_id ON user_sessions(thread_id);")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_sessions_active ON user_sessions(is_active);")
                    
                    if hasattr(db, 'connection') and hasattr(db.connection, 'commit'):
                        db.connection.commit()
                    
        except Exception as e:
            print(f"Warning: Could not initialize session table: {e}")
    
    def create_user_session(self, user_id: str, title: str) -> Dict[str, Any]:
        """Create a new session for a user and save it to the database."""
        thread_id = user_id + "_" + str(uuid.uuid4())  # Unique thread per user
        
        
        # Save to database
        self._save_session_to_db(user_id, thread_id, title)
        
        # Also store in memory for quick access
        self.user_sessions[user_id] = {
            "title": title,
            "thread_id": thread_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "is_active": True
        }
        
        return self.user_sessions[user_id]
    
    def _save_session_to_db(self, user_id: str, thread_id: str, title: str):
        """Save session data to the database."""
        try:
            with get_db_connection_context() as db:
                # Check if this is a database connection that supports SQL operations
                if hasattr(db, 'cursor') and callable(getattr(db, 'cursor', None)):
                    cursor = db.cursor()
                    
                    # Insert or update session
                    upsert_sql = """
                    INSERT INTO user_sessions (user_id, thread_id, title, created_at, updated_at, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (thread_id) 
                    DO UPDATE SET 
                        updated_at = EXCLUDED.updated_at,
                        is_active = EXCLUDED.is_active
                    """
                    
                    cursor.execute(upsert_sql, (
                        user_id,
                        thread_id,
                        title,
                        datetime.now().isoformat(),
                        datetime.now().isoformat(),
                        True
                    ))
                    
                    if hasattr(db, 'connection') and hasattr(db.connection, 'commit'):
                        db.connection.commit()
                    
        except Exception as e:
            print(f"Warning: Could not save session to database: {e}")
    
    def _load_session_from_db(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Load session data from the database."""
        try:
            with get_db_connection_context() as db:
                # Check if this is a database connection that supports SQL operations
                if hasattr(db, 'cursor') and callable(getattr(db, 'cursor', None)):
                    cursor = db.cursor()
                    
                    select_sql = """
                    SELECT * FROM user_sessions 
                    WHERE user_id = %s AND is_active = TRUE 
                    ORDER BY updated_at DESC 
                    LIMIT 1
                    """
                    
                    cursor.execute(select_sql, (user_id,))
                    result = cursor.fetchone()
                    
                    if result:
                        session_data = {
                            "title": result[2],
                            "thread_id": result[1],
                            "created_at": result[3],
                            "updated_at": result[4],
                            "is_active": result[5]
                        }
                        return session_data
                        
        except Exception as e:
            print(f"Warning: Could not load session from database: {e}")
        
        return None
    
    def get_or_create_user_session(self, user_id: str, title: str = "New Chat") -> Dict[str, Any]:
        """Get existing session or create new one for user."""
        # First check memory cache
        if user_id in self.user_sessions:
            return self.user_sessions[user_id]
        
        # Try to load from database
        session_data = self._load_session_from_db(user_id)
        if session_data:
            self.user_sessions[user_id] = session_data
            return session_data
        
        # Create new session if none exists
        return self.create_user_session(user_id, title)
    
    def get_current_user_session(self, user_id: str) -> Dict[str, Any]:
        """Get a user session from memory or database."""
        # First check memory cache
        if user_id in self.user_sessions:
            return self.user_sessions[user_id]
        
        # Try to load from database
        session_data = self._load_session_from_db(user_id)
        if session_data:
            self.user_sessions[user_id] = session_data
            return session_data
        
        raise ValueError(f"User session for user {user_id} not found")
    
    def update_session(self, user_id: str, updates: Dict[str, Any]):
        """Update session data and save to database."""
        if user_id in self.user_sessions:
            self.user_sessions[user_id].update(updates)
            self.user_sessions[user_id]["updated_at"] = datetime.now().isoformat()
            
            # Save updated session to database
            session_data = self.user_sessions[user_id]
            self._save_session_to_db(
                user_id, 
                session_data["thread_id"], 
                session_data["title"]
            )
    
    def deactivate_session(self, user_id: str):
        """Deactivate a user session."""
        try:
            with get_db_connection_context() as db:
                # Check if this is a database connection that supports SQL operations
                if hasattr(db, 'cursor') and callable(getattr(db, 'cursor', None)):
                    cursor = db.cursor()
                    
                    update_sql = """
                    UPDATE user_sessions 
                    SET is_active = FALSE, updated_at = %s 
                    WHERE user_id = %s
                    """
                    
                    cursor.execute(update_sql, (datetime.now().isoformat(), user_id))
                    if hasattr(db, 'connection') and hasattr(db.connection, 'commit'):
                        db.connection.commit()
                    
                    # Remove from memory cache
                    if user_id in self.user_sessions:
                        del self.user_sessions[user_id]
                        
        except Exception as e:
            print(f"Warning: Could not deactivate session: {e}")

    # TODO: Get all threads
    
    def list_active_sessions(self) -> list:
        """List all active sessions from database."""
        try:
            with get_db_connection_context() as db:
                # Check if this is a database connection that supports SQL operations
                if hasattr(db, 'cursor') and callable(getattr(db, 'cursor', None)):
                    cursor = db.cursor()
                    
                    select_sql = """
                    SELECT user_id, thread_id, created_at, updated_at 
                    FROM user_sessions 
                    WHERE is_active = TRUE 
                    ORDER BY updated_at DESC
                    """
                    
                    cursor.execute(select_sql)
                    results = cursor.fetchall()
                    
                    return [
                        {
                            "user_id": row[0],
                            "thread_id": row[1],
                            "created_at": row[2],
                            "updated_at": row[3]
                        }
                        for row in results
                    ]
                        
        except Exception as e:
            print(f"Warning: Could not list sessions: {e}")
        
        return []
    
    def clear_memory_cache(self):
        """Clear the in-memory session cache."""
        self.user_sessions.clear()
    
    def get_session_count(self) -> int:
        """Get the number of sessions in memory cache."""
        return len(self.user_sessions)
    
    def has_session(self, user_id: str) -> bool:
        """Check if a user has an active session in memory."""
        return user_id in self.user_sessions 