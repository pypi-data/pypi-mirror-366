"""
Constants for embedding models supported by LangChain.

This module contains constants representing the names of various embedding models
that can be used with LangChain's embedding interfaces.
"""

# OpenAI Embedding Models
OPENAI_EMBEDDING_MODELS = {
    "TEXT_EMBEDDING_ADA_002": "text-embedding-ada-002",
    "TEXT_EMBEDDING_3_SMALL": "text-embedding-3-small",
    "TEXT_EMBEDDING_3_LARGE": "text-embedding-3-large",
}

# Hugging Face Embedding Models
HUGGINGFACE_EMBEDDING_MODELS = {
    "ALL_MINI_LM_L6_V2": "sentence-transformers/all-MiniLM-L6-v2",
    "ALL_MPNET_BASE_V2": "sentence-transformers/all-mpnet-base-v2",
    "ALL_DISTILROBERTA_V1": "sentence-transformers/all-distilroberta-v1",
    "PARAPHRASE_MULTILINGUAL_MINI_LM_L12_V2": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    "MULTILINGUAL_E5_BASE": "intfloat/multilingual-e5-base",
    "MULTILINGUAL_E5_LARGE": "intfloat/multilingual-e5-large",
    "BGE_SMALL_EN_V1_5": "BAAI/bge-small-en-v1.5",
    "BGE_BASE_EN_V1_5": "BAAI/bge-base-en-v1.5",
    "BGE_LARGE_EN_V1_5": "BAAI/bge-large-en-v1.5",
    "BGE_SMALL_ZH_V1_5": "BAAI/bge-small-zh-v1.5",
    "BGE_BASE_ZH_V1_5": "BAAI/bge-base-zh-v1.5",
    "BGE_LARGE_ZH_V1_5": "BAAI/bge-large-zh-v1.5",
}

# Cohere Embedding Models
COHERE_EMBEDDING_MODELS = {
    "EMBED_ENGLISH_V3_0": "embed-english-v3.0",
    "EMBED_MULTILINGUAL_V3_0": "embed-multilingual-v3.0",
    "EMBED_ENGLISH_LIGHT_V3_0": "embed-english-light-v3.0",
    "EMBED_MULTILINGUAL_LIGHT_V3_0": "embed-multilingual-light-v3.0",
}

# Google AI (Vertex AI) Embedding Models
GOOGLE_AI_EMBEDDING_MODELS = {
    "GEMINI_EMBEDDING_EXP_03_07": "models/gemini-embedding-exp-03-07",
}

# Azure OpenAI Embedding Models
AZURE_OPENAI_EMBEDDING_MODELS = {
    "TEXT_EMBEDDING_ADA_002": "text-embedding-ada-002",
    "TEXT_EMBEDDING_3_SMALL": "text-embedding-3-small",
    "TEXT_EMBEDDING_3_LARGE": "text-embedding-3-large",
}

# AWS Bedrock Embedding Models
AWS_BEDROCK_EMBEDDING_MODELS = {
    "AMAZON_TITAN_EMBED_TEXT_V1": "amazon.titan-embed-text-v1",
    "COHERE_EMBED_ENGLISH_V3": "cohere.embed-english-v3",
    "COHERE_EMBED_MULTILINGUAL_V3": "cohere.embed-multilingual-v3",
}

# Local/Open Source Embedding Models
LOCAL_EMBEDDING_MODELS = {
    "INSTRUCTOR_LARGE": "hkunlp/instructor-large",
    "INSTRUCTOR_XL": "hkunlp/instructor-xl",
    "E5_LARGE_V2": "intfloat/e5-large-v2",
    "E5_BASE_V2": "intfloat/e5-base-v2",
    "E5_SMALL_V2": "intfloat/e5-small-v2",
    "GTE_LARGE": "thenlper/gte-large",
    "GTE_BASE": "thenlper/gte-base",
    "GTE_SMALL": "thenlper/gte-small",
}

# Jina AI Embedding Models
JINA_EMBEDDING_MODELS = {
    "JINA_EMBEDDINGS_V2_BASE_EN": "jina-embeddings-v2-base-en",
    "JINA_EMBEDDINGS_V2_BASE_DE": "jina-embeddings-v2-base-de",
    "JINA_EMBEDDINGS_V2_BASE_ZH": "jina-embeddings-v2-base-zh",
    "JINA_EMBEDDINGS_V2_SMALL_EN": "jina-embeddings-v2-small-en",
    "JINA_EMBEDDINGS_V2_SMALL_DE": "jina-embeddings-v2-small-de",
    "JINA_EMBEDDINGS_V2_SMALL_ZH": "jina-embeddings-v2-small-zh",
}

# Vectara Embedding Models
VECTARA_EMBEDDING_MODELS = {
    "VECTARA_EMBEDDINGS": "vectara-embeddings",
}

# Voyage AI Embedding Models
VOYAGE_EMBEDDING_MODELS = {
    "VOYAGE_01": "voyage-01",
    "VOYAGE_LARGE_2": "voyage-large-2",
    "VOYAGE_CODE_2": "voyage-code-2",
    "VOYAGE_FINANCE_2": "voyage-finance-2",
    "VOYAGE_LAW_2": "voyage-law-2",
    "VOYAGE_WORLD_2": "voyage-world-2",
}

# Ollama Embedding Models (Local)
OLLAMA_EMBEDDING_MODELS = {
    "NOMIC_EMBED_TEXT": "nomic-embed-text",
    "LLAMA2": "llama2",
    "MISTRAL": "mistral",
    "CODEGEM": "codegem",
}

# GPT4All Embedding Models (Local)
GPT4ALL_EMBEDDING_MODELS = {
    "GPT4ALL_FALCON": "gpt4all-falcon",
    "GPT4ALL_MPT": "gpt4all-mpt",
    "GPT4ALL_LLAMA": "gpt4all-llama",
}

# All embedding models combined
ALL_EMBEDDING_MODELS = {
    **OPENAI_EMBEDDING_MODELS,
    **HUGGINGFACE_EMBEDDING_MODELS,
    **COHERE_EMBEDDING_MODELS,
    **GOOGLE_AI_EMBEDDING_MODELS,
    **AZURE_OPENAI_EMBEDDING_MODELS,
    **AWS_BEDROCK_EMBEDDING_MODELS,
    **LOCAL_EMBEDDING_MODELS,
    **JINA_EMBEDDING_MODELS,
    **VECTARA_EMBEDDING_MODELS,
    **VOYAGE_EMBEDDING_MODELS,
    **OLLAMA_EMBEDDING_MODELS,
    **GPT4ALL_EMBEDDING_MODELS,
}

# Popular/Recommended embedding models
RECOMMENDED_EMBEDDING_MODELS = {
    "OPENAI_ADA_002": OPENAI_EMBEDDING_MODELS["TEXT_EMBEDDING_ADA_002"],
    "OPENAI_3_SMALL": OPENAI_EMBEDDING_MODELS["TEXT_EMBEDDING_3_SMALL"],
    "HUGGINGFACE_MINI_LM": HUGGINGFACE_EMBEDDING_MODELS["ALL_MINI_LM_L6_V2"],
    "HUGGINGFACE_MPNET": HUGGINGFACE_EMBEDDING_MODELS["ALL_MPNET_BASE_V2"],
    "COHERE_ENGLISH_V3": COHERE_EMBEDDING_MODELS["EMBED_ENGLISH_V3_0"],
    "BGE_SMALL_EN": HUGGINGFACE_EMBEDDING_MODELS["BGE_SMALL_EN_V1_5"],
    "BGE_BASE_EN": HUGGINGFACE_EMBEDDING_MODELS["BGE_BASE_EN_V1_5"],
    "E5_LARGE_V2": LOCAL_EMBEDDING_MODELS["E5_LARGE_V2"],
    "GTE_LARGE": LOCAL_EMBEDDING_MODELS["GTE_LARGE"],
} 