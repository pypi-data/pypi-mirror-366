"""
RAG (Retrieval-Augmented Generation) Module.

This module provides components for building RAG pipelines including:
- Text extraction from various sources
- Embedding models and vector databases
- Vector store operations
"""

from .text_extractor import (
    TextExtractor,
    extract_text_from_files,
    extract_text_from_apis,
    extract_text_from_urls,
    extract_text_from_mixed_sources,
    SUPPORTED_FILE_EXTENSIONS,
    SUPPORTED_MIME_TYPES
)

from .embedding_models import (
    OPENAI_EMBEDDING_MODELS,
    HUGGINGFACE_EMBEDDING_MODELS,
    COHERE_EMBEDDING_MODELS,
    GOOGLE_AI_EMBEDDING_MODELS,
    AZURE_OPENAI_EMBEDDING_MODELS,
    AWS_BEDROCK_EMBEDDING_MODELS,
    LOCAL_EMBEDDING_MODELS,
    JINA_EMBEDDING_MODELS,
    VECTARA_EMBEDDING_MODELS,
    VOYAGE_EMBEDDING_MODELS,
    OLLAMA_EMBEDDING_MODELS,
    GPT4ALL_EMBEDDING_MODELS,
    ALL_EMBEDDING_MODELS,
    RECOMMENDED_EMBEDDING_MODELS
)

from .vector_dbs import (
    IN_MEMORY_VECTOR_DBS,
    FILE_BASED_VECTOR_DBS,
    CLOUD_VECTOR_DBS,
    SELF_HOSTED_VECTOR_DBS,
    DATABASE_EXTENSION_VECTOR_DBS,
    SPECIALIZED_VECTOR_DBS,
    ALL_VECTOR_DBS,
    RECOMMENDED_VECTOR_DBS,
    VECTOR_DB_CATEGORIES,
    VECTOR_DB_FEATURES
)

__all__ = [
    # Text Extractor
    'TextExtractor',
    'extract_text_from_files',
    'extract_text_from_apis',
    'extract_text_from_urls',
    'extract_text_from_mixed_sources',
    'SUPPORTED_FILE_EXTENSIONS',
    'SUPPORTED_MIME_TYPES',
    
    # Embedding Models
    'OPENAI_EMBEDDING_MODELS',
    'HUGGINGFACE_EMBEDDING_MODELS',
    'COHERE_EMBEDDING_MODELS',
    'GOOGLE_AI_EMBEDDING_MODELS',
    'AZURE_OPENAI_EMBEDDING_MODELS',
    'AWS_BEDROCK_EMBEDDING_MODELS',
    'LOCAL_EMBEDDING_MODELS',
    'JINA_EMBEDDING_MODELS',
    'VECTARA_EMBEDDING_MODELS',
    'VOYAGE_EMBEDDING_MODELS',
    'OLLAMA_EMBEDDING_MODELS',
    'GPT4ALL_EMBEDDING_MODELS',
    'ALL_EMBEDDING_MODELS',
    'RECOMMENDED_EMBEDDING_MODELS',
    
    # Vector Databases
    'IN_MEMORY_VECTOR_DBS',
    'FILE_BASED_VECTOR_DBS',
    'CLOUD_VECTOR_DBS',
    'SELF_HOSTED_VECTOR_DBS',
    'DATABASE_EXTENSION_VECTOR_DBS',
    'SPECIALIZED_VECTOR_DBS',
    'ALL_VECTOR_DBS',
    'RECOMMENDED_VECTOR_DBS',
    'VECTOR_DB_CATEGORIES',
    'VECTOR_DB_FEATURES'
]

from .rag import RAGPipeline, RAGConfig, RAGResult, create_rag_pipeline