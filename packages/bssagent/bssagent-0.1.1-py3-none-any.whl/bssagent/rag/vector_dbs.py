"""
Constants for vector databases supported by LangChain.

This module contains constants representing the names of various vector databases
that can be used with LangChain's vector store interfaces.
"""

# In-Memory Vector Stores
IN_MEMORY_VECTOR_DBS = {
    "FAISS": "faiss",
    "CHROMA": "chroma",
    "HNSWLIB": "hnswlib",
    "ANNOY": "annoy",
    "DOCARRAY_IN_MEMORY": "docarray_in_memory",
}

# File-Based Vector Stores
FILE_BASED_VECTOR_DBS = {
    "FAISS": "faiss",
    "CHROMA": "chroma",
    "LANCE_DB": "lancedb",
    "DOCARRAY": "docarray",
    "SIMPLE_VECTOR_STORE": "simple_vector_store",
}

# Cloud-Based Vector Databases
CLOUD_VECTOR_DBS = {
    "PINECONE": "pinecone",
    "WEAVIATE_CLOUD": "weaviate_cloud",
    "QDANT_CLOUD": "qdrant_cloud",
    "MILVUS_CLOUD": "milvus_cloud",
    "ASTRA_DB": "astra_db",
    "SUPABASE_VECTOR": "supabase_vector",
    "VECTARA": "vectara",
    "ZILLIZ": "zilliz",
    "SINGLESTORE": "singlestore",
    "NEON": "neon",
}

# Self-Hosted Vector Databases
SELF_HOSTED_VECTOR_DBS = {
    "WEAVIATE": "weaviate",
    "QDANT": "qdrant",
    "MILVUS": "milvus",
    "CHROMA": "chroma",
    "LANCE_DB": "lancedb",
    "TYPESENSE": "typesense",
    "VALD": "vald",
    "VESPA": "vespa",
}

# Database Extensions with Vector Support
DATABASE_EXTENSION_VECTOR_DBS = {
    "POSTGRESQL_PGVECTOR": "postgresql_pgvector",
    "SQLITE_VSS": "sqlite_vss",
    "CLICKHOUSE": "clickhouse",
    "ELASTICSEARCH": "elasticsearch",
    "NEO4J": "neo4j",
    "REDIS": "redis",
    "MONGODB": "mongodb",
}

# Specialized Vector Stores
SPECIALIZED_VECTOR_DBS = {
    "DOCARRAY": "docarray",
    "VECTARA": "vectara",
    "ZILLIZ": "zilliz",
    "SINGLESTORE": "singlestore",
    "NEON": "neon",
    "TYPESENSE": "typesense",
    "VALD": "vald",
    "VESPA": "vespa",
    "ALIBABA_CLOUD_OPENSEARCH": "alibaba_cloud_opensearch",
    "AMAZON_OPENSEARCH": "amazon_opensearch",
    "AZURE_SEARCH": "azure_search",
    "GOOGLE_VERTEX_AI_SEARCH": "google_vertex_ai_search",
}

# All vector databases combined
ALL_VECTOR_DBS = {
    **IN_MEMORY_VECTOR_DBS,
    **FILE_BASED_VECTOR_DBS,
    **CLOUD_VECTOR_DBS,
    **SELF_HOSTED_VECTOR_DBS,
    **DATABASE_EXTENSION_VECTOR_DBS,
    **SPECIALIZED_VECTOR_DBS,
}

# Popular/Recommended vector databases
RECOMMENDED_VECTOR_DBS = {
    "FAISS": IN_MEMORY_VECTOR_DBS["FAISS"],
    "CHROMA": FILE_BASED_VECTOR_DBS["CHROMA"],
    "PINECONE": CLOUD_VECTOR_DBS["PINECONE"],
    "WEAVIATE": SELF_HOSTED_VECTOR_DBS["WEAVIATE"],
    "QDANT": SELF_HOSTED_VECTOR_DBS["QDANT"],
    "MILVUS": SELF_HOSTED_VECTOR_DBS["MILVUS"],
    "POSTGRESQL_PGVECTOR": DATABASE_EXTENSION_VECTOR_DBS["POSTGRESQL_PGVECTOR"],
    "REDIS": DATABASE_EXTENSION_VECTOR_DBS["REDIS"],
    "ELASTICSEARCH": DATABASE_EXTENSION_VECTOR_DBS["ELASTICSEARCH"],
    "VECTARA": SPECIALIZED_VECTOR_DBS["VECTARA"],
}

# Vector database categories for easy filtering
VECTOR_DB_CATEGORIES = {
    "IN_MEMORY": IN_MEMORY_VECTOR_DBS,
    "FILE_BASED": FILE_BASED_VECTOR_DBS,
    "CLOUD": CLOUD_VECTOR_DBS,
    "SELF_HOSTED": SELF_HOSTED_VECTOR_DBS,
    "DATABASE_EXTENSION": DATABASE_EXTENSION_VECTOR_DBS,
    "SPECIALIZED": SPECIALIZED_VECTOR_DBS,
}

# Vector database features comparison
VECTOR_DB_FEATURES = {
    "FAISS": {
        "type": "in_memory",
        "scalability": "medium",
        "ease_of_use": "high",
        "performance": "high",
        "cost": "low",
        "persistence": "file_based",
        "metadata_filtering": "limited",
        "hybrid_search": "no",
    },
    "CHROMA": {
        "type": "file_based",
        "scalability": "medium",
        "ease_of_use": "high",
        "performance": "medium",
        "cost": "low",
        "persistence": "file_based",
        "metadata_filtering": "yes",
        "hybrid_search": "yes",
    },
    "PINECONE": {
        "type": "cloud",
        "scalability": "high",
        "ease_of_use": "high",
        "performance": "high",
        "cost": "medium_high",
        "persistence": "managed",
        "metadata_filtering": "yes",
        "hybrid_search": "yes",
    },
    "WEAVIATE": {
        "type": "self_hosted_cloud",
        "scalability": "high",
        "ease_of_use": "medium",
        "performance": "high",
        "cost": "low_medium",
        "persistence": "managed",
        "metadata_filtering": "yes",
        "hybrid_search": "yes",
    },
    "QDANT": {
        "type": "self_hosted_cloud",
        "scalability": "high",
        "ease_of_use": "medium",
        "performance": "very_high",
        "cost": "low_medium",
        "persistence": "managed",
        "metadata_filtering": "yes",
        "hybrid_search": "yes",
    },
    "MILVUS": {
        "type": "self_hosted",
        "scalability": "very_high",
        "ease_of_use": "low",
        "performance": "very_high",
        "cost": "low",
        "persistence": "managed",
        "metadata_filtering": "yes",
        "hybrid_search": "yes",
    },
    "POSTGRESQL_PGVECTOR": {
        "type": "database_extension",
        "scalability": "high",
        "ease_of_use": "medium",
        "performance": "high",
        "cost": "low",
        "persistence": "database",
        "metadata_filtering": "yes",
        "hybrid_search": "yes",
    },
    "REDIS": {
        "type": "database_extension",
        "scalability": "high",
        "ease_of_use": "medium",
        "performance": "very_high",
        "cost": "low",
        "persistence": "database",
        "metadata_filtering": "yes",
        "hybrid_search": "yes",
    },
    "ELASTICSEARCH": {
        "type": "database_extension",
        "scalability": "high",
        "ease_of_use": "medium",
        "performance": "high",
        "cost": "medium",
        "persistence": "database",
        "metadata_filtering": "yes",
        "hybrid_search": "yes",
    },
    "VECTARA": {
        "type": "specialized",
        "scalability": "high",
        "ease_of_use": "high",
        "performance": "high",
        "cost": "medium_high",
        "persistence": "managed",
        "metadata_filtering": "yes",
        "hybrid_search": "yes",
    },
} 