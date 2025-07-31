"""
RAG (Retrieval-Augmented Generation) Pipeline.

This module provides a complete RAG implementation that:
1. Extracts text from various sources (files, APIs, URLs)
2. Loads appropriate embedding models
3. Stores embeddings in vector databases
4. Provides retrieval and generation capabilities
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
import time
from dataclasses import dataclass

# LangChain imports
from langchain.chat_models.base import BaseChatModel
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.vectorstores.base import VectorStore
from langchain.embeddings.base import Embeddings
from langchain.chains import RetrievalQA
from langchain.chat_models.openai import ChatOpenAI

# Import our modules
from .text_extractor import extract_text_from_mixed_sources
from .embedding_models import (
    ALL_EMBEDDING_MODELS,
    GOOGLE_AI_EMBEDDING_MODELS,
    RECOMMENDED_EMBEDDING_MODELS,
    OPENAI_EMBEDDING_MODELS,
    HUGGINGFACE_EMBEDDING_MODELS,
    COHERE_EMBEDDING_MODELS,
    LOCAL_EMBEDDING_MODELS
)
from .vector_dbs import (
    ALL_VECTOR_DBS,
    RECOMMENDED_VECTOR_DBS,
    VECTOR_DB_FEATURES
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class RAGConfig:
    """Configuration for RAG pipeline."""
    embedding_model_name: str
    vector_db_type: str
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_workers: int = 10
    timeout: int = 30
    retry_attempts: int = 3
    include_metadata: bool = True
    persist_directory: Optional[str] = None
    collection_name: Optional[str] = None
    index_name: Optional[str] = None


@dataclass
class RAGResult:
    """Result from RAG operations."""
    query: str
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float
    processing_time: float
    metadata: Dict[str, Any]


class RAGPipeline:
    """
    Complete RAG pipeline implementation.
    
    Handles text extraction, embedding, vector storage, and retrieval.
    """
    
    def __init__(self, config: RAGConfig):
        """
        Initialize RAG pipeline.
        
        Args:
            config: RAG configuration
        """
        self.config = config
        self.embeddings = None
        self.vector_store = None
        self.qa_chain = None
        self.documents = []
        
        # Initialize components
        self._init_embeddings()
        self._init_text_splitter()

    def _get_default_embeddings(self) -> Embeddings:
        """Get default embeddings."""
        from langchain.embeddings import OpenAIEmbeddings
        return OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=self._get_openai_api_key()
        )

    def _init_embeddings(self):
        """Initialize embedding model based on configuration."""
        embedding_model_name = self.config.embedding_model_name
        
        try:
            if embedding_model_name in list(OPENAI_EMBEDDING_MODELS.values()):
                from langchain.embeddings import OpenAIEmbeddings
                self.embeddings = OpenAIEmbeddings(
                    model=embedding_model_name,
                    api_key=self._get_openai_api_key()
                )
                logger.info(f"Initialized OpenAI embeddings: {embedding_model_name}")
                
            elif embedding_model_name in list(HUGGINGFACE_EMBEDDING_MODELS.values()):
                from langchain.embeddings import HuggingFaceEmbeddings
                self.embeddings = HuggingFaceEmbeddings(
                    model_name=embedding_model_name,
                    model_kwargs={'device': 'cpu'}
                )
                logger.info(f"Initialized HuggingFace embeddings: {embedding_model_name}")
                
            elif embedding_model_name in list(COHERE_EMBEDDING_MODELS.values()):
                from langchain.embeddings import CohereEmbeddings
                self.embeddings = CohereEmbeddings(
                    model=embedding_model_name,
                    cohere_api_key=self._get_cohere_api_key()
                )
                logger.info(f"Initialized Cohere embeddings: {embedding_model_name}")
                
            elif embedding_model_name in list(LOCAL_EMBEDDING_MODELS.values()):
                from langchain.embeddings import HuggingFaceEmbeddings
                self.embeddings = HuggingFaceEmbeddings(
                    model_name=embedding_model_name,
                    model_kwargs={'device': 'cpu'}
                )
                logger.info(f"Initialized local embeddings: {embedding_model_name}")
            elif embedding_model_name in list(GOOGLE_AI_EMBEDDING_MODELS.values()):
                from langchain_google_genai import GoogleGenerativeAIEmbeddings
                self.embeddings = GoogleGenerativeAIEmbeddings(
                    model=embedding_model_name
                )
                logger.info(f"Initialized Google AI embeddings: {embedding_model_name}")
                
            else:
                raise ValueError(f"Unsupported embedding model: {embedding_model_name}")
                
        except ImportError as e:
            logger.error(f"Failed to import embedding model {embedding_model_name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize embedding model {embedding_model_name}: {e}")
            raise
    
    def _init_text_splitter(self):
        """Initialize text splitter for chunking documents."""
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def _get_openai_api_key(self) -> str:
        """Get OpenAI API key from environment."""
        import os
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        return api_key
    
    def _get_cohere_api_key(self) -> str:
        """Get Cohere API key from environment."""
        import os
        api_key = os.getenv('COHERE_API_KEY')
        if not api_key:
            raise ValueError("COHERE_API_KEY environment variable not set")
        return api_key
    
    def load_sources(self, sources: List[Dict[str, Any]]) -> List[Document]:
        """
        Load and process sources into documents.
        
        Args:
            sources: List of source configurations
            
        Returns:
            List of processed documents
        """
        logger.info(f"Loading {len(sources)} sources...")
        start_time = time.time()
        
        # Extract text from sources
        extraction_results = extract_text_from_mixed_sources(
            sources,
            max_workers=self.config.max_workers,
            timeout=self.config.timeout,
            retry_attempts=self.config.retry_attempts,
            include_metadata=self.config.include_metadata
        )
        
        # Convert to documents
        documents = []
        for result in extraction_results:
            if result.get('text'):
                # Create document with metadata
                metadata = {
                    'source_type': result.get('source_type', 'unknown'),
                    'source_path': result.get('file_path') or result.get('url', ''),
                    'file_type': result.get('file_type', ''),
                    'file_size': result.get('file_size', 0),
                    'extraction_time': result.get('extraction_time', 0),
                    'status_code': result.get('status_code', ''),
                    'content_type': result.get('content_type', ''),
                    'title': result.get('title', ''),
                    'description': result.get('description', ''),
                    'author': result.get('author', ''),
                    'language': result.get('language', ''),
                }
                
                # Add source-specific metadata
                if 'file_path' in result:
                    metadata['source_type'] = 'file'
                    metadata['file_name'] = result.get('file_name', '')
                    metadata['file_extension'] = result.get('file_extension', '')
                elif 'url' in result:
                    metadata['source_type'] = 'url'
                    metadata['method'] = result.get('method', 'GET')
                
                # Split text into chunks
                text_chunks = self.text_splitter.split_text(result['text'])
                
                for i, chunk in enumerate(text_chunks):
                    chunk_metadata = metadata.copy()
                    chunk_metadata['chunk_index'] = i
                    chunk_metadata['total_chunks'] = len(text_chunks)
                    
                    document = Document(
                        page_content=chunk,
                        metadata=chunk_metadata
                    )
                    documents.append(document)
        
        self.documents = documents
        processing_time = time.time() - start_time
        logger.info(f"Loaded {len(documents)} document chunks in {processing_time:.2f}s")
        
        return documents
    
    def create_vector_store(self, documents: List[Document]) -> VectorStore:
        """
        Create and populate vector store with documents.
        
        Args:
            documents: List of documents to store
            
        Returns:
            Configured vector store
        """
        logger.info(f"Creating vector store with {len(documents)} documents...")
        start_time = time.time()
        
        vector_db_type = self.config.vector_db_type.lower()
        
        try:
            if vector_db_type == 'faiss':
                from langchain.vectorstores import FAISS
                self.vector_store = FAISS.from_documents(
                    documents=documents,
                    embedding=self.embeddings or self._get_default_embeddings()
                )
                if self.config.persist_directory:
                    self.vector_store.save_local(self.config.persist_directory)
                    
            elif vector_db_type == 'chroma':
                from langchain_community.vectorstores import Chroma
                self.vector_store = Chroma.from_documents(
                    documents=documents,
                    embedding=self.embeddings,
                    persist_directory=self.config.persist_directory
                )
                
            elif vector_db_type == 'pinecone':
                from langchain.vectorstores import Pinecone
                import pinecone
                
                # Initialize Pinecone
                pinecone.init(
                    api_key=self._get_pinecone_api_key(),
                    environment=self._get_pinecone_environment()
                )
                
                index_name = self.config.index_name or "rag-index"
                self.vector_store = Pinecone.from_documents(
                    documents=documents,
                    embedding=self.embeddings or self._get_default_embeddings(),
                    index_name=index_name
                )
                
            elif vector_db_type == 'weaviate':
                from langchain.vectorstores import Weaviate
                import weaviate
                
                client = weaviate.WeaviateClient()
                collection_name = self.config.collection_name or "RAGDocuments"
                
                self.vector_store = Weaviate.from_documents(
                    documents=documents,
                    embedding=self.embeddings or self._get_default_embeddings(),
                    client=client,
                    index_name=collection_name
                )
                
            elif vector_db_type == 'qdrant':
                from langchain.vectorstores import Qdrant
                from qdrant_client import QdrantClient
                
                client = QdrantClient(
                    url=self._get_qdrant_url(),
                    api_key=self._get_qdrant_api_key()
                )
                collection_name = self.config.collection_name or "rag_documents"
                
                self.vector_store = Qdrant.from_documents(
                    documents=documents,
                    embedding=self.embeddings or self._get_default_embeddings(),
                    client=client,
                    collection_name=collection_name
                )
                
            elif vector_db_type == 'postgresql_pgvector':
                from langchain.vectorstores import PGVector
                
                connection_string = self._get_postgresql_connection_string()
                collection_name = self.config.collection_name or "rag_documents"
                
                self.vector_store = PGVector.from_documents(
                    documents=documents,
                    embedding=self.embeddings or self._get_default_embeddings(),
                    connection_string=connection_string,
                    collection_name=collection_name
                )
                
            else:
                raise ValueError(f"Unsupported vector database type: {vector_db_type}")
                
        except ImportError as e:
            logger.error(f"Failed to import vector database {vector_db_type}: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to create vector store {vector_db_type}: {e}")
            raise
        
        processing_time = time.time() - start_time
        logger.info(f"Created vector store in {processing_time:.2f}s")
        
        return self.vector_store
    
    def _get_pinecone_api_key(self) -> str:
        """Get Pinecone API key from environment."""
        import os
        api_key = os.getenv('PINECONE_API_KEY')
        if not api_key:
            raise ValueError("PINECONE_API_KEY environment variable not set")
        return api_key
    
    def _get_pinecone_environment(self) -> str:
        """Get Pinecone environment from environment."""
        import os
        environment = os.getenv('PINECONE_ENVIRONMENT')
        if not environment:
            raise ValueError("PINECONE_ENVIRONMENT environment variable not set")
        return environment
    
    def _get_weaviate_url(self) -> str:
        """Get Weaviate URL from environment."""
        import os
        url = os.getenv('WEAVIATE_URL', 'http://localhost:8080')
        return url
    
    def _get_qdrant_url(self) -> str:
        """Get Qdrant URL from environment."""
        import os
        url = os.getenv('QDRANT_URL', 'http://localhost:6333')
        return url
    
    def _get_qdrant_api_key(self) -> Optional[str]:
        """Get Qdrant API key from environment."""
        import os
        return os.getenv('QDRANT_API_KEY')
    
    def _get_postgresql_connection_string(self) -> str:
        """Get PostgreSQL connection string from environment."""
        import os
        connection_string = os.getenv('POSTGRESQL_CONNECTION_STRING')
        if not connection_string:
            raise ValueError("POSTGRESQL_CONNECTION_STRING environment variable not set")
        return connection_string
    
    def setup_qa_chain(self, llm: Optional[BaseChatModel] = None) -> RetrievalQA:
        """
        Set up QA chain for question answering.
        
        Args:
            llm: Language model to use (defaults to OpenAI)
            
        Returns:
            Configured QA chain
        """
        if not self.vector_store:
            raise ValueError("Vector store not initialized. Call create_vector_store() first.")
        
        if llm is None:
            # Default to OpenAI
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0,
                api_key=self._get_openai_api_key()
            )
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 4}
            ),
            return_source_documents=True
        )
        
        logger.info("QA chain initialized successfully")
        return self.qa_chain
    
    def query(self, question: str, k: int = 4) -> RAGResult:
        """
        Query the RAG system.
        
        Args:
            question: Question to ask
            k: Number of documents to retrieve
            
        Returns:
            RAG result with answer and sources
        """
        if not self.qa_chain:
            raise ValueError("QA chain not initialized. Call setup_qa_chain() first.")
        
        start_time = time.time()
        
        # Get answer and sources
        result = self.qa_chain.invoke(question)
        
        # Extract sources
        sources = []
        if 'source_documents' in result:
            for doc in result['source_documents']:
                source_info = {
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'source': doc.metadata.get('source_path', ''),
                    'title': doc.metadata.get('title', ''),
                    'chunk_index': doc.metadata.get('chunk_index', 0)
                }
                sources.append(source_info)
        
        # Calculate confidence (simple heuristic)
        confidence = min(1.0, len(sources) / k)
        
        processing_time = time.time() - start_time
        
        rag_result = RAGResult(
            query=question,
            answer=result.get('result', ''),
            sources=sources,
            confidence=confidence,
            processing_time=processing_time,
            metadata={
                'num_sources': len(sources),
                'embedding_model': self.config.embedding_model_name,
                'vector_db_type': self.config.vector_db_type
            }
        )
        
        return rag_result
    
    def similarity_search(self, query: str, k: int = 4) -> List[Tuple[Document, float]]:
        """
        Perform similarity search without LLM.
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of (document, score) tuples
        """
        if not self.vector_store:
            raise ValueError("Vector store not initialized. Call create_vector_store() first.")
        
        return self.vector_store.similarity_search_with_score(query, k=k)
    
    # def save_vector_store(self, path: str):
    #     """Save vector store to disk."""
    #     if not self.vector_store:
    #         raise ValueError("Vector store not initialized.")
        
    #     if hasattr(self.vector_store, 'persist'):
    #         self.vector_store.persist(path)
    #         logger.info(f"Vector store saved to {path}")
    #     else:
    #         logger.warning("This vector store type doesn't support local saving")
    
    def load_vector_store(self, path: str):
        """Load vector store from disk."""
        vector_db_type = self.config.vector_db_type.lower()
        
        if vector_db_type == 'faiss':
            from langchain_community.vectorstores import FAISS
            self.vector_store = FAISS.load_local(path, self.embeddings or self._get_default_embeddings())
        elif vector_db_type == 'chroma':
            from langchain_chroma import Chroma
            self.vector_store = Chroma(
                persist_directory=path,
                embedding_function=self.embeddings
            )
        else:
            raise ValueError(f"Loading not supported for vector database type: {vector_db_type}")
        
        logger.info(f"Vector store loaded from {path}")


def create_rag_pipeline(
    sources: List[Dict[str, Any]],
    embedding_model_name: str,
    vector_db_type: str,
    config: Optional[RAGConfig] = None,
    llm: Optional[BaseChatModel] = None,
    **kwargs
) -> RAGPipeline:
    """
    Create and initialize a complete RAG pipeline.
    
    Args:
        sources: List of source configurations
        embedding_model_name: Name of embedding model to use
        vector_db_type: Type of vector database to use
        config: Optional RAG configuration
        **kwargs: Additional configuration parameters
        
    Returns:
        Initialized RAG pipeline
    """
    # Create config if not provided
    if config is None:
        config = RAGConfig(
            embedding_model_name=embedding_model_name,
            vector_db_type=vector_db_type,
            **kwargs
        )

    # Validate configuration
    if embedding_model_name not in list(ALL_EMBEDDING_MODELS.values()):
        raise ValueError(f"Unsupported embedding model: {embedding_model_name}")
    
    if vector_db_type not in list(ALL_VECTOR_DBS.values()):
        raise ValueError(f"Unsupported vector database type: {vector_db_type}")
    
    # Create pipeline
    pipeline = RAGPipeline(config)
    
    # Load sources
    documents = pipeline.load_sources(sources)
    
    # Create vector store
    pipeline.create_vector_store(documents)
    if kwargs.get('enable_qa', True):
        # Setup QA chain
        pipeline.setup_qa_chain(llm)
    
    logger.info("RAG pipeline created successfully")
    return pipeline


def get_available_models() -> Dict[str, List[str]]:
    """Get available embedding models and vector databases."""
    return {
        'embedding_models': list(ALL_EMBEDDING_MODELS.values()),
        'recommended_embedding_models': list(RECOMMENDED_EMBEDDING_MODELS.values()),
        'vector_databases': list(ALL_VECTOR_DBS.values()),
        'recommended_vector_databases': list(RECOMMENDED_VECTOR_DBS.values())
    }


def get_model_info(embedding_model_name: str, vector_db_type: str) -> Dict[str, Any]:
    """Get information about specific models."""
    info = {
        'embedding_model': {
            'name': embedding_model_name,
            'supported': embedding_model_name in ALL_EMBEDDING_MODELS.values(),
            'recommended': embedding_model_name in RECOMMENDED_EMBEDDING_MODELS.values()
        },
        'vector_database': {
            'type': vector_db_type,
            'supported': vector_db_type in ALL_VECTOR_DBS.values(),
            'recommended': vector_db_type in RECOMMENDED_VECTOR_DBS.values(),
            'features': VECTOR_DB_FEATURES.get(vector_db_type.upper(), {})
        }
    }
    return info 