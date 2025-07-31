from typing import Any, Literal
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.checkpoint.mysql.pymysql import PyMySQLSaver
# from langgraph.store.mysql.pymysql import PyMySQLStore
from langgraph.checkpoint.redis import RedisSaver
from langgraph.store.redis import RedisStore
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.store.sqlite import SqliteStore
import os
from .db_type import POSTGRES, MONGODB, MYSQL, REDIS, SQLITE


def get_dbsaver(db_type: str,  username: str, password: str, host: str, port: int, database: str) -> Any:
    """
    Get a dbsaver instance and return the correct type.
    """
    if db_type == POSTGRES:
        dbsaver = PostgresSaver.from_conn_string(f"postgresql://{username}:{password}@{host}:{port}/{database}")
        return dbsaver
    elif db_type == MONGODB:
        dbsaver = MongoDBSaver.from_conn_string(f"mongodb://{username}:{password}@{host}:{port}/{database}")
        return dbsaver
    elif db_type == MYSQL:
        dbsaver = PyMySQLSaver.from_conn_string(f"mysql://{username}:{password}@{host}:{port}/{database}")
        return dbsaver
    elif db_type == REDIS:
        dbsaver = RedisSaver.from_conn_string(f"redis://{username}:{password}@{host}:{port}/{database}")
        return dbsaver
    elif db_type == SQLITE:
        dbsaver = SqliteSaver.from_conn_string(f"sqlite:///{database}")
        return dbsaver
    else:
        return None

def setup_dbsaver():
    """
    Setup the dbsaver.
    """
    # Check whether or not using the same database for all purposes
    if int(os.getenv("ONE_DB", "0")) == 1:
        return get_dbsaver(
            os.getenv("DB_TYPE") or "", 
            os.getenv("DB_USERNAME") or "", 
            os.getenv("DB_PASSWORD") or "", 
            os.getenv("DB_HOST") or "", 
            int(os.getenv("DB_PORT") or "0"), 
            os.getenv("DB_NAME") or ""
        )
    else:
        return get_dbsaver(
            os.getenv("LANGGRAPH_CHECKPOINTER_TYPE") or "", 
            os.getenv("LANGGRAPH_CHECKPOINTER_USERNAME") or "", 
            os.getenv("LANGGRAPH_CHECKPOINTER_PASSWORD") or "", 
            os.getenv("LANGGRAPH_CHECKPOINTER_HOST") or "", 
            int(os.getenv("LANGGRAPH_CHECKPOINTER_PORT") or "0"), 
            os.getenv("LANGGRAPH_CHECKPOINTER_DATABASE") or ""
        )   

def get_dbstore(db_type: str,  username: str, password: str, host: str, port: int, database: str) -> Any:
    """
    Get a dbstore instance and return the correct type.
    """
    if db_type == POSTGRES:
        dbstore = PostgresStore.from_conn_string(f"postgresql://{username}:{password}@{host}:{port}/{database}")
        return dbstore
    # elif db_type == MYSQL:
    #     with PyMySQLStore.from_conn_string(f"mysql://{username}:{password}@{host}:{port}/{database}") as store:
    #         return store
    elif db_type == REDIS:
        dbstore = RedisStore.from_conn_string(f"redis://{username}:{password}@{host}:{port}/{database}")
        return dbstore
    elif db_type == SQLITE:
        dbstore = SqliteStore.from_conn_string(f"sqlite:///{database}")
        return dbstore
    else:
        return None

def setup_dbstore():
    """
    Setup the store.
    """
    # Check whether or not using the same database for all purposes
    if int(os.getenv("ONE_DB", "0")) == 1:
        return get_dbsaver(
            os.getenv("DB_TYPE") or "", 
            os.getenv("DB_USERNAME") or "", 
            os.getenv("DB_PASSWORD") or "", 
            os.getenv("DB_HOST") or "", 
            int(os.getenv("DB_PORT") or "0"), 
            os.getenv("DB_NAME") or ""
        )
    else:
        return get_dbsaver(
            os.getenv("LANGGRAPH_STORE_TYPE") or "", 
            os.getenv("LANGGRAPH_STORE_USERNAME") or "", 
            os.getenv("LANGGRAPH_STORE_PASSWORD") or "", 
            os.getenv("LANGGRAPH_STORE_HOST") or "", 
            int(os.getenv("LANGGRAPH_STORE_PORT") or "0"), 
            os.getenv("LANGGRAPH_STORE_DATABASE") or ""
        )   