from typing import Any, Optional, Union
import os
import psycopg2
import pymongo
import pymysql
import redis
import sqlite3
from contextlib import contextmanager

from .db_type import POSTGRES, MONGODB, MYSQL, REDIS, SQLITE


class DatabaseConnection:
    """Base class for database connections"""
    
    def __init__(self, connection: Any):
        self.connection = connection
    
    def get_connection(self) -> Any:
        """Get the underlying connection object"""
        return self.connection
    
    def close(self):
        """Close the database connection"""
        if hasattr(self.connection, 'close'):
            self.connection.close()

    def cursor(self):
        """Get a cursor for executing queries"""
        return self.connection.cursor()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

class PostgresConnection(DatabaseConnection):
    """PostgreSQL database connection"""
    
    def __init__(self, connection):
        super().__init__(connection)
    
    def cursor(self):
        """Get a cursor for executing queries"""
        return self.connection.cursor()

class MongoConnection(DatabaseConnection):
    """MongoDB database connection"""
    
    def __init__(self, connection, database_name: str):
        super().__init__(connection)
        self.database = connection[database_name]
    
    def get_database(self):
        """Get the database object"""
        return self.database
    
    def get_collection(self, collection_name: str):
        """Get a collection from the database"""
        return self.database[collection_name]

class MySQLConnection(DatabaseConnection):
    """MySQL database connection"""
    
    def __init__(self, connection):
        super().__init__(connection)
    
    def cursor(self):
        """Get a cursor for executing queries"""
        return self.connection.cursor()

class RedisConnection(DatabaseConnection):
    """Redis database connection"""
    
    def __init__(self, connection):
        super().__init__(connection)
    
    def get(self, key: str) -> Optional[str]:
        """Get a value by key"""
        return self.connection.get(key)
    
    def set(self, key: str, value: str, ex: Optional[int] = None):
        """Set a key-value pair"""
        return self.connection.set(key, value, ex=ex)

class SQLiteConnection(DatabaseConnection):
    """SQLite database connection"""
    
    def __init__(self, connection):
        super().__init__(connection)
    
    def cursor(self):
        """Get a cursor for executing queries"""
        return self.connection.cursor()

def get_db_connection(
    db_type: str, 
    username: str, 
    password: str, 
    host: str, 
    port: int, 
    database: str
) -> DatabaseConnection:
    """
    Get a database connection instance based on the database type.
    
    Args:
        db_type: Type of database (postgres, mongodb, mysql, redis, sqlite)
        username: Database username
        password: Database password
        host: Database host
        port: Database port
        database: Database name
    
    Returns:
        DatabaseConnection instance or None if unsupported database type
    """

    try:
        if db_type == POSTGRES:
            connection = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=username,
                password=password
            )
            return PostgresConnection(connection)
        
        elif db_type == MONGODB:
            # MongoDB connection string format
            if username and password:
                conn_string = f"mongodb://{username}:{password}@{host}:{port}/{database}"
            else:
                conn_string = f"mongodb://{host}:{port}/{database}"
            client = pymongo.MongoClient(conn_string)
            return MongoConnection(client, database)
        
        elif db_type == MYSQL:
            connection = pymysql.connect(
                host=host,
                port=port,
                database=database,
                user=username,
                password=password
            )
            return MySQLConnection(connection)
        
        elif db_type == REDIS:
            connection = redis.Redis(
                host=host,
                port=port,
                db=int(database) if database.isdigit() else 0,
                username=username if username else None,
                password=password if password else None
            )
            return RedisConnection(connection)
        
        elif db_type == SQLITE:
            # For SQLite, database parameter is the file path
            connection = sqlite3.connect(database)
            return SQLiteConnection(connection)
        
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    except Exception as e:
        raise ConnectionError(f"Failed to connect to {db_type} database: {str(e)}")

def setup_db_connection() -> DatabaseConnection:
    """
    Setup database connection using environment variables.
    
    Required environment variables:
    - DB_TYPE: Type of database (postgres, mongodb, mysql, redis, sqlite)
    - DB_USERNAME: Database username
    - DB_PASSWORD: Database password
    - DB_HOST: Database host
    - DB_PORT: Database port
    - DB_NAME: Database name
    
    Returns:
        DatabaseConnection instance
    
    Raises:
        ValueError: If required environment variables are not set
        ConnectionError: If connection fails
    """
    db_type = os.getenv("DB_TYPE")
    if not db_type:
        raise ValueError("DB_TYPE environment variable is not set")
    
    username = os.getenv("DB_USERNAME", "")
    password = os.getenv("DB_PASSWORD", "")
    host = os.getenv("DB_HOST", "")
    port = int(os.getenv("DB_PORT", "0"))
    database = os.getenv("DB_NAME", "")
    
    # Validate required parameters based on database type
    if db_type != SQLITE:  # SQLite doesn't need host, port, username, password
        if not host:
            raise ValueError("DB_HOST environment variable is not set")
        if not port:
            raise ValueError("DB_PORT environment variable is not set")
        if not database:
            raise ValueError("DB_NAME environment variable is not set")
    
    return get_db_connection(db_type, username, password, host, port, database)

@contextmanager
def get_db_connection_context():
    """
    Context manager for database connections that automatically closes the connection.
    
    Usage:
        with get_db_connection_context() as db:
            # Use db connection here
            pass
    """
    connection = setup_db_connection()
    try:
        yield connection
    finally:
        connection.close()

# Convenience functions for specific database types
def get_postgres_connection() -> PostgresConnection:
    """Get a PostgreSQL connection using environment variables"""
    connection = setup_db_connection()
    if isinstance(connection, PostgresConnection):
        return connection
    raise TypeError(f"Expected PostgresConnection, got {type(connection)}")

def get_mongo_connection() -> MongoConnection:
    """Get a MongoDB connection using environment variables"""
    connection = setup_db_connection()
    if isinstance(connection, MongoConnection):
        return connection
    raise TypeError(f"Expected MongoConnection, got {type(connection)}")

def get_mysql_connection() -> MySQLConnection:
    """Get a MySQL connection using environment variables"""
    connection = setup_db_connection()
    if isinstance(connection, MySQLConnection):
        return connection
    raise TypeError(f"Expected MySQLConnection, got {type(connection)}")

def get_redis_connection() -> RedisConnection:
    """Get a Redis connection using environment variables"""
    connection = setup_db_connection()
    if isinstance(connection, RedisConnection):
        return connection
    raise TypeError(f"Expected RedisConnection, got {type(connection)}")

def get_sqlite_connection() -> SQLiteConnection:
    """Get a SQLite connection using environment variables"""
    connection = setup_db_connection()
    if isinstance(connection, SQLiteConnection):
        return connection
    raise TypeError(f"Expected SQLiteConnection, got {type(connection)}") 