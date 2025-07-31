import uuid
import hashlib
from datetime import datetime
from typing import Optional
from bssagent.database.db_connection import get_db_connection_context

class APIKeyManagement:
    """
    Manages API keys for users, storing and validating them in the database.
    """
    def __init__(self):
        self._init_api_key_table()

    def _init_api_key_table(self):
        try:
            with get_db_connection_context() as db:
                if hasattr(db, 'cursor') and callable(getattr(db, 'cursor', None)):
                    cursor = db.cursor()
                    create_table_sql = '''
                    CREATE TABLE IF NOT EXISTS api_keys (
                        id SERIAL PRIMARY KEY,
                        user_id VARCHAR(255) NOT NULL,
                        api_key VARCHAR(255) UNIQUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        revoked BOOLEAN DEFAULT FALSE
                    );
                    '''
                    cursor.execute(create_table_sql)
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys(user_id);")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_api_keys_api_key ON api_keys(api_key);")
                    if hasattr(db, 'connection') and hasattr(db.connection, 'commit'):
                        db.connection.commit()
        except Exception as e:
            print(f"Warning: Could not initialize api_keys table: {e}")

    def generate_api_key(self, user_id: str) -> str:
        """
        Generate and store a new API key for a user.
        """
        raw_key = f"{user_id}-{uuid.uuid4()}"
        api_key = hashlib.sha256(raw_key.encode()).hexdigest()
        try:
            with get_db_connection_context() as db:
                if hasattr(db, 'cursor') and callable(getattr(db, 'cursor', None)):
                    cursor = db.cursor()
                    insert_sql = '''
                    INSERT INTO api_keys (user_id, api_key, created_at, revoked)
                    VALUES (%s, %s, %s, %s)
                    '''
                    cursor.execute(insert_sql, (user_id, api_key, datetime.now().isoformat(), False))
                    if hasattr(db, 'connection') and hasattr(db.connection, 'commit'):
                        db.connection.commit()
            return api_key
        except Exception as e:
            print(f"Warning: Could not generate API key: {e}")
            return ""

    def revoke_api_key(self, api_key: str) -> bool:
        """
        Revoke an API key (set revoked to True).
        """
        try:
            with get_db_connection_context() as db:
                if hasattr(db, 'cursor') and callable(getattr(db, 'cursor', None)):
                    cursor = db.cursor()
                    update_sql = '''
                    UPDATE api_keys SET revoked = TRUE WHERE api_key = %s
                    '''
                    cursor.execute(update_sql, (api_key,))
                    if hasattr(db, 'connection') and hasattr(db.connection, 'commit'):
                        db.connection.commit()
            return True
        except Exception as e:
            print(f"Warning: Could not revoke API key: {e}")
            return False

    def validate_api_key(self, api_key: str) -> Optional[str]:
        """
        Validate an API key. Returns user_id if valid, else None.
        """
        try:
            with get_db_connection_context() as db:
                if hasattr(db, 'cursor') and callable(getattr(db, 'cursor', None)):
                    cursor = db.cursor()
                    select_sql = '''
                    SELECT user_id FROM api_keys WHERE api_key = %s AND revoked = FALSE
                    '''
                    cursor.execute(select_sql, (api_key,))
                    result = cursor.fetchone()
                    if result:
                        return result[0]
        except Exception as e:
            print(f"Warning: Could not validate API key: {e}")
        return None 